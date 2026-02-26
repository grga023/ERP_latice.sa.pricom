#!/usr/bin/env python3
"""
add_missing_columns.py - Add missing database columns to existing tables.

This script safely adds any missing columns to the database schema.
Run this when the model definitions are updated but the database hasn't been migrated.
"""

import sqlite3
import os
import sys

# Ensure we can import from the project root
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

BASE_DIR = PROJECT_ROOT
DATA_DIR = os.path.join(BASE_DIR, 'data')
DB_PATH = os.path.join(DATA_DIR, 'erp.db')


def column_exists(cursor, table_name, column_name):
    """Check if a column exists in a table."""
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [row[1] for row in cursor.fetchall()]
    return column_name in columns


def add_missing_columns():
    """Add any missing columns to the database."""
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    changes_made = False

    # Add lager_id to orders table if missing
    if not column_exists(cursor, 'orders', 'lager_id'):
        print("Adding 'lager_id' column to 'orders' table...")
        cursor.execute("ALTER TABLE orders ADD COLUMN lager_id INTEGER")
        changes_made = True
        print("✓ Added 'lager_id' column")
    else:
        print("'lager_id' column already exists in 'orders' table")

    # Add any other missing columns here as needed
    # Example:
    # if not column_exists(cursor, 'table_name', 'column_name'):
    #     cursor.execute("ALTER TABLE table_name ADD COLUMN column_name TYPE DEFAULT VALUE")
    #     changes_made = True

    if changes_made:
        conn.commit()
        print("\n✓ Database schema updated successfully!")
    else:
        print("\n✓ Database schema is up to date")

    conn.close()


if __name__ == '__main__':
    print("=" * 60)
    print("Adding missing database columns...")
    print("=" * 60)
    add_missing_columns()
