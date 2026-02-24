#!/usr/bin/env python3
"""
Latice sa pričom ERP - Flask Application
=========================================
Refactored with:
  - Flask-SQLAlchemy (SQLite) instead of JSON files
  - Blueprints for route organization (orders, lager, email)
  - Jinja2 templates with base.html inheritance
  - Central error handling
"""

import os
import logging
import threading
from flask import Flask, jsonify, send_from_directory
from sqlalchemy import event
from models import db
from blueprints.orders import orders_bp
from blueprints.lager import lager_bp
from blueprints.email_notify import email_bp, notification_scheduler


def create_app():
    """Application factory pattern."""
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.path.join(BASE_DIR, 'data')
    IMAGES_DIR = os.path.join(BASE_DIR, 'images')

    # Ensure directories exist
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(IMAGES_DIR, exist_ok=True)

    app = Flask(
        __name__,
        static_folder='static',
        template_folder='templates'
    )

    # ─── Configuration ─────────────────────────────────────────
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(DATA_DIR, 'erp.db')}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['IMAGES_DIR'] = IMAGES_DIR
    app.config['SECRET_KEY'] = 'latice-sa-pricom-erp-secret'

    # Disable Flask default logging
    log = logging.getLogger('werkzeug')
    log.disabled = True
    app.logger.disabled = True

    # ─── Initialize Extensions ─────────────────────────────────
    db.init_app(app)

    # SQLite PRAGMA optimizacije za brži USB storage
    def set_sqlite_pragma(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=OFF")
        cursor.execute("PRAGMA temp_store=MEMORY")
        cursor.execute("PRAGMA cache_size=-32000")
        cursor.close()

    with app.app_context():
        event.listen(db.engine, "connect", set_sqlite_pragma)
        db.create_all()

    # ─── Register Blueprints ───────────────────────────────────
    app.register_blueprint(orders_bp)
    app.register_blueprint(lager_bp)
    app.register_blueprint(email_bp)

    # ─── Serve Uploaded Images ─────────────────────────────────
    @app.route('/images/<path:filename>')
    def serve_image(filename):
        return send_from_directory(IMAGES_DIR, filename)

    # ─── Central Error Handlers ────────────────────────────────
    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({'error': 'Neispravan zahtev', 'status': 400}), 400

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({'error': 'Resurs nije pronađen', 'status': 404}), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify({'error': 'Metoda nije dozvoljena', 'status': 405}), 405

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({'error': 'Greška na serveru', 'status': 500}), 500

    return app


if __name__ == '__main__':
    app = create_app()

    # Start notification scheduler in background
    t = threading.Thread(target=notification_scheduler, args=(app,), daemon=True)
    t.start()

    # Run Flask
    app.run(host='0.0.0.0', port=8000, debug=False)
