#!/usr/bin/env python3
from flask import Flask, request, jsonify, send_from_directory
import json, os, time
import logging

# Disable Flask default logging
log = logging.getLogger('werkzeug')
log.disabled = True

app = Flask(__name__)
app.logger.disabled = True

# Use the directory where this script is located
ERP_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(ERP_DIR, 'data')
NEW_ORD_FILE = os.path.join(DATA_DIR, 'new_ord.json')
FOR_DELIVERY_FILE = os.path.join(DATA_DIR, 'for_delivery.json')
REALIZED_FILE = os.path.join(DATA_DIR, 'realized.json')
LAGER_FILE = os.path.join(DATA_DIR, 'lager.json')
IMAGES_DIR = os.path.join(ERP_DIR, 'images')

# Map status to file path
STATUS_FILES = {
    'new': NEW_ORD_FILE,
    'for_delivery': FOR_DELIVERY_FILE,
    'realized': REALIZED_FILE
}

# Ensure directories and files exist
os.makedirs(DATA_DIR, exist_ok=True)
for filepath in STATUS_FILES.values():
    if not os.path.exists(filepath):
        with open(filepath, 'w') as f:
            json.dump([], f)
if not os.path.exists(LAGER_FILE):
    with open(LAGER_FILE, 'w') as f:
        json.dump([], f)
os.makedirs(IMAGES_DIR, exist_ok=True)

# --- Migrate old orders.json if it exists ---
OLD_ORDERS_FILE = os.path.join(ERP_DIR, 'orders.json')
if os.path.exists(OLD_ORDERS_FILE):
    try:
        with open(OLD_ORDERS_FILE) as f:
            old_orders = json.load(f)
        if old_orders:
            for status, filepath in STATUS_FILES.items():
                with open(filepath) as f:
                    existing = json.load(f)
                filtered = [o for o in old_orders if o.get('status') == status]
                existing.extend(filtered)
                with open(filepath, 'w') as f:
                    json.dump(existing, f, indent=2)
        os.rename(OLD_ORDERS_FILE, os.path.join(DATA_DIR, 'orders_backup.json'))
    except Exception:
        pass

def load_file(filepath):
    with open(filepath) as f:
        return json.load(f)

def save_file(filepath, data):
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)

def load_orders_by_status(status):
    return load_file(STATUS_FILES[status])

def save_orders_by_status(status, data):
    save_file(STATUS_FILES[status], data)

def find_order_across_files(order_id):
    """Find an order in any status file. Returns (order, status, list)."""
    for status, filepath in STATUS_FILES.items():
        orders = load_file(filepath)
        for o in orders:
            if o['id'] == order_id:
                return o, status, orders
    return None, None, None

@app.route('/')
def index():
    return send_from_directory(ERP_DIR, 'index.html')

@app.route('/<filename>')
def serve_static(filename):
    filepath = os.path.join(ERP_DIR, filename)
    if os.path.isfile(filepath):
        return send_from_directory(ERP_DIR, filename)
    return jsonify({'error': 'Not found'}), 404

@app.route('/orders/new', methods=['GET'])
def get_new_orders():
    return jsonify(load_orders_by_status('new'))

@app.route('/orders/for_delivery', methods=['GET'])
def get_delivery_orders():
    return jsonify(load_orders_by_status('for_delivery'))

@app.route('/orders/realized', methods=['GET'])
def get_realized_orders():
    return jsonify(load_orders_by_status('realized'))

@app.route('/orders', methods=['GET', 'POST'])
def orders():
    if request.method == 'GET':
        # Return all orders merged (backward compat)
        all_orders = []
        for filepath in STATUS_FILES.values():
            all_orders.extend(load_file(filepath))
        return jsonify(all_orders)
    elif request.method == 'POST':
        o = request.form
        file = request.files['slika']
        filename = f"{int(time.time())}_{file.filename}"
        file.save(os.path.join(IMAGES_DIR, filename))
        new_orders = load_orders_by_status('new')
        new_orders.append({
            'id': int(time.time()),
            'naziv': o['naziv'],
            'cena': float(o['cena']),
            'placeno': o['placeno'] == 'true',
            'kupac': o['kupac'],
            'datum': o.get('datum', ''),
            'kolicina': int(o.get('kolicina', 1)),
            'boja': o.get('boja', ''),
            'opis': o.get('opis', ''),
            'slika': filename,
            'status': 'new'
        })
        save_orders_by_status('new', new_orders)
        return jsonify({'ok': True})

@app.route('/update_status', methods=['POST'])
def update_status():
    data = request.get_json()
    order_id = data['id']
    new_status = data['status']

    # Find the order in its current file
    order, old_status, old_list = find_order_across_files(order_id)
    if order is None:
        return jsonify({'error': 'Not found'}), 404

    # Update payment if provided
    if 'placeno' in data:
        order['placeno'] = data['placeno']

    # Remove from old file
    old_list = [o for o in old_list if o['id'] != order_id]
    save_orders_by_status(old_status, old_list)

    # Update status and add to new file
    order['status'] = new_status
    new_list = load_orders_by_status(new_status)
    new_list.append(order)
    save_orders_by_status(new_status, new_list)

    return jsonify({'ok': True})

@app.route('/order/<int:order_id>', methods=['GET'])
def get_order(order_id):
    order, status, _ = find_order_across_files(order_id)
    if order:
        return jsonify(order)
    return jsonify({'error': 'Not found'}), 404

@app.route('/update_order/<int:order_id>', methods=['POST'])
def update_order(order_id):
    o = request.form
    order, status, orders = find_order_across_files(order_id)
    if order is None:
        return jsonify({'error': 'Not found'}), 404

    order['naziv'] = o.get('naziv', order['naziv'])
    order['cena'] = float(o.get('cena', order['cena']))
    order['placeno'] = o.get('placeno') == 'true'
    order['kupac'] = o.get('kupac', order['kupac'])
    order['datum'] = o.get('datum', order['datum'])
    order['opis'] = o.get('opis', order['opis'])
    # Handle file upload if provided
    if 'slika' in request.files and request.files['slika'].filename:
        file = request.files['slika']
        filename = f"{int(time.time())}_{file.filename}"
        file.save(os.path.join(IMAGES_DIR, filename))
        order['slika'] = filename

    save_orders_by_status(status, orders)
    return jsonify({'ok': True})

@app.route('/order_from_lager', methods=['POST'])
def order_from_lager():
    o = request.get_json()
    new_orders = load_orders_by_status('new')
    new_orders.append({
        'id': int(time.time()),
        'naziv': o.get('naziv', ''),
        'cena': float(o.get('cena', 0)),
        'placeno': o.get('placeno', 'false') == 'true',
        'kupac': o.get('kupac', ''),
        'datum': o.get('datum', ''),
        'kolicina': int(o.get('kolicina', 1)),
        'boja': o.get('boja', ''),
        'opis': o.get('opis', ''),
        'slika': o.get('slika', ''),
        'status': 'new'
    })
    save_orders_by_status('new', new_orders)
    return jsonify({'ok': True})

@app.route('/images/<path:filename>')
def images(filename):
    return send_from_directory(IMAGES_DIR, filename)

# --- Lager (Inventory) ---
def load_lager():
    with open(LAGER_FILE) as f:
        return json.load(f)

def save_lager(items):
    with open(LAGER_FILE,'w') as f:
        json.dump(items, f, indent=2)

@app.route('/lager', methods=['GET','POST'])
def lager():
    if request.method == 'GET':
        return jsonify(load_lager())
    elif request.method == 'POST':
        o = request.form
        file = request.files.get('slika')
        filename = ''
        if file and file.filename:
            filename = f"{int(time.time())}_{file.filename}"
            file.save(os.path.join(IMAGES_DIR, filename))
        items = load_lager()
        items.append({
            'id': int(time.time() * 1000),
            'naziv': o.get('naziv',''),
            'cena': float(o.get('cena', 0)),
            'boja': o.get('boja',''),
            'slika': filename
        })
        save_lager(items)
        return jsonify({'ok': True})

@app.route('/lager/<int:item_id>', methods=['DELETE'])
def delete_lager(item_id):
    items = load_lager()
    items = [i for i in items if i['id'] != item_id]
    save_lager(items)
    return jsonify({'ok': True})

if __name__ == '__main__':
    # Run Flask in background-safe mode
    app.run(host='0.0.0.0', port=8080, debug=False)
