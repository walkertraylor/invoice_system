from datetime import date
from calendar import monthrange
from config import THB_AMOUNT, DEFAULT_CURRENCY

def format_currency(amount, currency=DEFAULT_CURRENCY):
    return f"{currency} {amount:,.2f}"

def get_due_date(invoice_date):
    year, month = invoice_date.year, invoice_date.month
    last_day = monthrange(year, month)[1]
    if last_day > 30:
        due_date = date(year, month, 30)
    else:
        if month == 2:
            due_date = date(year, 3, 2) if last_day == 29 else date(year, 3, 1)
        else:
            due_date = date(year, month, last_day)
    return due_date

def generate_invoice_number(date):
    return f"INV-{date.strftime('%Y%m%d')}"

def generate_receipt_number(date):
    return f"REC-{date.strftime('%Y%m%d')}"

def format_date(date_obj):
    return date_obj.strftime("%Y-%m-%d")

def generate_summary_report(payments):
    total_usd = sum(payment['amount'] for payment in payments)
    total_thb = len(payments) * THB_AMOUNT
    avg_exchange_rate = total_thb / total_usd if total_usd > 0 else 0

    with open('output/summary_report.txt', 'w') as f:
        f.write("Summary Report\n")
        f.write("==============\n\n")
        f.write(f"Total Payments: {len(payments)}\n")
        f.write(f"Total Amount (USD): {format_currency(total_usd)}\n")
        f.write(f"Total Amount (THB): {format_currency(total_thb, 'THB')}\n")
        f.write(f"Average Exchange Rate: 1 USD = {avg_exchange_rate:.4f} THB\n\n")
        f.write("Unpaid Months:\n")
        
        start_date = date(2022, 7, 1)
        end_date = date.today()
        current_month = start_date
        paid_months = set(payment['invoice_date'].strftime("%Y-%m") for payment in payments)

        while current_month <= end_date:
            if current_month.strftime("%Y-%m") not in paid_months:
                f.write(f"- {current_month.strftime('%Y-%m')}\n")
            if current_month.month == 12:
                current_month = date(current_month.year + 1, 1, 1)
            else:
                current_month = date(current_month.year, current_month.month + 1, 1)
