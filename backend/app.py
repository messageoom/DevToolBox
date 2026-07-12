from flask import Flask, Blueprint, send_from_directory, request, jsonify, g
from flask_cors import CORS
import hmac
import os
import logging
from pathlib import Path

__version__ = '2.3.0'

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
    from .modules.im import im_bp
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
        from modules.im import im_bp
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
        from backend.modules.im import im_bp

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

    # 安全配置 — SECRET_KEY 持久化，重启后保持一致
    def _load_or_create_secret_key():
        env_key = os.environ.get('SECRET_KEY')
        if env_key:
            return env_key
        # Persist to a .secret file next to the config so it survives restarts
        try:
            from utils.config_manager import get_config_path as _gcp
            secret_file = _gcp().parent / '.devtoolbox_secret'
        except Exception:
            import tempfile
            secret_file = Path(tempfile.gettempdir()) / '.devtoolbox_secret'
        try:
            if secret_file.exists():
                return secret_file.read_text(encoding='utf-8').strip()
            new_key = os.urandom(24).hex()
            secret_file.write_text(new_key, encoding='utf-8')
            try:
                os.chmod(secret_file, 0o600)  # 仅本用户可读,防止同机其他用户窃取签名密钥
            except OSError:
                pass
            return new_key
        except (IOError, OSError):
            return os.urandom(24).hex()

    app.config['SECRET_KEY'] = _load_or_create_secret_key()

    # 上传大小上限:统一从 config 读取(默认 50MB),与 im/file_upload 校验保持一致
    try:
        from utils.config_manager import get_max_upload_bytes as _gmb
    except ImportError:
        try:
            from backend.utils.config_manager import get_max_upload_bytes as _gmb
        except ImportError:
            from .utils.config_manager import get_max_upload_bytes as _gmb
    app.config['MAX_CONTENT_LENGTH'] = _gmb()
    app.config['ACCESS_TOKEN'] = access_token

    # CORS 配置
    # Build allowed origins: env override takes priority, otherwise compute dynamically
    frontend_dist = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'frontend')
    _env_origins = os.environ.get('CORS_ORIGINS')
    if _env_origins:
        allowed_origins = _env_origins.split(',')
    elif os.path.isdir(frontend_dist):
        # Production: frontend is served by Flask on the same port.
        # The browser origin will be whatever host:port the user accessed,
        # so accept all origins — auth is handled by token middleware.
        allowed_origins = '*'
    else:
        # Dev mode: Vite dev server on 5173
        allowed_origins = 'http://localhost:5173,http://127.0.0.1:5173'.split(',')

    CORS(app, resources={
        r"/api/*": {
            "origins": allowed_origins,
            "methods": ["GET", "POST", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "X-Access-Token"],
            "max_age": 3600
        }
    })

    # 速率限制:宽松 per-IP 上限,挡扫描器噪声/暴力探测(token 本身已是 128-bit)
    try:
        from flask_limiter import Limiter
        from flask_limiter.util import get_remote_address
        Limiter(get_remote_address, app=app, default_limits=['300 per minute'])
    except ImportError:
        logging.warning('Flask-Limiter 未安装,跳过速率限制')

    # SocketIO initialization
    socketio = None
    if SocketIO is not None:
        socketio = SocketIO(
            app,
            cors_allowed_origins=allowed_origins,
            async_mode='threading',
            manage_session=False,
        )
        logging.info('Socket.IO: server instance created')

        # Inline diagnostic: test that event handlers actually work
        @socketio.on('connect')
        def _on_si_connect():
            from flask import request as _r
            token = app.config.get('ACCESS_TOKEN')
            # No token configured — allow all
            if not token:
                logging.info('Socket.IO: client CONNECTED sid=%s (no token required)', _r.sid)
                return
            # Check if token auth is enabled
            try:
                from utils.config_manager import load_config as _lc
            except ImportError:
                try:
                    from backend.utils.config_manager import load_config as _lc
                except ImportError:
                    _lc = None
            if _lc:
                cfg = _lc()
                if not cfg.get('security', {}).get('token_enabled', True):
                    logging.info('Socket.IO: client CONNECTED sid=%s (token disabled)', _r.sid)
                    return
            # Validate token from query or cookie
            from datetime import datetime as _dt
            provided = (
                (_r.args.get('token') or '')
                or _r.cookies.get('devtoolbox_token', '')
            )
            if hmac.compare_digest(provided, token):
                logging.info('Socket.IO: client CONNECTED sid=%s (authenticated)', _r.sid)
                return
            # Check temp tokens
            import time as _time
            temp_tokens = cfg.get('security', {}).get('temp_tokens', []) if _lc else []
            now_ts = _time.time()
            for t in temp_tokens:
                exp = t.get('expires_at', 0)
                if hmac.compare_digest(t.get('token', ''), provided) and isinstance(exp, (int, float)) and exp > now_ts:
                    logging.info('Socket.IO: client CONNECTED sid=%s (temp token)', _r.sid)
                    return
            # Reject
            logging.warning('Socket.IO: REJECTED sid=%s (invalid token)', _r.sid)
            return False

        @socketio.on('disconnect')
        def _on_si_disconnect():
            from flask import request as _r
            logging.info('Socket.IO: 🔌 CLIENT DISCONNECTED sid=%s', _r.sid)

        # IM module (SocketIO events)
        try:
            from .modules.im import register_im_events
        except ImportError:
            try:
                from modules.im import register_im_events
            except ImportError:
                from backend.modules.im import register_im_events
        try:
            register_im_events(socketio)
            logging.info('Socket.IO: ✅ IM events registered successfully')
        except Exception as e:
            logging.error('Socket.IO: ❌ register_im_events FAILED: %s', e, exc_info=True)
    else:
        logging.warning('Socket.IO: DISABLED — flask_socketio not installed! IM feature will NOT work.')
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
                from .utils.config_manager import load_config
        config = load_config()
        if not config.get('security', {}).get('token_enabled', True):
            return None

        # Exempt paths — static assets, Socket.IO (auth handled at Socket.IO layer)
        if (request.path in ('/favicon.ico', '/robots.txt', '/api/frontend-log')
                or request.path.startswith('/socket.io/')
                or request.path.startswith('/assets/')):
            return None

        provided = (
            request.args.get('token') or
            request.cookies.get('devtoolbox_token') or
            request.headers.get('X-Access-Token')
        )

        if hmac.compare_digest(provided or '', token):
            g.token_valid = True
            return None

        # Check temp tokens (expires_at is a Unix timestamp float)
        temp_tokens = config.get('security', {}).get('temp_tokens', [])
        import time as _time
        now_ts = _time.time()
        for t in temp_tokens:
            exp = t.get('expires_at', 0)
            if hmac.compare_digest(t.get('token', ''), provided or '') and isinstance(exp, (int, float)) and exp > now_ts:
                g.token_valid = True
                return None

        # Log rejection without leaking token value — fingerprint only
        import hashlib as _hashlib
        token_fp = _hashlib.sha256(token.encode()).hexdigest()[:8] if token else None
        logging.warning(
            'Auth rejected: path=%s provided=%s token_fp=%s',
            request.path,
            bool(provided),
            token_fp,
        )

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
    app.register_blueprint(im_bp, url_prefix='/api/im')

    # 前端静态文件服务（打包模式）— reuse frontend_dist computed earlier for CORS detection
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
        # level 白名单 + 消息截断:防止触发任意 logger 方法名或灌爆日志文件
        if level not in ('info', 'warning', 'warn', 'error', 'debug', 'critical'):
            level = 'info'
        msg = msg[:4000]
        log_fn = getattr(frontend_logger, level, frontend_logger.info)
        log_fn('[Frontend] %s', msg)
        return jsonify({'success': True})

    # 静态资源缓存头 — only cache successful responses (not 403 errors)
    @app.after_request
    def add_cache_headers(response):
        if '/assets/' in request.path and response.status_code == 200:
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

    # Token:优先复用 config 中持久化的 access_token,使设置页"刷新 token"在重启后仍生效
    if no_token:
        access_token = None
    else:
        access_token = uuid.uuid4().hex
        try:
            from utils.config_manager import load_config as _lc, save_config as _sc
        except ImportError:
            try:
                from backend.utils.config_manager import load_config as _lc, save_config as _sc
            except ImportError:
                _lc = _sc = None
        if _lc:
            try:
                _cfg = _lc()
                _existing = _cfg.get('security', {}).get('access_token')
                if _existing:
                    access_token = _existing
                else:
                    _cfg.setdefault('security', {})['access_token'] = access_token
                    if _sc:
                        _sc(_cfg)
            except Exception:
                pass

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
