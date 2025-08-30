from flask import Blueprint, request, jsonify
import yaml
from yaml import YAMLError

yaml_tools_bp = Blueprint('yaml_tools', __name__)

@yaml_tools_bp.route('/format', methods=['POST'])
def format_yaml():
    """格式化YAML"""
    try:
        data = request.get_json()
        if not data or 'yaml_text' not in data:
            return jsonify({'error': '请提供yaml_text字段'}), 400

        yaml_text = data['yaml_text']
        if not yaml_text.strip():
            return jsonify({'error': 'YAML文本不能为空'}), 400

        # 解析并格式化YAML
        parsed_yaml = yaml.safe_load(yaml_text)
        formatted_yaml = yaml.dump(parsed_yaml, default_flow_style=False, allow_unicode=True, indent=2)

        return jsonify({
            'success': True,
            'formatted_yaml': formatted_yaml,
            'original_length': len(yaml_text),
            'formatted_length': len(formatted_yaml)
        }), 200

    except YAMLError as e:
        return jsonify({
            'error': f'YAML格式错误: {str(e)}'
        }), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@yaml_tools_bp.route('/minify', methods=['POST'])
def minify_yaml():
    """压缩YAML"""
    try:
        data = request.get_json()
        if not data or 'yaml_text' not in data:
            return jsonify({'error': '请提供yaml_text字段'}), 400

        yaml_text = data['yaml_text']
        if not yaml_text.strip():
            return jsonify({'error': 'YAML文本不能为空'}), 400

        # 解析并压缩YAML
        parsed_yaml = yaml.safe_load(yaml_text)
        minified_yaml = yaml.dump(parsed_yaml, default_flow_style=True, allow_unicode=True)

        return jsonify({
            'success': True,
            'minified_yaml': minified_yaml,
            'original_length': len(yaml_text),
            'minified_length': len(minified_yaml)
        }), 200

    except YAMLError as e:
        return jsonify({
            'error': f'YAML格式错误: {str(e)}'
        }), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@yaml_tools_bp.route('/validate', methods=['POST'])
def validate_yaml():
    """验证YAML格式"""
    try:
        data = request.get_json()
        if not data or 'yaml_text' not in data:
            return jsonify({'error': '请提供yaml_text字段'}), 400

        yaml_text = data['yaml_text']
        if not yaml_text.strip():
            return jsonify({'error': 'YAML文本不能为空'}), 400

        # 尝试解析YAML
        parsed_yaml = yaml.safe_load(yaml_text)

        return jsonify({
            'success': True,
            'valid': True,
            'message': 'YAML格式正确',
            'parsed_data': parsed_yaml
        }), 200

    except YAMLError as e:
        return jsonify({
            'success': True,
            'valid': False,
            'error': f'YAML格式错误: {str(e)}'
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@yaml_tools_bp.route('/to-json', methods=['POST'])
def yaml_to_json():
    """YAML转JSON"""
    try:
        data = request.get_json()
        if not data or 'yaml_text' not in data:
            return jsonify({'error': '请提供yaml_text字段'}), 400

        yaml_text = data['yaml_text']
        if not yaml_text.strip():
            return jsonify({'error': 'YAML文本不能为空'}), 400

        # 解析YAML并转换为JSON
        parsed_yaml = yaml.safe_load(yaml_text)
        import json
        json_output = json.dumps(parsed_yaml, indent=2, ensure_ascii=False)

        return jsonify({
            'success': True,
            'json_output': json_output,
            'original_length': len(yaml_text),
            'json_length': len(json_output)
        }), 200

    except YAMLError as e:
        return jsonify({
            'error': f'YAML格式错误: {str(e)}'
        }), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@yaml_tools_bp.route('/from-json', methods=['POST'])
def json_to_yaml():
    """JSON转YAML"""
    try:
        data = request.get_json()
        if not data or 'json_text' not in data:
            return jsonify({'error': '请提供json_text字段'}), 400

        json_text = data['json_text']
        if not json_text.strip():
            return jsonify({'error': 'JSON文本不能为空'}), 400

        # 解析JSON并转换为YAML
        import json
        parsed_json = json.loads(json_text)
        yaml_output = yaml.dump(parsed_json, default_flow_style=False, allow_unicode=True, indent=2)

        return jsonify({
            'success': True,
            'yaml_output': yaml_output,
            'original_length': len(json_text),
            'yaml_length': len(yaml_output)
        }), 200

    except json.JSONDecodeError as e:
        return jsonify({
            'error': f'JSON格式错误: {str(e)}'
        }), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500
