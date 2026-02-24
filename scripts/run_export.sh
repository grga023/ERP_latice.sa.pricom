#!/bin/bash
cd /opt/appl/scripts/ERP

venv/bin/python scripts/export_to_json.py >> logs/export_backup.log 2>&1

sleep 10

cd /usb/ERP_data/data
git add *.json
git commit -m "Backup $(date '+%Y-%m-%d %H:%M')" || true
git push origin master
