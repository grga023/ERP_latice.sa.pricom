#!/bin/bash
# ERP Backup Script - exports data and pushes to git

set -e

# Find config file (script is in INSTALL_DIR)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="$SCRIPT_DIR/.erp.conf"

# Load configuration
if [ -f "$CONFIG_FILE" ]; then
    source "$CONFIG_FILE"
else
    echo "GREŠKA: Config fajl nije pronađen: $CONFIG_FILE"
    exit 1
fi

LOG_DIR="$DATA_DIR/logs"
LOG_FILE="$LOG_DIR/backup.log"

# Kreiraj logs dir ako ne postoji
mkdir -p "$LOG_DIR"

echo "=== Backup started: $(date) ===" >> "$LOG_FILE"

# Export to JSON
cd "$INSTALL_DIR"
./venv/bin/python scripts/export_to_json.py >> "$LOG_FILE" 2>&1

sleep 10

# Git backup
cd "$DATA_DIR"
git add *.json 2>> "$LOG_FILE"
git commit -m "Backup $(date '+%Y-%m-%d %H:%M')" >> "$LOG_FILE" 2>&1 || true
git push origin master >> "$LOG_FILE" 2>&1

echo "=== Backup finished: $(date) ===" >> "$LOG_FILE"
