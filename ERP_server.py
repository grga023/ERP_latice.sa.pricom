#!/usr/bin/env python3
from flask import Flask, request, jsonify, send_from_directory
import json, os, time

app = Flask(__name__)

ERP_DIR = '/opt/appl/scripts/ERP'
ORDERS_FILE = os.path.join(ERP_DIR,'orders.json')
IMAGES_DIR = os.path.join(ERP_DIR,'images')

# Ensure files exist
if not os.path.exists(ORDERS_FILE):
    with open(ORDERS_FILE,'w') as f: json.dump([],f)
os.makedirs(IMAGES_DIR, exist_ok=True)

def load_orders():
    with open(ORDERS_FILE) as f: return json.load(f)

def save_orders(orders):
    with open(ORDERS_FILE,'w') as f: json.dump(orders, f, indent=2)

@app.route('/')
def index():
    return send_from_directory(ERP_DIR,'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory(ERP_DIR, filename)

@app.route('/orders', methods=['GET','POST'])
def orders():
    if request.method == 'GET':
        return jsonify(load_orders())
    elif request.method == 'POST':
        o = request.form
        file = request.files['slika']
        filename = f"{int(time.time())}_{file.filename}"
        file.save(os.path.join(IMAGES_DIR, filename))
        orders = load_orders()
        orders.append({
            'id': int(time.time()),
            'naziv': o['naziv'],
            'cena': float(o['cena']),
            'placeno': o['placeno'] == 'true',
            'kupac': o['kupac'],
            'opis': o.get('opis',''),
            'slika': filename,
            'status': 'new'
        })
        save_orders(orders)
        return jsonify({'ok': True})

@app.route('/update_status', methods=['POST'])
def update_status():
    data = request.get_json()
    orders = load_orders()
    for o in orders:
        if o['id'] == data['id']:
            o['status'] = data['status']
    save_orders(orders)
    return jsonify({'ok': True})

@app.route('/images/<path:filename>')
def images(filename):
    return send_from_directory(IMAGES_DIR, filename)

app.run(host='0.0.0.0', port=8000)
