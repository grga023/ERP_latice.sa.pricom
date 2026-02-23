from flask import Blueprint, request, jsonify, render_template, current_app
import time
import os
from models import db, LagerItem

lager_bp = Blueprint('lager', __name__)


# ─── Page Route ────────────────────────────────────────────────

@lager_bp.route('/lager')
@lager_bp.route('/lager.html')
def lager_page():
    return render_template('lager.html')


# ─── API Routes ────────────────────────────────────────────────

@lager_bp.route('/api/lager', methods=['GET'])
def get_lager():
    items = LagerItem.query.all()
    return jsonify([i.to_dict() for i in items])


@lager_bp.route('/api/lager', methods=['POST'])
def add_lager():
    o = request.form
    file = request.files.get('slika')
    filename = ''
    if file and file.filename:
        filename = f"{int(time.time())}_{file.filename}"
        file.save(os.path.join(current_app.config['IMAGES_DIR'], filename))

    item = LagerItem(
        naziv=o.get('naziv', ''),
        cena=float(o.get('cena', 0)),
        boja=o.get('boja', ''),
        kolicina=int(o.get('kolicina', 0)),
        lokacija=o.get('lokacija', 'Kuća'),
        slika=filename
    )
    db.session.add(item)
    db.session.commit()
    return jsonify({'ok': True})


@lager_bp.route('/api/lager/<int:item_id>', methods=['DELETE'])
def delete_lager(item_id):
    item = db.session.get(LagerItem, item_id)
    if not item:
        return jsonify({'error': 'Artikal nije pronađen'}), 404
    db.session.delete(item)
    db.session.commit()
    return jsonify({'ok': True})
