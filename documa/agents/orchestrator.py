"""
Documa Multi-Agent Fleet Orchestrator.
Coordinates VisionAgent, AuditorAgent, and DiscrepancyAgent execution.
"""

import uuid
import logging
from typing import Dict, Any, Optional
from documa.sdk.antigravity_sdk import AntigravityFleetOrchestrator
from documa.agents.vision_agent import VisionAgent
from documa.agents.auditor_agent import AuditorAgent
from documa.agents.discrepancy_agent import DiscrepancyAgent
from documa.models import DocumentAuditRequest, DocumentAuditResponse, ExtractedDocument, AuditResult, DiscrepancyReport
from documa.services.firestore_service import FirestoreService
from documa.services.storage_service import StorageService

logger = logging.getLogger("DocumaFleet")


class DocumaFleet:
    """Master orchestrator for the Documa multi-agent procurement fleet."""

    def __init__(self, firestore_service: Optional[FirestoreService] = None, storage_service: Optional[StorageService] = None):
        self.firestore = firestore_service or FirestoreService()
        self.storage = storage_service or StorageService()

        self.vision_agent = VisionAgent(storage_service=self.storage)
        self.auditor_agent = AuditorAgent(firestore_service=self.firestore)
        self.discrepancy_agent = DiscrepancyAgent(firestore_service=self.firestore)

    def process_document(self, request: DocumentAuditRequest) -> DocumentAuditResponse:
        """Executes full end-to-end document intake, audit, and discrepancy dispatch workflow."""
        session_id = f"SES-{uuid.uuid4().hex[:8].upper()}"
        orchestrator = AntigravityFleetOrchestrator(session_id=session_id)

        orchestrator.add_agent(self.vision_agent)
        orchestrator.add_agent(self.auditor_agent)
        orchestrator.add_agent(self.discrepancy_agent)

        if request.po_number_override:
            orchestrator.state.set("po_number_override", request.po_number_override)

        input_data = {
            "document_id": request.document_id,
            "file_path_or_url": request.file_path_or_url
        }

        pipeline = [
            "MultimodalVisionAgent",
            "ContractAuditorAgent",
            "DiscrepancyDispatcherAgent"
        ]

        final_result = orchestrator.execute_pipeline(input_data, pipeline)

        extracted_doc: ExtractedDocument = orchestrator.state.get("extracted_document")
        audit_result: AuditResult = orchestrator.state.get("audit_result")
        discrepancy_report: DiscrepancyReport = orchestrator.state.get("discrepancy_report")

        return DocumentAuditResponse(
            success=True,
            extracted_document=extracted_doc,
            audit_result=audit_result,
            discrepancy_report=discrepancy_report,
            execution_log=orchestrator.state.execution_logs
        )
