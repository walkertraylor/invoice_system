import logging
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration

class FilteredWarnings(logging.Filter):
    def filter(self, record):
        return not record.getMessage().startswith("'created' timestamp seems very low")

logging.getLogger('weasyprint').addFilter(FilteredWarnings())

def render_template(template_name, context):
    env = Environment(loader=FileSystemLoader('templates'))
    template = env.get_template(template_name)
    return template.render(context)

def create_pdf(template_name, filename, data):
    html_content = render_template(template_name, data)
    font_config = FontConfiguration()
    css = CSS(string='''
        @page { size: letter; margin: 1cm; }
        body { 
            font-family: Helvetica, Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            position: relative;
        }
        .container {
            width: 100%;
            max-width: 800px;
            margin: 0 auto;
        }
        .header {
            text-align: center;
            margin-bottom: 20px;
        }
        h1 {
            color: #2c3e50;
            margin-bottom: 0.5em;
        }
        .details {
            margin-bottom: 20px;
            line-height: 1.8;
        }
        .from-to {
            display: flex;
            justify-content: space-between;
            margin-bottom: 20px;
        }
        .from-to > div {
            width: 48%;
        }
        .address {
            white-space: pre-line;
            line-height: 1.4;
        }
        .address-label {
            font-weight: bold;
            margin-bottom: 0.5em;
        }
        .table-container {
            position: relative;
        }
        table { 
            width: 100%; 
            border-collapse: collapse; 
            margin-bottom: 20px;
        }
        th, td { 
            border: 1px solid #ddd; 
            padding: 8px; 
            text-align: left; 
        }
        th { 
            background-color: #f2f2f2; 
        }
        .totals {
            text-align: right;
            margin-bottom: 20px;
            line-height: 1.8;
        }
        .watermark {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 100px;
            color: rgba(200, 200, 200, 0.5);
            z-index: 1000;
            pointer-events: none;
            transform: rotate(-45deg);
        }
        .content {
            position: relative;
            z-index: 1;
        }
        .thank-you {
            margin-top: 20px;
            font-style: italic;
        }
    ''', font_config=font_config)
    
    if filename:
        HTML(string=html_content).write_pdf(filename, stylesheets=[css], font_config=font_config)
    return html_content, css

create_invoice_pdf = lambda filename, data: create_pdf('invoice.html', filename, data)
create_receipt_pdf = lambda filename, data: create_pdf('receipt.html', filename, data)
