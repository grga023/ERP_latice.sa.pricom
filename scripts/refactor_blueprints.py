#!/usr/bin/env python3
"""
Refactor all Serbian field names to English across all Python files
"""

import re
import os

def refactor_file(filepath):
    """Replace Serbian field names with English equivalents"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # Database field names mapping
    replacements = {
        # Orders fields
        'naziv': 'name',
        'cena': 'price',
        'placeno': 'paid',
        'kupac': 'customer',
        'datum': 'date',
        'kolicina': 'quantity',
        'boja': 'color',
        'opis': 'description',
        'slika': 'image',
        'lokacija': 'location',
        # Function/variable names (Serbian)
        'kreiranje': 'create_order_page',
        'porudzbenice': 'new_orders_page',
        'realizovano': 'realized_page',
        'za_dostavu': 'for_delivery_page',
    }
    
    # Variable names in functions (more specific replacements)
    special_replacements = {
        "o = request.form": "form_data = request.form",
        "o = request.get_json()": "data = request.get_json()",
        "o['": "form_data['",
        "o.get(": "form_data.get(",
    }
    
    # Apply simple field name replacements (whole word match)
    for serbian, english in replacements.items():
        # Match as word boundary to avoid partial matches
        pattern = r'\b' + re.escape(serbian) + r'\b'
        content = re.sub(pattern, english, content)
    
    # Apply special replacements (order matters)
    for old, new in special_replacements.items():
        content = content.replace(old, new)
    
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

# Files to refactor
files = [
    'blueprints/orders.py',
    'blueprints/lager.py',
]

# Get parent directory (workspace root)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

for filepath in files:
    full_path = os.path.join(BASE_DIR, filepath)
    if os.path.exists(full_path):
        if refactor_file(full_path):
            print(f"✓ Refactored: {filepath}")
        else:
            print(f"- No changes: {filepath}")
    else:
        print(f"✗ File not found: {filepath}")

print("\n✅ Refactoring complete!")
