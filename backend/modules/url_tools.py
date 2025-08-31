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

@url_tools_bp.route('/send-request', methods=['POST'])
def send_request():
    """发送HTTP请求"""
    try:
        data = request.get_json()
        if not data or 'url' not in data:
            return jsonify({'error': '请提供url字段'}), 400

        url = data['url']
        method = data.get('method', 'GET').upper()
        headers = data.get('headers', {})
        body = data.get('body', '')

        try:
            import requests
            import time

            # 构建请求
            request_data = {
                'method': method,
                'url': url,
                'headers': headers,
                'timeout': 30  # 30秒超时
            }

            # 添加请求体（如果有的话）
            if body and method in ['POST', 'PUT', 'PATCH']:
                request_data['data'] = body

            # 记录请求开始时间
            start_time = time.time()

            # 发送请求
            response = requests.request(**request_data)

            # 计算响应时间
            response_time = time.time() - start_time

            # 构建响应数据
            result = {
                'success': True,
                'request': {
                    'method': method,
                    'url': url,
                    'headers': dict(headers),
                    'body': body if body else None
                },
                'response': {
                    'status_code': response.status_code,
                    'status_text': response.reason,
                    'headers': dict(response.headers),
                    'content_length': len(response.content),
                    'response_time': round(response_time * 1000, 2),  # 毫秒
                    'url': response.url  # 最终URL（可能重定向）
                }
            }

            # 尝试解析响应内容
            try:
                # 检测内容类型
                content_type = response.headers.get('content-type', '').lower()

                if 'application/json' in content_type:
                    result['response']['body'] = response.json()
                    result['response']['body_type'] = 'json'
                elif 'text/' in content_type or 'xml' in content_type:
                    result['response']['body'] = response.text
                    result['response']['body_type'] = 'text'
                else:
                    # 二进制内容，转换为base64
                    import base64
                    result['response']['body'] = base64.b64encode(response.content).decode()
                    result['response']['body_type'] = 'binary'

            except Exception as e:
                # 如果解析失败，返回原始文本
                result['response']['body'] = response.text
                result['response']['body_type'] = 'text'
                result['response']['parse_error'] = str(e)

            return jsonify(result), 200

        except requests.exceptions.RequestException as e:
            return jsonify({
                'success': False,
                'error': f'请求失败: {str(e)}',
                'error_type': 'request_error'
            }), 200

        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'处理请求时出错: {str(e)}',
                'error_type': 'processing_error'
            }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@url_tools_bp.route('/parse-curl', methods=['POST'])
def parse_curl():
    """解析curl命令"""
    try:
        data = request.get_json()
        if not data or 'curl_command' not in data:
            return jsonify({'error': '请提供curl_command字段'}), 400

        curl_command = data['curl_command'].strip()

        try:
            import re

            # 解析curl命令的基本结构
            parsed = {
                'method': 'GET',
                'url': '',
                'headers': {},
                'data': '',
                'original_command': curl_command
            }

            # 提取HTTP方法
            if '-X' in curl_command or '--request' in curl_command:
                method_match = re.search(r'(-X\s+|--request\s+)([A-Z]+)', curl_command)
                if method_match:
                    parsed['method'] = method_match.group(2)
            elif '-d' in curl_command or '--data' in curl_command or '--data-raw' in curl_command:
                # 如果有数据参数但没有指定方法，默认使用POST
                parsed['method'] = 'POST'
            elif '-d' in curl_command or '--data' in curl_command or '--data-raw' in curl_command:
                # 如果有数据参数但没有指定方法，默认使用POST
                parsed['method'] = 'POST'
            elif '-d' in curl_command or '--data' in curl_command or '--data-raw' in curl_command:
                # 如果有数据参数但没有指定方法，默认使用POST
                parsed['method'] = 'POST'
            elif '-d' in curl_command or '--data' in curl_command or '--data-raw' in curl_command:
                # 如果有数据参数但没有指定方法，默认使用POST
                parsed['method'] = 'POST'
            elif '-d' in curl_command or '--data' in curl_command or '--data-raw' in curl_command:
                # 如果有数据参数但没有指定方法，默认使用POST
                parsed['method'] = 'POST'

            # 提取URL - 支持多种格式
            # 1. 标准格式：curl -X GET "url"
            # 2. 简写格式：curl "url"
            # 3. URL在最后的格式：curl -H "..." --data "..." "url"

            # 先尝试标准格式（URL在-X之后）
            url_match = re.search(r'curl\s+(?:-X\s+[A-Z]+\s+)?[\'"]([^\'"]+)[\'"]', curl_command)
            if url_match:
                parsed['url'] = url_match.group(1)
            else:
                # 处理URL在最后的格式
                # 查找最后一个引号包围的URL
                url_matches = re.findall(r'[\'"](https?://[^\'"]+)[\'"]', curl_command)
                if url_matches:
                    parsed['url'] = url_matches[-1]  # 取最后一个匹配的URL
                else:
                    # 处理不带引号的URL
                    url_match = re.search(r'curl\s+(?:-X\s+[A-Z]+\s+)?(\S+)', curl_command)
                    if url_match:
                        parsed['url'] = url_match.group(1)

            # 提取请求头
            header_matches = re.findall(r'(-H\s+|--header\s+)[\'"]([^\'"]+)[\'"]', curl_command)
            for header_str in header_matches:
                if ':' in header_str[1]:
                    header_name, header_value = header_str[1].split(':', 1)
                    parsed['headers'][header_name.strip()] = header_value.strip()

            # 提取请求数据
            data_match = re.search(r'(-d\s+|--data\s+|--data-raw\s+)[\'"]([^\'"]*)[\'"]', curl_command)
            if data_match:
                parsed['data'] = data_match.group(2)

            return jsonify({
                'success': True,
                'parsed': parsed
            }), 200

        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'解析curl命令失败: {str(e)}'
            }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@url_tools_bp.route('/execute-curl', methods=['POST'])
def execute_curl():
    """执行curl命令（通过解析后发送请求）"""
    try:
        data = request.get_json()
        if not data or 'curl_command' not in data:
            return jsonify({'error': '请提供curl_command字段'}), 400

        curl_command = data['curl_command'].strip()

        try:
            import re
            import requests
            import time

            # 解析curl命令
            parsed = {
                'method': 'GET',
                'url': '',
                'headers': {},
                'data': ''
            }

            # 提取URL - 支持多种格式
            # 1. 标准格式：curl -X GET "url"
            # 2. 简写格式：curl "url"
            # 3. URL在最后的格式：curl -H "..." --data "..." "url"

            # 先尝试标准格式（URL在-X之后）
            url_match = re.search(r'curl\s+(?:-X\s+[A-Z]+\s+)?[\'"]([^\'"]+)[\'"]', curl_command)
            if url_match:
                parsed['url'] = url_match.group(1)
            else:
                # 处理URL在最后的格式
                # 查找最后一个引号包围的URL
                url_matches = re.findall(r'[\'"](https?://[^\'"]+)[\'"]', curl_command)
                if url_matches:
                    parsed['url'] = url_matches[-1]  # 取最后一个匹配的URL
                else:
                    # 处理不带引号的URL
                    url_match = re.search(r'curl\s+(?:-X\s+[A-Z]+\s+)?(\S+)', curl_command)
                    if url_match:
                        parsed['url'] = url_match.group(1)

            if not parsed['url']:
                return jsonify({'error': '无法从curl命令中提取URL'}), 400

            # 提取HTTP方法
            if '-X' in curl_command or '--request' in curl_command:
                method_match = re.search(r'(-X\s+|--request\s+)([A-Z]+)', curl_command)
                if method_match:
                    parsed['method'] = method_match.group(2)

            # 提取请求头
            header_matches = re.findall(r'(-H\s+|--header\s+)[\'"]([^\'"]+)[\'"]', curl_command)
            for header_str in header_matches:
                if ':' in header_str[1]:
                    header_name, header_value = header_str[1].split(':', 1)
                    parsed['headers'][header_name.strip()] = header_value.strip()

            # 提取请求数据
            data_match = re.search(r'(-d\s+|--data\s+|--data-raw\s+)[\'"]([^\'"]*)[\'"]', curl_command)
            if data_match:
                parsed['data'] = data_match.group(2)

            # 发送请求
            request_data = {
                'method': parsed['method'],
                'url': parsed['url'],
                'headers': parsed['headers'],
                'timeout': 30
            }

            if parsed['data'] and parsed['method'] in ['POST', 'PUT', 'PATCH']:
                request_data['data'] = parsed['data']

            # 记录请求开始时间
            start_time = time.time()

            # 发送请求
            response = requests.request(**request_data)

            # 计算响应时间
            response_time = time.time() - start_time

            # 构建响应数据
            result = {
                'success': True,
                'curl_command': curl_command,
                'parsed_request': parsed,
                'response': {
                    'status_code': response.status_code,
                    'status_text': response.reason,
                    'headers': dict(response.headers),
                    'content_length': len(response.content),
                    'response_time': round(response_time * 1000, 2),
                    'url': response.url
                }
            }

            # 尝试解析响应内容
            try:
                content_type = response.headers.get('content-type', '').lower()

                if 'application/json' in content_type:
                    # 已经是JSON类型，直接解析
                    result['response']['body'] = response.json()
                    result['response']['body_type'] = 'json'
                    result['response']['body_raw'] = response.text
                elif 'text/' in content_type or 'xml' in content_type:
                    # 文本类型，先尝试解析为JSON，如果失败则保持原始格式
                    try:
                        # 尝试解析为JSON
                        json_data = response.json()
                        result['response']['body'] = json_data
                        result['response']['body_type'] = 'json'
                        result['response']['body_raw'] = response.text
                    except (ValueError, TypeError):
                        # 不是有效的JSON，保持原始文本
                        result['response']['body'] = response.text
                        result['response']['body_type'] = 'raw'
                else:
                    # 二进制内容或其他类型
                    import base64
                    result['response']['body'] = base64.b64encode(response.content).decode()
                    result['response']['body_type'] = 'binary'
                    result['response']['body_raw'] = response.text

            except Exception as e:
                # 解析失败时，尝试检测是否为JSON
                try:
                    json_data = response.json()
                    result['response']['body'] = json_data
                    result['response']['body_type'] = 'json'
                    result['response']['body_raw'] = response.text
                except (ValueError, TypeError):
                    result['response']['body'] = response.text
                    result['response']['body_type'] = 'raw'
                    result['response']['parse_error'] = str(e)

            return jsonify(result), 200

        except requests.exceptions.RequestException as e:
            return jsonify({
                'success': False,
                'curl_command': curl_command,
                'error': f'请求失败: {str(e)}',
                'error_type': 'request_error'
            }), 200

        except Exception as e:
            return jsonify({
                'success': False,
                'curl_command': curl_command,
                'error': f'执行curl命令失败: {str(e)}',
                'error_type': 'execution_error'
            }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@url_tools_bp.route('/generate-curl', methods=['POST'])
def generate_curl():
    """生成curl命令"""
    try:
        data = request.get_json()
        if not data or 'har' not in data:
            return jsonify({'error': '请提供har字段'}), 400

        har_data = data['har']

        try:
            # 提取请求信息
            if 'log' not in har_data or 'entries' not in har_data['log'] or not har_data['log']['entries']:
                return jsonify({'error': '无效的HAR格式'}), 400

            entry = har_data['log']['entries'][0]
            request_data = entry['request']

            method = request_data.get('method', 'GET')
            url = request_data.get('url', '')

            # 构建curl命令
            curl_cmd = f'curl -X {method} "{url}"'

            # 添加头部
            if 'headers' in request_data and request_data['headers']:
                for header in request_data['headers']:
                    name = header.get('name', '')
                    value = header.get('value', '')
                    if name and value:
                        curl_cmd += f' \\\n  -H "{name}: {value}"'

            # 添加请求体（对于POST等方法）
            if 'postData' in request_data and request_data['postData']:
                post_data = request_data['postData']
                mime_type = post_data.get('mimeType', '')

                if mime_type == 'application/x-www-form-urlencoded':
                    if 'text' in post_data and post_data['text']:
                        curl_cmd += f' \\\n  -d "{post_data["text"]}"'
                    elif 'params' in post_data and post_data['params']:
                        # 从params构建表单数据
                        form_data = []
                        for param in post_data['params']:
                            name = param.get('name', '')
                            value = param.get('value', '')
                            if name:
                                form_data.append(f'{name}={value}')
                        if form_data:
                            curl_cmd += f' \\\n  -d "{ "&".join(form_data) }"'

                elif mime_type == 'application/json':
                    if 'text' in post_data and post_data['text']:
                        curl_cmd += f' \\\n  -d \'{post_data["text"]}\''

            return jsonify({
                'success': True,
                'curl_command': curl_cmd,
                'method': method,
                'url': url
            }), 200

        except Exception as e:
            return jsonify({'error': f'生成curl命令错误: {str(e)}'}), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@url_tools_bp.route('/to-har', methods=['POST'])
def url_to_har():
    """URL转HAR格式"""
    try:
        data = request.get_json()
        if not data or 'url' not in data:
            return jsonify({'error': '请提供url字段'}), 400

        url = data['url']
        method = data.get('method', 'GET').upper()

        try:
            # 解析URL
            parsed = urllib.parse.urlparse(url)

            if not parsed.scheme or not parsed.netloc:
                return jsonify({'error': '无效的URL格式'}), 400

            # 根据HTTP方法决定URL是否包含查询参数
            if method in ['GET', 'HEAD', 'DELETE']:
                # GET等方法：参数在URL的queryString中
                har_url = url
            else:
                # POST等方法：参数在postData中，URL不应该包含查询参数
                base_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
                if parsed.params:
                    base_url += f";{parsed.params}"
                if parsed.fragment:
                    base_url += f"#{parsed.fragment}"
                har_url = base_url

            # 构建HAR格式的请求对象
            har_request = {
                'method': method,
                'url': har_url,
                'httpVersion': 'HTTP/1.1',
                'headers': [],
                'queryString': [],
                'cookies': [],
                'headersSize': -1,
                'bodySize': -1
            }

            # 添加基本头部
            har_request['headers'].append({
                'name': 'Host',
                'value': parsed.netloc
            })

            if parsed.scheme.lower() == 'https':
                har_request['headers'].append({
                    'name': 'Connection',
                    'value': 'keep-alive'
                })

            # 根据HTTP方法处理参数位置
            if parsed.query:
                query_params = urllib.parse.parse_qs(parsed.query, keep_blank_values=True)

                if method in ['GET', 'HEAD', 'DELETE']:
                    # GET等方法：参数在queryString中
                    for key, values in query_params.items():
                        for value in values:
                            har_request['queryString'].append({
                                'name': key,
                                'value': value
                            })
                else:
                    # POST等方法：参数在postData中
                    har_request['postData'] = {
                        'mimeType': 'application/x-www-form-urlencoded',
                        'params': [],
                        'text': ''
                    }

                    # 构建postData的params数组
                    for key, values in query_params.items():
                        for value in values:
                            har_request['postData']['params'].append({
                                'name': key,
                                'value': value
                            })

                    # 构建postData的text（原始表单数据）
                    har_request['postData']['text'] = parsed.query

            # 构建完整的HAR对象
            har_data = {
                'log': {
                    'version': '1.2',
                    'creator': {
                        'name': 'DevToolBox URL Tools',
                        'version': '1.0'
                    },
                    'entries': [
                        {
                            'request': har_request,
                            'response': {
                                'status': 0,
                                'statusText': '',
                                'httpVersion': 'HTTP/1.1',
                                'headers': [],
                                'cookies': [],
                                'content': {
                                    'size': 0,
                                    'mimeType': ''
                                },
                                'redirectURL': '',
                                'headersSize': -1,
                                'bodySize': -1
                            },
                            'cache': {},
                            'timings': {
                                'send': -1,
                                'wait': -1,
                                'receive': -1
                            },
                            'startedDateTime': '',
                            'time': 0
                        }
                    ]
                }
            }

            # 简化输出格式：分离URL和参数
            base_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
            if parsed.params:
                base_url += f";{parsed.params}"
            if parsed.fragment:
                base_url += f"#{parsed.fragment}"

            simplified_result = {
                'base_url': base_url,
                'method': method,
                'query_params': {}
            }

            # 解析查询参数
            if parsed.query:
                query_params = urllib.parse.parse_qs(parsed.query, keep_blank_values=True)
                simplified_result['query_params'] = query_params

            return jsonify({
                'success': True,
                'original_url': url,
                'method': method,
                'base_url': simplified_result['base_url'],
                'query_params': simplified_result['query_params'],
                'har': har_data,
                'har_json': json.dumps(har_data, indent=2, ensure_ascii=False),
                'simplified_json': json.dumps(simplified_result, indent=2, ensure_ascii=False)
            }), 200

        except Exception as e:
            return jsonify({'error': f'URL转HAR错误: {str(e)}'}), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500
