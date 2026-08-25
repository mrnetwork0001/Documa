"""
Documa — Autonomous Multimodal Audit & Procurement Fleet CLI Runner.
Built for the Google All Things Agentic Hackathon ($180,000 Cash Pool).
Powered by Gemini 3.5 Flash, Antigravity SDK, and Google Cloud Run.
"""

import os
import sys
import json
from documa.models import DocumentAuditRequest
from documa.services.firestore_service import FirestoreService
from documa.services.storage_service import StorageService
from documa.agents.orchestrator import DocumaFleet
from documa.sample_data.seed_data import seed_sample_purchase_orders


def print_banner():
    print("==========================================================================================")
    print(" 👁️ DOCUMA — Autonomous Multimodal Audit & Procurement Fleet")
    print(" Powered by Gemini 3.5 Flash + Antigravity SDK + Google Cloud Run")
    print("==========================================================================================")


def run_demo():
    print_banner()

    firestore_service = FirestoreService()
    storage_service = StorageService()
    seed_sample_purchase_orders(firestore_service)

    fleet = DocumaFleet(firestore_service=firestore_service, storage_service=storage_service)

    test_scenarios = [
        {
            "title": "Scenario 1: Compliant Receipt Audit (Auto-Approved Payout)",
            "document_id": "DOC-COMPLIANT-101",
            "file_path": "receipts/compliant_invoice.png",
            "po_override": "PO-9921"
        },
        {
            "title": "Scenario 2: Major Unit Price Overcharge Audit (Human Finance Escalation Alert)",
            "document_id": "DOC-OVERCHARGE-202",
            "file_path": "receipts/overcharged_invoice.png",
            "po_override": "PO-9921"
        },
        {
            "title": "Scenario 3: Unauthorized Line Item Audit (Human Finance Escalation Alert)",
            "document_id": "DOC-UNAUTHORIZED-303",
            "file_path": "receipts/unauthorized_fees_invoice.png",
            "po_override": "PO-9921"
        },
        {
            "title": "Scenario 4: Minor Overcharge Audit (Autonomous Vendor Dispute Notice)",
            "document_id": "DOC-MINOR-404",
            "file_path": "receipts/minor_overcharge_invoice.png",
            "po_override": "PO-9921"
        }
    ]

    total = len(test_scenarios)
    for idx, test in enumerate(test_scenarios, 1):
        print(f"\n------------------------------------------------------------------------------------------")
        print(f" ▶ [{idx}/{total}] {test['title']}")
        print(f"   Document ID: {test['document_id']} | Target PO: {test['po_override']}")
        print(f"------------------------------------------------------------------------------------------")

        req = DocumentAuditRequest(
            document_id=test["document_id"],
            file_path_or_url=test["file_path"],
            po_number_override=test["po_override"]
        )

        response = fleet.process_document(req)

        print(f"\n   [Agent 1: Multimodal Vision]")
        print(f"   Extraction Mode: {response.extracted_document.extraction_mode.value}")
        print(f"   Vendor Extracted: {response.extracted_document.vendor_name}")
        print(f"   Line Items Count: {len(response.extracted_document.line_items)}")
        print(f"   Billed Grand Total: ${response.extracted_document.grand_total:.2f} USD")

        print(f"\n   [Agent 2: Contract Auditor]")
        print(f"   Audit Status: {response.audit_result.status.value}")
        print(f"   Net Variance: ${response.audit_result.net_variance:.2f} USD")
        print(f"   Discrepancies Detected: {len(response.audit_result.discrepancies)}")

        print(f"\n   [Agent 3: Discrepancy Dispatcher]")
        if response.discrepancy_report:
            print(f"   Action Taken: {response.discrepancy_report.action_taken.value}")
            print(f"   Human Escalation Required: {response.discrepancy_report.requires_human_signature}")

            print(f"\n   --- DISPATCHED MARKDOWN OUTPUT ---")
            print(response.discrepancy_report.formal_dispute_markdown.strip())
            print(f"   ----------------------------------")

    print("\n==========================================================================================")
    print(" ✅ Documa Fleet Multi-Agent Execution Completed Successfully!")
    print("==========================================================================================\n")


if __name__ == "__main__":
    run_demo()
