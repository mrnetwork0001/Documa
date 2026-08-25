"""
Synthetic Visual Invoice & Receipt Generator for Documa.
Generates high-resolution invoice image files for Gemini 3.5 Flash multimodal vision testing.
"""

import os
from PIL import Image, ImageDraw, ImageFont


def create_invoice_image(filename: str, title: str, inv_number: str, po_number: str, items: list, subtotal: float, tax: float, grand_total: float, note: str = ""):
    """Renders a realistic scanned invoice image file."""
    os.makedirs("receipts", exist_ok=True)
    file_path = os.path.join("receipts", filename)

    width, height = 800, 1050
    image = Image.new("RGB", (width, height), color="#f8fafc")
    draw = ImageDraw.Draw(image)

    # Header Card
    draw.rectangle([(30, 30), (770, 140)], fill="#0f172a")
    draw.text((50, 45), "ACME INDUSTRIAL TECH INC.", fill="#ffffff", font_size=24)
    draw.text((50, 80), "100 Innovation Way, Suite 400 • San Jose, CA 95134", fill="#94a3b8", font_size=14)
    draw.text((50, 102), "Phone: (800) 555-0199 • Email: billing@acmeindustrial.com", fill="#94a3b8", font_size=14)

    # Document Meta Box
    draw.rectangle([(30, 160), (770, 240)], fill="#ffffff", outline="#e2e8f0", width=2)
    draw.text((50, 175), f"DOCUMENT TYPE: {title.upper()}", fill="#1e293b", font_size=16)
    draw.text((50, 202), f"INVOICE REF: {inv_number}", fill="#475569", font_size=14)
    draw.text((450, 175), f"DATE: 2026-08-14", fill="#475569", font_size=14)
    draw.text((450, 202), f"PO REFERENCE: {po_number}", fill="#6366f1", font_size=14)

    # Table Header
    draw.rectangle([(30, 260), (770, 300)], fill="#334155")
    draw.text((50, 272), "ITEM CODE", fill="#ffffff", font_size=12)
    draw.text((150, 272), "DESCRIPTION", fill="#ffffff", font_size=12)
    draw.text((500, 272), "QTY", fill="#ffffff", font_size=12)
    draw.text((580, 272), "UNIT PRICE", fill="#ffffff", font_size=12)
    draw.text((680, 272), "TOTAL", fill="#ffffff", font_size=12)

    # Table Rows
    y_offset = 320
    for item in items:
        draw.text((50, y_offset), item["code"], fill="#334155", font_size=13)
        draw.text((150, y_offset), item["desc"][:38], fill="#0f172a", font_size=13)
        draw.text((510, y_offset), str(item["qty"]), fill="#0f172a", font_size=13)
        draw.text((580, y_offset), f"${item['price']:.2f}", fill="#0f172a", font_size=13)
        draw.text((680, y_offset), f"${item['total']:.2f}", fill="#0f172a", font_size=13)
        draw.line([(30, y_offset + 25), (770, y_offset + 25)], fill="#e2e8f0", width=1)
        y_offset += 40

    # Summary Box
    draw.rectangle([(450, y_offset + 20), (770, y_offset + 140)], fill="#f1f5f9", outline="#cbd5e1", width=2)
    draw.text((470, y_offset + 35), "Subtotal:", fill="#475569", font_size=14)
    draw.text((680, y_offset + 35), f"${subtotal:.2f}", fill="#0f172a", font_size=14)
    draw.text((470, y_offset + 65), "Tax Total:", fill="#475569", font_size=14)
    draw.text((680, y_offset + 65), f"${tax:.2f}", fill="#0f172a", font_size=14)
    draw.text((470, y_offset + 95), "GRAND TOTAL:", fill="#0f172a", font_size=16)
    draw.text((660, y_offset + 95), f"${grand_total:.2f}", fill="#6366f1", font_size=16)

    # Notes & Signature Area
    if note:
        draw.rectangle([(30, y_offset + 20), (420, y_offset + 140)], fill="#fffbeb", outline="#fcd34d", width=1)
        draw.text((45, y_offset + 35), "VENDOR NOTES:", fill="#b45309", font_size=12)
        draw.text((45, y_offset + 60), note[:45], fill="#78350f", font_size=12)

    # Footer Signature Stamp
    draw.text((50, height - 70), "AUTHORIZED SIGNATURE: J. Doe (Accounts Receivable)", fill="#64748b", font_size=13)
    draw.text((50, height - 40), "AUDIT DISPATCH STATUS: Pending Documa Multimodal Fleet Audit", fill="#94a3b8", font_size=11)

    image.save(file_path)
    print(f"Generated visual invoice image: {file_path}")
    return file_path


def generate_all_sample_invoices():
    """Generates 4 test receipt PNG files in receipts/."""
    # 1. Compliant Invoice
    create_invoice_image(
        filename="compliant_invoice.png",
        title="COMMERCIAL INVOICE",
        inv_number="INV-2026-1001",
        po_number="PO-9921",
        items=[
            {"code": "SKU-881", "desc": "Dell UltraSharp 27-inch Monitor", "qty": 10, "price": 180.0, "total": 1800.0},
            {"code": "SKU-402", "desc": "Ergonomic Executive Office Chair", "qty": 5, "price": 250.0, "total": 1250.0}
        ],
        subtotal=3050.0,
        tax=200.0,
        grand_total=3250.0,
        note="Standard Net 30 payment terms per PO-9921 agreement."
    )

    # 2. Overcharged Invoice
    create_invoice_image(
        filename="overcharged_invoice.png",
        title="COMMERCIAL INVOICE",
        inv_number="INV-2026-9081",
        po_number="PO-9921",
        items=[
            {"code": "SKU-881", "desc": "Dell UltraSharp 27-inch Monitor", "qty": 10, "price": 240.0, "total": 2400.0},
            {"code": "SKU-402", "desc": "Ergonomic Executive Office Chair", "qty": 5, "price": 350.0, "total": 1750.0}
        ],
        subtotal=4150.0,
        tax=250.0,
        grand_total=4400.0,
        note="INFLATED RATES APPLIED: Mid-quarter price adjustment applied."
    )

    # 3. Unauthorized Line Item Invoice
    create_invoice_image(
        filename="unauthorized_fees_invoice.png",
        title="COMMERCIAL INVOICE",
        inv_number="INV-2026-9912",
        po_number="PO-9921",
        items=[
            {"code": "SKU-881", "desc": "Dell UltraSharp 27-inch Monitor", "qty": 10, "price": 180.0, "total": 1800.0},
            {"code": "SKU-402", "desc": "Ergonomic Executive Office Chair", "qty": 5, "price": 250.0, "total": 1250.0},
            {"code": "FEE-999", "desc": "Unapproved Expedited Freight & Priority Surcharge", "qty": 1, "price": 450.0, "total": 450.0}
        ],
        subtotal=3500.0,
        tax=200.0,
        grand_total=3700.0,
        note="UNAUTHORIZED SURCHARGE: Priority expedited delivery fee added."
    )

    # 4. Minor Overcharge Invoice — variance stays under the $500 human-signoff
    #    threshold, so the fleet resolves it autonomously by issuing a formal
    #    vendor dispute notice instead of escalating to a person.
    create_invoice_image(
        filename="minor_overcharge_invoice.png",
        title="COMMERCIAL INVOICE",
        inv_number="INV-2026-9330",
        po_number="PO-9921",
        items=[
            {"code": "SKU-881", "desc": "Dell UltraSharp 27-inch Monitor", "qty": 10, "price": 210.0, "total": 2100.0},
            {"code": "SKU-402", "desc": "Ergonomic Executive Office Chair", "qty": 5, "price": 250.0, "total": 1250.0}
        ],
        subtotal=3350.0,
        tax=200.0,
        grand_total=3550.0,
        note="Monitor rate billed at $210.00 vs contracted $180.00 per unit."
    )


if __name__ == "__main__":
    generate_all_sample_invoices()
