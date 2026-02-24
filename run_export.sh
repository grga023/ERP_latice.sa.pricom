#!/bin/bash
# Script to run the daily database export at 3 AM
# This script ensures the correct Python environment is used

# Change to the project directory
cd /opt/appl/scripts/ERP_T/ERP_latice.sa.pricom

# Run the export script using the virtual environment Python
venv/bin/python export_to_json.py >> logs/export_backup.log 2>&1
