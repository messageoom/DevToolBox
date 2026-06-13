"""
Settings management API for DevToolBox.
Provides config CRUD, token management, and runtime status.
"""

from flask import Blueprint, request, jsonify
from datetime import datetime
import uuid
import os
import sys
import time
import platform
import logging

try:
    from ..utils.config_manager import load_config, save_config, cleanup_expired_tokens, get_upload_dir
except ImportError:
    try:
        from utils.config_manager import load_config, save_config, cleanup_expired_tokens, get_upload_dir
    except ImportError:
        from backend.utils.config_manager import load_config, save_config, cleanup_expired_tokens, get_upload_dir

logger = logging.getLogger(__name__)
settings_bp = Blueprint('settings', __name__)

# App start time for uptime calculation
_start_time = time.time()


def _get_version():
    try:
        from app import __version__
        return __version__
    except ImportError:
        try:
            from backend.app import __version__
            return __version__
        except ImportError:
            return 'unknown'


@settings_bp.route('/config', methods=['GET'])
def get_config():
    config = load_config()
    config = cleanup_expired_tokens(config)

    # Mask the access token for display
    response_config = {
        'security': {
            'token_enabled': config.get('security', {}).get('token_enabled', True),
            'has_token': bool(config.get('security', {}).get('access_token')),
            'temp_tokens': config.get('security', {}).get('temp_tokens', [])
        },
        'storage': config.get('storage', {}),
        'network': config.get('network', {})
    }
    return jsonify({'success': True, 'config': response_config})


@settings_bp.route('/config', methods=['POST'])
def update_config():
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'error': 'No data provided'}), 400

    config = load_config()

    # Update sections
    if 'storage' in data:
        storage = data['storage']
        if 'upload_dir' in storage:
            config['storage']['upload_dir'] = str(storage['upload_dir'])
        if 'auto_cleanup_days' in storage:
            config['storage']['auto_cleanup_days'] = max(0, int(storage['auto_cleanup_days']))
        if 'max_file_size_mb' in storage:
            config['storage']['max_file_size_mb'] = max(1, min(100, int(storage['max_file_size_mb'])))

    if 'security' in data:
        security = data['security']
        if 'token_enabled' in security:
            config['security']['token_enabled'] = bool(security['token_enabled'])

    if save_config(config):
        return jsonify({'success': True, 'message': 'Configuration saved'})
    return jsonify({'success': False, 'error': 'Failed to save configuration'}), 500


@settings_bp.route('/security/token', methods=['POST'])
def refresh_token():
    config = load_config()
    new_token = uuid.uuid4().hex
    config['security']['access_token'] = new_token
    save_config(config)

    from flask import current_app
    current_app.config['ACCESS_TOKEN'] = new_token

    # Rebuild temp_tokens list for the response
    port = config.get('network', {}).get('port', 5000)
    token_url = f"http://127.0.0.1:{port}/?token={new_token}"

    return jsonify({
        'success': True,
        'token': new_token,
        'token_url': token_url
    })


@settings_bp.route('/security/temp-token', methods=['POST'])
def create_temp_token():
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'error': 'No data provided'}), 400

    label = data.get('label', 'Temporary')
    expires_minutes = int(data.get('expires_minutes', 60))

    if expires_minutes < 1:
        return jsonify({'success': False, 'error': 'Expiration must be at least 1 minute'}), 400

    token = uuid.uuid4().hex[:16]
    expires_at = time.time() + expires_minutes * 60

    config = load_config()
    config = cleanup_expired_tokens(config)

    temp_entry = {
        'token': token,
        'label': label,
        'expires_at': expires_at,
        'created_at': datetime.utcnow().isoformat()
    }
    config.setdefault('security', {}).setdefault('temp_tokens', []).append(temp_entry)
    save_config(config)

    # Update app-level temp tokens
    from flask import current_app
    current_app.config.setdefault('TEMP_TOKENS', []).append(temp_entry)

    port = config.get('network', {}).get('port', 5000)
    token_url = f"http://127.0.0.1:{port}/?token={token}"

    return jsonify({
        'success': True,
        'temp_token': temp_entry,
        'token_url': token_url
    })


@settings_bp.route('/security/temp-token/<token>', methods=['DELETE'])
def delete_temp_token(token):
    config = load_config()
    tokens = config.get('security', {}).get('temp_tokens', [])
    original_len = len(tokens)
    config['security']['temp_tokens'] = [t for t in tokens if t.get('token') != token]

    if len(config['security']['temp_tokens']) < original_len:
        save_config(config)

        # Update app-level temp tokens
        from flask import current_app
        app_tokens = current_app.config.get('TEMP_TOKENS', [])
        current_app.config['TEMP_TOKENS'] = [t for t in app_tokens if t.get('token') != token]

        return jsonify({'success': True, 'message': 'Temp token deleted'})

    return jsonify({'success': False, 'error': 'Token not found'}), 404


@settings_bp.route('/status', methods=['GET'])
def get_status():
    config = load_config()

    # Upload stats
    upload_dir = get_upload_dir(config)
    file_count = 0
    disk_usage = 0
    if os.path.isdir(upload_dir):
        for f in os.listdir(upload_dir):
            fp = os.path.join(upload_dir, f)
            if os.path.isfile(fp):
                file_count += 1
                try:
                    disk_usage += os.path.getsize(fp)
                except OSError:
                    pass

    uptime = int(time.time() - _start_time)

    return jsonify({
        'success': True,
        'status': {
            'version': _get_version(),
            'python_version': platform.python_version(),
            'platform': platform.system(),
            'uptime_seconds': uptime,
            'file_count': file_count,
            'disk_usage_bytes': disk_usage,
            'config_path': str(upload_dir),
        }
    })
