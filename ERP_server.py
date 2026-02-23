#!/usr/bin/env python3
from flask import Flask, request, jsonify, send_from_directory
import json, os, time
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import threading

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

# --- Email Notification Config ---
EMAIL_CONFIG_FILE = os.path.join(DATA_DIR, 'email_config.json')
NOTIFICATION_LOG_FILE = os.path.join(DATA_DIR, 'notified.json')

def load_email_config():
    if os.path.exists(EMAIL_CONFIG_FILE):
        with open(EMAIL_CONFIG_FILE) as f:
            return json.load(f)
    return {'enabled': False, 'sender_email': '', 'app_password': '', 'receiver_email': '', 'days_before': 2}

def save_email_config(config):
    with open(EMAIL_CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)

def load_notified():
    if os.path.exists(NOTIFICATION_LOG_FILE):
        with open(NOTIFICATION_LOG_FILE) as f:
            return json.load(f)
    return []

def save_notified(notified):
    with open(NOTIFICATION_LOG_FILE, 'w') as f:
        json.dump(notified, f, indent=2)

def send_email(subject, body, config):
    try:
        msg = MIMEMultipart()
        msg['From'] = config['sender_email']
        msg['To'] = config['receiver_email']
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'html'))
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(config['sender_email'], config['app_password'])
            server.send_message(msg)
        return True
    except Exception as e:
        print(f'[EMAIL ERROR] {e}')
        return False

def check_and_notify():
    """Check all new + for_delivery orders and send email if date is within N days."""
    config = load_email_config()
    if not config.get('enabled'):
        return
    days_before = int(config.get('days_before', 2))
    notified = load_notified()
    today = datetime.now().date()
    target_date = today + timedelta(days=days_before)

    # Check new and for_delivery orders
    orders_to_check = []
    for status in ['new', 'for_delivery']:
        orders_to_check.extend(load_orders_by_status(status))

    alerts = []
    for order in orders_to_check:
        datum_str = order.get('datum', '')
        if not datum_str:
            continue
        try:
            order_date = datetime.strptime(datum_str, '%d.%m.%Y').date()
        except ValueError:
            continue

        # Notify if order date is within range (today <= order_date <= today + days_before)
        notify_key = f"{order['id']}_{datum_str}"
        if today <= order_date <= target_date and notify_key not in notified:
            alerts.append(order)
            notified.append(notify_key)

    if alerts:
        body = '<h2>\u26A0\uFE0F Porud\u017ebine sa pribli\u017eavaju\u0107im datumom!</h2>'
        body += f'<p>Slede\u0107e porud\u017ebine imaju rok u narednih {days_before} dana:</p>'
        body += '<table border="1" cellpadding="8" cellspacing="0" style="border-collapse:collapse;">'
        body += '<tr style="background:#f0f0f0;"><th>Naziv</th><th>Kupac</th><th>Datum</th><th>Cena</th><th>Opis</th></tr>'
        for o in alerts:
            opis = (o.get('opis', '') or '').replace('\r\n', '<br>').replace('\n', '<br>')
            body += f"<tr><td>{o.get('naziv','')}</td><td>{o.get('kupac','')}</td>"
            body += f"<td><strong>{o.get('datum','')}</strong></td><td>{o.get('cena','')}</td>"
            body += f"<td>{opis}</td></tr>"
        body += '</table>'
        body += f'<br><p style="color:#888;">Latice sa pri\u010dom ERP - automatska notifikacija</p>'

        send_email(
            f'\u26A0\uFE0F {len(alerts)} porud\u017ebin(a) - rok uskoro!',
            body, config
        )
        save_notified(notified)

def notification_scheduler():
    """Background thread that checks every hour."""
    while True:
        try:
            check_and_notify()
        except Exception as e:
            print(f'[SCHEDULER ERROR] {e}')
        time.sleep(3600)  # Check every hour

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
    order_qty = int(o.get('kolicina', 1))
    lager_id = o.get('lager_id')

    # Subtract quantity from lager (minimum 0)
    if lager_id:
        items = load_lager()
        for item in items:
            if item['id'] == int(lager_id):
                item['kolicina'] = max(0, item.get('kolicina', 0) - order_qty)
                break
        save_lager(items)

    new_orders = load_orders_by_status('new')
    new_orders.append({
        'id': int(time.time()),
        'naziv': o.get('naziv', ''),
        'cena': float(o.get('cena', 0)),
        'placeno': o.get('placeno', 'false') == 'true',
        'kupac': o.get('kupac', ''),
        'datum': o.get('datum', ''),
        'kolicina': order_qty,
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
            'kolicina': int(o.get('kolicina', 0)),
            'lokacija': o.get('lokacija', 'Kuća'),
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

# --- Email Notification Settings API ---
@app.route('/email_config', methods=['GET', 'POST'])
def email_config():
    if request.method == 'GET':
        config = load_email_config()
        # Don't expose password in GET
        safe = {k: v for k, v in config.items() if k != 'app_password'}
        safe['has_password'] = bool(config.get('app_password'))
        return jsonify(safe)
    elif request.method == 'POST':
        data = request.get_json()
        config = load_email_config()
        config['enabled'] = data.get('enabled', config.get('enabled', False))
        config['sender_email'] = data.get('sender_email', config.get('sender_email', ''))
        config['receiver_email'] = data.get('receiver_email', config.get('receiver_email', ''))
        config['days_before'] = int(data.get('days_before', config.get('days_before', 2)))
        if data.get('app_password'):
            config['app_password'] = data['app_password']
        save_email_config(config)
        return jsonify({'ok': True})

@app.route('/test_email', methods=['POST'])
def test_email():
    config = load_email_config()
    if not config.get('sender_email') or not config.get('app_password') or not config.get('receiver_email'):
        return jsonify({'ok': False, 'error': 'Email konfiguracija nije kompletna.'}), 400
    success = send_email(
        '\u2705 Test - Latice sa pri\u010dom ERP',
        '<h2>Test notifikacija</h2><p>Email notifikacije su uspe\u0161no konfigurisane!</p>',
        config
    )
    return jsonify({'ok': success})

@app.route('/check_notifications', methods=['POST'])
def trigger_check():
    check_and_notify()
    return jsonify({'ok': True})

if __name__ == '__main__':
    # Start notification scheduler in background
    t = threading.Thread(target=notification_scheduler, daemon=True)
    t.start()
    # Run Flask
    app.run(host='0.0.0.0', port=8000, debug=False)
