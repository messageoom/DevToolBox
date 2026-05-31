from flask import Blueprint, request, jsonify
import secrets
import hashlib
import base64
import uuid
import re
import logging

try:
    from ..utils.error_handler import safe_error
except ImportError:
    from backend.utils.error_handler import safe_error

logger = logging.getLogger(__name__)
apikey_tools_bp = Blueprint('apikey_tools', __name__)

# Key type constants
KEY_TYPES = ['random', 'base64', 'uuid', 'hex']

# Regex patterns for type detection
BASE64_PATTERN = re.compile(r'^[A-Za-z0-9+/]+=*$')
HEX_PATTERN = re.compile(r'^[a-fA-F0-9]+$')
UUID_PATTERN = re.compile(
    r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$'
)

# Supported hash algorithms for key hashing
HASH_ALGORITHMS = {
    'sha256': hashlib.sha256,
    'sha384': hashlib.sha384,
    'sha512': hashlib.sha512,
    'md5': hashlib.md5,
}


def _generate_single_key(key_type, length):
    """Generate a single API key of the specified type and length."""
    if key_type == 'uuid':
        return str(uuid.uuid4())

    if key_type == 'random':
        raw = secrets.token_urlsafe(length)
        return raw[:length]

    if key_type == 'base64':
        raw = base64.b64encode(secrets.token_bytes(length)).decode()
        return raw[:length]

    if key_type == 'hex':
        raw = secrets.token_hex(max(1, length // 2))
        return raw[:length]

    return secrets.token_urlsafe(length)[:length]


def _detect_key_type(key):
    """Detect the type of a given key string."""
    if UUID_PATTERN.match(key):
        return 'uuid'
    if HEX_PATTERN.match(key):
        return 'hex'
    if BASE64_PATTERN.match(key):
        return 'base64'
    return 'random'


def _mask_key(key):
    """Return a masked version of the key showing first 4 and last 4 chars."""
    if len(key) <= 8:
        return '****'
    return key[:4] + '****...****' + key[-4:]


@apikey_tools_bp.route('/generate', methods=['POST'])
def generate_keys():
    """Generate API keys."""
    try:
        data = request.get_json()
        if not data:
            data = {}

        key_type = data.get('type', 'random')
        if key_type not in KEY_TYPES:
            return jsonify({'error': f'不支持的类型: {key_type}', 'success': False}), 400

        length = data.get('length', 32)
        try:
            length = int(length)
        except (TypeError, ValueError):
            length = 32
        length = max(16, min(512, length))

        prefix = data.get('prefix', '').strip()

        count = data.get('count', 1)
        try:
            count = int(count)
        except (TypeError, ValueError):
            count = 1
        count = max(1, min(50, count))

        keys = []
        for _ in range(count):
            raw_key = _generate_single_key(key_type, length)
            if prefix:
                prefixed_key = f"{prefix}_{raw_key}"
            else:
                prefixed_key = raw_key

            keys.append({
                'key': raw_key,
                'prefixed_key': prefixed_key,
                'type': key_type,
                'length': len(raw_key),
            })

        return jsonify({
            'success': True,
            'keys': keys,
            'count': len(keys),
        }), 200

    except Exception as e:
        return safe_error(e)


@apikey_tools_bp.route('/validate', methods=['POST'])
def validate_key():
    """Validate an API key format."""
    try:
        data = request.get_json()
        if not data or 'key' not in data:
            return jsonify({'error': '请提供key字段', 'success': False}), 400

        key = data['key']
        expected_type = data.get('expected_type')
        min_length = data.get('min_length', 16)
        expected_prefix = data.get('expected_prefix')

        try:
            min_length = int(min_length)
        except (TypeError, ValueError):
            min_length = 16

        issues = []
        valid = True

        # Check not empty
        if not key or not key.strip():
            issues.append('Key为空')
            valid = False
            return jsonify({
                'success': True,
                'valid': False,
                'detected_type': 'unknown',
                'length': 0,
                'has_prefix': False,
                'issues': issues,
            }), 200

        # Check min length
        if len(key) < min_length:
            issues.append(f'Key长度({len(key)})小于最小要求({min_length})')
            valid = False

        # Detect type
        detected_type = _detect_key_type(key)

        # Check expected type
        if expected_type:
            if expected_type not in KEY_TYPES:
                issues.append(f'未知的预期类型: {expected_type}')
                valid = False
            else:
                if detected_type != expected_type:
                    issues.append(f'Key类型({detected_type})与预期类型({expected_type})不匹配')
                    valid = False

        # Check expected prefix
        has_prefix = False
        if expected_prefix:
            if key.startswith(expected_prefix + '_'):
                has_prefix = True
            elif key.startswith(expected_prefix):
                has_prefix = True
            else:
                issues.append(f'Key不以预期前缀({expected_prefix})开头')
                valid = False
        else:
            # Auto-detect prefix: check if key has a prefix pattern like xxx_
            prefix_match = re.match(r'^([a-zA-Z][a-zA-Z0-9]*)_+', key)
            if prefix_match:
                has_prefix = True

        return jsonify({
            'success': True,
            'valid': valid,
            'detected_type': detected_type,
            'length': len(key),
            'has_prefix': has_prefix,
            'issues': issues,
        }), 200

    except Exception as e:
        return safe_error(e)


@apikey_tools_bp.route('/hash-key', methods=['POST'])
def hash_key():
    """Hash an API key for storage."""
    try:
        data = request.get_json()
        if not data or 'key' not in data:
            return jsonify({'error': '请提供key字段', 'success': False}), 400

        key = data['key']
        algorithm = data.get('algorithm', 'sha256').lower()

        if not key or not key.strip():
            return jsonify({'error': 'Key不能为空', 'success': False}), 400

        if algorithm not in HASH_ALGORITHMS:
            return jsonify({
                'error': f'不支持的算法: {algorithm}，支持: {", ".join(HASH_ALGORITHMS.keys())}',
                'success': False,
            }), 400

        hash_obj = HASH_ALGORITHMS[algorithm]()
        hash_obj.update(key.encode('utf-8'))
        hash_value = hash_obj.hexdigest()

        masked = _mask_key(key)

        return jsonify({
            'success': True,
            'hash': hash_value,
            'algorithm': algorithm,
            'key_length': len(key),
            'hash_length': len(hash_value),
            'masked': masked,
        }), 200

    except Exception as e:
        return safe_error(e)
