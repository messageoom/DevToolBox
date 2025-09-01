from flask import Flask, Blueprint, send_from_directory
from flask_cors import CORS
import os

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

def create_app():
    app = Flask(__name__)
    CORS(app)

    # 配置
    app.config['SECRET_KEY'] = 'your-secret-key-here'
    app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
    app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 1024  # 1GB - 进一步增加上传大小限制

    # 确保上传目录存在
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

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

    # 为前端静态文件提供服务
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve_frontend(path):
        frontend_dir = os.path.join(app.root_path, 'static', 'frontend')
        if path != "" and os.path.exists(os.path.join(frontend_dir, path)):
            return send_from_directory(os.path.join(frontend_dir), path)
        else:
            return send_from_directory(os.path.join(frontend_dir), 'index.html')

    return app

if __name__ == '__main__':
    app = create_app()
    # 获取本机IP地址
    import socket
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    print(f"本机IP地址: {local_ip}")
    app.run(host='0.0.0.0', port=5000, debug=True)
