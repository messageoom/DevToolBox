"""
Configuration manager for DevToolBox.
Persists settings to a JSON file next to the executable (packaged) or project root (dev).
"""

import os
import sys
import json
import copy
import time
from pathlib import Path

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
    },
    "ui": {
        "language": "zh"
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


# 配置缓存:基于文件 mtime 失效,避免每个 /api 请求都读盘(before_request 高频调用)
_config_cache = None
_config_mtime = None


def load_config():
    """Load config from disk, merging with defaults for missing keys.

    使用基于 mtime 的缓存:文件未改动时直接返回缓存副本,避免高频请求读盘。
    """
    global _config_cache, _config_mtime
    config_path = get_config_path()
    try:
        mtime = config_path.stat().st_mtime
    except OSError:
        mtime = None

    # 缓存命中(文件未改动)
    if _config_cache is not None and mtime is not None and _config_mtime == mtime:
        return copy.deepcopy(_config_cache)

    if config_path.exists():
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                saved = json.load(f)
            _config_cache = _deep_merge(DEFAULT_CONFIG, saved)
            _config_mtime = mtime
            return copy.deepcopy(_config_cache)
        except (json.JSONDecodeError, IOError):
            pass
    _config_cache = copy.deepcopy(DEFAULT_CONFIG)
    _config_mtime = mtime
    return copy.deepcopy(_config_cache)


def save_config(config):
    """Save config to disk atomically (temp file + os.replace) and refresh cache."""
    global _config_cache, _config_mtime
    config_path = get_config_path()
    tmp_path = config_path.with_suffix(config_path.suffix + '.tmp')
    try:
        with open(tmp_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        os.replace(tmp_path, config_path)
        try:
            os.chmod(config_path, 0o600)  # config 含 access_token 等敏感信息,限制仅本用户可读
        except OSError:
            pass
        # 写盘成功后刷新缓存
        _config_cache = copy.deepcopy(config)
        try:
            _config_mtime = config_path.stat().st_mtime
        except OSError:
            _config_mtime = None
        return True
    except (IOError, OSError):
        # Clean up temp file on failure
        try:
            if tmp_path.exists():
                tmp_path.unlink()
        except OSError:
            pass
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


def get_max_upload_bytes(config=None):
    """返回上传文件大小上限(字节)—— 全项目统一的单一数据源。

    读取 config['storage']['max_file_size_mb'](默认 50MB),钳到 [1, 500]MB。
    im.py / file_upload / Flask MAX_CONTENT_LENGTH / settings 校验均应引用本函数,
    避免多处魔术数字不一致。
    """
    if config is None:
        config = load_config()
    try:
        mb = int(config.get('storage', {}).get('max_file_size_mb', 50))
    except (TypeError, ValueError):
        mb = 50
    return max(1, min(mb, 500)) * 1024 * 1024


def cleanup_expired_tokens(config):
    """Remove expired temp tokens from config."""
    now = time.time()
    tokens = config.get('security', {}).get('temp_tokens', [])
    config['security']['temp_tokens'] = [
        t for t in tokens
        if isinstance(t.get('expires_at'), (int, float)) and t['expires_at'] > now
    ]
    return config
