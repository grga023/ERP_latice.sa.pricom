from flask import Blueprint, jsonify, request, render_template, current_app
from flask_login import login_required
import json
import os
import logging

config_bp = Blueprint('config', __name__)
logger = logging.getLogger(__name__)

def get_config_path():
    return os.path.join(current_app.config.get('DATA_DIR', 'data'), 'config.json')

def load_config():
    config_file = get_config_path()
    logger.debug(f"Loading config from {config_file}")
    if os.path.exists(config_file):
        try:
            with open(config_file) as f:
                config = json.load(f)
            logger.info(f"Configuration loaded: {len(config)} entries")
            return config
        except Exception as e:
            logger.error(f"Error loading config file: {e}", exc_info=True)
            return {}
    logger.warning(f"Config file not found: {config_file}")
    return {}

def save_config(data):
    config_file = get_config_path()
    logger.info(f"Saving configuration to {config_file}")
    try:
        with open(config_file, 'w') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logger.info(f"Configuration saved successfully: {len(data)} entries")
    except Exception as e:
        logger.error(f"Error saving config: {e}", exc_info=True)
        raise

@config_bp.route('/config')
@config_bp.route('/config/')
@login_required
def config_page():
    """Config stranica"""
    logger.debug("Config page accessed")
    config = load_config()
    return render_template('settings.html', config=config)

@config_bp.route('/api/config', methods=['GET'])
@login_required
def api_get_config():
    return jsonify(load_config())

@config_bp.route('/api/config', methods=['POST'])
@login_required
def api_save_config():
    data = request.get_json()
    logger.info("Saving configuration via API")
    try:
        save_config(data)
        return jsonify({'status': 'ok', 'message': 'Konfiguracija sačuvana'})
    except Exception as e:
        logger.error(f"Failed to save config: {e}", exc_info=True)
        return jsonify({'status': 'error', 'message': f'Greška: {str(e)}'}), 500

@config_bp.route('/api/config/branding', methods=['POST'])
@login_required
def upload_branding():
    """Upload logo/favicon"""
    logger.info("Branding upload requested")
    
    if 'file' not in request.files:
        logger.warning("Branding upload failed: no file in request")
        return jsonify({'error': 'Nema fajla'}), 400
    
    file = request.files['file']
    file_type = request.form.get('type', 'logo')  # logo, logoSmall, favicon
    
    logger.debug(f"Branding file type: {file_type}, filename: {file.filename}")
    
    if file.filename == '':
        logger.warning("Branding upload failed: empty filename")
        return jsonify({'error': 'Nije izabran fajl'}), 400
    
    # Sačuvaj fajl
    branding_dir = os.path.join(current_app.config.get('IMAGES_DIR', 'images'), 'branding')
    os.makedirs(branding_dir, exist_ok=True)
    
    filename_map = {
        'logo': 'logo.png',
        'logoSmall': 'logo-small.png',
        'favicon': 'favicon.ico'
    }
    
    filename = filename_map.get(file_type, 'logo.png')
    filepath = os.path.join(branding_dir, filename)
    
    try:
        file.save(filepath)
        logger.info(f"Branding file saved: {filename} at {filepath}")
        return jsonify({'status': 'ok', 'path': f'/images/branding/{filename}'})
    except Exception as e:
        logger.error(f"Error saving branding file: {e}", exc_info=True)
        return jsonify({'error': f'Greška pri snimanju: {str(e)}'}), 500
