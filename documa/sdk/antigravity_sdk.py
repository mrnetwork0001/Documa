"""
Antigravity SDK Base Classes and Framework Abstractions.
Provides multi-agent routing, tool calling, state management, and Gemini 3.5 Flash model integration.
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional, Callable, Type
from datetime import datetime, timezone

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AntigravitySDK")


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
            "details": details
        }
        self.execution_logs.append(entry)
        logger.info(f"[{agent_name}] {action}: {json.dumps(details, default=str)[:120]}...")


class BaseAgent:
    """Base Agent class in the Antigravity SDK specification."""
    def __init__(self, name: str, role: str, model_name: str = "gemini-3.5-flash"):
        self.name = name
        self.role = role
        self.model_name = model_name
        self.tools: Dict[str, Callable] = {}
        self._init_genai()

    def _init_genai(self):
        """Initializes the Google GenAI SDK if GEMINI_API_KEY or GOOGLE_API_KEY is available."""
        self.api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        self.client = None
        if self.api_key:
            try:
                from google import genai
                self.client = genai.Client(api_key=self.api_key)
                logger.info(f"[{self.name}] Initialized GenAI Client with model {self.model_name}")
            except Exception as e:
                logger.warning(f"[{self.name}] Could not initialize google-genai client: {e}. Falling back to simulation mode.")
        else:
            logger.info(f"[{self.name}] No GEMINI_API_KEY found. Agent operating in deterministic/fallback mode.")

    def register_tool(self, tool_name: str, func: Callable):
        """Register a function tool with the agent."""
        self.tools[tool_name] = func

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
        self.state.log("Orchestrator", "StartPipeline", {"pipeline": agent_pipeline, "session_id": self.state.session_id})

        for agent_name in agent_pipeline:
            if agent_name not in self.agents:
                raise ValueError(f"Agent '{agent_name}' not registered in Antigravity fleet.")
            agent = self.agents[agent_name]
            self.state.log("Orchestrator", f"Executing_{agent_name}", {"input_type": type(current_data).__name__})
            current_data = agent.run(current_data, self.state)

        self.state.log("Orchestrator", "PipelineCompleted", {"logs_count": len(self.state.execution_logs)})
        return current_data
