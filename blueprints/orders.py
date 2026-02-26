from flask import Blueprint, request, jsonify, render_template, redirect, url_for, current_app
from flask_login import login_required
import time
import os
from models import db, Order, LagerItem

orders_bp = Blueprint('orders', __name__)


# ─── Page Routes ───────────────────────────────────────────────

@orders_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')


@orders_bp.route('/kreiranje')
@orders_bp.route('/index.html')
@login_required
def kreiranje():
    return render_template('kreiranje.html')


@orders_bp.route('/porudzbenice')
@orders_bp.route('/porudzbenice.html')
@login_required
def porudzbenice():
    return render_template('porudzbenice.html')


@orders_bp.route('/realizovano')
@orders_bp.route('/realizovano.html')
@login_required
def realizovano():
    return render_template('realizovano.html')


@orders_bp.route('/za-dostavu')
@orders_bp.route('/za_daostavu.html')
@login_required
def za_dostavu():
    return render_template('za_dostavu.html')


@orders_bp.route('/edit')
@orders_bp.route('/edit.html')
@login_required
def edit():
    return render_template('edit.html')


# ─── API Routes ────────────────────────────────────────────────

@orders_bp.route('/api/orders', methods=['GET'])
@login_required
def get_all_orders():
    try:
        orders = Order.query.all()
        return jsonify([o.to_dict() for o in orders])
    except Exception as e:
        print(f"Error getting all orders: {str(e)}")
        return jsonify({'error': f'Greška pri učitavanju porudžbina: {str(e)}'}), 500


@orders_bp.route('/api/orders/new', methods=['GET'])
@login_required
def get_new_orders():
    try:
        orders = Order.query.filter_by(status='new').all()
        return jsonify([o.to_dict() for o in orders])
    except Exception as e:
        print(f"Error getting new orders: {str(e)}")
        return jsonify({'error': f'Greška pri učitavanju novih porudžbina: {str(e)}'}), 500


@orders_bp.route('/api/orders/for_delivery', methods=['GET'])
@login_required
def get_delivery_orders():
    try:
        orders = Order.query.filter_by(status='for_delivery').all()
        return jsonify([o.to_dict() for o in orders])
    except Exception as e:
        print(f"Error getting delivery orders: {str(e)}")
        return jsonify({'error': f'Greška pri učitavanju porudžbina za dostavu: {str(e)}'}), 500


@orders_bp.route('/api/orders/realized', methods=['GET'])
@login_required
def get_realized_orders():
    try:
        orders = Order.query.filter_by(status='realized').all()
        return jsonify([o.to_dict() for o in orders])
    except Exception as e:
        print(f"Error getting realized orders: {str(e)}")
        return jsonify({'error': f'Greška pri učitavanju realizovanih porudžbina: {str(e)}'}), 500


@orders_bp.route('/api/orders', methods=['POST'])
@login_required
def create_order():
    try:
        o = request.form
        file = request.files.get('slika')
        filename = ''
        if file and file.filename:
            filename = f"{int(time.time())}_{file.filename}"
            file.save(os.path.join(current_app.config['IMAGES_DIR'], filename))

        # Validate required fields
        if not o.get('naziv'):
            return jsonify({'error': 'Naziv je obavezan'}), 400
        if not o.get('kupac'):
            return jsonify({'error': 'Kupac je obavezan'}), 400
        
        try:
            cena = float(o.get('cena', 0))
        except (ValueError, TypeError):
            return jsonify({'error': 'Cena mora biti broj'}), 400
        
        try:
            kolicina = int(o.get('kolicina', 1))
        except (ValueError, TypeError):
            kolicina = 1

        order = Order(
            naziv=o['naziv'],
            cena=cena,
            placeno=o.get('placeno', 'false') == 'true',
            kupac=o['kupac'],
            datum=o.get('datum', ''),
            kolicina=kolicina,
            boja=o.get('boja', ''),
            opis=o.get('opis', ''),
            slika=filename,
            status='new'
        )
        db.session.add(order)
        db.session.commit()
        return jsonify({'ok': True})
    except Exception as e:
        db.session.rollback()
        print(f"Error creating order: {str(e)}")
        return jsonify({'error': f'Greška pri kreiranju porudžbine: {str(e)}'}), 500


@orders_bp.route('/api/update_status', methods=['POST'])
@login_required
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
@login_required
def get_order(order_id):
    order = db.session.get(Order, order_id)
    if not order:
        return jsonify({'error': 'Porudžbina nije pronađena'}), 404
    return jsonify(order.to_dict())


@orders_bp.route('/api/delete_order/<int:order_id>', methods=['DELETE'])
@login_required
def delete_order(order_id):
    order = db.session.get(Order, order_id)
    if not order:
        return jsonify({'error': 'Porudžbina nije pronađena'}), 404
    db.session.delete(order)
    db.session.commit()
    return jsonify({'ok': True})

@orders_bp.route('/api/update_order/<int:order_id>', methods=['POST'])
@login_required
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
@login_required
def order_from_lager():
    o = request.get_json()
    order_qty = int(o.get('kolicina', 1))
    lager_id = int(o.get('lager_id', 0)) if o.get('lager_id') else None

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
        status='new',
        lager_id=lager_id if lager_id else None
    )
    db.session.add(order)
    db.session.commit()
    return jsonify({'ok': True})

# return_to_lager
@orders_bp.route('/api/return_to_lager/<int:order_id>', methods=['POST'])
@login_required
def return_to_lager(order_id):
    order = db.session.get(Order, order_id)
    if not order:
        return jsonify({'error': 'Order not found'}), 404
    
    if not order.lager_id:
        return jsonify({'error': 'Order has no lager_id'}), 404
    
    item = db.session.get(LagerItem, int(order.lager_id))
    if not item:
        return jsonify({'error': 'Lager item not found'}), 404
    
    # Return the order quantity back to lager
    item.kolicina += order.kolicina
    
    # Delete the order after returning to lager
    db.session.delete(order)
    
    db.session.commit()
    return jsonify({'ok': True})