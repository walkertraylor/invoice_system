from datetime import date
from pathlib import Path

# Configuration flags
GENERATE_MERGED_PDFS = True
GENERATE_SUMMARY_REPORT = True
USE_DATE_RANGE_FILTER = False
START_DATE = date(2022, 7, 1)
END_DATE = date(2024, 12, 31)
CREATE_BACKUP = True

# Constants
FROM = """David Rucker
PO Box 16656
Chapel Hill, NC 27516
USA"""

TO = """ROBERT W TRAYLOR JR
1400 Village Square Blvd, #3-80930
Tallahassee, FL 32312
USA"""

ITEM = "Rental Unit - Sukhumvit House, Apartment 9C"
THB_AMOUNT = 40000

# PDF settings
PAGE_SIZE = 'letter'
TOP_MARGIN = 0.5
BOTTOM_MARGIN = 0.5

# Company details
COMPANY_DETAILS = {
    "name": "David Rucker",
    "address": "PO Box 16656, Chapel Hill, NC 27516, USA",
    "email": "dgrucker@gmail.com",
    "phone": "+1 917 612 4802"
}

# Currency and payment settings
DEFAULT_CURRENCY = "USD"
TAX_RATE = 0  # Set to 0 if not applicable

# File and directory settings
INPUT_FILE = 'data/payments.txt'
BACKUP_FILE = 'data/payments_backup.txt'
OUTPUT_DIRECTORY = Path('output')
LOG_FILE = 'invoice_generator.log'

# Date formats
DATE_FORMAT = '%Y-%m-%d'
MONTH_FORMAT = '%B %Y'

# PDF file name formats
INVOICE_FILE_FORMAT = 'invoice_{}.pdf'
RECEIPT_FILE_FORMAT = 'receipt_{}.pdf'
MERGED_INVOICE_FILE = 'merged_invoices.pdf'
MERGED_RECEIPT_FILE = 'merged_receipts.pdf'
SUMMARY_REPORT_FILE = 'summary_report.txt'
