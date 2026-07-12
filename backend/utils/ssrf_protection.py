import ipaddress
import socket
import urllib.parse
import logging

logger = logging.getLogger(__name__)

PRIVATE_NETWORKS = [
    ipaddress.ip_network('10.0.0.0/8'),
    ipaddress.ip_network('172.16.0.0/12'),
    ipaddress.ip_network('192.168.0.0/16'),
    ipaddress.ip_network('127.0.0.0/8'),
    ipaddress.ip_network('169.254.0.0/16'),
    ipaddress.ip_network('::1/128'),
    ipaddress.ip_network('fc00::/7'),
    ipaddress.ip_network('fe80::/10'),
]

ALLOWED_SCHEMES = {'http', 'https'}

MAX_RESPONSE_SIZE = 5 * 1024 * 1024  # 5MB


def validate_url(url: str) -> tuple:
    if not url:
        return False, 'URL不能为空'

    try:
        parsed = urllib.parse.urlparse(url)
    except Exception:
        return False, 'URL格式无效'

    if parsed.scheme.lower() not in ALLOWED_SCHEMES:
        return False, f'不支持的协议: {parsed.scheme}，仅允许 http/https'

    hostname = parsed.hostname
    if not hostname:
        return False, 'URL缺少主机名'

    try:
        resolved_ips = socket.getaddrinfo(hostname, None, socket.AF_UNSPEC, socket.SOCK_STREAM)
    except socket.gaierror:
        return False, f'无法解析主机名: {hostname}'
    except Exception as e:
        return False, f'主机名解析失败: {e}'

    for family, socktype, proto, canonname, addr in resolved_ips:
        ip_str = addr[0]
        try:
            ip = ipaddress.ip_address(ip_str)
            for network in PRIVATE_NETWORKS:
                if ip in network:
                    return False, f'目标地址 {ip_str} 属于私有/保留网络，禁止访问'
        except ValueError:
            continue

    return True, 'URL验证通过'


def safe_request(url, method='GET', headers=None, data=None, timeout=30, max_redirects=5):
    """安全发起 HTTP 请求。

    对初始 URL 与每个重定向目标都重新做 SSRF 校验(防止公网域名 302 跳到内网/
    云元数据 169.254.169.254),手动跟随重定向而非依赖 requests 默认行为,
    并限制响应体大小防止内存耗尽。

    返回 (response, elapsed_seconds, error_message);出错时 response 为 None。
    """
    import requests
    import time

    headers = headers or {}
    current_url = url
    redirects = 0
    start = time.time()

    while True:
        is_valid, msg = validate_url(current_url)
        if not is_valid:
            return None, time.time() - start, msg

        request_data = {
            'method': method,
            'url': current_url,
            'headers': headers,
            'timeout': timeout,
            'allow_redirects': False,  # 手动跟随,确保每一跳都过 SSRF 校验
            'stream': True,            # 流式读取以便限制响应体大小
        }
        if data and method in ('POST', 'PUT', 'PATCH'):
            request_data['data'] = data

        try:
            response = requests.request(**request_data)
        except requests.RequestException as e:
            return None, time.time() - start, f'请求失败: {e}'

        # 手动跟随重定向(下一轮循环会对新 URL 重新校验)
        if response.is_redirect or response.is_permanent_redirect:
            response.close()
            redirects += 1
            if redirects > max_redirects:
                return None, time.time() - start, '重定向次数超过上限'
            location = response.headers.get('Location')
            if not location:
                break
            current_url = urllib.parse.urljoin(current_url, location)
            continue

        # 限制响应体大小
        chunks = []
        total = 0
        too_large = False
        for chunk in response.iter_content(8192):
            if not chunk:
                continue
            total += len(chunk)
            if total > MAX_RESPONSE_SIZE:
                too_large = True
                break
            chunks.append(chunk)
        if too_large:
            response.close()
            return None, time.time() - start, f'响应体超过 {MAX_RESPONSE_SIZE // 1024 // 1024}MB 限制'
        response._content = b''.join(chunks)
        return response, time.time() - start, None
