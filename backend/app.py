from flask import Flask, Blueprint, send_from_directory, request, jsonify, g
from flask_cors import CORS
import os
import logging

__version__ = '2.1.0'

frontend_logger = logging.getLogger('frontend')

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
    from .modules.uuid_tools import uuid_tools_bp
    from .modules.password_tools import password_tools_bp
    from .modules.apikey_tools import apikey_tools_bp
    from .modules.settings import settings_bp
except ImportError:
    try:
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
        from modules.uuid_tools import uuid_tools_bp
        from modules.password_tools import password_tools_bp
        from modules.apikey_tools import apikey_tools_bp
        from modules.settings import settings_bp
    except ImportError:
        from backend.modules.file_upload import file_upload_bp
        from backend.modules.json_tools import json_tools_bp
        from backend.modules.yaml_tools import yaml_tools_bp
        from backend.modules.timestamp_tools import timestamp_tools_bp
        from backend.modules.base64_tools import base64_tools_bp
        from backend.modules.hash_tools import hash_tools_bp
        from backend.modules.url_tools import url_tools_bp
        from backend.modules.markdown_tools import markdown_tools_bp
        from backend.modules.data_conversion import data_conversion_bp
        from backend.modules.qr_tools import qr_tools_bp
        from backend.modules.crypto_tools import crypto_tools_bp
        from backend.modules.uuid_tools import uuid_tools_bp
        from backend.modules.password_tools import password_tools_bp
        from backend.modules.apikey_tools import apikey_tools_bp
        from backend.modules.settings import settings_bp

# Lock page for unauthorized access
try:
    from .utils.lock_page import get_lock_page_html
except ImportError:
    try:
        from utils.lock_page import get_lock_page_html
    except ImportError:
        from backend.utils.lock_page import get_lock_page_html

try:
    from flask_socketio import SocketIO
except ImportError:
    SocketIO = None


def create_app(access_token=None):
    app = Flask(__name__)

    # 安全配置
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', os.urandom(24).hex())
    app.config['MAX_CONTENT_LENGTH'] = 20 * 1024 * 1024 * 1024  # 20GB
    app.config['ACCESS_TOKEN'] = access_token

    # CORS 配置
    allowed_origins = os.environ.get('CORS_ORIGINS', 'http://localhost:5173,http://127.0.0.1:5173').split(',')
    CORS(app, resources={
        r"/api/*": {
            "origins": allowed_origins,
            "methods": ["GET", "POST", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "X-Access-Token"],
            "max_age": 3600
        }
    })

    # SocketIO initialization
    socketio = None
    if SocketIO is not None:
        socketio = SocketIO(
            app,
            cors_allowed_origins='*',
            async_mode='threading',
            manage_session=False,
        )
        try:
            from .modules.text_transfer import register_socketio_events
        except ImportError:
            try:
                from modules.text_transfer import register_socketio_events
            except ImportError:
                from backend.modules.text_transfer import register_socketio_events
        register_socketio_events(socketio)
    app.config['SOCKETIO'] = socketio

    # Token 认证中间件
    @app.before_request
    def check_access_token():
        if request.path.startswith('/api/') and not request.path.startswith('/api/frontend-log'):
            logging.info('%s %s %s', request.method, request.path, request.remote_addr)

        token = app.config.get('ACCESS_TOKEN')
        if not token:
            return None

        # Check if token is disabled via config
        try:
            from utils.config_manager import load_config
        except ImportError:
            try:
                from backend.utils.config_manager import load_config
            except ImportError:
                from backend.utils.config_manager import load_config
        config = load_config()
        if not config.get('security', {}).get('token_enabled', True):
            return None

        # Exempt paths
        if request.path in ('/favicon.ico', '/robots.txt', '/api/frontend-log') or request.path.startswith('/socket.io/'):
            return None

        provided = (
            request.args.get('token') or
            request.cookies.get('devtoolbox_token') or
            request.headers.get('X-Access-Token')
        )

        if provided == token:
            g.token_valid = True
            return None

        # Check temp tokens
        temp_tokens = config.get('security', {}).get('temp_tokens', [])
        from datetime import datetime
        now = datetime.utcnow().isoformat()
        for t in temp_tokens:
            if t.get('token') == provided and t.get('expires_at', '') > now:
                g.token_valid = True
                return None

        # Unauthorized
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Unauthorized', 'success': False}), 401

        lang = config.get('ui', {}).get('language', 'zh')
        return get_lock_page_html(lang), 403

    # Cookie 设置
    @app.after_request
    def set_token_cookie(response):
        if getattr(g, 'token_valid', False):
            response.set_cookie(
                'devtoolbox_token',
                app.config['ACCESS_TOKEN'],
                max_age=31536000,
                httponly=True,
                samesite='Lax'
            )
        return response

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
    app.register_blueprint(uuid_tools_bp, url_prefix='/api/uuid-tools')
    app.register_blueprint(password_tools_bp, url_prefix='/api/password-tools')
    app.register_blueprint(apikey_tools_bp, url_prefix='/api/apikey-tools')
    app.register_blueprint(settings_bp, url_prefix='/api/settings')

    # 前端静态文件服务（打包模式）
    frontend_dist = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'frontend')
    if os.path.isdir(frontend_dist):
        @app.route('/', defaults={'path': ''})
        @app.route('/<path:path>')
        def serve_frontend(path):
            if path and os.path.exists(os.path.join(frontend_dist, path)):
                return send_from_directory(frontend_dist, path)
            return send_from_directory(frontend_dist, 'index.html')

    # Frontend log bridge — allows JS to send logs to Python logger
    @app.route('/api/frontend-log', methods=['POST'])
    def frontend_log():
        data = request.get_json(silent=True) or {}
        level = data.get('level', 'info').lower()
        msg = data.get('message', '')
        if not msg:
            return jsonify({'success': False}), 400
        log_fn = getattr(frontend_logger, level, frontend_logger.info)
        log_fn('[Frontend] %s', msg)
        return jsonify({'success': True})

    # 静态资源缓存头
    @app.after_request
    def add_cache_headers(response):
        if '/assets/' in request.path:
            response.cache_control.max_age = 31536000
        return response

    return app

if __name__ == '__main__':
    import uuid

    logging.basicConfig(level=logging.INFO)

    host = os.environ.get('FLASK_HOST', '0.0.0.0')
    port = int(os.environ.get('FLASK_PORT', '5000'))
    no_token = os.environ.get('DEVTOOLBOX_NO_TOKEN', '').lower() == '1'
    no_tray = os.environ.get('DEVTOOLBOX_NO_TRAY', '').lower() == '1'

    access_token = None if no_token else uuid.uuid4().hex
    app = create_app(access_token=access_token)

    no_gui = os.environ.get('DEVTOOLBOX_NO_GUI', '').lower() == '1'

    if access_token and not no_gui:
        # Native GUI mode (pywebview) with fallback to tray/console
        try:
            from utils.gui_window import run_gui_app
            run_gui_app(app, host, port, access_token, __version__)
        except ImportError:
            try:
                from backend.utils.gui_window import run_gui_app
                run_gui_app(app, host, port, access_token, __version__)
            except ImportError:
                no_gui = True

    if access_token and no_gui:
        # Tray mode fallback
        try:
            from utils.tray_app import run_tray_app, run_console_app
        except ImportError:
            try:
                from backend.utils.tray_app import run_tray_app, run_console_app
            except ImportError:
                no_tray = True

        if no_tray:
            run_console_app(app, host, port, access_token, __version__)
        else:
            run_tray_app(app, host, port, access_token, __version__)

    if not access_token:
        # Dev mode: no token, no gui, no tray
        debug = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
        socketio = app.config.get('SOCKETIO')
        if socketio:
            socketio.run(app, host=host, port=port, debug=debug, allow_unsafe_werkzeug=True)
        else:
            app.run(host=host, port=port, debug=debug)
