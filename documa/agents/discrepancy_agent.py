"""
Agent 3: Discrepancy Dispatcher Agent
Auto-approves compliant payouts or generates formal vendor price-discrepancy reports and human approval alerts.
"""

import uuid
import logging
from typing import Dict, Any, Optional
from documa.sdk.antigravity_sdk import BaseAgent, AgentState
from documa.models import AuditResult, AuditStatus, DiscrepancyReport, ActionTaken
from documa.services.firestore_service import FirestoreService

logger = logging.getLogger("DiscrepancyAgent")


class DiscrepancyAgent(BaseAgent):
    """Discrepancy Dispatcher Agent resolving payout approvals or drafting vendor reports."""

    def __init__(self, firestore_service: Optional[FirestoreService] = None):
        super().__init__(
            name="DiscrepancyDispatcherAgent",
            role="Dispatch automated payout approvals for compliant audits or draft formal vendor price discrepancy notices and finance escalation alerts."
        )
        self.firestore = firestore_service or FirestoreService()

    def run(self, input_data: AuditResult, state: AgentState) -> DiscrepancyReport:
        audit: AuditResult = input_data
        report_id = f"RPT-{uuid.uuid4().hex[:8].upper()}"

        state.log(self.name, "StartDiscrepancyResolution", {"audit_id": audit.audit_id, "status": audit.status.value})

        # 1. Compliant Payout Case
        if audit.status == AuditStatus.APPROVED:
            markdown_content = f"""# ✅ PAYOUT AUTHORIZATION NOTICE
**Document ID:** {audit.document_id}  
**Purchase Order:** {audit.po_number}  
**Vendor:** {audit.vendor_name}  

**Status:** APPROVED FOR IMMEDIATE PAYOUT  
**Authorized Amount:** ${audit.total_billed:.2f} USD  
**Reconciliation Result:** Billed totals strictly comply with contracted Purchase Order rates.

*Processed automatically by Documa Antigravity Fleet.*
"""
            report = DiscrepancyReport(
                report_id=report_id,
                audit_id=audit.audit_id,
                document_id=audit.document_id,
                po_number=audit.po_number,
                vendor_name=audit.vendor_name,
                action_taken=ActionTaken.AUTO_APPROVED_PAYOUT,
                total_overcharge=0.0,
                formal_dispute_markdown=markdown_content,
                requires_human_signature=False
            )

        # 2. Human Escalation Case (High Overcharge / Unauthorized Line Items)
        elif audit.status == AuditStatus.REQUIRES_HUMAN_APPROVAL:
            discrepancy_table = ""
            for item in audit.discrepancies:
                discrepancy_table += f"| {item.item_description} | {item.issue_type} | ${item.billed_unit_price:.2f} | ${item.approved_unit_price:.2f} | **${item.variance_amount:.2f}** |\n"

            markdown_content = f"""# ⚠️ HUMAN FINANCE APPROVAL REQUIRED: ANOMALY DETECTED
**Document ID:** {audit.document_id}  
**Purchase Order:** {audit.po_number}  
**Vendor:** {audit.vendor_name}  
**Net Overcharge / Variance:** **${audit.net_variance:.2f} USD**  

### Identified Line Item Discrepancies
| Item Description | Issue Type | Billed Unit Price | Approved Rate | Financial Impact |
| :--- | :--- | :--- | :--- | :--- |
{discrepancy_table}

> **Audit Summary:** {audit.summary_notes}

### Recommended Finance Action:
- **Reject Overcharge:** Issue payment for approved PO baseline only (${audit.total_approved:.2f}).
- **Approve Exception:** Override audit and release full payout (${audit.total_billed:.2f}).
"""
            report = DiscrepancyReport(
                report_id=report_id,
                audit_id=audit.audit_id,
                document_id=audit.document_id,
                po_number=audit.po_number,
                vendor_name=audit.vendor_name,
                action_taken=ActionTaken.ESCALATED_TO_HUMAN_FINANCE,
                total_overcharge=audit.net_variance,
                formal_dispute_markdown=markdown_content,
                requires_human_signature=True
            )

        # 3. Standard Vendor Dispute Case
        else:
            discrepancy_details = ""
            for idx, item in enumerate(audit.discrepancies, 1):
                discrepancy_details += f"{idx}. **{item.item_description}** ({item.issue_type}): {item.explanation}\n"

            markdown_content = f"""# 📄 FORMAL VENDOR PRICE DISCREPANCY NOTICE
**To Accounts Receivable:** {audit.vendor_name}  
**Invoice Reference:** {audit.document_id}  
**Associated PO Reference:** {audit.po_number}  

Our automated procurement auditing system (Documa Fleet) has completed an itemized reconciliation of your recent invoice submission against our master purchase agreement.

### Audit Findings & Price Adjustments Required:
{discrepancy_details}
- **Total Billed Amount:** ${audit.total_billed:.2f} USD
- **Approved Contract Basis:** ${audit.total_approved:.2f} USD
- **Net Price Variance (Disputed Amount):** **${audit.net_variance:.2f} USD**

**Action Requested:**  
Please issue a revised invoice reflecting contracted rates or issue a Credit Memo in the amount of **${audit.net_variance:.2f} USD**. Payout for the undisputed portion (${audit.total_approved:.2f}) will be remitted per payment terms.
"""
            report = DiscrepancyReport(
                report_id=report_id,
                audit_id=audit.audit_id,
                document_id=audit.document_id,
                po_number=audit.po_number,
                vendor_name=audit.vendor_name,
                action_taken=ActionTaken.GENERATED_DISCREPANCY_REPORT,
                total_overcharge=audit.net_variance,
                formal_dispute_markdown=markdown_content,
                requires_human_signature=False
            )

        self.firestore.save_discrepancy_report(report)
        state.set("discrepancy_report", report)
        state.log(self.name, "ReportDispatched", {"report_id": report.report_id, "action_taken": report.action_taken.value})

        return report
