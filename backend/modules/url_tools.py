from flask import Blueprint, request, jsonify
import urllib.parse
import urllib.request
import json

url_tools_bp = Blueprint('url_tools', __name__)

@url_tools_bp.route('/encode', methods=['POST'])
def encode_url():
    """URL编码"""
    try:
        data = request.get_json()
        if not data or 'url' not in data:
            return jsonify({'error': '请提供url字段'}), 400

        url = data['url']
        encoding = data.get('encoding', 'utf-8')
        safe_chars = data.get('safe', '')  # 安全字符

        try:
            # URL编码
            encoded_url = urllib.parse.quote(url, safe=safe_chars, encoding=encoding)

            return jsonify({
                'success': True,
                'encoded_url': encoded_url,
                'original_length': len(url),
                'encoded_length': len(encoded_url),
                'encoding': encoding,
                'safe_chars': safe_chars
            }), 200

        except UnicodeEncodeError as e:
            return jsonify({'error': f'编码错误: {str(e)}'}), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@url_tools_bp.route('/decode', methods=['POST'])
def decode_url():
    """URL解码"""
    try:
        data = request.get_json()
        if not data or 'encoded_url' not in data:
            return jsonify({'error': '请提供encoded_url字段'}), 400

        encoded_url = data['encoded_url']
        encoding = data.get('encoding', 'utf-8')

        try:
            # URL解码
            decoded_url = urllib.parse.unquote(encoded_url, encoding=encoding)

            return jsonify({
                'success': True,
                'decoded_url': decoded_url,
                'original_length': len(encoded_url),
                'decoded_length': len(decoded_url),
                'encoding': encoding
            }), 200

        except UnicodeDecodeError as e:
            return jsonify({'error': f'解码错误: {str(e)}'}), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@url_tools_bp.route('/parse', methods=['POST'])
def parse_url():
    """解析URL"""
    try:
        data = request.get_json()
        if not data or 'url' not in data:
            return jsonify({'error': '请提供url字段'}), 400

        url = data['url']

        try:
            # 解析URL
            parsed = urllib.parse.urlparse(url)

            result = {
                'success': True,
                'scheme': parsed.scheme,
                'netloc': parsed.netloc,
                'hostname': parsed.hostname,
                'port': parsed.port,
                'path': parsed.path,
                'params': parsed.params,
                'query': parsed.query,
                'fragment': parsed.fragment,
                'username': parsed.username,
                'password': parsed.password
            }

            # 解析查询参数
            if parsed.query:
                query_params = urllib.parse.parse_qs(parsed.query, keep_blank_values=True)
                result['query_params'] = query_params

            return jsonify(result), 200

        except Exception as e:
            return jsonify({'error': f'URL解析错误: {str(e)}'}), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@url_tools_bp.route('/build', methods=['POST'])
def build_url():
    """构建URL"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': '请提供URL组件'}), 400

        # 提取URL组件
        scheme = data.get('scheme', 'http')
        netloc = data.get('netloc', '')
        path = data.get('path', '')
        params = data.get('params', '')
        query = data.get('query', '')
        fragment = data.get('fragment', '')

        # 如果提供了查询参数字典，转换为查询字符串
        if 'query_params' in data and isinstance(data['query_params'], dict):
            query = urllib.parse.urlencode(data['query_params'], doseq=True)

        try:
            # 构建URL
            url_components = urllib.parse.ParseResult(
                scheme=scheme,
                netloc=netloc,
                path=path,
                params=params,
                query=query,
                fragment=fragment
            )
            built_url = urllib.parse.urlunparse(url_components)

            return jsonify({
                'success': True,
                'url': built_url,
                'components': {
                    'scheme': scheme,
                    'netloc': netloc,
                    'path': path,
                    'params': params,
                    'query': query,
                    'fragment': fragment
                }
            }), 200

        except Exception as e:
            return jsonify({'error': f'URL构建错误: {str(e)}'}), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@url_tools_bp.route('/validate', methods=['POST'])
def validate_url():
    """验证URL格式"""
    try:
        data = request.get_json()
        if not data or 'url' not in data:
            return jsonify({'error': '请提供url字段'}), 400

        url = data['url']

        try:
            # 尝试解析URL
            parsed = urllib.parse.urlparse(url)

            # 检查是否为有效的URL
            is_valid = bool(parsed.scheme and parsed.netloc)

            result = {
                'success': True,
                'valid': is_valid,
                'url': url
            }

            if is_valid:
                result.update({
                    'scheme': parsed.scheme,
                    'netloc': parsed.netloc,
                    'is_https': parsed.scheme.lower() == 'https',
                    'has_port': parsed.port is not None,
                    'has_query': bool(parsed.query),
                    'has_fragment': bool(parsed.fragment)
                })
            else:
                result['error'] = '无效的URL格式'

            return jsonify(result), 200

        except Exception as e:
            return jsonify({
                'success': True,
                'valid': False,
                'url': url,
                'error': f'URL验证错误: {str(e)}'
            }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@url_tools_bp.route('/shorten', methods=['POST'])
def shorten_url():
    """URL缩短（模拟）"""
    try:
        data = request.get_json()
        if not data or 'url' not in data:
            return jsonify({'error': '请提供url字段'}), 400

        url = data['url']
        service = data.get('service', 'tinyurl')  # 支持的缩短服务

        try:
            # 验证原始URL
            parsed = urllib.parse.urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                return jsonify({'error': '无效的URL格式'}), 400

            # 这里是模拟的URL缩短服务
            # 在实际应用中，你需要集成真实的URL缩短服务API
            import hashlib
            import base64

            # 生成短链接标识符
            url_hash = hashlib.md5(url.encode()).digest()
            short_id = base64.urlsafe_b64encode(url_hash[:6]).decode().rstrip('=')

            # 模拟短链接
            short_url = f"https://{service}.com/{short_id}"

            return jsonify({
                'success': True,
                'original_url': url,
                'short_url': short_url,
                'short_id': short_id,
                'service': service,
                'note': '这是一个模拟的URL缩短服务，实际应用中需要集成真实的缩短服务API'
            }), 200

        except Exception as e:
            return jsonify({'error': f'URL缩短错误: {str(e)}'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@url_tools_bp.route('/extract-links', methods=['POST'])
def extract_links():
    """从文本中提取链接"""
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({'error': '请提供text字段'}), 400

        text = data['text']

        try:
            import re

            # URL正则表达式
            url_pattern = r'https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:\w)*)?)?'

            # 提取链接
            urls = re.findall(url_pattern, text, re.IGNORECASE)

            # 去重并保持顺序
            seen = set()
            unique_urls = []
            for url in urls:
                if url not in seen:
                    seen.add(url)
                    unique_urls.append(url)

            return jsonify({
                'success': True,
                'text_length': len(text),
                'total_links': len(unique_urls),
                'links': unique_urls
            }), 200

        except Exception as e:
            return jsonify({'error': f'链接提取错误: {str(e)}'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@url_tools_bp.route('/encode-query', methods=['POST'])
def encode_query_params():
    """编码查询参数"""
    try:
        data = request.get_json()
        if not data or 'params' not in data:
            return jsonify({'error': '请提供params字段'}), 400

        params = data['params']
        encoding = data.get('encoding', 'utf-8')
        doseq = data.get('doseq', True)  # 是否支持序列值

        if not isinstance(params, dict):
            return jsonify({'error': 'params必须是字典格式'}), 400

        try:
            # 编码查询参数
            query_string = urllib.parse.urlencode(params, doseq=doseq, encoding=encoding)

            return jsonify({
                'success': True,
                'query_string': query_string,
                'params': params,
                'encoding': encoding,
                'doseq': doseq
            }), 200

        except UnicodeEncodeError as e:
            return jsonify({'error': f'编码错误: {str(e)}'}), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@url_tools_bp.route('/decode-query', methods=['POST'])
def decode_query_params():
    """解码查询参数"""
    try:
        data = request.get_json()
        if not data or 'query_string' not in data:
            return jsonify({'error': '请提供query_string字段'}), 400

        query_string = data['query_string']
        encoding = data.get('encoding', 'utf-8')
        keep_blank_values = data.get('keep_blank_values', True)

        try:
            # 解码查询参数
            params = urllib.parse.parse_qs(query_string, keep_blank_values=keep_blank_values, encoding=encoding)

            return jsonify({
                'success': True,
                'query_string': query_string,
                'params': params,
                'encoding': encoding,
                'keep_blank_values': keep_blank_values
            }), 200

        except UnicodeDecodeError as e:
            return jsonify({'error': f'解码错误: {str(e)}'}), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500
