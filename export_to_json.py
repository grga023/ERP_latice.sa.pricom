#!/usr/bin/env python3
"""
export_to_json.py - Export SQLite database to JSON files (daily backup).

This script reads data from the SQLite database and exports it to JSON files
in the data/ directory. It creates a snapshot of the current state of the database.

Run manually:
    python export_to_json.py

Or schedule it to run daily at 3 AM using cron (Linux) or Task Scheduler (Windows).
"""

import json
import os
import sys
from datetime import datetime

# Ensure we can import from the project root
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ERP_server import create_app
from models import db, Order, LagerItem, EmailConfig, NotificationLog


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')


def export_orders():
    """Export orders to separate JSON files based on status."""
    # Get orders by status
    new_orders = Order.query.filter_by(status='new').all()
    for_delivery = Order.query.filter_by(status='for_delivery').all()
    realized = Order.query.filter_by(status='realized').all()

    # Convert to dictionaries
    new_data = [o.to_dict() for o in new_orders]
    delivery_data = [o.to_dict() for o in for_delivery]
    realized_data = [o.to_dict() for o in realized]

    # Save to files
    with open(os.path.join(DATA_DIR, 'new_ord.json'), 'w', encoding='utf-8') as f:
        json.dump(new_data, f, ensure_ascii=False, indent=2)

    with open(os.path.join(DATA_DIR, 'for_delivery.json'), 'w', encoding='utf-8') as f:
        json.dump(delivery_data, f, ensure_ascii=False, indent=2)

    with open(os.path.join(DATA_DIR, 'realized.json'), 'w', encoding='utf-8') as f:
        json.dump(realized_data, f, ensure_ascii=False, indent=2)

    return len(new_data), len(delivery_data), len(realized_data)


def export_lager():
    """Export lager items to JSON."""
    items = LagerItem.query.all()
    data = [item.to_dict() for item in items]

    with open(os.path.join(DATA_DIR, 'lager.json'), 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return len(data)


def export_email_config():
    """Export email config to JSON."""
    config = EmailConfig.query.first()
    if config:
        data = {
            'enabled': config.enabled,
            'sender_email': config.sender_email,
            'app_password': config.app_password,
            'receiver_email': config.receiver_email,
            'days_before': config.days_before
        }
        with open(os.path.join(DATA_DIR, 'email_config.json'), 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    return False


def export_notifications():
    """Export notification log to JSON."""
    logs = NotificationLog.query.all()
    data = [log.notify_key for log in logs]

    with open(os.path.join(DATA_DIR, 'notified.json'), 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return len(data)


def main():
    print('=' * 50)
    print(f'Database Export to JSON - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    print('=' * 50)

    app = create_app()

    with app.app_context():
        # Ensure data directory exists
        os.makedirs(DATA_DIR, exist_ok=True)

        print('\nExporting orders...')
        new_count, delivery_count, realized_count = export_orders()
        print(f'  new_ord.json: {new_count} orders')
        print(f'  for_delivery.json: {delivery_count} orders')
        print(f'  realized.json: {realized_count} orders')

        print('\nExporting lager...')
        lager_count = export_lager()
        print(f'  lager.json: {lager_count} items')

        print('\nExporting email config...')
        email_exported = export_email_config()
        if email_exported:
            print('  email_config.json: exported')
        else:
            print('  email_config.json: no config found')

        print('\nExporting notification log...')
        notif_count = export_notifications()
        print(f'  notified.json: {notif_count} entries')

        print('\n' + '=' * 50)
        print('Export complete!')
        print(f'  Total orders: {new_count + delivery_count + realized_count}')
        print(f'  Lager items: {lager_count}')
        print(f'  Location: {DATA_DIR}')
        print('=' * 50)


if __name__ == '__main__':
    main()
