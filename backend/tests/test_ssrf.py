"""SSRF 防护:validate_url / safe_request —— 含重定向绕过拦截(本次修复的核心)。"""
from unittest.mock import patch
from utils.ssrf_protection import validate_url, safe_request


def test_validate_url_blocks_private_networks():
    assert validate_url('http://192.168.1.1')[0] is False
    assert validate_url('http://127.0.0.1')[0] is False
    assert validate_url('http://10.0.0.1')[0] is False
    assert validate_url('http://169.254.169.254')[0] is False  # 云元数据
    assert validate_url('http://[::1]')[0] is False
    assert validate_url('http://localhost')[0] is False


def test_validate_url_allows_public_ip():
    # 公网 IP 不需 DNS,直接判断
    assert validate_url('http://93.184.216.34')[0] is True


def test_validate_url_blocks_bad_scheme_and_empty():
    assert validate_url('ftp://example.com')[0] is False
    assert validate_url('')[0] is False


def test_safe_request_blocks_redirect_to_cloud_metadata():
    """公网 URL 302 → 169.254.169.254 必须被第二跳校验拦截。"""
    class FakeRedirect:
        is_redirect = True
        is_permanent_redirect = False
        headers = {'Location': 'http://169.254.169.254/latest/meta-data/iam/'}
        def close(self): pass

    with patch('requests.request') as mock_req:
        mock_req.return_value = FakeRedirect()
        resp, elapsed, err = safe_request('http://93.184.216.34')
        assert resp is None
        assert err is not None
        # 第二跳校验即拒绝,不应继续发请求到云元数据
        assert mock_req.call_count == 1


def test_safe_request_allows_normal_response():
    class FakeOk:
        is_redirect = False
        is_permanent_redirect = False
        status_code = 200
        reason = 'OK'
        headers = {'content-type': 'text/plain'}
        url = 'http://93.184.216.34'
        _content = None
        def iter_content(self, n):
            yield b'hello'
        def close(self): pass

    with patch('requests.request') as mock_req:
        mock_req.return_value = FakeOk()
        resp, elapsed, err = safe_request('http://93.184.216.34')
        assert resp is not None
        assert err is None
        assert resp.status_code == 200
