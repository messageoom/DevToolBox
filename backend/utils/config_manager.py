"""
Configuration manager for DevToolBox.
Persists settings to a JSON file next to the executable (packaged) or project root (dev).
"""

import os
import sys
import json
import copy
from pathlib import Path
from datetime import datetime

CONFIG_FILENAME = 'devtoolbox_config.json'

DEFAULT_CONFIG = {
    "security": {
        "token_enabled": True,
        "access_token": None,
        "temp_tokens": []
    },
    "storage": {
        "upload_dir": "uploads",
        "auto_cleanup_days": 0,
        "max_file_size_mb": 50
    },
    "network": {
        "port": 5000,
        "host": "0.0.0.0"
    }
}


def get_config_path():
    """Return the config file path."""
    if getattr(sys, 'frozen', False):
        # Packaged exe: same directory as the executable
        base = os.path.dirname(sys.executable)
    else:
        # Dev mode: project root (2 levels up from this file)
        base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    return Path(base) / CONFIG_FILENAME


def _deep_merge(default, actual):
    """Merge actual config into default, filling missing keys."""
    result = copy.deepcopy(default)
    for key, value in actual.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def load_config():
    """Load config from disk, merging with defaults for missing keys."""
    config_path = get_config_path()
    if config_path.exists():
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                saved = json.load(f)
            return _deep_merge(DEFAULT_CONFIG, saved)
        except (json.JSONDecodeError, IOError):
            pass
    return copy.deepcopy(DEFAULT_CONFIG)


def save_config(config):
    """Save config to disk."""
    config_path = get_config_path()
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        return True
    except IOError:
        return False


def get_upload_dir(config):
    """Return the absolute upload directory path."""
    upload_dir = config.get('storage', {}).get('upload_dir', 'uploads')
    if os.path.isabs(upload_dir):
        return upload_dir
    if getattr(sys, 'frozen', False):
        base = os.path.dirname(sys.executable)
    else:
        base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    return os.path.join(base, upload_dir)


def cleanup_expired_tokens(config):
    """Remove expired temp tokens from config."""
    now = datetime.utcnow().isoformat()
    tokens = config.get('security', {}).get('temp_tokens', [])
    config['security']['temp_tokens'] = [
        t for t in tokens if t.get('expires_at', '') > now
    ]
    return config
