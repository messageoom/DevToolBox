from flask import Blueprint, request, jsonify
import uuid
import logging
from datetime import datetime, timezone

try:
    from ..utils.error_handler import safe_error
except ImportError:
    from backend.utils.error_handler import safe_error

logger = logging.getLogger(__name__)

uuid_tools_bp = Blueprint('uuid_tools', __name__)

# Namespace mapping
NAMESPACE_MAP = {
    'DNS': uuid.NAMESPACE_DNS,
    'URL': uuid.NAMESPACE_URL,
    'OID': uuid.NAMESPACE_OID,
    'X500': uuid.NAMESPACE_X500,
}

VARIANT_MAP = {
    'reserved for NCS compatibility': 'reserved',
    'RFC 4122': 'rfc4122',
    'reserved for Microsoft compatibility': 'microsoft',
    'reserved for future definition': 'future',
}


def get_variant_name(u):
    """Get human-readable variant name from a UUID object."""
    variant = u.variant
    for desc, name in VARIANT_MAP.items():
        if variant == getattr(uuid, 'RESERVED_NCS', None) and name == 'reserved':
            return 'reserved (NCS)'
        if variant == getattr(uuid, 'RFC_4122', None) and name == 'rfc4122':
            return 'RFC 4122'
        if variant == getattr(uuid, 'RESERVED_MICROSOFT', None) and name == 'microsoft':
            return 'reserved (Microsoft)'
        if variant == getattr(uuid, 'RESERVED_FUTURE', None) and name == 'future':
            return 'reserved (future)'
    return str(variant)


@uuid_tools_bp.route('/generate', methods=['POST'])
def generate_uuid():
    """Generate UUIDs"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': '请提供请求参数'}), 400

        version = data.get('version', 4)
        namespace_str = data.get('namespace', 'DNS')
        name = data.get('name', '')
        count = data.get('count', 1)
        uppercase = data.get('uppercase', False)

        # Validate version
        if version not in (1, 3, 4, 5):
            return jsonify({'error': '版本号必须是 1、3、4 或 5'}), 400

        # Validate count
        try:
            count = int(count)
        except (TypeError, ValueError):
            return jsonify({'error': 'count 必须是整数'}), 400
        if count < 1 or count > 100:
            return jsonify({'error': 'count 必须在 1-100 之间'}), 400

        # v3 and v5 require name
        if version in (3, 5):
            if not name:
                return jsonify({'error': '版本 3 和 5 需要提供 name 参数'}), 400
            if namespace_str not in NAMESPACE_MAP:
                return jsonify({'error': f'不支持的空间命名: {namespace_str}，可选值: DNS, URL, OID, X500'}), 400

        uuids = []
        for _ in range(count):
            if version == 1:
                generated = uuid.uuid1()
            elif version == 3:
                ns = NAMESPACE_MAP[namespace_str]
                generated = uuid.uuid3(ns, name)
            elif version == 4:
                generated = uuid.uuid4()
            elif version == 5:
                ns = NAMESPACE_MAP[namespace_str]
                generated = uuid.uuid5(ns, name)
            else:
                return jsonify({'error': f'不支持的版本: {version}'}), 400

            uuid_str = str(generated)
            if uppercase:
                uuid_str = uuid_str.upper()
            uuids.append(uuid_str)

        return jsonify({
            'success': True,
            'uuids': uuids,
            'version': version,
            'count': len(uuids)
        }), 200

    except Exception as e:
        return safe_error(e)


@uuid_tools_bp.route('/validate', methods=['POST'])
def validate_uuid():
    """Validate a UUID string"""
    try:
        data = request.get_json()
        if not data or 'uuid_str' not in data:
            return jsonify({'error': '请提供 uuid_str 参数'}), 400

        uuid_str = data['uuid_str']
        if not uuid_str:
            return jsonify({'error': 'uuid_str 不能为空'}), 400

        try:
            parsed = uuid.UUID(uuid_str)
            valid = True
            version = parsed.version
            variant = get_variant_name(parsed)
        except (ValueError, AttributeError):
            valid = False
            version = None
            variant = None

        return jsonify({
            'success': True,
            'valid': valid,
            'version': version,
            'variant': variant
        }), 200

    except Exception as e:
        return safe_error(e)


@uuid_tools_bp.route('/parse', methods=['POST'])
def parse_uuid():
    """Parse UUID details"""
    try:
        data = request.get_json()
        if not data or 'uuid_str' not in data:
            return jsonify({'error': '请提供 uuid_str 参数'}), 400

        uuid_str = data['uuid_str']
        if not uuid_str:
            return jsonify({'error': 'uuid_str 不能为空'}), 400

        try:
            parsed = uuid.UUID(uuid_str)
        except ValueError:
            return jsonify({'error': '无效的 UUID 字符串'}), 400

        result = {
            'success': True,
            'uuid': str(parsed),
            'version': parsed.version,
            'variant': get_variant_name(parsed),
            'fields': {
                'time_low': parsed.time_low,
                'time_mid': parsed.time_mid,
                'time_hi_version': parsed.time_hi_version,
                'clock_seq_hi_variant': parsed.clock_seq_hi_variant,
                'clock_seq_low': parsed.clock_seq_low,
                'node': parsed.node,
            }
        }

        # For UUIDv1, include extra fields
        if parsed.version == 1:
            # Get time value (100-nanosecond intervals since 1582-10-15)
            time_value = parsed.time

            # Convert UUID time to datetime
            # UUID time is in 100ns intervals since 1582-10-15 00:00:00
            # Unix epoch is 1970-01-01 00:00:00
            # Difference: 122192928000000000 (100ns intervals)
            ns_intervals = time_value - 0x01b21dd213814000
            seconds = ns_intervals / 10000000.0
            try:
                dt = datetime.fromtimestamp(seconds, tz=timezone.utc)
                time_as_datetime = dt.isoformat()
            except (OSError, OverflowError, ValueError):
                time_as_datetime = None

            # Format MAC address from node field
            node = parsed.node
            mac_address = ':'.join([f'{(node >> (8 * (5 - i))) & 0xff:02X}' for i in range(6)])

            # Clock sequence
            clock_seq = parsed.clock_seq

            result['time'] = time_value
            result['time_as_datetime'] = time_as_datetime
            result['mac_address'] = mac_address
            result['clock_seq'] = clock_seq

        return jsonify(result), 200

    except Exception as e:
        return safe_error(e)
