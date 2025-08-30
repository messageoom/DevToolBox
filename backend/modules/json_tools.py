from flask import Blueprint, request, jsonify
import json

json_tools_bp = Blueprint('json_tools', __name__)

@json_tools_bp.route('/format', methods=['POST'])
def format_json():
    """格式化JSON"""
    try:
        data = request.get_json()
        if not data or 'json_text' not in data:
            return jsonify({'error': '请提供json_text字段'}), 400

        json_text = data['json_text']
        if not json_text.strip():
            return jsonify({'error': 'JSON文本不能为空'}), 400

        # 解析并格式化JSON
        parsed_json = json.loads(json_text)
        formatted_json = json.dumps(parsed_json, indent=2, ensure_ascii=False)

        return jsonify({
            'success': True,
            'formatted_json': formatted_json,
            'original_length': len(json_text),
            'formatted_length': len(formatted_json)
        }), 200

    except json.JSONDecodeError as e:
        return jsonify({
            'error': f'JSON格式错误: {str(e)}',
            'position': e.pos if hasattr(e, 'pos') else None
        }), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@json_tools_bp.route('/minify', methods=['POST'])
def minify_json():
    """压缩JSON"""
    try:
        data = request.get_json()
        if not data or 'json_text' not in data:
            return jsonify({'error': '请提供json_text字段'}), 400

        json_text = data['json_text']
        if not json_text.strip():
            return jsonify({'error': 'JSON文本不能为空'}), 400

        # 解析并压缩JSON
        parsed_json = json.loads(json_text)
        minified_json = json.dumps(parsed_json, separators=(',', ':'), ensure_ascii=False)

        return jsonify({
            'success': True,
            'minified_json': minified_json,
            'original_length': len(json_text),
            'minified_length': len(minified_json)
        }), 200

    except json.JSONDecodeError as e:
        return jsonify({
            'error': f'JSON格式错误: {str(e)}',
            'position': e.pos if hasattr(e, 'pos') else None
        }), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@json_tools_bp.route('/validate', methods=['POST'])
def validate_json():
    """验证JSON格式"""
    try:
        data = request.get_json()
        if not data or 'json_text' not in data:
            return jsonify({'error': '请提供json_text字段'}), 400

        json_text = data['json_text']
        if not json_text.strip():
            return jsonify({'error': 'JSON文本不能为空'}), 400

        # 尝试解析JSON
        parsed_json = json.loads(json_text)

        return jsonify({
            'success': True,
            'valid': True,
            'message': 'JSON格式正确',
            'parsed_data': parsed_json
        }), 200

    except json.JSONDecodeError as e:
        return jsonify({
            'success': True,
            'valid': False,
            'error': f'JSON格式错误: {str(e)}',
            'position': e.pos if hasattr(e, 'pos') else None
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@json_tools_bp.route('/escape', methods=['POST'])
def escape_json():
    """转义JSON字符串"""
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({'error': '请提供text字段'}), 400

        text = data['text']
        escaped_text = json.dumps(text, ensure_ascii=False)

        return jsonify({
            'success': True,
            'escaped_text': escaped_text,
            'original_length': len(text),
            'escaped_length': len(escaped_text)
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@json_tools_bp.route('/unescape', methods=['POST'])
def unescape_json():
    """反转义JSON字符串"""
    try:
        data = request.get_json()
        if not data or 'json_string' not in data:
            return jsonify({'error': '请提供json_string字段'}), 400

        json_string = data['json_string']
        if not json_string.strip():
            return jsonify({'error': 'JSON字符串不能为空'}), 400

        # 解析JSON字符串
        unescaped_text = json.loads(json_string)

        return jsonify({
            'success': True,
            'unescaped_text': unescaped_text,
            'original_length': len(json_string),
            'unescaped_length': len(str(unescaped_text))
        }), 200

    except json.JSONDecodeError as e:
        return jsonify({
            'error': f'JSON字符串格式错误: {str(e)}',
            'position': e.pos if hasattr(e, 'pos') else None
        }), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500
