"""
FastAPI Server & Background Daemon for Google Cloud Run.
Exposes RESTful endpoints for autonomous document auditing, PO management, and dispute processing.
"""

import os
import pathlib
from fastapi import FastAPI, HTTPException, Body, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, Response
from typing import List, Optional
import shutil
import csv
import io

from documa.models import DocumentAuditRequest, DocumentAuditResponse, PurchaseOrder, AuditResult, DiscrepancyReport, HumanDecision
from documa.services.firestore_service import FirestoreService
from documa.services.storage_service import StorageService
from documa.services.eventarc_simulator import EventarcTriggerHandler
from documa.agents.orchestrator import DocumaFleet
from documa.sample_data.seed_data import seed_sample_purchase_orders

app = FastAPI(
    title="Documa - Autonomous Multimodal Audit & Procurement Fleet API",
    description="Google Cloud Run service powered by Gemini 3.5 Flash and Antigravity SDK.",
    version="1.0.0",
    # /docs serves the Documa documentation site; the interactive schema
    # explorer moves aside rather than being disabled.
    docs_url="/openapi-docs",
    redoc_url="/openapi-redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def revalidate_static_assets(request, call_next):
    """Forces browsers to revalidate stylesheets, scripts and documents.

    Without this a cached stylesheet renders the current markup with stale rules -
    an unstyled button in place of the menu, for instance - which looks like a
    broken build rather than a caching artefact. StaticFiles still serves ETags,
    so an unchanged asset costs a 304 rather than a re-download.
    """
    response = await call_next(request)
    path = request.url.path
    if path.startswith(("/static/", "/receipts/")) or path in ("/", "/app", "/docs"):
        response.headers["Cache-Control"] = "no-cache"
    return response

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

# Mount receipts directory for live document previews
receipts_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "receipts")
os.makedirs(receipts_dir, exist_ok=True)
app.mount("/receipts", StaticFiles(directory=receipts_dir), name="receipts")


import re as _re


def _serve_page(filename: str) -> HTMLResponse:
    """Serves an HTML page with cache-busted asset URLs.

    Every /static/*.css and /static/*.js reference is stamped with the file's
    mtime (?v=...). A changed asset therefore gets a URL the browser has never
    cached, which defeats even stylesheets cached before no-cache headers were
    introduced - the failure mode that rendered the menu button unstyled.
    """
    html = pathlib.Path(static_dir, filename).read_text()

    def stamp(match: "_re.Match") -> str:
        rel = match.group(1)
        asset = os.path.join(static_dir, os.path.basename(rel))
        try:
            version = int(os.path.getmtime(asset))
        except OSError:
            return match.group(0)
        return f'/static/{os.path.basename(rel)}?v={version}'

    html = _re.sub(r'/static/([A-Za-z0-9_.-]+\.(?:css|js))', stamp, html)
    return HTMLResponse(content=html)



@app.get("/")
def read_landing_page():
    """Serves the Documa Landing Page with Launch App CTA."""
    if os.path.exists(os.path.join(static_dir, "landing.html")):
        return _serve_page("landing.html")
    return _serve_page("index.html")


@app.get("/app")
def read_dashboard_app():
    """Serves the interactive Documa Web Dashboard UI."""
    if os.path.exists(os.path.join(static_dir, "index.html")):
        return _serve_page("index.html")
    return {
        "service": "Documa - Autonomous Multimodal Audit & Procurement Fleet",
        "status": "OPERATIONAL",
        "model": "Gemini 3.5 Flash",
        "framework": "Antigravity SDK",
        "cloud": "Google Cloud Run"
    }


@app.get("/docs", include_in_schema=False)
def read_docs_page():
    """Serves the Documa documentation site.

    Overrides FastAPI's default Swagger UI at /docs; the interactive schema
    explorer stays available at /openapi-docs.
    """
    if os.path.exists(os.path.join(static_dir, "docs.html")):
        return _serve_page("docs.html")
    raise HTTPException(status_code=404, detail="Documentation page not found.")


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


@app.post("/api/audit/upload", response_model=DocumentAuditResponse)
async def upload_and_process_document(file: UploadFile = File(...), po_number: Optional[str] = None):
    """Uploads a real scanned receipt/invoice file and runs the real multi-agent audit fleet."""
    try:
        os.makedirs("receipts", exist_ok=True)

        # Never trust the client-supplied filename: strip any directory
        # component so an upload cannot escape the receipts/ directory.
        safe_name = os.path.basename(file.filename or "").replace("\\", "/").split("/")[-1]
        if not safe_name or safe_name in (".", ".."):
            raise HTTPException(status_code=400, detail="Invalid upload filename.")

        file_path = os.path.join("receipts", safe_name)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        document_id = f"UPL-{safe_name.split('.')[0].upper()}"
        req = DocumentAuditRequest(
            document_id=document_id,
            file_path_or_url=file_path,
            po_number_override=po_number or "PO-9921"
        )
        return fleet.process_document(req)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload & audit error: {str(e)}")


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


@app.get("/api/stats")
def fleet_stats():
    """Live fleet counters, computed from the Firestore audit trail.

    The landing page renders these rather than hardcoded copy, so the headline
    figures are always the fleet's actual record rather than an illustration.
    """
    audits = firestore_service.list_audit_results()
    reports = firestore_service.list_discrepancy_reports()

    needing_human = sum(1 for r in reports if r.requires_human_signature)
    autonomous = len(reports) - needing_human
    caught = sum(a.net_variance for a in audits if a.net_variance > 0)

    return {
        "documents_audited": len(audits),
        "required_human_signature": needing_human,
        "resolved_autonomously": autonomous,
        "variance_caught_usd": round(caught, 2),
    }


@app.get("/api/disputes", response_model=List[DiscrepancyReport])
def list_discrepancy_reports():
    """Retrieve generated vendor discrepancy reports and human approval alerts."""
    return firestore_service.list_discrepancy_reports()


@app.get("/api/disputes/{report_id}/export/pdf")
def export_dispute_pdf(report_id: str):
    """Generates an official printable PDF Vendor Dispute Notice document."""
    reports = firestore_service.list_discrepancy_reports()
    matching = [r for r in reports if r.report_id == report_id]
    if not matching:
        raise HTTPException(status_code=404, detail=f"Discrepancy report {report_id} not found.")

    report = matching[0]
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>OFFICIAL VENDOR DISPUTE NOTICE - {report.report_id}</title>
    <style>
        body {{ font-family: 'Helvetica Neue', Arial, sans-serif; padding: 40px; color: #1e293b; }}
        .header {{ border-bottom: 3px solid #6366f1; padding-bottom: 20px; margin-bottom: 30px; }}
        .title {{ font-size: 24px; font-weight: bold; color: #0f172a; }}
        .meta {{ font-size: 13px; color: #64748b; margin-top: 5px; }}
        .box {{ background: #f8fafc; border: 1px solid #e2e8f0; padding: 20px; border-radius: 8px; margin-bottom: 20px; }}
        .discrepancy-title {{ color: #dc2626; font-weight: bold; }}
        .footer {{ margin-top: 40px; border-top: 1px solid #cbd5e1; padding-top: 15px; font-size: 11px; color: #94a3b8; }}
        pre {{ white-space: pre-wrap; font-family: monospace; font-size: 12px; background: #0f172a; color: #f8fafc; padding: 15px; border-radius: 6px; }}
    </style>
</head>
<body>
    <div class="header">
        <div class="title">DOCUMA FLEET - OFFICIAL VENDOR DISPUTE NOTICE</div>
        <div class="meta">Report ID: {report.report_id} | Created: {report.created_at} | Action: {report.action_taken.value}</div>
    </div>
    <div class="box">
        <p><strong>Vendor Name:</strong> {report.vendor_name}</p>
        <p><strong>Document Reference:</strong> {report.document_id}</p>
        <p><strong>PO Reference:</strong> {report.po_number}</p>
        <p class="discrepancy-title"><strong>Total Disputed Amount:</strong> ${report.total_overcharge:.2f} USD</p>
    </div>
    <h3>Formally Dispatched Audit Markdown Notice:</h3>
    <pre>{report.formal_dispute_markdown}</pre>
    <div class="footer">
        Generated automatically by Documa Multimodal Procurement Fleet (Gemini 3.5 Flash & Antigravity SDK).
    </div>
</body>
</html>"""
    return HTMLResponse(content=html_content)


@app.get("/api/audit/export/csv")
def export_audit_logs_csv():
    """Generates an ERP-compatible CSV file (SAP / QuickBooks format) of all audit results."""
    audits = firestore_service.list_audit_results()
    output = io.StringIO()
    writer = csv.writer(output)

    # Write CSV Header
    writer.writerow([
        "Audit ID", "Document ID", "PO Number", "Vendor Name", 
        "Timestamp", "Status", "Total Billed ($)", "Total Approved ($)", 
        "Net Variance ($)", "Has Unauthorized Items", "Summary Notes"
    ])

    for a in audits:
        writer.writerow([
            a.audit_id, a.document_id, a.po_number, a.vendor_name,
            a.audit_timestamp, a.status.value, a.total_billed, a.total_approved,
            a.net_variance, a.has_unauthorized_items, a.summary_notes
        ])

    csv_content = output.getvalue()
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=documa_erp_audit_logs.csv"}
    )


@app.post("/api/disputes/{report_id}/approve")
def approve_dispute_override(report_id: str, new_action: HumanDecision = Body(..., embed=True)):
    """Human finance manager approval or status override endpoint.

    new_action is typed to HumanDecision so an unrecognised value is rejected as
    a 422 before it can reach the store. It is recorded against human_decision,
    leaving action_taken as the fleet's own account of what it dispatched.
    """
    success = firestore_service.update_discrepancy_action(report_id, new_action)
    if not success:
        raise HTTPException(status_code=404, detail=f"Discrepancy report {report_id} not found.")
    return {"report_id": report_id, "status": "UPDATED", "new_action": new_action.value}
