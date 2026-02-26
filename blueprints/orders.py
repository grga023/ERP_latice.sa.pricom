from flask import Blueprint, request, jsonify, render_template, redirect, url_for, current_app
from flask_login import login_required
import time
import os
from models import db, Order, InventoryItem

orders_bp = Blueprint('orders', __name__)


# ─── Page Routes ───────────────────────────────────────────────

@orders_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')


@orders_bp.route('/create')
@orders_bp.route('/index.html')
@login_required
def create_order_page():
    return render_template('create_order.html')


@orders_bp.route('/new-orders')
@orders_bp.route('/new_orders.html')
@login_required
def new_orders_page():
    return render_template('new_orders.html')


@orders_bp.route('/realized')
@orders_bp.route('/realized.html')
@login_required
def realized_page():
    return render_template('realized.html')


@orders_bp.route('/for-delivery')
@orders_bp.route('/for_delivery.html')
@login_required
def for_delivery_page():
    return render_template('for_delivery.html')


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
        return jsonify({'error': f'Error loading orders: {str(e)}'}), 500


@orders_bp.route('/api/orders/new', methods=['GET'])
@login_required
def get_new_orders():
    try:
        orders = Order.query.filter_by(status='new').all()
        return jsonify([o.to_dict() for o in orders])
    except Exception as e:
        print(f"Error getting new orders: {str(e)}")
        return jsonify({'error': f'Error loading new orders: {str(e)}'}), 500


@orders_bp.route('/api/orders/for_delivery', methods=['GET'])
@login_required
def get_delivery_orders():
    try:
        orders = Order.query.filter_by(status='for_delivery').all()
        return jsonify([o.to_dict() for o in orders])
    except Exception as e:
        print(f"Error getting delivery orders: {str(e)}")
        return jsonify({'error': f'Error loading delivery orders: {str(e)}'}), 500


@orders_bp.route('/api/orders/realized', methods=['GET'])
@login_required
def get_realized_orders():
    try:
        orders = Order.query.filter_by(status='realized').all()
        return jsonify([o.to_dict() for o in orders])
    except Exception as e:
        print(f"Error getting realized orders: {str(e)}")
        return jsonify({'error': f'Error loading realized orders: {str(e)}'}), 500


@orders_bp.route('/api/orders', methods=['POST'])
@login_required
def create_order():
    try:
        form_data = request.form
        file = request.files.get('image')
        filename = ''
        if file and file.filename:
            filename = f"{int(time.time())}_{file.filename}"
            file.save(os.path.join(current_app.config['IMAGES_DIR'], filename))

        # Validate required fields
        if not form_data.get('name'):
            return jsonify({'error': 'Name is required'}), 400
        if not form_data.get('customer'):
            return jsonify({'error': 'Customer is required'}), 400
        
        try:
            price = float(form_data.get('price', 0))
        except (ValueError, TypeError):
            return jsonify({'error': 'Price must be a number'}), 400
        
        try:
            quantity = int(form_data.get('quantity', 1))
        except (ValueError, TypeError):
            quantity = 1

        order = Order(
            name=form_data['name'],
            price=price,
            paid=form_data.get('paid', 'false') == 'true',
            customer=form_data['customer'],
            date=form_data.get('date', ''),
            quantity=quantity,
            color=form_data.get('color', ''),
            description=form_data.get('description', ''),
            image=filename,
            status='new'
        )
        db.session.add(order)
        db.session.commit()
        return jsonify({'ok': True})
    except Exception as e:
        db.session.rollback()
        print(f"Error creating order: {str(e)}")
        return jsonify({'error': f'Error creating order: {str(e)}'}), 500


@orders_bp.route('/api/update_status', methods=['POST'])
@login_required
def update_status():
    data = request.get_json()
    order = db.session.get(Order, data['id'])
    if not order:
        return jsonify({'error': 'Order not found'}), 404

    if 'paid' in data:
        order.paid = data['paid']
    order.status = data['status']
    db.session.commit()
    return jsonify({'ok': True})


@orders_bp.route('/api/order/<int:order_id>', methods=['GET'])
@login_required
def get_order(order_id):
    order = db.session.get(Order, order_id)
    if not order:
        return jsonify({'error': 'Order not found'}), 404
    return jsonify(order.to_dict())


@orders_bp.route('/api/delete_order/<int:order_id>', methods=['DELETE'])
@login_required
def delete_order(order_id):
    order = db.session.get(Order, order_id)
    if not order:
        return jsonify({'error': 'Order not found'}), 404
    db.session.delete(order)
    db.session.commit()
    return jsonify({'ok': True})

@orders_bp.route('/api/update_order/<int:order_id>', methods=['POST'])
@login_required
def update_order(order_id):
    order = db.session.get(Order, order_id)
    if not order:
        return jsonify({'error': 'Order not found'}), 404

    form_data = request.form
    order.name = form_data.get('name', order.name)
    order.price = float(form_data.get('price', order.price))
    order.paid = form_data.get('paid') == 'true'
    order.customer = form_data.get('customer', order.customer)
    order.date = form_data.get('date', order.date)
    order.description = form_data.get('description', order.description)

    if 'image' in request.files and request.files['image'].filename:
        file = request.files['image']
        filename = f"{int(time.time())}_{file.filename}"
        file.save(os.path.join(current_app.config['IMAGES_DIR'], filename))
        order.image = filename

    db.session.commit()
    return jsonify({'ok': True})


@orders_bp.route('/api/order_from_lager', methods=['POST'])
@login_required
def order_from_lager():
    data = request.get_json()
    order_qty = int(data.get('quantity', 1))
    inventory_id = int(data.get('lager_id', 0)) if data.get('lager_id') else None

    # Subtract quantity from inventory (minimum 0)
    if inventory_id:
        item = db.session.get(InventoryItem, int(inventory_id))
        if item:
            item.quantity = max(0, item.quantity - order_qty)

    order = Order(
        name=data.get('name', ''),
        price=float(data.get('price', 0)),
        paid=data.get('paid', 'false') == 'true',
        customer=data.get('customer', ''),
        date=data.get('date', ''),
        quantity=order_qty,
        color=data.get('color', ''),
        description=data.get('description', ''),
        image=data.get('image', ''),
        status='new',
        inventory_id=inventory_id if inventory_id else None
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
    
    if not order.inventory_id:
        return jsonify({'error': 'Order has no inventory_id'}), 404
    
    item = db.session.get(InventoryItem, int(order.inventory_id))
    if not item:
        return jsonify({'error': 'Inventory item not found'}), 404
    
    # Return the order quantity back to lager
    item.quantity += order.quantity
    
    # Delete the order after returning to lager
    db.session.delete(order)
    
    db.session.commit()
    return jsonify({'ok': True})
