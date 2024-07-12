import csv
from datetime import datetime
import os
import shutil
import logging
from tqdm import tqdm
from PyPDF2 import PdfMerger

logging.basicConfig(filename='weasyprint.log', level=logging.WARNING)

from config import *
from pdf_operations import create_invoice_pdf, create_receipt_pdf
from utils import get_due_date, generate_summary_report

def merge_pdfs(input_files, output_file):
    merger = PdfMerger()
    for pdf in input_files:
        merger.append(pdf)
    merger.write(output_file)
    merger.close()

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

    os.makedirs('output', exist_ok=True)

    invoice_files = []
    receipt_files = []

    print("Generating individual PDFs...")
    for payment in tqdm(payments, desc="Creating PDFs", unit="document"):
        due_date = get_due_date(payment['invoice_date'])
        exchange_rate = THB_AMOUNT / payment['amount']

        data = {
            'from': FROM,
            'to': TO,
            'invoice_number': f"INV-{payment['invoice_date'].strftime('%Y%m%d')}",
            'receipt_number': f"REC-{payment['payment_date'].strftime('%Y%m%d')}",
            'invoice_date': payment['invoice_date'],
            'due_date': due_date,
            'payment_date': payment['payment_date'],
            'item': ITEM,
            'thb_amount': THB_AMOUNT,
            'usd_amount': payment['amount'],
            'exchange_rate': exchange_rate,
            'payment_method': payment['method']
        }

        invoice_file = f"output/invoice_{payment['invoice_date'].strftime('%Y-%m-%d')}.pdf"
        receipt_file = f"output/receipt_{payment['payment_date'].strftime('%Y-%m-%d')}.pdf"
        
        create_invoice_pdf(invoice_file, data)
        create_receipt_pdf(receipt_file, data)
        
        invoice_files.append(invoice_file)
        receipt_files.append(receipt_file)

    if GENERATE_MERGED_PDFS:
        print("Generating merged PDFs...")
        merge_pdfs(invoice_files, "output/merged_invoices.pdf")
        merge_pdfs(receipt_files, "output/merged_receipts.pdf")

    if GENERATE_SUMMARY_REPORT:
        print("Generating summary report...")
        generate_summary_report(payments)

    print("Process completed successfully!")

if __name__ == "__main__":
    main()
