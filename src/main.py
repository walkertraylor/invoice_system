import csv
from datetime import datetime
import os
import shutil
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, PageBreak, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

from config import *
from pdf_operations import create_invoice_pdf, create_receipt_pdf
from utils import get_due_date, generate_summary_report

def main():
    if CREATE_BACKUP:
        shutil.copy2('data/payments.txt', 'data/payments_backup.txt')

    payments = []
    with open('data/payments.txt', 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            payment_date, invoice_date, usd_amount, payment_method = row
            payment_date = datetime.strptime(payment_date, "%Y-%m-%d").date()
            invoice_date = datetime.strptime(invoice_date, "%Y-%m-%d").date()
            
            if USE_DATE_RANGE_FILTER:
                if not (START_DATE <= payment_date <= END_DATE):
                    continue
            
            payments.append({
                'payment_date': payment_date,
                'invoice_date': invoice_date,
                'amount': float(usd_amount),
                'method': payment_method
            })

    for payment in payments:
        due_date = get_due_date(payment['invoice_date'])
        exchange_rate = THB_AMOUNT / payment['amount']

        data = {
            'from': FROM,
            'to': TO,
            'invoice_number': f"INV-{payment['invoice_date'].strftime('%Y%m%d')}",
            'receipt_number': f"REC-{payment['payment_date'].strftime('%Y%m%d')}",
            'invoice_date': payment['invoice_date'].strftime("%Y-%m-%d"),
            'due_date': due_date.strftime("%Y-%m-%d"),
            'payment_date': payment['payment_date'].strftime("%Y-%m-%d"),
            'item': ITEM,
            'thb_amount': THB_AMOUNT,
            'usd_amount': payment['amount'],
            'exchange_rate': exchange_rate,
            'payment_method': payment['method']
        }

        create_invoice_pdf(f"output/invoice_{payment['invoice_date'].strftime('%Y-%m-%d')}.pdf", data)
        create_receipt_pdf(f"output/receipt_{payment['payment_date'].strftime('%Y-%m-%d')}.pdf", data)

    if GENERATE_MERGED_PDFS:
        styles = getSampleStyleSheet()
        merged_invoice_elements = []
        merged_receipt_elements = []
        for payment in payments:
            due_date = get_due_date(payment['invoice_date'])
            exchange_rate = THB_AMOUNT / payment['amount']

            data = {
                'from': FROM,
                'to': TO,
                'invoice_number': f"INV-{payment['invoice_date'].strftime('%Y%m%d')}",
                'receipt_number': f"REC-{payment['payment_date'].strftime('%Y%m%d')}",
                'invoice_date': payment['invoice_date'].strftime("%Y-%m-%d"),
                'due_date': due_date.strftime("%Y-%m-%d"),
                'payment_date': payment['payment_date'].strftime("%Y-%m-%d"),
                'item': ITEM,
                'thb_amount': THB_AMOUNT,
                'usd_amount': payment['amount'],
                'exchange_rate': exchange_rate,
                'payment_method': payment['method']
            }

            invoice_elements = create_invoice_pdf(None, data)
            receipt_elements = create_receipt_pdf(None, data)

            merged_invoice_elements.extend(invoice_elements)
            merged_invoice_elements.append(PageBreak())
            merged_receipt_elements.extend(receipt_elements)
            merged_receipt_elements.append(PageBreak())

        doc = SimpleDocTemplate("output/merged_invoices.pdf", pagesize=letter, topMargin=TOP_MARGIN, bottomMargin=BOTTOM_MARGIN)
        doc.build(merged_invoice_elements)

        doc = SimpleDocTemplate("output/merged_receipts.pdf", pagesize=letter, topMargin=TOP_MARGIN, bottomMargin=BOTTOM_MARGIN)
        doc.build(merged_receipt_elements)

    if GENERATE_SUMMARY_REPORT:
        generate_summary_report(payments)

    print("Process completed successfully!")

if __name__ == "__main__":
    main()
