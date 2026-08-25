"""
Antigravity SDK integration layer for the Documa multi-agent fleet.

Documa's agents are synchronous, but the official Google Antigravity SDK
(``pip install google-antigravity``) is async-only. This module wraps the real
SDK behind the synchronous ``BaseAgent`` / ``AgentState`` / orchestrator
interface the fleet already uses, so agent code stays plain Python while every
model call runs on the real Antigravity harness.

Model access is resolved from the environment:
  * ``GEMINI_API_KEY`` / ``GOOGLE_API_KEY``  -> Gemini API
  * ``GOOGLE_GENAI_USE_VERTEXAI=true`` plus ``GOOGLE_CLOUD_PROJECT`` -> Vertex AI
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional, Sequence, Type, Union

from pydantic import BaseModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AntigravitySDK")

DEFAULT_MODEL = "gemini-3.5-flash"

# Documa agents perform pure document inference. The Antigravity local harness
# enables filesystem and shell tools by default, which is unacceptable for an
# agent whose input is an untrusted third-party invoice -- a malicious document
# could attempt tool-driven prompt injection. Everything except the terminal
# FINISH tool is disabled, and a deny-all policy backs that up.
_DISABLED_TOOLS = (
    "run_command",
    "create_file",
    "edit_file",
    "view_file",
    "find_file",
    "list_directory",
    "search_directory",
    "search_web",
    "read_url_content",
    "generate_image",
    "start_subagent",
    "ask_question",
)


class AntigravityUnavailableError(RuntimeError):
    """Raised when a model call cannot be served by the real Antigravity harness.

    Documa deliberately raises instead of silently degrading: a fabricated
    extraction that looks like a successful one is worse than a visible failure.
    """


def _run_sync(coro):
    """Runs an async coroutine from synchronous code.

    Safe both off the event loop (FastAPI's ``def`` endpoints, the CLI, pytest)
    and on it (FastAPI's ``async def`` endpoints), where ``asyncio.run`` would
    otherwise raise.
    """
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)

    with ThreadPoolExecutor(max_workers=1) as pool:
        return pool.submit(asyncio.run, coro).result()


def build_media_part(data: bytes, mime_type: str, description: str = ""):
    """Wraps raw document bytes in the right Antigravity content primitive."""
    import google.antigravity as ag

    primitive = ag.Document if mime_type == "application/pdf" else ag.Image
    return primitive(data=data, mime_type=mime_type, description=description)


class AgentState:
    """Persistent state container shared across agents in an execution pipeline."""

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.data: Dict[str, Any] = {}
        self.execution_logs: List[Dict[str, Any]] = []

    def set(self, key: str, value: Any):
        self.data[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        return self.data.get(key, default)

    def log(self, agent_name: str, action: str, details: Dict[str, Any]):
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "agent": agent_name,
            "action": action,
            "details": details,
        }
        self.execution_logs.append(entry)
        logger.info(f"[{agent_name}] {action}: {json.dumps(details, default=str)[:120]}...")


class BaseAgent:
    """Base Agent class backed by the official Google Antigravity SDK."""

    def __init__(self, name: str, role: str, model_name: str = DEFAULT_MODEL):
        self.name = name
        self.role = role
        self.model_name = model_name
        self.tools: Dict[str, Callable] = {}
        self._configure_model()

    def _configure_model(self):
        """Resolves Antigravity availability and Gemini/Vertex credentials."""
        self.api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        self.use_vertex = os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "").lower() in ("1", "true", "yes")
        self.project = os.getenv("GOOGLE_CLOUD_PROJECT")
        self.location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")

        try:
            import google.antigravity  # noqa: F401

            self.sdk_available = True
        except ImportError:
            self.sdk_available = False
            logger.warning(
                f"[{self.name}] google-antigravity is not installed. "
                "Run 'pip install google-antigravity' to enable live model calls."
            )

        self.model_available = self.sdk_available and bool(
            self.api_key or (self.use_vertex and self.project)
        )

        if self.model_available:
            backend = "Vertex AI" if self.use_vertex else "Gemini API"
            logger.info(f"[{self.name}] Antigravity harness ready ({self.model_name} via {backend}).")
        elif self.sdk_available:
            logger.warning(
                f"[{self.name}] No GEMINI_API_KEY (or Vertex project) set. "
                "Live model calls will raise AntigravityUnavailableError."
            )

    def register_tool(self, tool_name: str, func: Callable):
        """Register a function tool with the agent."""
        self.tools[tool_name] = func

    def _agent_config(
        self,
        response_schema: Optional[Union[Type[BaseModel], Dict[str, Any]]],
        system_instructions: Optional[str],
    ):
        import google.antigravity as ag
        from google.antigravity import policy

        kwargs: Dict[str, Any] = {
            "system_instructions": system_instructions or self.role,
            "model": self.model_name,
            "capabilities": ag.CapabilitiesConfig(disabled_tools=list(_DISABLED_TOOLS)),
            "policies": [policy.deny_all()],
        }
        if response_schema is not None:
            kwargs["response_schema"] = response_schema
        if self.use_vertex and self.project:
            kwargs["vertex"] = True
            kwargs["project"] = self.project
            kwargs["location"] = self.location
        elif self.api_key:
            kwargs["api_key"] = self.api_key

        return ag.LocalAgentConfig(**kwargs)

    async def _generate_async(self, parts, response_schema, system_instructions):
        import google.antigravity as ag

        config = self._agent_config(response_schema, system_instructions)
        async with ag.Agent(config) as agent:
            response = await agent.chat(list(parts))

            if response_schema is None:
                return await response.text()

            payload = await response.structured_output()
            if payload is not None:
                return payload

            # Harness returned prose despite a schema -- recover if it is JSON,
            # otherwise fail loudly rather than guessing.
            text = await response.text()
            try:
                return json.loads(text)
            except json.JSONDecodeError as exc:
                raise AntigravityUnavailableError(
                    f"Antigravity returned no structured output for {self.name}: {text[:200]}"
                ) from exc

    def generate(
        self,
        parts: Sequence[Any],
        response_schema: Optional[Union[Type[BaseModel], Dict[str, Any]]] = None,
        system_instructions: Optional[str] = None,
    ) -> Any:
        """Synchronously runs one turn on the Antigravity harness.

        Returns parsed structured output when ``response_schema`` is supplied,
        otherwise the response text. Raises ``AntigravityUnavailableError``
        rather than returning fabricated data when the harness cannot run.
        """
        if not self.sdk_available:
            raise AntigravityUnavailableError(
                "google-antigravity is not installed. Run 'pip install google-antigravity'."
            )
        if not self.model_available:
            raise AntigravityUnavailableError(
                "No Gemini credentials found. Set GEMINI_API_KEY, or set "
                "GOOGLE_GENAI_USE_VERTEXAI=true with GOOGLE_CLOUD_PROJECT for Vertex AI."
            )

        return _run_sync(self._generate_async(parts, response_schema, system_instructions))

    def run(self, input_data: Any, state: AgentState) -> Any:
        """Core execution entrypoint for agent subclasses."""
        raise NotImplementedError("Subclasses must implement run()")


class AntigravityFleetOrchestrator:
    """Coordinates message passing and sequential execution across an Agent Fleet."""

    def __init__(self, session_id: str):
        self.state = AgentState(session_id=session_id)
        self.agents: Dict[str, BaseAgent] = {}

    def add_agent(self, agent: BaseAgent):
        self.agents[agent.name] = agent

    def execute_pipeline(self, initial_input: Any, agent_pipeline: List[str]) -> Any:
        """Executes a list of agents sequentially, passing updated state down the chain."""
        current_data = initial_input
        self.state.log(
            "Orchestrator",
            "StartPipeline",
            {"pipeline": agent_pipeline, "session_id": self.state.session_id},
        )

        for agent_name in agent_pipeline:
            if agent_name not in self.agents:
                raise ValueError(f"Agent '{agent_name}' not registered in Antigravity fleet.")
            agent = self.agents[agent_name]
            self.state.log(
                "Orchestrator",
                f"Executing_{agent_name}",
                {"input_type": type(current_data).__name__},
            )
            current_data = agent.run(current_data, self.state)

        self.state.log("Orchestrator", "PipelineCompleted", {"logs_count": len(self.state.execution_logs)})
        return current_data
