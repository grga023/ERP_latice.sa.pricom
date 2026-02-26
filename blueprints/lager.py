from flask import Blueprint, request, jsonify, render_template, current_app
from flask_login import login_required
import time
import os
from models import db, LagerItem

lager_bp = Blueprint('lager', __name__)


# ─── Page Route ────────────────────────────────────────────────

@lager_bp.route('/lager')
@lager_bp.route('/lager.html')
@login_required
def lager_page():
    return render_template('lager.html')


# ─── API Routes ────────────────────────────────────────────────

@lager_bp.route('/api/lager', methods=['GET'])
@login_required
def get_lager():
    items = LagerItem.query.all()
    return jsonify([i.to_dict() for i in items])


@lager_bp.route('/api/lager', methods=['POST'])
@login_required
def add_lager():
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
        
        try:
            cena = float(o.get('cena', 0))
        except (ValueError, TypeError):
            cena = 0.0
        
        try:
            kolicina = int(o.get('kolicina', 0))
        except (ValueError, TypeError):
            kolicina = 0

        item = LagerItem(
            naziv=o.get('naziv', ''),
            cena=cena,
            boja=o.get('boja', ''),
            kolicina=kolicina,
            lokacija=o.get('lokacija', 'Kuća'),
            slika=filename
        )
        db.session.add(item)
        db.session.commit()
        return jsonify({'ok': True})
    except Exception as e:
        db.session.rollback()
        print(f"Error adding lager item: {str(e)}")
        return jsonify({'error': f'Greška pri dodavanju artikla: {str(e)}'}), 500


@lager_bp.route('/api/lager/<int:item_id>', methods=['DELETE'])
@login_required
def delete_lager(item_id):
    item = db.session.get(LagerItem, item_id)
    if not item:
        return jsonify({'error': 'Artikal nije pronađen'}), 404
    db.session.delete(item)
    db.session.commit()
    return jsonify({'ok': True})


@lager_bp.route('/api/lager/<int:item_id>/increase_quantity', methods=['POST'])
@login_required
def increase_quantity(item_id):
    item = db.session.get(LagerItem, item_id)
    if not item:
        return jsonify({'error': 'Artikal nije pronađen'}), 404
    
    data = request.get_json()
    increase_by = int(data.get('quantity', 0))
    
    if increase_by <= 0:
        return jsonify({'error': 'Količina mora biti veća od 0'}), 400
    
    item.kolicina += increase_by
    db.session.commit()
    return jsonify({'ok': True, 'new_quantity': item.kolicina})
