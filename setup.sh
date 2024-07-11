#!/bin/bash

set -e

# Check if Python 3.9 or higher is installed
if ! command -v python3 &> /dev/null || [[ $(python3 -c 'import sys; print(sys.version_info >= (3, 9))') != "True" ]]; then
    echo "Python 3.9 or higher is required. Please install it and try again."
    exit 1
fi

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install required packages
pip install -r requirements.txt

# Create necessary directories
mkdir -p data output

# Check if payments.txt exists, create a sample if it doesn't
if [ ! -f data/payments.txt ]; then
    echo "2023-07-01,2023-07-01,1100,Wire Transfer" > data/payments.txt
    echo "Sample payments.txt created. Please update with your actual payment data."
fi

echo "Setup complete. You can now run the invoice generator using './run_invoice_generator.sh'"
