from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from config import PAGE_SIZE, TOP_MARGIN, BOTTOM_MARGIN

def create_invoice_pdf(filename, data, elements=None):
    styles = getSampleStyleSheet()
    elements = elements or []

    # Add invoice content as reportlab flowables
    elements.append(Paragraph("INVOICE", styles['Title']))
    elements.append(Spacer(1, 0.25*inch))
    elements.append(Paragraph(f"Invoice Number: {data['invoice_number']}", styles['Normal']))
    elements.append(Paragraph(f"Date: {data['invoice_date']}", styles['Normal']))
    elements.append(Paragraph(f"Due Date: {data['due_date']}", styles['Normal']))
    elements.append(Spacer(1, 0.25*inch))
    elements.append(Paragraph("From:", styles['Heading2']))
    elements.append(Paragraph(data['from'], styles['Normal']))
    elements.append(Spacer(1, 0.25*inch))
    elements.append(Paragraph("To:", styles['Heading2']))
    elements.append(Paragraph(data['to'], styles['Normal']))
    elements.append(Spacer(1, 0.25*inch))
    
    # Create the item table
    item_data = [
        ['Description', 'Quantity', 'Rate (THB)', 'Amount (THB)'],
        [data['item'], '1', f"{data['thb_amount']:.2f}", f"{data['thb_amount']:.2f}"]
    ]
    item_table = Table(item_data)
    item_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 12),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(item_table)
    
    elements.append(Spacer(1, 0.25*inch))
    elements.append(Paragraph(f"Total Amount (THB): {data['thb_amount']:.2f}", styles['Normal']))
    elements.append(Paragraph(f"Amount (USD): {data['usd_amount']:.2f}", styles['Normal']))
    elements.append(Paragraph(f"Exchange Rate: 1 USD = {data['exchange_rate']:.4f} THB", styles['Normal']))
    elements.append(Spacer(1, 0.25*inch))
    elements.append(Paragraph(f"Payment Method: {data['payment_method']}", styles['Normal']))

    if filename:
        doc = SimpleDocTemplate(filename, pagesize=PAGE_SIZE, topMargin=TOP_MARGIN, bottomMargin=BOTTOM_MARGIN)
        doc.build(elements)
    return elements

def create_receipt_pdf(filename, data, elements=None):
    styles = getSampleStyleSheet()
    elements = elements or []

    # Add receipt content as reportlab flowables
    elements.append(Paragraph("RECEIPT", styles['Title']))
    elements.append(Spacer(1, 0.25*inch))
    elements.append(Paragraph(f"Receipt Number: {data['receipt_number']}", styles['Normal']))
    elements.append(Paragraph(f"Date: {data['payment_date']}", styles['Normal']))
    elements.append(Paragraph(f"Invoice Number: {data['invoice_number']}", styles['Normal']))
    elements.append(Spacer(1, 0.25*inch))
    elements.append(Paragraph("From:", styles['Heading2']))
    elements.append(Paragraph(data['from'], styles['Normal']))
    elements.append(Spacer(1, 0.25*inch))
    elements.append(Paragraph("To:", styles['Heading2']))
    elements.append(Paragraph(data['to'], styles['Normal']))
    elements.append(Spacer(1, 0.25*inch))
    
    # Create the payment table
    payment_data = [
        ['Description', 'Amount (THB)', 'Amount (USD)'],
        [data['item'], f"{data['thb_amount']:.2f}", f"{data['usd_amount']:.2f}"]
    ]
    payment_table = Table(payment_data)
    payment_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 12),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(payment_table)
    
    elements.append(Spacer(1, 0.25*inch))
    elements.append(Paragraph(f"Exchange Rate: 1 USD = {data['exchange_rate']:.4f} THB", styles['Normal']))
    elements.append(Spacer(1, 0.25*inch))
    elements.append(Paragraph(f"Payment Method: {data['payment_method']}", styles['Normal']))
    elements.append(Spacer(1, 0.25*inch))
    elements.append(Paragraph("Thank you for your payment!", styles['Heading2']))

    if filename:
        doc = SimpleDocTemplate(filename, pagesize=PAGE_SIZE, topMargin=TOP_MARGIN, bottomMargin=BOTTOM_MARGIN)
        doc.build(elements)
    return elements
