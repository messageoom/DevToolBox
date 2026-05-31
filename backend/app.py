from flask import Flask, Blueprint, send_from_directory
from flask_cors import CORS
import os
import logging

# 兼容处理导入，支持从不同目录运行
try:
    from .modules.file_upload import file_upload_bp
    from .modules.json_tools import json_tools_bp
    from .modules.yaml_tools import yaml_tools_bp
    from .modules.timestamp_tools import timestamp_tools_bp
    from .modules.base64_tools import base64_tools_bp
    from .modules.hash_tools import hash_tools_bp
    from .modules.url_tools import url_tools_bp
    from .modules.markdown_tools import markdown_tools_bp
    from .modules.data_conversion import data_conversion_bp
    from .modules.qr_tools import qr_tools_bp
    from .modules.crypto_tools import crypto_tools_bp
except ImportError:
    from modules.file_upload import file_upload_bp
    from modules.json_tools import json_tools_bp
    from modules.yaml_tools import yaml_tools_bp
    from modules.timestamp_tools import timestamp_tools_bp
    from modules.base64_tools import base64_tools_bp
    from modules.hash_tools import hash_tools_bp
    from modules.url_tools import url_tools_bp
    from modules.markdown_tools import markdown_tools_bp
    from modules.data_conversion import data_conversion_bp
    from modules.qr_tools import qr_tools_bp
    from modules.crypto_tools import crypto_tools_bp

def create_app():
    app = Flask(__name__)

    # 安全配置
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', os.urandom(24).hex())
    app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB

    # CORS 配置
    allowed_origins = os.environ.get('CORS_ORIGINS', 'http://localhost:5173,http://127.0.0.1:5173').split(',')
    CORS(app, resources={
        r"/api/*": {
            "origins": allowed_origins,
            "methods": ["GET", "POST", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type"],
            "max_age": 3600
        }
    })

    # 注册蓝图
    app.register_blueprint(file_upload_bp, url_prefix='/api/file-upload')
    app.register_blueprint(json_tools_bp, url_prefix='/api/json-tools')
    app.register_blueprint(yaml_tools_bp, url_prefix='/api/yaml-tools')
    app.register_blueprint(timestamp_tools_bp, url_prefix='/api/timestamp-tools')
    app.register_blueprint(base64_tools_bp, url_prefix='/api/base64-tools')
    app.register_blueprint(hash_tools_bp, url_prefix='/api/hash-tools')
    app.register_blueprint(url_tools_bp, url_prefix='/api/url-tools')
    app.register_blueprint(markdown_tools_bp, url_prefix='/api/markdown-tools')
    app.register_blueprint(data_conversion_bp, url_prefix='/api/data-conversion')
    app.register_blueprint(qr_tools_bp, url_prefix='/api/qr-tools')
    app.register_blueprint(crypto_tools_bp, url_prefix='/api/crypto-tools')

    # 静态资源缓存头
    @app.after_request
    def add_cache_headers(response):
        if '/static/frontend/assets/' in response.headers.get('Content-Type', ''):
            response.cache_control.max_age = 31536000
        return response

    return app

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    app = create_app()
    import socket
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    logging.info(f"本机IP地址: {local_ip}")
    debug = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    app.run(host='0.0.0.0', port=5000, debug=debug)
