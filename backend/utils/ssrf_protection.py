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
