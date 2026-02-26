from flask import Blueprint, jsonify, request, render_template, current_app
from flask_login import login_required
import json
import os

config_bp = Blueprint('config', __name__)


def get_config_path():
    """Get path to config.json file"""
    data_dir = current_app.config.get('DATA_DIR')
    if not data_dir:
        # Fallback for production environment
        if os.path.exists('/usb/ERP_data/data'):
            data_dir = '/usb/ERP_data/data'
        else:
            data_dir = 'data'
    return os.path.join(data_dir, 'config.json')


def load_config():
    """Load configuration from JSON file"""
    config_file = get_config_path()
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading config: {str(e)}")
            return {}
    return {}


def save_config(data):
    """Save configuration to JSON file"""
    config_file = get_config_path()
    try:
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving config: {str(e)}")
        raise


@config_bp.route('/settings')
@config_bp.route('/settings.html')
@login_required
def settings_page():
    """Settings page"""
    config = load_config()
    return render_template('settings.html', config=config)


@config_bp.route('/api/config', methods=['GET'])
@login_required
def get_config_api():
    """Get application configuration"""
    return jsonify(load_config())


@config_bp.route('/api/config', methods=['POST'])
@login_required
def save_config_api():
    """Save application configuration"""
    try:
        data = request.get_json()
        save_config(data)
        return jsonify({'status': 'ok', 'message': 'Configuration saved successfully'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@config_bp.route('/api/config/branding', methods=['POST'])
@login_required
def upload_branding_file():
    """Upload branding files (logo, favicon)"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    file_type = request.form.get('type', 'logo')  # logo, logoSmall, favicon
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    try:
        # Get branding directory
        images_dir = current_app.config.get('IMAGES_DIR')
        if not images_dir:
            if os.path.exists('/usb/ERP_data/images'):
                images_dir = '/usb/ERP_data/images'
            else:
                images_dir = 'images'
        
        branding_dir = os.path.join(images_dir, 'branding')
        os.makedirs(branding_dir, exist_ok=True)
        
        # Map file type to filename
        filename_map = {
            'logo': 'logo.png',
            'logoSmall': 'logo-small.png',
            'favicon': 'favicon.ico'
        }
        
        filename = filename_map.get(file_type, 'logo.png')
        filepath = os.path.join(branding_dir, filename)
        file.save(filepath)
        
        return jsonify({'status': 'ok', 'path': f'/images/branding/{filename}'})
    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)}), 500
