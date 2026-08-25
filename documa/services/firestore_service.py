"""
Firestore database service for Documa with seamless in-memory fallback.
"""

import os
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

from documa.models import PurchaseOrder, AuditResult, DiscrepancyReport, HumanDecision

logger = logging.getLogger("FirestoreService")


class FirestoreService:
    """Manages Firestore persistent database connections with mock fallback."""
    def __init__(self, project_id: Optional[str] = None):
        self.project_id = project_id or os.getenv("GOOGLE_CLOUD_PROJECT", "documa-hackathon")
        self.db = None
        self._in_memory_pos: Dict[str, Dict[str, Any]] = {}
        self._in_memory_audits: Dict[str, Dict[str, Any]] = {}
        self._in_memory_disputes: Dict[str, Dict[str, Any]] = {}

        self._init_client()

    def _init_client(self):
        try:
            from google.cloud import firestore
            self.db = firestore.Client(project=self.project_id)
            logger.info(f"Connected to Google Cloud Firestore (Project: {self.project_id})")
        except Exception as e:
            logger.info(f"GCP Firestore client not configured ({e}). Operating in resilient In-Memory Mode.")

    # --- Purchase Orders ---
    def save_purchase_order(self, po: PurchaseOrder) -> bool:
        data = po.model_dump()
        if self.db:
            try:
                self.db.collection("purchase_orders").document(po.po_number).set(data)
                return True
            except Exception as e:
                logger.error(f"Firestore save error: {e}")
        self._in_memory_pos[po.po_number] = data
        return True

    def get_purchase_order(self, po_number: str) -> Optional[PurchaseOrder]:
        if self.db:
            try:
                doc = self.db.collection("purchase_orders").document(po_number).get()
                if doc.exists:
                    return PurchaseOrder(**doc.to_dict())
            except Exception as e:
                logger.warning(f"Firestore read error: {e}. Checking in-memory.")

        if po_number in self._in_memory_pos:
            return PurchaseOrder(**self._in_memory_pos[po_number])
        return None

    def list_purchase_orders(self) -> List[PurchaseOrder]:
        pos = []
        if self.db:
            try:
                docs = self.db.collection("purchase_orders").stream()
                for doc in docs:
                    pos.append(PurchaseOrder(**doc.to_dict()))
                if pos:
                    return pos
            except Exception as e:
                logger.warning(f"Firestore list error: {e}")

        return [PurchaseOrder(**p) for p in self._in_memory_pos.values()]

    # --- Audit Results ---
    def save_audit_result(self, result: AuditResult) -> bool:
        data = result.model_dump()
        if self.db:
            try:
                self.db.collection("audit_logs").document(result.audit_id).set(data)
                return True
            except Exception as e:
                logger.error(f"Firestore save audit error: {e}")

        self._in_memory_audits[result.audit_id] = data
        return True

    def list_audit_results(self) -> List[AuditResult]:
        audits = []
        if self.db:
            try:
                docs = self.db.collection("audit_logs").stream()
                for doc in docs:
                    audits.append(AuditResult(**doc.to_dict()))
                if audits:
                    return audits
            except Exception as e:
                logger.warning(f"Firestore list audit error: {e}")

        return [AuditResult(**a) for a in self._in_memory_audits.values()]

    # --- Discrepancy Reports ---
    def save_discrepancy_report(self, report: DiscrepancyReport) -> bool:
        data = report.model_dump()
        if self.db:
            try:
                self.db.collection("disputes").document(report.report_id).set(data)
                return True
            except Exception as e:
                logger.error(f"Firestore save dispute error: {e}")

        self._in_memory_disputes[report.report_id] = data
        return True

    def list_discrepancy_reports(self) -> List[DiscrepancyReport]:
        disputes = []
        if self.db:
            try:
                docs = self.db.collection("disputes").stream()
                for doc in docs:
                    disputes.append(DiscrepancyReport(**doc.to_dict()))
                if disputes:
                    return disputes
            except Exception as e:
                logger.warning(f"Firestore list dispute error: {e}")

        return [DiscrepancyReport(**d) for d in self._in_memory_disputes.values()]

    def update_discrepancy_action(self, report_id: str, new_action: HumanDecision) -> bool:
        """Records a finance manager's ruling against an existing report.

        Writes to human_decision, never to action_taken: action_taken is the
        fleet's own record of what it dispatched, and overwriting it with a
        human verdict both loses that history and stores a value outside the
        ActionTaken enum, which breaks every later read of the collection.
        """
        decision = HumanDecision(new_action).value
        decided_at = datetime.now(timezone.utc).isoformat()
        patch = {"human_decision": decision, "decided_at": decided_at}

        if self.db:
            try:
                self.db.collection("disputes").document(report_id).update(patch)
                return True
            except Exception as e:
                logger.error(f"Firestore update error: {e}")

        if report_id in self._in_memory_disputes:
            self._in_memory_disputes[report_id].update(patch)
            return True
        return False
