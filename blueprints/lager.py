from flask import Blueprint, request, jsonify, render_template, current_app
from flask_login import login_required
import time
import os
from models import db, LagerItem

lager_bp = Blueprint('lager', __name__)


# ─── Page Route ────────────────────────────────────────────────

@lager_bp.route('/inventory')
@lager_bp.route('/inventory.html')
@lager_bp.route('/lager')
@lager_bp.route('/lager.html')
@login_required
def inventory_page():
    """Inventory/lager page"""
    return render_template('inventory.html')


# ─── API Routes ────────────────────────────────────────────────

@lager_bp.route('/api/inventory', methods=['GET'])
@lager_bp.route('/api/lager', methods=['GET'])
@login_required
def get_inventory():
    """Get all inventory items"""
    try:
        items = LagerItem.query.all()
        return jsonify([i.to_dict() for i in items])
    except Exception as e:
        print(f"Error getting inventory: {str(e)}")
        return jsonify({'error': str(e)}), 500


@lager_bp.route('/api/inventory', methods=['POST'])
@lager_bp.route('/api/lager', methods=['POST'])
@login_required
def add_inventory():
    """Add new inventory item"""
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
        
        try:
            price = float(form_data.get('price', 0))
        except (ValueError, TypeError):
            price = 0.0
        
        try:
            quantity = int(form_data.get('quantity', 0))
        except (ValueError, TypeError):
            quantity = 0

        item = LagerItem(
            name=form_data.get('name', ''),
            price=price,
            color=form_data.get('color', ''),
            quantity=quantity,
            location=form_data.get('location', 'House'),
            image=filename
        )
        db.session.add(item)
        db.session.commit()
        return jsonify({'ok': True})
    except Exception as e:
        db.session.rollback()
        print(f"Error adding inventory item: {str(e)}")
        return jsonify({'error': f'Error adding inventory item: {str(e)}'}), 500


@lager_bp.route('/api/inventory/<int:item_id>', methods=['DELETE'])
@lager_bp.route('/api/lager/<int:item_id>', methods=['DELETE'])
@login_required
def delete_inventory(item_id):
    """Delete inventory item"""
    try:
        item = db.session.get(LagerItem, item_id)
        if not item:
            return jsonify({'error': 'Item not found'}), 404
        db.session.delete(item)
        db.session.commit()
        return jsonify({'ok': True})
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting inventory item: {str(e)}")
        return jsonify({'error': str(e)}), 500


@lager_bp.route('/api/inventory/<int:item_id>/increase_quantity', methods=['POST'])
@lager_bp.route('/api/lager/<int:item_id>/increase_quantity', methods=['POST'])
@login_required
def increase_quantity(item_id):
    """Increase quantity of inventory item"""
    try:
        item = db.session.get(LagerItem, item_id)
        if not item:
            return jsonify({'error': 'Item not found'}), 404
        
        data = request.get_json()
        increase_by = int(data.get('quantity', 0))
        
        if increase_by <= 0:
            return jsonify({'error': 'Quantity must be greater than 0'}), 400
        
        item.quantity += increase_by
        db.session.commit()
        return jsonify({'ok': True, 'new_quantity': item.quantity})
    except Exception as e:
        db.session.rollback()
        print(f"Error increasing quantity: {str(e)}")
        return jsonify({'error': str(e)}), 500
