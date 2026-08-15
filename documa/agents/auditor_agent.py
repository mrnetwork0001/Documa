"""
Agent 2: Contract Auditor Agent
Cross-references extracted document line items against Purchase Orders stored in Firestore.
"""

import uuid
import logging
from typing import Dict, Any, Optional, List
from documa.sdk.antigravity_sdk import BaseAgent, AgentState
from documa.models import ExtractedDocument, PurchaseOrder, AuditResult, AuditStatus, ItemDiscrepancy
from documa.services.firestore_service import FirestoreService

logger = logging.getLogger("AuditorAgent")


class AuditorAgent(BaseAgent):
    """Contract Auditor Agent cross-checking invoice line items against Firestore POs."""

    def __init__(self, firestore_service: Optional[FirestoreService] = None):
        super().__init__(
            name="ContractAuditorAgent",
            role="Audit extracted line items against approved purchase orders in Firestore to detect price inflation, quantity errors, and unauthorized items."
        )
        self.firestore = firestore_service or FirestoreService()

    def run(self, input_data: ExtractedDocument, state: AgentState) -> AuditResult:
        extracted_doc: ExtractedDocument = input_data
        po_override = state.get("po_number_override")
        po_number = po_override or extracted_doc.purchase_order_ref or "PO-9921"

        state.log(self.name, "StartContractAudit", {"document_id": extracted_doc.document_id, "po_number": po_number})

        # Fetch Purchase Order from Firestore
        po = self.firestore.get_purchase_order(po_number)

        if not po:
            state.log(self.name, "PurchaseOrderNotFound", {"po_number": po_number})
            # Generate unassigned/missing PO audit failure
            return AuditResult(
                audit_id=f"AUD-{uuid.uuid4().hex[:8].upper()}",
                document_id=extracted_doc.document_id,
                po_number=po_number,
                vendor_name=extracted_doc.vendor_name,
                status=AuditStatus.REQUIRES_HUMAN_APPROVAL,
                discrepancies=[
                    ItemDiscrepancy(
                        item_description="Purchase Order Missing",
                        issue_type="MISSING_PO_RECORD",
                        billed_quantity=1.0,
                        expected_quantity=0.0,
                        billed_unit_price=extracted_doc.grand_total,
                        approved_unit_price=0.0,
                        variance_amount=extracted_doc.grand_total,
                        explanation=f"No approved Purchase Order found matching reference '{po_number}' in Firestore database."
                    )
                ],
                total_billed=extracted_doc.grand_total,
                total_approved=0.0,
                net_variance=extracted_doc.grand_total,
                has_unauthorized_items=True,
                summary_notes=f"Audit failed: PO '{po_number}' not found in Firestore."
            )

        # Build lookup maps for PO items by item_code or description
        po_items_by_code = {item.item_code.lower(): item for item in po.line_items if item.item_code}
        po_items_by_desc = {item.description.lower(): item for item in po.line_items}

        discrepancies: List[ItemDiscrepancy] = []
        total_approved_amount = 0.0
        has_unauthorized = False

        for line in extracted_doc.line_items:
            po_match = None
            if line.item_code and line.item_code.lower() in po_items_by_code:
                po_match = po_items_by_code[line.item_code.lower()]
            elif line.description.lower() in po_items_by_desc:
                po_match = po_items_by_desc[line.description.lower()]

            if po_match:
                approved_line_total = line.quantity * po_match.approved_unit_price
                total_approved_amount += approved_line_total

                # 1. Price inflation check
                if line.unit_price > po_match.approved_unit_price:
                    unit_diff = line.unit_price - po_match.approved_unit_price
                    variance = unit_diff * line.quantity
                    discrepancies.append(
                        ItemDiscrepancy(
                            item_description=line.description,
                            issue_type="OVERCHARGE",
                            billed_quantity=line.quantity,
                            expected_quantity=po_match.quantity,
                            billed_unit_price=line.unit_price,
                            approved_unit_price=po_match.approved_unit_price,
                            variance_amount=variance,
                            explanation=f"Billed unit price of ${line.unit_price:.2f} exceeds PO approved rate of ${po_match.approved_unit_price:.2f} per unit (Overcharge: ${variance:.2f})."
                        )
                    )

                # 2. Quantity discrepancy check
                if line.quantity > po_match.quantity:
                    qty_diff = line.quantity - po_match.quantity
                    variance = qty_diff * po_match.approved_unit_price
                    discrepancies.append(
                        ItemDiscrepancy(
                            item_description=line.description,
                            issue_type="QUANTITY_MISMATCH",
                            billed_quantity=line.quantity,
                            expected_quantity=po_match.quantity,
                            billed_unit_price=line.unit_price,
                            approved_unit_price=po_match.approved_unit_price,
                            variance_amount=variance,
                            explanation=f"Billed quantity ({line.quantity}) exceeds PO authorized quantity ({po_match.quantity})."
                        )
                    )
            else:
                # 3. Unauthorized Line Item
                has_unauthorized = True
                unauth_total = line.total_amount
                discrepancies.append(
                    ItemDiscrepancy(
                        item_description=line.description,
                        issue_type="UNAUTHORIZED_ITEM",
                        billed_quantity=line.quantity,
                        expected_quantity=0.0,
                        billed_unit_price=line.unit_price,
                        approved_unit_price=0.0,
                        variance_amount=unauth_total,
                        explanation=f"Line item '{line.description}' was not found in approved PO #{po.po_number}."
                    )
                )

        # Account for tax in total approved calculation
        total_approved_amount += po.max_allowed_tax
        net_variance = extracted_doc.grand_total - po.approved_grand_total

        # Determine Audit Status
        if len(discrepancies) == 0 and abs(net_variance) <= 1.00:
            status = AuditStatus.APPROVED
            summary = "Audit passed cleanly. Billed totals match approved Purchase Order exactly."
        elif net_variance > 500.0 or has_unauthorized:
            status = AuditStatus.REQUIRES_HUMAN_APPROVAL
            summary = f"Audit flagged for human sign-off: Discrepancy total of ${net_variance:.2f} detected with unauthorized items or major price overcharge."
        else:
            status = AuditStatus.DISCREPANCY_DETECTED
            summary = f"Audit completed with discrepancies: Vendor overcharged total of ${net_variance:.2f} across {len(discrepancies)} line items."

        audit_result = AuditResult(
            audit_id=f"AUD-{uuid.uuid4().hex[:8].upper()}",
            document_id=extracted_doc.document_id,
            po_number=po.po_number,
            vendor_name=extracted_doc.vendor_name,
            status=status,
            discrepancies=discrepancies,
            total_billed=extracted_doc.grand_total,
            total_approved=po.approved_grand_total,
            net_variance=net_variance,
            has_unauthorized_items=has_unauthorized,
            summary_notes=summary
        )

        # Save to Firestore database
        self.firestore.save_audit_result(audit_result)
        state.set("audit_result", audit_result)
        state.log(self.name, "AuditCompleted", {"status": status.value, "net_variance": net_variance, "discrepancies_count": len(discrepancies)})

        return audit_result
