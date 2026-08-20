"""
FastAPI Server & Background Daemon for Google Cloud Run.
Exposes RESTful endpoints for autonomous document auditing, PO management, and dispute processing.
"""

import os
from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import List, Optional

from documa.models import DocumentAuditRequest, DocumentAuditResponse, PurchaseOrder, AuditResult, DiscrepancyReport
from documa.services.firestore_service import FirestoreService
from documa.services.storage_service import StorageService
from documa.services.eventarc_simulator import EventarcTriggerHandler
from documa.agents.orchestrator import DocumaFleet
from documa.sample_data.seed_data import seed_sample_purchase_orders

app = FastAPI(
    title="Documa — Autonomous Multimodal Audit & Procurement Fleet API",
    description="Google Cloud Run service powered by Gemini 3.5 Flash and Antigravity SDK.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global service instances
firestore_service = FirestoreService()
storage_service = StorageService()
fleet = DocumaFleet(firestore_service=firestore_service, storage_service=storage_service)
eventarc_handler = EventarcTriggerHandler(fleet=fleet)

# Seed initial PO database on startup
seed_sample_purchase_orders(firestore_service)

# Mount static files directory
static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/")
def read_root():
    """Serves the interactive Documa Web Dashboard UI."""
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {
        "service": "Documa — Autonomous Multimodal Audit & Procurement Fleet",
        "status": "OPERATIONAL",
        "model": "Gemini 3.5 Flash",
        "framework": "Antigravity SDK",
        "cloud": "Google Cloud Run"
    }


@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": os.getenv("PORT", "8080")}


@app.post("/api/audit/process", response_model=DocumentAuditResponse)
def process_audit_document(request: DocumentAuditRequest):
    """Submits a document for autonomous vision extraction, contract audit, and discrepancy resolution."""
    try:
        response = fleet.process_document(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Audit processing error: {str(e)}")


@app.post("/api/events/gcs", response_model=DocumentAuditResponse)
def process_gcs_eventarc_trigger(event_payload: dict = Body(...)):
    """Asynchronous Cloud Storage Eventarc notification trigger handler for Cloud Run."""
    try:
        response = eventarc_handler.handle_gcs_event(event_payload)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Eventarc trigger processing error: {str(e)}")


@app.get("/api/po", response_model=List[PurchaseOrder])
def list_purchase_orders():
    """List all active Purchase Orders in Firestore."""
    return firestore_service.list_purchase_orders()


@app.post("/api/po", response_model=PurchaseOrder)
def create_purchase_order(po: PurchaseOrder):
    """Create or update a Purchase Order record in Firestore."""
    firestore_service.save_purchase_order(po)
    return po


@app.get("/api/audit/logs", response_model=List[AuditResult])
def list_audit_logs():
    """Retrieve audit history records from Firestore."""
    return firestore_service.list_audit_results()


@app.get("/api/disputes", response_model=List[DiscrepancyReport])
def list_discrepancy_reports():
    """Retrieve generated vendor discrepancy reports and human approval alerts."""
    return firestore_service.list_discrepancy_reports()


@app.post("/api/disputes/{report_id}/approve")
def approve_dispute_override(report_id: str, new_action: str = Body(..., embed=True)):
    """Human finance manager approval or status override endpoint."""
    success = firestore_service.update_discrepancy_action(report_id, new_action)
    if not success:
        raise HTTPException(status_code=404, detail=f"Discrepancy report {report_id} not found.")
    return {"report_id": report_id, "status": "UPDATED", "new_action": new_action}
