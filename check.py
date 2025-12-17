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
from datetime import datetime

# ====================== DYNAMIC DATA ======================
quotation_data = {
    "quotation_id": "QT-2025-0012",
    "date": "16 Dec 2025",

    "customer": {
        "company_name": "ABC Infra Pvt Ltd",
        "email": "procurement@abcinfra.com",
        "address": "Bangalore, Karnataka",
    },

    "shipper": {
        "company_name": "Tata Hitachi Construction Machinery",
        "address": "123 Business Street<br/>Industrial Area<br/>Mumbai, Maharashtra - 400001",
        "phone": "+91 98765 43210",
        "email": "sales@tatahitachi.com",
        "gstin": "27AAACY1234D1Z5",
        "website": "www.tatahitachi.com",
    },

    "items": [
        {"name": "Tata Hitachi EX 210", "article_number": "EX210", "quantity": 1, "unit_price": 5800000},
        {"name": "Rock Breaker Attachment", "article_number": "RB-210", "quantity": 1, "unit_price": 650000},
    ],

    "tax_percent": 18,
    "currency_symbol": "₹",
    "notes": "Prices are indicative and subject to availability.",
    "terms": [
        "Payment: 50% advance, balance on delivery.",
        "Validity: 30 days from quotation date.",
        "Prices exclude transportation unless specified.",
    ],
}

def generate_quotation_pdf(data: dict, output_path: str, logo_path: str = None):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=15 * mm,
        leftMargin=15 * mm,
        topMargin=15 * mm,
        bottomMargin=15 * mm,
    )

    styles = getSampleStyleSheet()

    # Custom styles with proper names
    styles.add(ParagraphStyle(
        name='CompanyName',
        fontSize=18,
        leading=20,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor('#4472C4')
    ))
    styles.add(ParagraphStyle(
        name='CompanyInfo',
        fontSize=10,
        leading=12
    ))
    styles.add(ParagraphStyle(
        name='SectionHeader',
        fontSize=12,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor('#4472C4'),
        spaceAfter=8
    ))
    styles.add(ParagraphStyle(
        name='CustomItalic',
        fontName='Helvetica-Oblique',
        fontSize=10,
        leading=13
    ))
    styles.add(ParagraphStyle(
        name='QuoteTitle',
        parent=styles['Title'],
        fontSize=26,
        alignment=1,  # Center
        textColor=colors.HexColor('#4472C4'),
        spaceAfter=20
    ))
    styles.add(ParagraphStyle(
        name='ThankYou',
        alignment=1,  # Center
        fontSize=12,
        fontName='Helvetica-Bold',
        spaceBefore=20
    ))

    elements = []

    # --- Top Header: Logo + Company (Left) | Quotation No/Date (Right) ---
    logo = None
    if logo_path:
        try:
            logo = Image(logo_path)
            logo.drawHeight = 25 * mm   # Max height
            logo.drawWidth = 60 * mm    # Max width
            # ReportLab automatically preserves aspect ratio when both are set
        except Exception as e:
            print(f"Warning: Could not load logo: {e}")
            logo = None

    shipper = data["shipper"]
    left_parts = [
        Paragraph(shipper["company_name"], styles['CompanyName']),
        Paragraph(shipper["address"], styles['CompanyInfo']),
        Paragraph(f"Phone: {shipper['phone']} | Email: {shipper['email']}", styles['CompanyInfo']),
        Paragraph(f"GSTIN: {shipper['gstin']} | Website: {shipper['website']}", styles['CompanyInfo']),
    ]

    if logo:
        left_parts.insert(0, logo)

    left_table = Table([[p] for p in left_parts], colWidths=[120*mm])
    left_table.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP')]))

    # Right: Quotation No & Date
    quote_date = data.get('date', datetime.today().strftime('%d %b %Y'))
    right_parts = [
        Paragraph(f"<b>Quotation No:</b> {data['quotation_id']}", styles["Normal"]),
        Paragraph(f"<b>Date:</b> {quote_date}", styles["Normal"]),
    ]
    right_table = Table([[p] for p in right_parts], colWidths=[70*mm])
    right_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'RIGHT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))

    # Full header row
    header_table = Table([[left_table, right_table]], colWidths=[120*mm, 70*mm])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BACKGROUND', (0,0), (-1,-1), colors.transparent),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 15))

    # --- QUOTATION Title ---
    elements.append(Paragraph("QUOTATION", styles['QuoteTitle']))

    # --- Bill To ---
    customer = data["customer"]
    elements.append(Paragraph("Bill To:", styles['SectionHeader']))
    elements.append(Paragraph(f"<b>{customer['company_name']}</b>", styles["Normal"]))
    elements.append(Paragraph(customer["address"].replace(", ", "<br/>"), styles["Normal"]))
    elements.append(Paragraph(f"Email: {customer['email']}", styles["Normal"]))
    elements.append(Spacer(1, 20))

    # --- Items Table ---
    currency = data["currency_symbol"]
    table_data = [
        ["S.No.", "Description", "Article No.", "Qty", f"Unit Price ({currency})", f"Amount ({currency})"]
    ]

    subtotal = 0
    for i, item in enumerate(data["items"], 1):
        total = item["quantity"] * item["unit_price"]
        subtotal += total
        table_data.append([
            str(i),
            item["name"],
            item["article_number"],
            str(item["quantity"]),
            f"{item['unit_price']:,.2f}",
            f"{total:,.2f}",
        ])

    tax = subtotal * data["tax_percent"] / 100
    grand_total = subtotal + tax

    table_data += [
        ["", "", "", "", "Subtotal", f"{subtotal:,.2f}"],
        ["", "", "", "", f"GST ({data['tax_percent']}%)", f"{tax:,.2f}"],
        ["", "", "", "", Paragraph("<b>Grand Total</b>", styles["Normal"]),
         Paragraph(f"<b>{grand_total:,.2f}</b>", styles["Normal"])],
    ]

    col_widths = [15*mm, 85*mm, 30*mm, 15*mm, 35*mm, 35*mm]  # Wider description
    table = Table(table_data, colWidths=col_widths)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4472C4')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('ALIGN', (3, 1), (-1, -1), 'RIGHT'),  # Qty, prices right-aligned
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('BACKGROUND', (0, 1), (-1, -4), colors.whitesmoke),
        ('BACKGROUND', (0, -3), (-1, -1), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 0.8, colors.grey),
        ('FONTNAME', (-2, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (-1, -1), (-1, -1), 12),
        ('ALIGN', (-2, -1), (-1, -1), 'RIGHT'),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 30))

    # --- Notes ---
    if data.get("notes"):
        elements.append(Paragraph("Notes:", styles['SectionHeader']))
        elements.append(Paragraph(data["notes"], styles['CustomItalic']))
        elements.append(Spacer(1, 15))

    # --- Terms ---
    if data.get("terms"):
        elements.append(Paragraph("Terms & Conditions:", styles['SectionHeader']))
        terms_text = "<br/>• " + "<br/>• ".join(data["terms"])
        elements.append(Paragraph(terms_text, styles['CustomItalic']))
        elements.append(Spacer(1, 20))

    # --- Thank You ---
    elements.append(Paragraph("Thank you for your business!", styles['ThankYou']))

    doc.build(elements)


# ====================== USAGE ======================
pdf_path = "professional_quotation_final.pdf"

generate_quotation_pdf(
    data=quotation_data,
    output_path=pdf_path,
    logo_path="tata-hitachi-logo.png"  # Set to None if no logo
)

print(f"Professional quotation PDF generated successfully: {pdf_path}")