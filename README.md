# Invoice and Receipt Generator

This project generates invoices and receipts based on payment data, with support for multiple currencies and PDF generation.

## Setup

1. Ensure you have Python 3.9 or higher installed.
2. Clone this repository and navigate to the project directory.
3. Run the setup script:

   ```
   ./setup.sh
   ```

   This will create a virtual environment, install dependencies, and set up the necessary directories.

## Usage

1. Update the `data/payments.txt` file with your payment information. Each line should be in the format:

   ```
   YYYY-MM-DD,YYYY-MM-DD,AMOUNT,PAYMENT_METHOD
   ```

   Where the first date is the payment date, and the second is the invoice date.

2. Adjust settings in `src/config.py` if needed.

3. Run the invoice generator:

   ```
   ./run_invoice_generator.sh
   ```

4. Generated PDFs will be in the `output/` directory. A summary report will also be generated if enabled in the config.

## Customization

- Modify `src/config.py` to change global settings.
- Edit PDF generation in `src/pdf_operations.py` to adjust invoice and receipt layouts.
- Update utility functions in `src/utils.py` as needed.
- Modify HTML templates in the `templates/` directory to change the structure of invoices and receipts.
- Update `templates/styles.css` to change the appearance of generated PDFs.

## Features

- Generate individual invoices and receipts as PDFs
- Option to create merged PDFs for all invoices and receipts
- Support for multiple currencies with exchange rate calculation
- Customizable templates using HTML and CSS
- Summary report generation

## Maintenance

- Regularly update your Python packages:
  
  ```
  source .venv/bin/activate
  pip install --upgrade -r requirements.txt
  deactivate
  ```

- Keep your `data/payments.txt` file up to date with new payments.

## Troubleshooting

If you encounter any issues, please check the following:

1. Ensure all dependencies are correctly installed.
2. Verify that the `data/payments.txt` file is correctly formatted.
3. Check that you have write permissions in the `output/` directory.

For any other issues, please open an issue on the GitHub repository.

## License

This project is licensed under the MIT License.
