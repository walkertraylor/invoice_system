import csv
from datetime import datetime, timedelta
import os
import shutil
import logging
from tqdm import tqdm
from PyPDF2 import PdfMerger
import argparse
import sys
from collections import Counter
import statistics
from colorama import init, Fore, Style

from config import *
from pdf_operations import create_invoice_pdf, create_receipt_pdf
from utils import get_due_date, generate_summary_report

__version__ = "1.0.0"

init(autoreset=True)  # Initialize colorama

def setup_logging(log_level):
    logging.basicConfig(filename=LOG_FILE, level=log_level,
                        format='%(asctime)s - %(levelname)s - %(message)s')

def merge_pdfs(input_files, output_file):
    try:
        merger = PdfMerger()
        for pdf in tqdm(input_files, desc="Merging PDFs", unit="file"):
            merger.append(pdf)
        merger.write(output_file)
        merger.close()
    except Exception as e:
        logging.error(f"Error merging PDFs: {str(e)}")
        raise

def validate_payment_data(row):
    if len(row) != 4:
        raise ValueError(f"Expected 4 fields, got {len(row)}")
    
    payment_date, invoice_date, usd_amount, payment_method = row
    
    try:
        datetime.strptime(payment_date, DATE_FORMAT).date()
    except ValueError:
        raise ValueError(f"Invalid payment date format: {payment_date}")
    
    try:
        datetime.strptime(invoice_date, DATE_FORMAT).date()
    except ValueError:
        raise ValueError(f"Invalid invoice date format: {invoice_date}")
    
    try:
        float(usd_amount)
    except ValueError:
        raise ValueError(f"Invalid USD amount: {usd_amount}")
    
    if not payment_method:
        raise ValueError("Payment method is empty")

def parse_arguments():
    parser = argparse.ArgumentParser(description=f"Invoice Generator v{__version__}")
    parser.add_argument("-o", "--output", choices=['quiet', 'normal', 'verbose'], default='normal',
                        help="Control the level of output (default: normal)")
    parser.add_argument("--no-merge", action="store_true", help="Do not generate merged PDFs")
    parser.add_argument("--no-summary", action="store_true", help="Do not generate summary report")
    parser.add_argument("--start-date", help="Start date for filtering (YYYY-MM-DD)")
    parser.add_argument("--end-date", help="End date for filtering (YYYY-MM-DD)")
    parser.add_argument("--yearly-summary", action="store_true", help="Generate yearly summary")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return parser.parse_args()

def analyze_payments(payments):
    total_payments = len(payments)
    total_amount_usd = sum(payment['amount'] for payment in payments)
    total_amount_thb = THB_AMOUNT * total_payments  # Fixed THB amount per payment
    exchange_rates = [THB_AMOUNT / payment['amount'] for payment in payments]
    avg_exchange_rate = statistics.mean(exchange_rates)
    min_exchange_rate = min(exchange_rates)
    max_exchange_rate = max(exchange_rates)
    exchange_rate_range = max_exchange_rate - min_exchange_rate
    exchange_rate_variation = (exchange_rate_range / avg_exchange_rate) * 100

    usd_amounts = [payment['amount'] for payment in payments]
    min_usd = min(usd_amounts)
    max_usd = max(usd_amounts)
    usd_variation = ((max_usd - min_usd) / statistics.mean(usd_amounts)) * 100

    payment_methods = Counter(payment['method'] for payment in payments)

    # Calculate time to pay and late payments
    time_to_pay = []
    late_payments = 0
    for payment in payments:
        days_to_pay = (payment['payment_date'] - payment['invoice_date']).days
        time_to_pay.append(days_to_pay)
        if days_to_pay > 30:  # Assuming 30 days as the due date
            late_payments += 1

    avg_time_to_pay = statistics.mean(time_to_pay)
    median_time_to_pay = statistics.median(time_to_pay)

    # Predict next payment amount
    if len(payments) > 1:
        last_3_payments = [p['amount'] for p in payments[-3:]]
        predicted_next_payment = sum(last_3_payments) / len(last_3_payments)
    else:
        predicted_next_payment = total_amount_usd / total_payments if total_payments > 0 else 0

    return {
        "total_payments": total_payments,
        "total_amount_usd": total_amount_usd,
        "total_amount_thb": total_amount_thb,
        "avg_exchange_rate": avg_exchange_rate,
        "min_exchange_rate": min_exchange_rate,
        "max_exchange_rate": max_exchange_rate,
        "exchange_rate_range": exchange_rate_range,
        "exchange_rate_variation": exchange_rate_variation,
        "min_usd": min_usd,
        "max_usd": max_usd,
        "usd_variation": usd_variation,
        "payment_methods": payment_methods,
        "avg_time_to_pay": avg_time_to_pay,
        "median_time_to_pay": median_time_to_pay,
        "late_payments": late_payments,
        "predicted_next_payment": predicted_next_payment
    }

def validate_config():
    required_fields = ['FROM', 'TO', 'ITEM', 'THB_AMOUNT', 'INPUT_FILE', 'OUTPUT_DIRECTORY']
    for field in required_fields:
        if not hasattr(sys.modules['config'], field):
            raise ValueError(f"Missing required configuration field: {field}")
    
    if not os.path.exists(INPUT_FILE):
        raise FileNotFoundError(f"Input file not found: {INPUT_FILE}")

def generate_yearly_summary(payments):
    yearly_data = {}
    for payment in payments:
        year = payment['payment_date'].year
        if year not in yearly_data:
            yearly_data[year] = {'total_usd': 0, 'total_thb': 0, 'count': 0}
        yearly_data[year]['total_usd'] += payment['amount']
        yearly_data[year]['total_thb'] += THB_AMOUNT
        yearly_data[year]['count'] += 1
    
    print(Fore.CYAN + "\nYearly Summary:")
    for year, data in sorted(yearly_data.items()):
        print(f"{year}:")
        print(f"  Total payments: {data['count']}")
        print(f"  Total USD: ${data['total_usd']:,.2f}")
        print(f"  Total THB: ฿{data['total_thb']:,.2f}")
        print(f"  Average USD per payment: ${data['total_usd']/data['count']:,.2f}")
        print()

def main():
    args = parse_arguments()
    log_level = logging.WARNING if args.output == 'quiet' else logging.INFO if args.output == 'normal' else logging.DEBUG
    setup_logging(log_level)
    logging.info(f"Starting invoice generation process (v{__version__})")

    error_count = 0
    warning_count = 0

    try:
        validate_config()

        if CREATE_BACKUP:
            shutil.copy2(INPUT_FILE, BACKUP_FILE)
            logging.info(f"Backup created: {BACKUP_FILE}")

        payments = []
        with open(INPUT_FILE, 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                try:
                    validate_payment_data(row)
                    payment_date, invoice_date, usd_amount, payment_method = row
                    payment_date = datetime.strptime(payment_date, DATE_FORMAT).date()
                    invoice_date = datetime.strptime(invoice_date, DATE_FORMAT).date()
                    
                    if args.start_date:
                        start_date = datetime.strptime(args.start_date, DATE_FORMAT).date()
                        if payment_date < start_date:
                            continue
                    
                    if args.end_date:
                        end_date = datetime.strptime(args.end_date, DATE_FORMAT).date()
                        if payment_date > end_date:
                            continue
                    
                    payments.append({
                        'payment_date': payment_date,
                        'invoice_date': invoice_date,
                        'amount': float(usd_amount),
                        'method': payment_method
                    })
                except ValueError as e:
                    logging.error(f"Error parsing row {row}: {str(e)}")
                    error_count += 1
                    continue

        OUTPUT_DIRECTORY.mkdir(exist_ok=True)

        invoice_files = []
        receipt_files = []

        logging.info("Generating individual PDFs...")
        for payment in tqdm(payments, desc="Creating PDFs", unit="document", disable=args.output=='quiet'):
            try:
                due_date = get_due_date(payment['invoice_date'])
                exchange_rate = THB_AMOUNT / payment['amount']

                data = {
                    'from': FROM,
                    'to': TO,
                    'invoice_number': f"INV-{payment['invoice_date'].strftime(DATE_FORMAT)}",
                    'receipt_number': f"REC-{payment['payment_date'].strftime(DATE_FORMAT)}",
                    'invoice_date': payment['invoice_date'],
                    'due_date': due_date,
                    'payment_date': payment['payment_date'],
                    'item': ITEM,
                    'thb_amount': THB_AMOUNT,
                    'usd_amount': payment['amount'],
                    'exchange_rate': exchange_rate,
                    'payment_method': payment['method']
                }

                invoice_file = OUTPUT_DIRECTORY / INVOICE_FILE_FORMAT.format(payment['invoice_date'].strftime(DATE_FORMAT))
                receipt_file = OUTPUT_DIRECTORY / RECEIPT_FILE_FORMAT.format(payment['payment_date'].strftime(DATE_FORMAT))
                
                create_invoice_pdf(invoice_file, data)
                create_receipt_pdf(receipt_file, data)
                
                invoice_files.append(invoice_file)
                receipt_files.append(receipt_file)
                logging.debug(f"Generated invoice and receipt for payment date {payment['payment_date']}")
            except Exception as e:
                logging.error(f"Error generating PDF for payment {payment}: {str(e)}")
                error_count += 1
                continue

        if GENERATE_MERGED_PDFS and not args.no_merge:
            logging.info("Generating merged PDFs...")
            merge_pdfs(invoice_files, OUTPUT_DIRECTORY / MERGED_INVOICE_FILE)
            merge_pdfs(receipt_files, OUTPUT_DIRECTORY / MERGED_RECEIPT_FILE)

        if GENERATE_SUMMARY_REPORT and not args.no_summary:
            logging.info("Generating summary report...")
            summary_report = generate_summary_report(payments)

        analysis = analyze_payments(payments)
        
        if args.output != 'quiet':
            print(Fore.GREEN + "\nPayment Analysis:")
            print(f"Total number of payments: {analysis['total_payments']}")
            print(f"Total amount (USD): ${analysis['total_amount_usd']:,.2f}")
            print(f"Total amount (THB): ฿{analysis['total_amount_thb']:,.2f}")
            print(f"Average exchange rate: 1 USD = {analysis['avg_exchange_rate']:.2f} THB")
            print(f"Exchange rate range: {analysis['min_exchange_rate']:.2f} - {analysis['max_exchange_rate']:.2f} THB")
            print(f"Exchange rate variation: {analysis['exchange_rate_variation']:.2f}%")
            print(f"USD amount range: ${analysis['min_usd']:.2f} - ${analysis['max_usd']:.2f}")
            print(f"USD amount variation: {analysis['usd_variation']:.2f}%")
            print(f"\nAverage time to pay: {analysis['avg_time_to_pay']:.1f} days")
            print(f"Median time to pay: {analysis['median_time_to_pay']:.1f} days")
            print(f"Number of late payments: {analysis['late_payments']} ({analysis['late_payments']/analysis['total_payments']*100:.1f}%)")
            print(f"\nPredicted next payment amount: ${analysis['predicted_next_payment']:.2f}")
            print(Fore.YELLOW + "\nPayment methods used:")
            for method, count in analysis['payment_methods'].items():
                print(f"  {method}: {count}")

        if args.yearly_summary:
            generate_yearly_summary(payments)

        if args.output != 'quiet':
            print(Fore.GREEN + f"\nProcess completed with {Fore.RED if error_count > 0 else Fore.GREEN}{error_count} errors{Style.RESET_ALL} and {Fore.YELLOW if warning_count > 0 else Fore.GREEN}{warning_count} warnings{Style.RESET_ALL}.")
            print(f"Generated {len(invoice_files)} invoices and {len(receipt_files)} receipts.")
            if not args.no_merge:
                print("Merged PDFs have been created.")
            if not args.no_summary:
                print("Summary report has been generated.")
            print(f"For more details, check the log file: {LOG_FILE}")

        logging.info("Invoice generation process completed successfully")

    except Exception as e:
        logging.exception(f"An unexpected error occurred: {str(e)}")
        print(Fore.RED + f"An error occurred: {str(e)}")
        print(f"Check {LOG_FILE} for details.")
        sys.exit(1)

if __name__ == "__main__":
    main()
