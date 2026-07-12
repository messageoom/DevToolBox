"""文件完整性回归:上传 -> 存储 -> 下载,文件内容必须字节级无损。

守护用户的核心硬要求:文件内容绝对不能被损坏或篡改。
"""
import io
import hashlib
from flask import Flask
from modules.file_upload import file_upload_bp


def _sha(b):
    return hashlib.sha256(b).hexdigest()


def _client(upload_dir):
    app = Flask(__name__)
    app.config['UPLOAD_FOLDER'] = upload_dir
    app.register_blueprint(file_upload_bp, url_prefix='/api/file-upload')
    return app.test_client()


def test_chinese_filename_roundtrip_intact(tmp_path):
    """中文文件名 PDF:文件名保留中文 + 内容字节级无损。"""
    client = _client(str(tmp_path))
    original = b'%PDF-1.4 binary \x00\xff\xfe\x01\x02 test'
    r = client.post('/api/file-upload/upload',
                    data={'files': (io.BytesIO(original), '中文文档.pdf')},
                    content_type='multipart/form-data')
    body = r.get_json()
    assert body['files'][0]['unique_name'] == '中文文档.pdf'

    downloaded = client.get('/api/file-upload/files/中文文档.pdf').data
    assert _sha(downloaded) == _sha(original)
    assert len(downloaded) == len(original)


def test_full_binary_range_intact(tmp_path):
    """全 256 字节值循环的二进制文件必须无损(最严苛的二进制完整性)。"""
    client = _client(str(tmp_path))
    original = bytes(range(256)) * 8
    client.post('/api/file-upload/upload',
                data={'files': (io.BytesIO(original), '二进制全字节测试.bin')},
                content_type='multipart/form-data')
    downloaded = client.get('/api/file-upload/files/二进制全字节测试.bin').data
    assert _sha(downloaded) == _sha(original)
    assert len(downloaded) == len(original)


def test_duplicate_upload_keeps_extension_and_integrity(tmp_path):
    """重复上传同名文件:去重为 _1 后缀,扩展名保留,内容无损。"""
    client = _client(str(tmp_path))
    original = bytes(range(256)) * 2
    client.post('/api/file-upload/upload',
                data={'files': (io.BytesIO(original), '重复文件.dat')},
                content_type='multipart/form-data')
    r2 = client.post('/api/file-upload/upload',
                     data={'files': (io.BytesIO(original), '重复文件.dat')},
                     content_type='multipart/form-data')
    assert r2.get_json()['files'][0]['unique_name'] == '重复文件_1.dat'
    downloaded = client.get('/api/file-upload/files/重复文件_1.dat').data
    assert _sha(downloaded) == _sha(original)
