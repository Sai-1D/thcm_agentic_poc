# src/utils/quotation_generator.py

import os
import io
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Table,
    TableStyle,
    Spacer,
    Image,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from src.models.quotation_data import Quotation

BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../")
)

FONT_DIR = os.path.join(BASE_DIR, "public", "fonts")
LOGO_PATH = os.path.join(BASE_DIR, "public", "images", "tata-hitachi-logo.png")

# ---------------- FONT REGISTRATION (UNICODE SAFE) ----------------
pdfmetrics.registerFont(TTFont("DejaVu", os.path.join(FONT_DIR, "DejaVuSans.ttf")))
pdfmetrics.registerFont(TTFont("DejaVu-Bold", os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")))
pdfmetrics.registerFont(TTFont("DejaVu-Oblique", os.path.join(FONT_DIR, "DejaVuSans-Oblique.ttf")))


def generate_quotation_pdf(
    quotation: Quotation,
    logo_path: str = LOGO_PATH,
) -> bytes:
    """
    Generates quotation PDF in-memory and returns it as bytes.
    """

    buffer = io.BytesIO()

    # ---------------- Document ----------------
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=15 * mm,
        rightMargin=15 * mm,
        topMargin=15 * mm,
        bottomMargin=15 * mm,
    )

    styles = getSampleStyleSheet()

    # ---------------- OVERRIDE DEFAULT NORMAL ----------------
    styles["Normal"].fontName = "DejaVu"
    styles["Normal"].fontSize = 10

    # ---------------- CUSTOM STYLES ----------------
    styles.add(ParagraphStyle(
        name="CompanyName",
        fontName="DejaVu-Bold",
        fontSize=16,
        leading=18,
        textColor=colors.HexColor("#4472C4"),
    ))
    styles.add(ParagraphStyle(
        name="CompanyInfo",
        fontName="DejaVu",
        fontSize=10,
        leading=13,
    ))
    styles.add(ParagraphStyle(
        name="QuoteTitle",
        fontName="DejaVu-Bold",
        fontSize=24,
        alignment=1,
        textColor=colors.HexColor("#4472C4"),
        spaceAfter=12,
    ))
    styles.add(ParagraphStyle(
        name="RightInfo",
        fontName="DejaVu",
        fontSize=11,
        alignment=2,
    ))
    styles.add(ParagraphStyle(
        name="SectionHeader",
        fontName="DejaVu-Bold",
        fontSize=12,
        textColor=colors.HexColor("#4472C4"),
        spaceAfter=6,
    ))
    styles.add(ParagraphStyle(
        name="BodyItalic",
        fontName="DejaVu-Oblique",
        fontSize=10,
    ))
    styles.add(ParagraphStyle(
        name="ThankYou",
        fontName="DejaVu-Bold",
        fontSize=12,
        alignment=1,
        spaceBefore=20,
    ))

    elements = []

    # ---------------- HEADER ----------------
    logo = ""
    if logo_path and os.path.exists(logo_path):
        logo = Image(logo_path)
        logo.drawHeight = 32 * mm
        logo.drawWidth = 32 * mm

    shipper = quotation.shipper
    company_info = [
        Paragraph(shipper.company_name, styles["CompanyName"]),
        Paragraph(shipper.address, styles["CompanyInfo"]),
        Paragraph(f"Phone: {shipper.phone} | Email: {shipper.email}", styles["CompanyInfo"]),
        Paragraph(f"GSTIN: {shipper.gstin} | Website: {shipper.website}", styles["CompanyInfo"]),
    ]

    elements.append(Table(
        [[logo, company_info]],
        colWidths=[45 * mm, doc.width - 45 * mm],
        style=[("VALIGN", (0, 0), (-1, -1), "TOP")],
    ))

    elements.append(Spacer(1, 16))
    elements.append(Paragraph("QUOTATION", styles["QuoteTitle"]))

    # ---------------- BILL TO | QUOTE INFO ----------------
    customer = quotation.customer

    elements.append(Table(
        [[
            [
                Paragraph("<b>Bill To:</b>", styles["Normal"]),
                Paragraph(customer.company_name, styles["Normal"]),
                Paragraph(customer.address, styles["Normal"]),
                Paragraph(f"Phone: {customer.phone}", styles["Normal"]),
                Paragraph(f"Email: {customer.email}", styles["Normal"]),
            ],
            [
                Paragraph(f"<b>Quotation No:</b> {quotation.quotation_id}", styles["RightInfo"]),
                Paragraph(f"<b>Date:</b> {quotation.date}", styles["RightInfo"]),
            ]
        ]],
        colWidths=[doc.width * 0.6, doc.width * 0.4],
        style=[("VALIGN", (0, 0), (-1, -1), "TOP")],
    ))

    elements.append(Spacer(1, 20))

    # ---------------- ITEMS TABLE ----------------
    currency = quotation.currency_symbol
    table_data = [[
        "S.No.", "Description", "Article No.", "Qty",
        f"Unit Price ({currency})", f"Amount ({currency})"
    ]]

    for idx, product in enumerate(quotation.items, start=1):
        total_price = product.total_price
        if total_price is None:
            unit_price_str = "On Request"
            amount_str = "On Request"
        else:
            unit_price_str = f"{product.price:,.2f}"
            amount_str = f"{total_price:,.2f}"

        table_data.append([
            idx,
            product.identifier,
            product.article_number,
            product.quantity,
            unit_price_str,
            amount_str,
        ])

    table_data.extend([
        ["", "", "", "", "Subtotal", f"{quotation.subtotal:,.2f}"],
        ["", "", "", "", f"GST ({quotation.tax_percent}%)", f"{quotation.tax_amount:,.2f}"],
        ["", "", "", "", "Grand Total", f"{quotation.grand_total:,.2f}"],
    ])

    table = Table(
        table_data,
        colWidths=[15*mm, 78*mm, 30*mm, 15*mm, 30*mm, 30*mm],
    )
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4472C4")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "DejaVu-Bold"),
        ("FONTNAME", (0, 1), (-1, -1), "DejaVu"),
        ("ALIGN", (0, 0), (-1, 0), "CENTER"),
        ("ALIGN", (3, 1), (-1, -1), "RIGHT"),
        ("GRID", (0, 0), (-1, -1), 0.6, colors.grey),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 20))

    # ---------------- NOTES & TERMS ----------------
    if quotation.notes:
        elements.append(Paragraph("Notes:", styles["SectionHeader"]))
        elements.append(Paragraph(quotation.notes, styles["BodyItalic"]))
        elements.append(Spacer(1, 10))

    if quotation.terms:
        elements.append(Paragraph("Terms & Conditions:", styles["SectionHeader"]))
        elements.append(
            Paragraph("<br/>• " + "<br/>• ".join(quotation.terms), styles["BodyItalic"])
        )

    elements.append(Paragraph("Thank you for your business!", styles["ThankYou"]))

    # ---------------- BUILD & RETURN ----------------
    doc.build(elements)
    buffer.seek(0)

    return buffer.getvalue()
