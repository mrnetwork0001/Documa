"""
Eventarc GCS Event Trigger Service for Documa.
Processes Google Cloud Storage object finalized events asynchronously on Cloud Run.
"""

import logging
from typing import Dict, Any
from documa.models import DocumentAuditRequest, DocumentAuditResponse
from documa.agents.orchestrator import DocumaFleet

logger = logging.getLogger("EventarcTrigger")


class EventarcTriggerHandler:
    """Handles GCS bucket notification payloads (Cloud Storage Object Finalized)."""

    def __init__(self, fleet: DocumaFleet):
        self.fleet = fleet

    def handle_gcs_event(self, event_payload: Dict[str, Any]) -> DocumentAuditResponse:
        """
        Parses Eventarc / Cloud Storage notification payload:
        {
          "name": "receipts/compliant_invoice.png",
          "bucket": "documa-receipts-bucket",
          "contentType": "image/png"
        }
        """
        bucket = event_payload.get("bucket", "documa-receipts-bucket")
        name = event_payload.get("name", "receipts/compliant_invoice.png")
        
        gcs_uri = f"gs://{bucket}/{name}"
        document_id = name.split("/")[-1].split(".")[0].upper()

        logger.info(f"Eventarc trigger received for object: {gcs_uri}")

        request = DocumentAuditRequest(
            document_id=f"EVT-{document_id}",
            file_path_or_url=gcs_uri,
            po_number_override="PO-9921"
        )

        return self.fleet.process_document(request)
