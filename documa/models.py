"""
Pydantic data models for Documa multi-agent audit fleet.
"""

from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime, timezone


class DocumentType(str, Enum):
    INVOICE = "INVOICE"
    RECEIPT = "RECEIPT"
    PURCHASE_ORDER = "PURCHASE_ORDER"
    BILL_OF_LADING = "BILL_OF_LADING"
    UNKNOWN = "UNKNOWN"


class ExtractionMode(str, Enum):
    """Provenance of an extraction. Surfaced through the API and dashboard so a
    simulated demo result can never be mistaken for a live Gemini extraction."""
    ANTIGRAVITY_GEMINI = "ANTIGRAVITY_GEMINI"
    SIMULATED_FALLBACK = "SIMULATED_FALLBACK"


class AuditStatus(str, Enum):
    APPROVED = "APPROVED"
    DISCREPANCY_DETECTED = "DISCREPANCY_DETECTED"
    REQUIRES_HUMAN_APPROVAL = "REQUIRES_HUMAN_APPROVAL"
    REJECTED = "REJECTED"


class ActionTaken(str, Enum):
    AUTO_APPROVED_PAYOUT = "AUTO_APPROVED_PAYOUT"
    GENERATED_DISCREPANCY_REPORT = "GENERATED_DISCREPANCY_REPORT"
    ESCALATED_TO_HUMAN_FINANCE = "ESCALATED_TO_HUMAN_FINANCE"


class LineItem(BaseModel):
    item_code: Optional[str] = Field(default=None, description="SKU or item identifier code")
    description: str = Field(description="Description of item or service")
    quantity: float = Field(description="Quantity billed or supplied")
    unit_price: float = Field(description="Billed unit price in USD")
    tax_amount: float = Field(default=0.0, description="Tax allocated to this line item")
    total_amount: float = Field(description="Line total amount (quantity * unit_price + tax)")


class ExtractedDocument(BaseModel):
    document_id: str = Field(description="Unique ID of extracted document")
    document_type: DocumentType = Field(default=DocumentType.INVOICE)
    vendor_name: str = Field(description="Name of supplier/vendor")
    vendor_address: Optional[str] = Field(default=None)
    invoice_number: Optional[str] = Field(default=None, description="Invoice or receipt reference number")
    purchase_order_ref: Optional[str] = Field(default=None, description="Referenced PO number if printed on doc")
    invoice_date: Optional[str] = Field(default=None, description="Date on invoice (YYYY-MM-DD)")
    line_items: List[LineItem] = Field(default_factory=list)
    subtotal: float = Field(description="Calculated or printed subtotal")
    tax_total: float = Field(default=0.0, description="Total tax amount")
    grand_total: float = Field(description="Grand total billed amount")
    currency: str = Field(default="USD")
    signature_detected: bool = Field(default=False, description="Whether vendor/receiver signature was detected")
    extraction_confidence: float = Field(default=0.95, description="Gemini vision confidence score (0.0 - 1.0)")
    extraction_mode: ExtractionMode = Field(
        default=ExtractionMode.SIMULATED_FALLBACK,
        description="Whether these values came from a live Gemini vision call or from simulated demo data"
    )
    raw_notes: Optional[str] = Field(default=None)


class DocumentExtractionSchema(BaseModel):
    """Structured-output contract handed to the Antigravity harness for vision extraction.

    Mirrors ExtractedDocument minus the fields Documa supplies itself
    (document_id, extraction_mode, extraction_confidence).
    """
    document_type: DocumentType = Field(default=DocumentType.INVOICE)
    vendor_name: str = Field(description="Name of supplier/vendor")
    vendor_address: Optional[str] = Field(default=None)
    invoice_number: Optional[str] = Field(default=None)
    purchase_order_ref: Optional[str] = Field(default=None, description="PO number if printed on the document")
    invoice_date: Optional[str] = Field(default=None, description="Date on invoice (YYYY-MM-DD)")
    line_items: List[LineItem] = Field(default_factory=list)
    subtotal: float = Field(description="Calculated or printed subtotal")
    tax_total: float = Field(default=0.0)
    grand_total: float = Field(description="Grand total billed amount")
    currency: str = Field(default="USD")
    signature_detected: bool = Field(default=False)
    raw_notes: Optional[str] = Field(default=None, description="Any handwritten notes or warnings visible")


class POLineItem(BaseModel):
    item_code: Optional[str] = None
    description: str
    quantity: float
    approved_unit_price: float
    max_total_amount: float


class PurchaseOrder(BaseModel):
    po_number: str = Field(description="Unique PO reference string (e.g., PO-9921)")
    vendor_name: str
    created_date: str
    expiration_date: Optional[str] = None
    line_items: List[POLineItem]
    approved_subtotal: float
    max_allowed_tax: float
    approved_grand_total: float
    payment_terms: str = Field(default="Net 30")
    status: str = Field(default="ACTIVE")


class ItemDiscrepancy(BaseModel):
    item_description: str
    issue_type: str = Field(description="OVERCHARGE | QUANTITY_MISMATCH | UNAUTHORIZED_ITEM | TAX_DISCREPANCY")
    billed_quantity: float
    expected_quantity: float
    billed_unit_price: float
    approved_unit_price: float
    variance_amount: float = Field(description="Financial impact (positive means overcharge)")
    explanation: str


class AuditResult(BaseModel):
    audit_id: str
    document_id: str
    po_number: str
    vendor_name: str
    audit_timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    status: AuditStatus
    discrepancies: List[ItemDiscrepancy] = Field(default_factory=list)
    total_billed: float
    total_approved: float
    net_variance: float = Field(description="Positive means overcharged, negative means undercharged")
    has_unauthorized_items: bool = Field(default=False)
    summary_notes: str


class DiscrepancyReport(BaseModel):
    report_id: str
    audit_id: str
    document_id: str
    po_number: str
    vendor_name: str
    action_taken: ActionTaken
    total_overcharge: float
    formal_dispute_markdown: str
    requires_human_signature: bool = Field(default=False)
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class DocumentAuditRequest(BaseModel):
    document_id: str
    file_path_or_url: str
    po_number_override: Optional[str] = None


class DocumentAuditResponse(BaseModel):
    success: bool
    extracted_document: ExtractedDocument
    audit_result: AuditResult
    discrepancy_report: Optional[DiscrepancyReport] = None
    execution_log: List[Dict[str, Any]] = Field(default_factory=list)
