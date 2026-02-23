from flask import Blueprint, request, jsonify, render_template, redirect, url_for, current_app
import time
import os
from models import db, Order, LagerItem

orders_bp = Blueprint('orders', __name__)


# ─── Page Routes ───────────────────────────────────────────────

@orders_bp.route('/')
@orders_bp.route('/index.html')
def index():
    return render_template('index.html')


@orders_bp.route('/porudzbenice')
@orders_bp.route('/porudzbenice.html')
def porudzbenice():
    return render_template('porudzbenice.html')


@orders_bp.route('/realizovano')
@orders_bp.route('/realizovano.html')
def realizovano():
    return render_template('realizovano.html')


@orders_bp.route('/za-dostavu')
@orders_bp.route('/za_daostavu.html')
def za_dostavu():
    return render_template('za_dostavu.html')


@orders_bp.route('/edit')
@orders_bp.route('/edit.html')
def edit():
    return render_template('edit.html')


# ─── API Routes ────────────────────────────────────────────────

@orders_bp.route('/api/orders', methods=['GET'])
def get_all_orders():
    orders = Order.query.all()
    return jsonify([o.to_dict() for o in orders])


@orders_bp.route('/api/orders/new', methods=['GET'])
def get_new_orders():
    orders = Order.query.filter_by(status='new').all()
    return jsonify([o.to_dict() for o in orders])


@orders_bp.route('/api/orders/for_delivery', methods=['GET'])
def get_delivery_orders():
    orders = Order.query.filter_by(status='for_delivery').all()
    return jsonify([o.to_dict() for o in orders])


@orders_bp.route('/api/orders/realized', methods=['GET'])
def get_realized_orders():
    orders = Order.query.filter_by(status='realized').all()
    return jsonify([o.to_dict() for o in orders])


@orders_bp.route('/api/orders', methods=['POST'])
def create_order():
    o = request.form
    file = request.files.get('slika')
    filename = ''
    if file and file.filename:
        filename = f"{int(time.time())}_{file.filename}"
        file.save(os.path.join(current_app.config['IMAGES_DIR'], filename))

    order = Order(
        naziv=o['naziv'],
        cena=float(o['cena']),
        placeno=o['placeno'] == 'true',
        kupac=o['kupac'],
        datum=o.get('datum', ''),
        kolicina=int(o.get('kolicina', 1)),
        boja=o.get('boja', ''),
        opis=o.get('opis', ''),
        slika=filename,
        status='new'
    )
    db.session.add(order)
    db.session.commit()
    return jsonify({'ok': True})


@orders_bp.route('/api/update_status', methods=['POST'])
def update_status():
    data = request.get_json()
    order = db.session.get(Order, data['id'])
    if not order:
        return jsonify({'error': 'Porudžbina nije pronađena'}), 404

    if 'placeno' in data:
        order.placeno = data['placeno']
    order.status = data['status']
    db.session.commit()
    return jsonify({'ok': True})


@orders_bp.route('/api/order/<int:order_id>', methods=['GET'])
def get_order(order_id):
    order = db.session.get(Order, order_id)
    if not order:
        return jsonify({'error': 'Porudžbina nije pronađena'}), 404
    return jsonify(order.to_dict())


@orders_bp.route('/api/delete_order/<int:order_id>', methods=['DELETE'])
def delete_order(order_id):
    order = db.session.get(Order, order_id)
    if not order:
        return jsonify({'error': 'Porudžbina nije pronađena'}), 404
    db.session.delete(order)
    db.session.commit()
    return jsonify({'ok': True})

@orders_bp.route('/api/update_order/<int:order_id>', methods=['POST'])
def update_order(order_id):
    order = db.session.get(Order, order_id)
    if not order:
        return jsonify({'error': 'Porudžbina nije pronađena'}), 404

    o = request.form
    order.naziv = o.get('naziv', order.naziv)
    order.cena = float(o.get('cena', order.cena))
    order.placeno = o.get('placeno') == 'true'
    order.kupac = o.get('kupac', order.kupac)
    order.datum = o.get('datum', order.datum)
    order.opis = o.get('opis', order.opis)

    if 'slika' in request.files and request.files['slika'].filename:
        file = request.files['slika']
        filename = f"{int(time.time())}_{file.filename}"
        file.save(os.path.join(current_app.config['IMAGES_DIR'], filename))
        order.slika = filename

    db.session.commit()
    return jsonify({'ok': True})


@orders_bp.route('/api/order_from_lager', methods=['POST'])
def order_from_lager():
    o = request.get_json()
    order_qty = int(o.get('kolicina', 1))
    lager_id = o.get('lager_id')

    # Subtract quantity from lager (minimum 0)
    if lager_id:
        item = db.session.get(LagerItem, int(lager_id))
        if item:
            item.kolicina = max(0, item.kolicina - order_qty)

    order = Order(
        naziv=o.get('naziv', ''),
        cena=float(o.get('cena', 0)),
        placeno=o.get('placeno', 'false') == 'true',
        kupac=o.get('kupac', ''),
        datum=o.get('datum', ''),
        kolicina=order_qty,
        boja=o.get('boja', ''),
        opis=o.get('opis', ''),
        slika=o.get('slika', ''),
        status='new'
    )
    db.session.add(order)
    db.session.commit()
    return jsonify({'ok': True})
