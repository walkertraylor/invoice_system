#!/bin/bash

# Activate the virtual environment
source .venv/bin/activate

# Run the main Python script
python src/main.py

# Deactivate the virtual environment
deactivate

echo "Invoice generation complete. Check the output directory for generated files."
