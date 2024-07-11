from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
from PyPDF2 import PdfMerger
from config import PAGE_SIZE, TOP_MARGIN, BOTTOM_MARGIN

def render_template(template_name, context):
    env = Environment(loader=FileSystemLoader('templates'))
    template = env.get_template(template_name)
    return template.render(context)

def html_to_pdf(html_content, output_path):
    HTML(string=html_content).write_pdf(output_path)

def merge_pdfs(pdf_list, output_path):
    merger = PdfMerger()
    for pdf in pdf_list:
        merger.append(pdf)
    merger.write(output_path)
    merger.close()

def create_invoice_pdf(filename, data, elements=None):
    html_content = render_template('invoice.html', data)
    if filename:
        html_to_pdf(html_content, filename)
    return html_content

def create_receipt_pdf(filename, data, elements=None):
    html_content = render_template('receipt.html', data)
    if filename:
        html_to_pdf(html_content, filename)
    return html_content
