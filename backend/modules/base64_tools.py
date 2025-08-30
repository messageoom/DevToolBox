from flask import Blueprint, request, jsonify
import base64
import binascii

base64_tools_bp = Blueprint('base64_tools', __name__)

@base64_tools_bp.route('/encode', methods=['POST'])
def encode_base64():
    """Base64编码"""
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({'error': '请提供text字段'}), 400

        text = data['text']
        encoding = data.get('encoding', 'utf-8')

        try:
            # 编码文本
            encoded_bytes = text.encode(encoding)
            encoded_string = base64.b64encode(encoded_bytes).decode('ascii')

            return jsonify({
                'success': True,
                'encoded': encoded_string,
                'original_length': len(text),
                'encoded_length': len(encoded_string),
                'encoding': encoding
            }), 200

        except UnicodeEncodeError as e:
            return jsonify({'error': f'编码错误: {str(e)}'}), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@base64_tools_bp.route('/decode', methods=['POST'])
def decode_base64():
    """Base64解码"""
    try:
        data = request.get_json()
        if not data or 'encoded_text' not in data:
            return jsonify({'error': '请提供encoded_text字段'}), 400

        encoded_text = data['encoded_text']
        encoding = data.get('encoding', 'utf-8')

        try:
            # 解码Base64
            decoded_bytes = base64.b64decode(encoded_text)
            decoded_text = decoded_bytes.decode(encoding)

            return jsonify({
                'success': True,
                'decoded': decoded_text,
                'original_length': len(encoded_text),
                'decoded_length': len(decoded_text),
                'encoding': encoding
            }), 200

        except binascii.Error as e:
            return jsonify({'error': f'Base64格式错误: {str(e)}'}), 400
        except UnicodeDecodeError as e:
            return jsonify({'error': f'解码错误: {str(e)}'}), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@base64_tools_bp.route('/encode-file', methods=['POST'])
def encode_file_base64():
    """文件Base64编码"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': '没有上传文件'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': '没有选择文件'}), 400

        try:
            # 读取文件内容并编码
            file_content = file.read()
            encoded_string = base64.b64encode(file_content).decode('ascii')

            return jsonify({
                'success': True,
                'filename': file.filename,
                'encoded': encoded_string,
                'file_size': len(file_content),
                'encoded_length': len(encoded_string),
                'mime_type': file.mimetype or 'application/octet-stream'
            }), 200

        except Exception as e:
            return jsonify({'error': f'文件处理错误: {str(e)}'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@base64_tools_bp.route('/decode-file', methods=['POST'])
def decode_file_base64():
    """Base64解码为文件"""
    try:
        data = request.get_json()
        if not data or 'encoded_data' not in data:
            return jsonify({'error': '请提供encoded_data字段'}), 400

        encoded_data = data['encoded_data']
        filename = data.get('filename', 'decoded_file')

        try:
            # 解码Base64数据
            decoded_bytes = base64.b64decode(encoded_data)

            # 确定文件扩展名（简单检测）
            if decoded_bytes.startswith(b'\xff\xd8\xff'):
                extension = 'jpg'
            elif decoded_bytes.startswith(b'\x89PNG\r\n\x1a\n'):
                extension = 'png'
            elif decoded_bytes.startswith(b'GIF87a') or decoded_bytes.startswith(b'GIF89a'):
                extension = 'gif'
            elif decoded_bytes.startswith(b'%PDF'):
                extension = 'pdf'
            else:
                extension = 'bin'

            if not filename.endswith(f'.{extension}'):
                filename = f"{filename}.{extension}"

            return jsonify({
                'success': True,
                'filename': filename,
                'file_size': len(decoded_bytes),
                'encoded_length': len(encoded_data),
                'extension': extension,
                'download_url': f'data:application/octet-stream;base64,{encoded_data}'
            }), 200

        except binascii.Error as e:
            return jsonify({'error': f'Base64格式错误: {str(e)}'}), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@base64_tools_bp.route('/validate', methods=['POST'])
def validate_base64():
    """验证Base64格式"""
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({'error': '请提供text字段'}), 400

        text = data['text']

        try:
            # 尝试解码验证
            decoded_bytes = base64.b64decode(text, validate=True)

            return jsonify({
                'success': True,
                'valid': True,
                'message': '有效的Base64格式',
                'decoded_length': len(decoded_bytes),
                'original_length': len(text)
            }), 200

        except binascii.Error as e:
            return jsonify({
                'success': True,
                'valid': False,
                'error': f'无效的Base64格式: {str(e)}'
            }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@base64_tools_bp.route('/url-safe/encode', methods=['POST'])
def encode_url_safe_base64():
    """URL安全的Base64编码"""
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({'error': '请提供text字段'}), 400

        text = data['text']
        encoding = data.get('encoding', 'utf-8')

        try:
            # URL安全的Base64编码
            encoded_bytes = text.encode(encoding)
            encoded_string = base64.urlsafe_b64encode(encoded_bytes).decode('ascii')

            return jsonify({
                'success': True,
                'encoded': encoded_string,
                'original_length': len(text),
                'encoded_length': len(encoded_string),
                'encoding': encoding
            }), 200

        except UnicodeEncodeError as e:
            return jsonify({'error': f'编码错误: {str(e)}'}), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@base64_tools_bp.route('/url-safe/decode', methods=['POST'])
def decode_url_safe_base64():
    """URL安全的Base64解码"""
    try:
        data = request.get_json()
        if not data or 'encoded_text' not in data:
            return jsonify({'error': '请提供encoded_text字段'}), 400

        encoded_text = data['encoded_text']
        encoding = data.get('encoding', 'utf-8')

        try:
            # URL安全的Base64解码
            decoded_bytes = base64.urlsafe_b64decode(encoded_text)
            decoded_text = decoded_bytes.decode(encoding)

            return jsonify({
                'success': True,
                'decoded': decoded_text,
                'original_length': len(encoded_text),
                'decoded_length': len(decoded_text),
                'encoding': encoding
            }), 200

        except binascii.Error as e:
            return jsonify({'error': f'Base64格式错误: {str(e)}'}), 400
        except UnicodeDecodeError as e:
            return jsonify({'error': f'解码错误: {str(e)}'}), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500
