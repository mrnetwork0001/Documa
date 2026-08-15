"""
Automated unit & integration test suite for Documa Multi-Agent Fleet.
"""

import pytest
from documa.models import DocumentAuditRequest, AuditStatus, ActionTaken
from documa.services.firestore_service import FirestoreService
from documa.services.storage_service import StorageService
from documa.agents.vision_agent import VisionAgent
from documa.agents.auditor_agent import AuditorAgent
from documa.agents.discrepancy_agent import DiscrepancyAgent
from documa.agents.orchestrator import DocumaFleet
from documa.sample_data.seed_data import seed_sample_purchase_orders


@pytest.fixture
def services():
    firestore = FirestoreService()
    storage = StorageService()
    seed_sample_purchase_orders(firestore)
    return firestore, storage


def test_vision_agent_mock_extraction(services):
    firestore, storage = services
    agent = VisionAgent(storage_service=storage)
    
    # Test compliant document extraction
    doc = agent._extract_mock_fallback("receipts/compliant.png", "DOC-001")
    assert doc.vendor_name == "Acme Industrial Tech"
    assert len(doc.line_items) == 2
    assert doc.grand_total == 3250.0


def test_auditor_agent_compliant(services):
    firestore, storage = services
    vision_agent = VisionAgent(storage_service=storage)
    auditor_agent = AuditorAgent(firestore_service=firestore)

    doc = vision_agent._extract_mock_fallback("receipts/compliant.png", "DOC-001")
    from documa.sdk.antigravity_sdk import AgentState
    state = AgentState(session_id="TEST-01")

    result = auditor_agent.run(doc, state)

    assert result.status == AuditStatus.APPROVED
    assert result.net_variance <= 1.0
    assert len(result.discrepancies) == 0


def test_auditor_agent_overcharge(services):
    firestore, storage = services
    vision_agent = VisionAgent(storage_service=storage)
    auditor_agent = AuditorAgent(firestore_service=firestore)

    doc = vision_agent._extract_mock_fallback("receipts/doc-overcharge.png", "DOC-002")
    from documa.sdk.antigravity_sdk import AgentState
    state = AgentState(session_id="TEST-02")

    result = auditor_agent.run(doc, state)

    assert result.status in [AuditStatus.DISCREPANCY_DETECTED, AuditStatus.REQUIRES_HUMAN_APPROVAL]
    assert result.net_variance > 0.0
    assert len(result.discrepancies) > 0


def test_discrepancy_dispatcher_actions(services):
    firestore, storage = services
    vision_agent = VisionAgent(storage_service=storage)
    auditor_agent = AuditorAgent(firestore_service=firestore)
    discrepancy_agent = DiscrepancyAgent(firestore_service=firestore)

    # Run compliant pipeline
    doc = vision_agent._extract_mock_fallback("receipts/compliant.png", "DOC-001")
    from documa.sdk.antigravity_sdk import AgentState
    state = AgentState(session_id="TEST-03")

    audit = auditor_agent.run(doc, state)
    report = discrepancy_agent.run(audit, state)

    assert report.action_taken == ActionTaken.AUTO_APPROVED_PAYOUT
    assert report.requires_human_signature is False


def test_fleet_orchestration_end_to_end(services):
    firestore, storage = services
    fleet = DocumaFleet(firestore_service=firestore, storage_service=storage)

    req = DocumentAuditRequest(
        document_id="DOC-TEST-END2END",
        file_path_or_url="receipts/doc-unauthorized.png",
        po_number_override="PO-9921"
    )

    response = fleet.process_document(req)

    assert response.success is True
    assert response.extracted_document is not None
    assert response.audit_result is not None
    assert response.discrepancy_report is not None
    assert len(response.execution_log) > 0
