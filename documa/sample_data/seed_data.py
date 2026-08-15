"""
Sample data seeder for Documa PO database.
"""

import logging
from documa.models import PurchaseOrder, POLineItem
from documa.services.firestore_service import FirestoreService

logger = logging.getLogger("SeedData")


def seed_sample_purchase_orders(firestore_service: FirestoreService):
    """Populates Firestore / In-Memory database with standard sample Purchase Orders."""
    po1 = PurchaseOrder(
        po_number="PO-9921",
        vendor_name="Acme Industrial Tech",
        created_date="2026-08-01",
        expiration_date="2026-12-31",
        line_items=[
            POLineItem(
                item_code="SKU-881",
                description="Dell UltraSharp 27-inch Monitor",
                quantity=10.0,
                approved_unit_price=180.0,
                max_total_amount=1800.0
            ),
            POLineItem(
                item_code="SKU-402",
                description="Ergonomic Executive Office Chair",
                quantity=5.0,
                approved_unit_price=250.0,
                max_total_amount=1250.0
            )
        ],
        approved_subtotal=3050.0,
        max_allowed_tax=200.0,
        approved_grand_total=3250.0,
        payment_terms="Net 30",
        status="ACTIVE"
    )

    po2 = PurchaseOrder(
        po_number="PO-8810",
        vendor_name="Global Logistics Corp",
        created_date="2026-08-05",
        expiration_date="2026-12-31",
        line_items=[
            POLineItem(
                item_code="SKU-101",
                description="Pallet Freight Shipping",
                quantity=2.0,
                approved_unit_price=650.0,
                max_total_amount=1300.0
            )
        ],
        approved_subtotal=1300.0,
        max_allowed_tax=100.0,
        approved_grand_total=1400.0,
        payment_terms="Net 15",
        status="ACTIVE"
    )

    firestore_service.save_purchase_order(po1)
    firestore_service.save_purchase_order(po2)
    logger.info("Successfully seeded sample Purchase Orders: PO-9921, PO-8810")
