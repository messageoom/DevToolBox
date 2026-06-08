"""
pywebview native desktop GUI window for DevToolBox.
macOS-inspired dark UI with glassmorphism design.
"""

import os
import sys
import json
import time
import socket
import threading
import webview
from collections import deque


def _import_config_manager():
    """Import config_manager with 3-tier fallback (same pattern as app.py)."""
    for prefix in ('utils.', 'backend.utils.', ''):
        try:
            mod = __import__(prefix + 'config_manager', fromlist=['load_config', 'save_config', 'get_upload_dir'])
            return mod
        except ImportError:
            continue
    raise ImportError('Cannot import config_manager')
import webbrowser
import logging
import uuid
from datetime import datetime

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
#  Reuse helpers from tray_app
# ---------------------------------------------------------------------------

_log_handler = None


class _GUILogHandler(logging.Handler):
    def __init__(self, max_records=500):
        super().__init__()
        self.records = deque(maxlen=max_records)
        self.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)-8s %(name)s: %(message)s',
            datefmt='%H:%M:%S',
        ))

    def emit(self, record):
        self.records.append(self.format(record))


def _copy_to_clipboard(text):
    try:
        import pyperclip
        pyperclip.copy(text)
        return True
    except Exception:
        if sys.platform == 'win32':
            try:
                import subprocess
                p = subprocess.Popen(['clip'], stdin=subprocess.PIPE)
                p.communicate(text.encode('utf-8'))
                return True
            except Exception:
                pass
    return False


def wait_for_server(host, port, timeout=15):
    start = time.time()
    while time.time() - start < timeout:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1)
            s.connect((host.replace('0.0.0.0', '127.0.0.1'), port))
            s.close()
            return True
        except (ConnectionRefusedError, OSError):
            time.sleep(0.3)
    return False


def start_flask_thread(app, host, port):
    def run():
        socketio = app.config.get('SOCKETIO')
        if socketio:
            socketio.run(app, host=host, port=port, debug=False, allow_unsafe_werkzeug=True)
        else:
            app.run(host=host, port=port, debug=False, use_reloader=False)
    thread = threading.Thread(target=run, daemon=True)
    thread.start()
    return thread


def _is_rfc1918(ip):
    """Check if IP is in RFC 1918 private range (real LAN)."""
    if ip.startswith('192.168.'):
        return True
    if ip.startswith('10.'):
        return True
    if ip.startswith('172.'):
        parts = ip.split('.')
        if len(parts) >= 2:
            second = int(parts[1])
            if 16 <= second <= 31:
                return True
    return False


_cached_local_ip = None


def _get_local_ip():
    """Get the primary LAN IP address, universal across all OSes.
    Result is cached after first call.

    Strategy:
      1. UDP socket to 8.8.8.8 — OS picks the default-route interface.
         If the result is a private IP, no VPN interference — done.
      2. If VPN/proxy intercepted (non-private result like 198.18.x.x),
         parse the OS routing table to find the physical gateway's interface IP.
      3. Fallback: hostname resolution.
    """
    global _cached_local_ip
    if _cached_local_ip is not None:
        return _cached_local_ip

    # Method 1: UDP socket — fastest, works when no VPN
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        if _is_rfc1918(ip):
            _cached_local_ip = ip
            logger.info(f'LAN IP detected (UDP socket): {ip}')
            return ip
        else:
            logger.info(f'UDP socket returned non-LAN IP {ip}, falling back to routing table')
    except Exception:
        pass

    # Method 2: VPN intercepted — find real LAN interface via routing table
    try:
        import subprocess
        if sys.platform == 'win32':
            out = subprocess.check_output('route print 0.0.0.0', shell=True, text=True, timeout=3)
            for line in out.splitlines():
                parts = line.split()
                if (len(parts) >= 5 and parts[0] == '0.0.0.0' and parts[1] == '0.0.0.0'
                        and parts[2] != parts[3] and _is_rfc1918(parts[2])):
                    _cached_local_ip = parts[3]
                    logger.info(f'LAN IP detected (routing table): {parts[3]} via gateway {parts[2]}')
                    return parts[3]
        elif sys.platform == 'darwin':
            out = subprocess.check_output(['route', '-n', 'get', 'default'], text=True, timeout=3)
            iface = None
            for line in out.splitlines():
                if 'interface:' in line:
                    iface = line.split(':')[1].strip()
            if iface:
                out2 = subprocess.check_output(['ifconfig', iface], text=True, timeout=3)
                for line in out2.splitlines():
                    if 'inet ' in line:
                        ip = line.strip().split()[1]
                        _cached_local_ip = ip
                        logger.info(f'LAN IP detected (routing table): {ip}')
                        return ip
        else:  # Linux
            out = subprocess.check_output(['ip', 'route', 'show', 'default'], text=True, timeout=3)
            parts = out.split()
            if 'dev' in parts:
                iface = parts[parts.index('dev') + 1]
                out2 = subprocess.check_output(['ip', 'addr', 'show', iface], text=True, timeout=3)
                for line in out2.splitlines():
                    if 'inet ' in line:
                        ip = line.strip().split()[1].split('/')[0]
                        _cached_local_ip = ip
                        logger.info(f'LAN IP detected (routing table): {ip}')
                        return ip
    except Exception:
        pass

    # Method 3: hostname resolution fallback
    try:
        ip = socket.gethostbyname(socket.gethostname())
        _cached_local_ip = ip
        logger.warning(f'LAN IP detection fallback (hostname): {ip}')
        return ip
    except Exception:
        _cached_local_ip = '127.0.0.1'
        return '127.0.0.1'


# ---------------------------------------------------------------------------
#  Python API exposed to JavaScript via pywebview bridge
# ---------------------------------------------------------------------------

class Api:
    def __init__(self, app, host, port, access_token, version, start_time):
        self._app = app
        self._host = host
        self._port = port
        self._access_token = access_token
        self._version = version
        self._start_time = start_time
        self._window = None
        self._server_running = False

    @property
    def base_url(self):
        return f"http://127.0.0.1:{self._port}"

    @property
    def token_url(self):
        return f"http://{_get_local_ip()}:{self._port}/?token={self._access_token}"

    @property
    def local_token_url(self):
        return f"{self.base_url}/?token={self._access_token}"

    def set_window(self, window):
        self._window = window

    def set_server_running(self, running):
        self._server_running = running

    # --- Status ---

    def get_status(self):
        uptime = int(time.time() - self._start_time)
        local_ip = _get_local_ip()

        _cm = _import_config_manager()
        config = _cm.load_config()
        upload_dir = _cm.get_upload_dir(config)

        file_count = 0
        disk_bytes = 0
        try:
            if os.path.isdir(upload_dir):
                for f in os.listdir(upload_dir):
                    fp = os.path.join(upload_dir, f)
                    if os.path.isfile(fp):
                        file_count += 1
                        disk_bytes += os.path.getsize(fp)
        except Exception:
            pass

        network_url = f"http://{local_ip}:{self._port}/?token={self._access_token}"

        return {
            'version': self._version,
            'uptime': uptime,
            'server_running': self._server_running,
            'access_url': self.token_url,
            'local_url': self.base_url,
            'network_url': network_url,
            'local_ip': local_ip,
            'port': self._port,
            'host': self._host,
            'python_version': sys.version.split()[0],
            'platform': sys.platform,
            'file_count': file_count,
            'disk_bytes': disk_bytes,
        }

    # --- Config ---

    def get_config(self):
        _cm = _import_config_manager()
        config = _cm.load_config()
        masked = {}
        if 'security' in config:
            masked['security'] = {
                'token_enabled': config['security'].get('token_enabled', True),
                'has_token': bool(self._access_token),
                'temp_tokens': config['security'].get('temp_tokens', []),
            }
        if 'storage' in config:
            masked['storage'] = dict(config['storage'])
        if 'network' in config:
            masked['network'] = dict(config['network'])
        return masked

    def save_config(self, params):
        try:
            _cm = _import_config_manager()
            config = _cm.load_config()
            for section, values in params.items():
                if section in config and isinstance(values, dict):
                    config[section].update(values)
            _cm.save_config(config)
            return {'success': True}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    # --- Security ---

    def refresh_token(self):
        new_token = uuid.uuid4().hex
        self._access_token = new_token
        self._app.config['ACCESS_TOKEN'] = new_token

        _cm = _import_config_manager()
        config = _cm.load_config()
        config['security']['access_token'] = new_token
        _cm.save_config(config)

        return {'success': True, 'token_url': self.token_url}

    def toggle_token(self, params):
        enabled = params.get('enabled', True) if isinstance(params, dict) else params
        _cm = _import_config_manager()
        config = _cm.load_config()
        config['security']['token_enabled'] = enabled
        _cm.save_config(config)
        return {'success': True, 'enabled': enabled}

    def create_temp_token(self, params):
        label = params.get('label', '')
        minutes = params.get('expires_minutes', 60)
        if not label.strip():
            return {'success': False, 'error': 'Label required'}

        _cm = _import_config_manager()
        import uuid as _uuid
        config = _cm.load_config()
        token = _uuid.uuid4().hex[:16]
        expires_at = datetime.utcnow().timestamp() + minutes * 60
        config.setdefault('security', {}).setdefault('temp_tokens', []).append({
            'token': token,
            'label': label,
            'expires_at': expires_at,
        })
        _cm.save_config(config)

        return {
            'success': True,
            'token': token,
            'token_url': f"{self.base_url}/?token={token}",
            'expires_at': expires_at,
        }

    def delete_temp_token(self, token):
        _cm = _import_config_manager()
        config = _cm.load_config()
        tokens = config.get('security', {}).get('temp_tokens', [])
        config['security']['temp_tokens'] = [t for t in tokens if t.get('token') != token]
        _cm.save_config(config)
        return {'success': True}

    # --- Actions ---

    def open_browser(self):
        try:
            webbrowser.open(self.token_url)
            return {'success': True}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def get_qr_code(self):
        """Generate QR code for the access URL as base64 PNG."""
        try:
            import qrcode
            from io import BytesIO
            import base64

            qr = qrcode.QRCode(version=1, box_size=10, border=2)
            qr.add_data(self.token_url)
            qr.make(fit=True)
            img = qr.make_image(fill_color='#1d1d1f', back_color='#ffffff')

            buf = BytesIO()
            img.save(buf, format='PNG')
            b64 = base64.b64encode(buf.getvalue()).decode('ascii')
            return {'success': True, 'image': 'data:image/png;base64,' + b64, 'url': self.token_url}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def copy_url(self):
        ok = _copy_to_clipboard(self.token_url)
        return {'success': ok}

    def copy_text(self, params):
        text = params if isinstance(params, str) else params.get('text', '')
        ok = _copy_to_clipboard(text)
        return {'success': ok}

    def open_storage_folder(self):
        _cm = _import_config_manager()
        upload_dir = _cm.get_upload_dir(_cm.load_config())
        try:
            os.makedirs(upload_dir, exist_ok=True)
            if sys.platform == 'win32':
                os.startfile(upload_dir)
            elif sys.platform == 'darwin':
                os.system(f'open "{upload_dir}"')
            else:
                os.system(f'xdg-open "{upload_dir}"')
            return {'success': True}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def pick_folder(self):
        """Open native folder picker dialog, return selected path."""
        try:
            result = self._window.create_file_dialog(
                webview.FOLDER_DIALOG,
                directory='',
            )
            if result and len(result) > 0:
                return {'success': True, 'path': result[0]}
        except Exception:
            pass
        return {'success': False}
        try:
            os.makedirs(upload_dir, exist_ok=True)
            if sys.platform == 'win32':
                os.startfile(upload_dir)
            elif sys.platform == 'darwin':
                os.system(f'open "{upload_dir}"')
            else:
                os.system(f'xdg-open "{upload_dir}"')
            return {'success': True}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    # --- Language ---

    def get_language(self):
        try:
            _cm = _import_config_manager()
            config = _cm.load_config()
            return config.get('ui', {}).get('language', 'zh')
        except Exception:
            return 'zh'

    def set_language(self, params):
        lang = params if isinstance(params, str) else params.get('language', 'zh')
        try:
            _cm = _import_config_manager()
            config = _cm.load_config()
            config.setdefault('ui', {})['language'] = lang
            _cm.save_config(config)
            return {'success': True}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    # --- Logs ---

    def get_logs(self):
        if _log_handler is None:
            return json.dumps([f'{datetime.now().strftime("%H:%M:%S")} ERROR    gui_window: _log_handler is None!'])
        return json.dumps(list(_log_handler.records))

    def clear_logs(self):
        if _log_handler is not None:
            _log_handler.records.clear()
        return {'success': True}

    def copy_logs(self):
        if _log_handler is None:
            return {'success': False}
        text = '\n'.join(_log_handler.records)
        ok = _copy_to_clipboard(text)
        return {'success': ok}

    def exit_app(self):
        if self._window:
            self._window.destroy()
        os._exit(0)


# ---------------------------------------------------------------------------
#  HTML / CSS / JS for the native window
# ---------------------------------------------------------------------------

GUI_HTML = r'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>DevToolBox</title>
<style>
*, *::before, *::after { margin: 0; padding: 0; box-sizing: border-box; }

:root {
  --bg: #1d1d1f;
  --bg-sidebar: rgba(28, 28, 30, 0.95);
  --card: rgba(255, 255, 255, 0.05);
  --card-border: rgba(255, 255, 255, 0.08);
  --card-hover: rgba(255, 255, 255, 0.08);
  --text: #f5f5f7;
  --text-dim: rgba(245, 245, 247, 0.5);
  --text-secondary: rgba(245, 245, 247, 0.7);
  --accent: #0071e3;
  --accent-hover: #0077ed;
  --danger: #ff453a;
  --danger-hover: #ff6961;
  --success: #30d158;
  --warning: #ffd60a;
  --input-bg: rgba(255, 255, 255, 0.06);
  --input-border: rgba(255, 255, 255, 0.1);
  --sidebar-width: 140px;
  --radius: 12px;
  --radius-sm: 8px;
}

body {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--bg);
  color: var(--text);
  font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
  overflow: hidden;
  -webkit-font-smoothing: antialiased;
  user-select: none;
}

/* Background gradient */
.bg-layer {
  position: fixed;
  inset: 0;
  z-index: 0;
  background:
    radial-gradient(ellipse 80% 60% at 20% 80%, rgba(0, 113, 227, 0.06) 0%, transparent 60%),
    radial-gradient(ellipse 60% 80% at 80% 20%, rgba(88, 86, 214, 0.04) 0%, transparent 60%);
  animation: bgShift 12s ease-in-out infinite alternate;
}
@keyframes bgShift {
  0% { opacity: 0.6; } 50% { opacity: 1; } 100% { opacity: 0.6; }
}

/* Layout */
.app-layout {
  position: relative;
  z-index: 1;
  display: flex;
  flex: 1;
  overflow: hidden;
}

/* Sidebar */
.sidebar {
  width: var(--sidebar-width);
  min-width: var(--sidebar-width);
  background: var(--bg-sidebar);
  border-right: 1px solid var(--card-border);
  display: flex;
  flex-direction: column;
  padding: 16px 0;
  backdrop-filter: blur(20px);
}

.sidebar-brand {
  padding: 0 16px 20px;
  border-bottom: 1px solid var(--card-border);
  margin-bottom: 8px;
}

.sidebar-brand h1 {
  font-size: 15px;
  font-weight: 700;
  letter-spacing: -0.02em;
  color: var(--text);
}

.sidebar-brand .version {
  font-size: 11px;
  color: var(--text-dim);
  margin-top: 2px;
}

.nav-list {
  list-style: none;
  padding: 4px 8px;
  flex: 1;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  border-radius: var(--radius-sm);
  cursor: pointer;
  font-size: 13px;
  color: var(--text-secondary);
  transition: all 0.15s ease;
  margin-bottom: 2px;
}
.nav-item:hover { background: var(--card); color: var(--text); }
.nav-item.active { background: rgba(0, 113, 227, 0.15); color: var(--accent); }
.nav-item svg { width: 18px; height: 18px; flex-shrink: 0; }

/* Content */
.content {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 24px 28px;
}

.content::-webkit-scrollbar { width: 6px; }
.content::-webkit-scrollbar-track { background: transparent; }
.content::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 3px; }

.page { display: none; animation: fadeIn 0.3s ease; }
.page.active { display: block; }
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Cards */
.card {
  background: var(--card);
  border: 1px solid var(--card-border);
  border-radius: var(--radius);
  padding: 20px;
  margin-bottom: 16px;
  backdrop-filter: blur(20px);
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.card-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--text);
}

/* Status indicator */
.status-dot {
  display: inline-block;
  width: 8px; height: 8px;
  border-radius: 50%;
  margin-right: 8px;
}
.status-dot.running { background: var(--success); box-shadow: 0 0 8px rgba(48, 209, 88, 0.4); animation: pulse 2s infinite; }
.status-dot.stopped { background: var(--danger); }
@keyframes pulse {
  0%, 100% { opacity: 1; } 50% { opacity: 0.5; }
}

/* Buttons */
.btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border: none;
  border-radius: var(--radius-sm);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
  color: white;
  font-family: inherit;
}
.btn:active { transform: scale(0.97); }
.btn-primary { background: var(--accent); }
.btn-primary:hover { background: var(--accent-hover); }
.btn-danger { background: var(--danger); }
.btn-danger:hover { background: var(--danger-hover); }
.btn-ghost {
  background: var(--card);
  color: var(--text-secondary);
  border: 1px solid var(--card-border);
}
.btn-ghost:hover { background: var(--card-hover); color: var(--text); }
.btn-sm { padding: 6px 10px; font-size: 12px; }

.btn-row { display: flex; gap: 8px; flex-wrap: wrap; }

/* URL display */
.url-row {
  display: flex;
  align-items: center;
  gap: 8px;
  background: var(--input-bg);
  border: 1px solid var(--input-border);
  border-radius: var(--radius-sm);
  padding: 8px 12px;
  margin-bottom: 8px;
}
.url-row code {
  flex: 1;
  font-family: 'SF Mono', 'Consolas', 'Menlo', monospace;
  font-size: 12px;
  color: var(--text);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.url-row .copy-btn {
  background: none;
  border: none;
  color: var(--text-dim);
  cursor: pointer;
  padding: 2px;
  transition: color 0.15s;
}
.url-row .copy-btn:hover { color: var(--accent); }
.url-row .copy-btn svg { width: 14px; height: 14px; }

/* Tag */
.tag {
  display: inline-flex;
  align-items: center;
  padding: 3px 10px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
}
.tag-success { background: rgba(48, 209, 88, 0.15); color: var(--success); }
.tag-danger { background: rgba(255, 69, 58, 0.15); color: var(--danger); }
.tag-info { background: rgba(255, 255, 255, 0.08); color: var(--text-dim); }

/* Form */
.form-group { margin-bottom: 16px; }
.form-label {
  display: block;
  font-size: 13px;
  color: var(--text-secondary);
  margin-bottom: 6px;
}
.form-input {
  width: 100%;
  padding: 8px 12px;
  background: var(--input-bg);
  border: 1px solid var(--input-border);
  border-radius: var(--radius-sm);
  color: var(--text);
  font-size: 13px;
  font-family: inherit;
  outline: none;
  transition: border-color 0.15s;
}
.form-input:focus { border-color: var(--accent); }
.form-input::placeholder { color: var(--text-dim); }
.form-row { display: flex; gap: 8px; align-items: center; }
.form-hint { font-size: 11px; color: var(--text-dim); margin-top: 4px; }

select.form-input {
  appearance: none;
  cursor: pointer;
}

/* Slider */
.slider-wrap { display: flex; align-items: center; gap: 12px; }
.slider-wrap input[type="range"] {
  flex: 1;
  -webkit-appearance: none;
  height: 4px;
  background: var(--input-border);
  border-radius: 2px;
  outline: none;
}
.slider-wrap input[type="range"]::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 16px; height: 16px;
  border-radius: 50%;
  background: var(--accent);
  cursor: pointer;
}
.slider-value {
  font-size: 13px;
  color: var(--text-secondary);
  min-width: 50px;
  text-align: right;
}

/* Toggle */
.toggle {
  position: relative;
  display: inline-block;
  width: 44px;
  height: 24px;
  cursor: pointer;
}
.toggle input { opacity: 0; width: 0; height: 0; }
.toggle .slider {
  position: absolute;
  inset: 0;
  background: var(--input-border);
  border-radius: 12px;
  transition: background 0.2s;
}
.toggle .slider::before {
  content: '';
  position: absolute;
  width: 18px; height: 18px;
  left: 3px; top: 3px;
  background: white;
  border-radius: 50%;
  transition: transform 0.2s;
}
.toggle input:checked + .slider { background: var(--accent); }
.toggle input:checked + .slider::before { transform: translateX(20px); }

/* Temp token table */
.token-table { width: 100%; border-collapse: collapse; }
.token-table th {
  text-align: left;
  font-size: 11px;
  font-weight: 600;
  color: var(--text-dim);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  padding: 8px 0;
  border-bottom: 1px solid var(--card-border);
}
.token-table td {
  padding: 10px 0;
  font-size: 13px;
  color: var(--text-secondary);
  border-bottom: 1px solid rgba(255,255,255,0.03);
}
.token-table td code {
  font-family: 'SF Mono', 'Consolas', monospace;
  font-size: 11px;
  background: var(--input-bg);
  padding: 2px 6px;
  border-radius: 4px;
}

/* Description list */
.desc-list { display: grid; grid-template-columns: 120px 1fr; gap: 12px 16px; }
.desc-label { font-size: 13px; color: var(--text-dim); }
.desc-value { font-size: 13px; color: var(--text); }
.desc-value a { color: var(--accent); text-decoration: none; }
.desc-value a:hover { text-decoration: underline; }

/* Stat grid */
.stat-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 12px;
}
.stat-item {
  background: var(--input-bg);
  border-radius: var(--radius-sm);
  padding: 12px;
}
.stat-value { font-size: 20px; font-weight: 600; color: var(--text); }
.stat-label { font-size: 11px; color: var(--text-dim); margin-top: 2px; }

/* Confirm modal */
.modal-overlay {
  display: none;
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.5);
  z-index: 100;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(4px);
}
.modal-overlay.active { display: flex; }
.modal-box {
  background: #2c2c2e;
  border: 1px solid var(--card-border);
  border-radius: 14px;
  padding: 24px;
  min-width: 320px;
  max-width: 400px;
  text-align: center;
}
.modal-box h3 { font-size: 16px; font-weight: 600; margin-bottom: 8px; }
.modal-box p { font-size: 13px; color: var(--text-secondary); margin-bottom: 20px; }
.modal-actions { display: flex; gap: 8px; justify-content: center; }

/* Toast */
.toast {
  position: fixed;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%) translateY(60px);
  background: #3a3a3c;
  color: var(--text);
  padding: 10px 20px;
  border-radius: 20px;
  font-size: 13px;
  z-index: 200;
  opacity: 0;
  transition: all 0.3s ease;
  pointer-events: none;
}
.toast.show {
  opacity: 1;
  transform: translateX(-50%) translateY(0);
}

/* Footer */
.footer {
  padding: 8px 28px;
  font-size: 11px;
  color: rgba(255,255,255,0.15);
  text-align: center;
  border-top: 1px solid rgba(255,255,255,0.04);
}

/* Empty state */
.empty-state {
  text-align: center;
  padding: 24px;
  color: var(--text-dim);
  font-size: 13px;
}

/* Log viewer */
.log-container {
  background: rgba(0,0,0,0.3);
  border: 1px solid var(--card-border);
  border-radius: var(--radius-sm);
  padding: 12px;
  max-height: 360px;
  overflow-y: auto;
  font-family: 'SF Mono', 'Consolas', 'Menlo', monospace;
  font-size: 12px;
  line-height: 1.6;
}
.log-container::-webkit-scrollbar { width: 5px; }
.log-container::-webkit-scrollbar-track { background: transparent; }
.log-container::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.08); border-radius: 3px; }

.log-line { white-space: pre-wrap; word-break: break-all; }
.log-line.log-DEBUG { color: rgba(255,255,255,0.35); }
.log-line.log-INFO { color: rgba(100,180,255,0.9); }
.log-line.log-WARNING { color: rgba(255,214,10,0.9); }
.log-line.log-ERROR { color: rgba(255,69,58,0.95); }
.log-line.log-CRITICAL { color: #ff453a; font-weight: 600; }

.log-filter-bar { display: flex; gap: 6px; align-items: center; }
.log-filter-btn {
  padding: 4px 10px;
  border: 1px solid var(--card-border);
  border-radius: 6px;
  background: transparent;
  color: var(--text-secondary);
  font-size: 11px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s;
  font-family: inherit;
}
.log-filter-btn:hover { background: var(--card); }
.log-filter-btn.active { background: rgba(0,113,227,0.15); border-color: var(--accent); color: var(--accent); }

/* QR Code Modal — Telegram-inspired */
.qr-card {
  background: #1c1c1e;
  border: 1px solid var(--card-border);
  border-radius: 16px;
  min-width: 320px;
  max-width: 380px;
  overflow: hidden;
  animation: qrFadeIn 0.25s ease;
}
@keyframes qrFadeIn {
  from { opacity: 0; transform: scale(0.95); }
  to { opacity: 1; transform: scale(1); }
}
.qr-header {
  text-align: center;
  padding: 28px 24px 16px;
  background: linear-gradient(135deg, rgba(0,113,227,0.12) 0%, rgba(88,86,214,0.08) 100%);
}
.qr-brand {
  font-size: 20px;
  font-weight: 700;
  color: var(--text);
  margin-bottom: 6px;
  letter-spacing: -0.3px;
}
.qr-title {
  font-size: 13px;
  font-weight: 400;
  color: var(--text-dim);
  margin: 0 0 0;
}
.qr-desc {
  font-size: 12px;
  color: var(--text-dim);
  margin: 0;
}
.qr-body {
  display: flex;
  justify-content: center;
  padding: 20px 24px;
}
.qr-img-wrap {
  padding: 12px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 16px rgba(0,0,0,0.25);
}
.qr-img-wrap img {
  width: 192px;
  height: 192px;
  display: block;
  border-radius: 4px;
}
.qr-footer {
  padding: 0 24px 24px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.qr-url-row {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  background: var(--input-bg);
  border: 1px solid var(--input-border);
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.15s;
}
.qr-url-row:hover { border-color: var(--accent); }
.qr-url-row:active { transform: scale(0.98); }
.qr-url-row code {
  flex: 1;
  font-family: 'SF Mono', 'Consolas', monospace;
  font-size: 11px;
  color: var(--text-secondary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.qr-url-row svg { color: var(--text-dim); flex-shrink: 0; }
.qr-close-btn {
  width: 100%;
  padding: 10px;
  background: var(--input-bg);
  border: 1px solid var(--card-border);
  border-radius: 10px;
  color: var(--text-secondary);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s;
  font-family: inherit;
}
.qr-close-btn:hover { background: var(--card-hover); color: var(--text); }
.qr-close-btn:active { transform: scale(0.98); }
</style>
</head>
<body>
<div class="bg-layer"></div>

<div class="app-layout">
  <!-- Sidebar -->
  <nav class="sidebar">
    <div class="sidebar-brand">
      <h1>DevToolBox</h1>
      <div class="version" id="version-label">v-</div>
    </div>
    <ul class="nav-list">
      <li class="nav-item active" data-page="dashboard" onclick="switchPage('dashboard')">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/></svg>
        <span>概览</span>
      </li>
      <li class="nav-item" data-page="security" onclick="switchPage('security')">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
        <span>安全</span>
      </li>
      <li class="nav-item" data-page="storage" onclick="switchPage('storage')">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/></svg>
        <span>存储</span>
      </li>
      <li class="nav-item" data-page="network" onclick="switchPage('network')">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10A15.3 15.3 0 0 1 12 2z"/></svg>
        <span>网络</span>
      </li>
      <li class="nav-item" data-page="logs" onclick="switchPage('logs')">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><line x1="10" y1="9" x2="8" y2="9"/></svg>
        <span>运行日志</span>
      </li>
      <li class="nav-item" data-page="about" onclick="switchPage('about')">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>
        <span>关于</span>
      </li>
    </ul>
    <div style="padding:8px 12px;margin-top:auto;">
      <button class="btn btn-ghost btn-sm" style="width:100%;" id="lang-toggle" onclick="toggleLanguage()">EN</button>
    </div>
  </nav>

  <!-- Content -->
  <div class="content" id="content">

    <!-- Dashboard -->
    <div class="page active" id="page-dashboard">
      <h2 id="dashboard-title" style="font-size:20px;font-weight:600;margin-bottom:20px;">Server Status</h2>

      <div class="card">
        <div class="card-header">
          <span class="card-title"><span class="status-dot" id="status-dot"></span><span id="status-text">Starting...</span></span>
        </div>
        <div id="url-section">
          <div class="form-label" id="local-access-label">Local Access</div>
          <div class="url-row">
            <code id="local-url">-</code>
            <button class="copy-btn" onclick="copyUrl('local')" title="Copy">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>
            </button>
          </div>
          <div class="form-label" id="network-access-label" style="margin-top:10px;">Network Access</div>
          <div class="url-row">
            <code id="network-url">-</code>
            <button class="copy-btn" onclick="copyUrl('network')" title="Copy">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>
            </button>
          </div>
        </div>
        <div class="btn-row" style="margin-top:16px;">
          <button class="btn btn-primary" id="btn-open-browser" onclick="api.open_browser()">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/></svg>
            Open in Browser
          </button>
          <button class="btn btn-primary" id="btn-qr-scan" onclick="showQrCode()">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/><rect x="14" y="14" width="3" height="3"/><line x1="21" y1="14" x2="21" y2="14.01"/><line x1="21" y1="21" x2="21" y2="21.01"/><line x1="17" y1="21" x2="17" y2="21.01"/></svg>
            <span id="btn-qr-label">QR Code</span>
          </button>
          <button class="btn btn-ghost" id="btn-copy-url" onclick="copyMainUrl()">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>
            Copy URL
          </button>
          <button class="btn btn-ghost" id="btn-open-storage" onclick="api.open_storage_folder()">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/></svg>
            Open Storage
          </button>
        </div>
      </div>

      <div class="stat-grid" id="stat-grid">
        <div class="stat-item"><div class="stat-value" id="stat-uptime">-</div><div class="stat-label" id="stat-uptime-label">Uptime</div></div>
        <div class="stat-item"><div class="stat-value" id="stat-files">-</div><div class="stat-label" id="stat-files-label">Files</div></div>
        <div class="stat-item"><div class="stat-value" id="stat-disk">-</div><div class="stat-label" id="stat-disk-label">Disk Usage</div></div>
      </div>
    </div>

    <!-- Security -->
    <div class="page" id="page-security">
      <h2 id="security-title" style="font-size:20px;font-weight:600;margin-bottom:20px;">Security Center</h2>

      <div class="card">
        <div class="card-header">
          <span class="card-title" id="access-token-title">Access Token</span>
          <span class="tag" id="token-status-tag">-</span>
        </div>
        <div class="url-row" id="token-url-row" style="display:none;">
          <code id="token-url-display">-</code>
          <button class="copy-btn" onclick="copyUrl('token')" title="Copy">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>
          </button>
        </div>
        <div class="btn-row" style="margin-top:12px;">
          <button class="btn btn-ghost" id="toggle-token-btn" onclick="toggleToken()">-</button>
          <button class="btn btn-danger btn-sm" id="refresh-token-btn" onclick="confirmRefreshToken()">Refresh Token</button>
        </div>
      </div>

      <div class="card">
        <div class="card-header">
          <span class="card-title" id="temp-tokens-title">Temporary Tokens</span>
        </div>
        <div class="form-row" style="margin-bottom:16px;">
          <input class="form-input" id="temp-label" placeholder="Label (e.g. colleague)" style="flex:1;">
          <select class="form-input" id="temp-expires" style="width:130px;">
            <option value="30">30 min</option>
            <option value="60" selected>1 hour</option>
            <option value="360">6 hours</option>
            <option value="1440">24 hours</option>
            <option value="10080">7 days</option>
          </select>
          <button class="btn btn-primary btn-sm" id="generate-btn" onclick="createTempToken()">Generate</button>
        </div>
        <div id="temp-token-list"></div>
      </div>
    </div>

    <!-- Storage -->
    <div class="page" id="page-storage">
      <h2 id="storage-title" style="font-size:20px;font-weight:600;margin-bottom:20px;">Storage</h2>

      <div class="card">
        <div class="form-group">
          <label class="form-label" id="upload-dir-label">Upload Directory</label>
          <div class="form-row">
            <input class="form-input" id="cfg-upload-dir" placeholder="uploads" style="flex:1;">
            <button class="btn btn-ghost btn-sm" id="browse-btn" onclick="pickFolder()">Browse</button>
          </div>
        </div>
        <div class="form-group">
          <label class="form-label" id="max-file-size-label">Max File Size</label>
          <div class="slider-wrap">
            <input type="range" id="cfg-max-size" min="1" max="100" value="50" oninput="document.getElementById('max-size-val').textContent=this.value+' MB'">
            <span class="slider-value" id="max-size-val">50 MB</span>
          </div>
        </div>
        <div class="form-group">
          <label class="form-label" id="auto-cleanup-label">Auto Cleanup (days)</label>
          <div class="form-row">
            <input class="form-input" id="cfg-cleanup-days" type="number" min="0" max="365" value="0" style="width:100px;">
            <span class="form-hint" id="cleanup-hint">0 = disabled</span>
          </div>
        </div>
        <button class="btn btn-primary" id="save-storage-btn" onclick="saveStorageConfig()">Save</button>

        <div style="margin-top:20px;padding-top:16px;border-top:1px solid var(--card-border);">
          <div class="form-label" id="current-usage-label" style="margin-bottom:8px;">Current Usage</div>
          <div class="stat-grid">
            <div class="stat-item"><div class="stat-value" id="storage-file-count">-</div><div class="stat-label" id="storage-files-label">Files</div></div>
            <div class="stat-item"><div class="stat-value" id="storage-disk">-</div><div class="stat-label" id="storage-disk-label">Disk</div></div>
          </div>
        </div>
      </div>
    </div>

    <!-- Network -->
    <div class="page" id="page-network">
      <h2 id="network-title" style="font-size:20px;font-weight:600;margin-bottom:20px;">Network</h2>

      <div class="card">
        <div class="form-group">
          <label class="form-label" id="listen-port-label">Listen Port</label>
          <input class="form-input" id="cfg-port" type="number" min="1024" max="65535">
        </div>
        <div class="form-group">
          <label class="form-label" id="bind-address-label">Bind Address</label>
          <select class="form-input" id="cfg-host" style="width:260px;">
            <option value="127.0.0.1">Localhost only (127.0.0.1)</option>
            <option value="0.0.0.0">All interfaces (0.0.0.0)</option>
          </select>
        </div>
        <button class="btn btn-primary" id="save-network-btn" onclick="saveNetworkConfig()">Save</button>
        <p class="form-hint" id="network-hint" style="margin-top:12px;">Changes take effect after restart.</p>
      </div>
    </div>

    <!-- About -->
    <div class="page" id="page-about">
      <h2 id="about-title" style="font-size:20px;font-weight:600;margin-bottom:20px;">About</h2>

      <div class="card" style="text-align:center;padding:32px;">
        <div style="display:inline-flex;align-items:center;justify-content:center;width:64px;height:64px;border-radius:16px;background:var(--accent);color:white;font-size:24px;font-weight:700;margin-bottom:16px;">DT</div>
        <h3 style="font-size:22px;font-weight:700;">DevToolBox</h3>
        <p style="font-size:13px;color:var(--text-dim);margin-top:4px;" id="about-version">v-</p>
        <p id="about-desc" style="font-size:13px;color:var(--text-secondary);margin-top:12px;max-width:360px;margin-left:auto;margin-right:auto;">Local-first developer toolkit. All data processed locally, nothing uploaded or sent externally.</p>
      </div>

      <div class="card">
        <div class="desc-list" id="about-info">
          <span class="desc-label" id="about-version-label">Version</span><span class="desc-value" id="about-ver">-</span>
          <span class="desc-label" id="about-python-label">Python</span><span class="desc-value" id="about-python">-</span>
          <span class="desc-label" id="about-platform-label">Platform</span><span class="desc-value" id="about-platform">-</span>
          <span class="desc-label" id="about-project-label">Project</span><span class="desc-value"><a href="https://github.com/messageoom/DevToolBox" onclick="event.preventDefault();api.open_browser && window.open('https://github.com/messageoom/DevToolBox')">github.com/messageoom/DevToolBox</a></span>
          <span class="desc-label" id="about-license-label">License</span><span class="desc-value" id="about-license-value">MIT License</span>
        </div>
      </div>
    </div>

    <!-- Logs -->
    <div class="page" id="page-logs">
      <h2 id="logs-title" style="font-size:20px;font-weight:600;margin-bottom:20px;">Runtime Logs</h2>

      <div class="card">
        <div class="card-header">
          <span class="card-title" id="logs-card-title">Application Logs</span>
          <div class="log-filter-bar">
            <button class="log-filter-btn active" data-level="ALL" onclick="setLogFilter('ALL', this)">ALL</button>
            <button class="log-filter-btn" data-level="INFO" onclick="setLogFilter('INFO', this)">INFO</button>
            <button class="log-filter-btn" data-level="WARNING" onclick="setLogFilter('WARNING', this)">WARN</button>
            <button class="log-filter-btn" data-level="ERROR" onclick="setLogFilter('ERROR', this)">ERROR</button>
          </div>
        </div>
        <div class="log-container" id="log-container">
          <div class="empty-state" id="log-empty">No logs yet</div>
        </div>
        <div class="btn-row" style="margin-top:12px;">
          <button class="btn btn-ghost btn-sm" onclick="copyLogs()">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>
            Copy
          </button>
          <button class="btn btn-ghost btn-sm" onclick="confirmClearLogs()">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>
            Clear
          </button>
        </div>
      </div>
    </div>
  </div>
</div>

<div class="footer" id="footer-text">DevToolBox — Local-First Developer Toolkit</div>

<!-- Confirm modal -->
<div class="modal-overlay" id="confirm-modal">
  <div class="modal-box">
    <h3 id="modal-title">Confirm</h3>
    <p id="modal-message">Are you sure?</p>
    <div class="modal-actions">
      <button class="btn btn-ghost" id="modal-cancel-btn" onclick="closeModal()">Cancel</button>
      <button class="btn btn-danger" id="modal-confirm-btn" onclick="modalConfirmAction()">Confirm</button>
    </div>
  </div>
</div>

<!-- QR Code Modal -->
<div class="modal-overlay" id="qr-modal" onclick="if(event.target===this)closeQrModal()">
  <div class="qr-card">
    <div class="qr-header">
      <div class="qr-brand">DevToolBox</div>
      <p id="qr-modal-title" class="qr-title">Scan to Access</p>
      <p id="qr-modal-desc" class="qr-desc">Scan with your phone camera</p>
    </div>
    <div class="qr-body">
      <div class="qr-img-wrap">
        <img id="qr-modal-img" src="" alt="QR Code" />
      </div>
    </div>
    <div class="qr-footer">
      <div class="qr-url-row" onclick="copyUrl('qr-modal')">
        <code id="qr-modal-url">-</code>
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>
      </div>
      <button class="qr-close-btn" onclick="closeQrModal()" id="qr-close-btn">Close</button>
    </div>
  </div>
</div>

<!-- Toast -->
<div class="toast" id="toast"></div>

<script>
// --- i18n ---
const LANG = {
  zh: {
    // Sidebar
    dashboard: '概览', security: '安全', storage: '存储', network: '网络', logs: '运行日志', about: '关于',
    // Dashboard
    serverStatus: '服务器状态', starting: '启动中...', running: '运行中', stopped: '已停止',
    localAccess: '本地访问', networkAccess: '网络访问',
    openInBrowser: '在浏览器中打开', copied: '已复制！', copyFailed: '复制失败',
    copyUrl: '复制URL', openStorage: '打开存储',
    qrCode: '扫码访问', scanToAccess: '扫码访问', scanDesc: '使用手机相机扫描二维码',
    uptime: '运行时间', files: '文件数', diskUsage: '磁盘使用',
    // Security
    securityCenter: '安全中心', accessToken: '访问令牌', refreshToken: '刷新令牌',
    tempTokens: '临时令牌', label: '标签', labelPlaceholder: '标签（例如：同事）',
    '30min': '30分钟', '1hour': '1小时', '6hours': '6小时', '24hours': '24小时', '7days': '7天',
    generate: '生成', enabled: '已启用', disabled: '已禁用',
    disableToken: '禁用令牌', enableToken: '启用令牌',
    tokenDisabled: '令牌已禁用', tokenEnabled: '令牌已启用',
    refreshConfirm: '旧令牌将失效，确定继续？', tokenRefreshed: '令牌已刷新',
    labelRequired: '请输入标签', tokenCreated: '临时令牌已创建', failed: '失败',
    deleteToken: '删除令牌', deleteConfirm: '确定删除此临时令牌？', deleted: '已删除',
    noTempTokens: '暂无临时令牌', token: '令牌', expires: '过期时间',
    status: '状态', expired: '已过期', active: '有效', delete: '删除',
    // Storage
    uploadDir: '上传目录', browse: '浏览', maxFileSize: '最大文件大小',
    autoCleanup: '自动清理（天）', cleanupDisabled: '0 = 禁用', save: '保存',
    currentUsage: '当前使用', disk: '磁盘',
    // Network
    listenPort: '监听端口', bindAddress: '绑定地址',
    localhostOnly: '仅本地 (127.0.0.1)', allInterfaces: '所有接口 (0.0.0.0)',
    savedRestartRequired: '已保存（需重启生效）', restartRequired: '更改在重启后生效。',
    // About
    aboutDesc: '本地优先的开发者工具箱。所有数据在本地处理，不上传或发送到外部。',
    version: '版本', python: 'Python', platform: '平台',
    project: '项目', license: '许可证', mitLicense: 'MIT许可证',
    // Logs
    logsTitle: '运行日志', logsCardTitle: '应用日志', noLogs: '暂无日志',
    copyLogs: '复制日志', clearLogs: '清空日志', clearLogsConfirm: '确定清空所有日志？',
    logsCopied: '日志已复制', logsCleared: '日志已清空',
    // Footer
    footer: 'DevToolBox — 本地优先的开发工具箱',
    // Modal
    confirm: '确认', areYouSure: '你确定吗？', cancel: '取消', close: '关闭',
    // Language
    lang: 'EN'
  },
  en: {
    // Sidebar
    dashboard: 'Dashboard', security: 'Security', storage: 'Storage', network: 'Network', logs: 'Runtime Logs', about: 'About',
    // Dashboard
    serverStatus: 'Server Status', starting: 'Starting...', running: 'Running', stopped: 'Stopped',
    localAccess: 'Local Access', networkAccess: 'Network Access',
    openInBrowser: 'Open in Browser', copied: 'Copied!', copyFailed: 'Copy failed',
    copyUrl: 'Copy URL', openStorage: 'Open Storage',
    qrCode: 'QR Code', scanToAccess: 'Scan to Access', scanDesc: 'Scan QR code with your phone camera',
    uptime: 'Uptime', files: 'Files', diskUsage: 'Disk Usage',
    // Security
    securityCenter: 'Security Center', accessToken: 'Access Token', refreshToken: 'Refresh Token',
    tempTokens: 'Temporary Tokens', label: 'Label', labelPlaceholder: 'Label (e.g. colleague)',
    '30min': '30 min', '1hour': '1 hour', '6hours': '6 hours', '24hours': '24 hours', '7days': '7 days',
    generate: 'Generate', enabled: 'Enabled', disabled: 'Disabled',
    disableToken: 'Disable Token', enableToken: 'Enable Token',
    tokenDisabled: 'Token disabled', tokenEnabled: 'Token enabled',
    refreshConfirm: 'The old token will be invalidated. Continue?', tokenRefreshed: 'Token refreshed',
    labelRequired: 'Please enter a label', tokenCreated: 'Temp token created', failed: 'Failed',
    deleteToken: 'Delete Token', deleteConfirm: 'Remove this temporary token?', deleted: 'Deleted',
    noTempTokens: 'No temporary tokens', token: 'Token', expires: 'Expires',
    status: 'Status', expired: 'Expired', active: 'Active', delete: 'Delete',
    // Storage
    uploadDir: 'Upload Directory', browse: 'Browse', maxFileSize: 'Max File Size',
    autoCleanup: 'Auto Cleanup (days)', cleanupDisabled: '0 = disabled', save: 'Save',
    currentUsage: 'Current Usage', disk: 'Disk',
    // Network
    listenPort: 'Listen Port', bindAddress: 'Bind Address',
    localhostOnly: 'Localhost only (127.0.0.1)', allInterfaces: 'All interfaces (0.0.0.0)',
    savedRestartRequired: 'Saved (restart required)', restartRequired: 'Changes take effect after restart.',
    // About
    aboutDesc: 'Local-first developer toolkit. All data processed locally, nothing uploaded or sent externally.',
    version: 'Version', python: 'Python', platform: 'Platform',
    project: 'Project', license: 'License', mitLicense: 'MIT License',
    // Logs
    logsTitle: 'Runtime Logs', logsCardTitle: 'Application Logs', noLogs: 'No logs yet',
    copyLogs: 'Copy Logs', clearLogs: 'Clear Logs', clearLogsConfirm: 'Clear all logs?',
    logsCopied: 'Logs copied', logsCleared: 'Logs cleared',
    // Footer
    footer: 'DevToolBox — Local-First Developer Toolkit',
    // Modal
    confirm: 'Confirm', areYouSure: 'Are you sure?', cancel: 'Cancel', close: 'Close',
    // Language
    lang: '中文'
  }
};
let currentLang = 'zh';
function t(key) { return (LANG[currentLang] && LANG[currentLang][key]) || key; }

function applyTranslations() {
  // Sidebar nav labels
  document.querySelectorAll('.nav-item').forEach(function(item) {
    var page = item.getAttribute('data-page');
    if (page && LANG[currentLang][page]) {
      var span = item.querySelector('span');
      if (span) span.textContent = t(page);
    }
  });
  // Dashboard page
  var el;
  el = document.getElementById('dashboard-title'); if (el) el.textContent = t('serverStatus');
  el = document.getElementById('status-text'); if (el) el.textContent = _statusData.server_running ? t('running') : t('stopped');
  el = document.getElementById('local-access-label'); if (el) el.textContent = t('localAccess');
  el = document.getElementById('network-access-label'); if (el) el.textContent = t('networkAccess');
  el = document.getElementById('btn-open-browser'); if (el) el.innerHTML = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/></svg>' + t('openInBrowser');
  el = document.getElementById('btn-copy-url'); if (el) el.innerHTML = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>' + t('copyUrl');
  el = document.getElementById('btn-open-storage'); if (el) el.innerHTML = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/></svg>' + t('openStorage');
  el = document.getElementById('stat-uptime-label'); if (el) el.textContent = t('uptime');
  el = document.getElementById('stat-files-label'); if (el) el.textContent = t('files');
  el = document.getElementById('stat-disk-label'); if (el) el.textContent = t('diskUsage');
  // Security page
  el = document.getElementById('security-title'); if (el) el.textContent = t('securityCenter');
  el = document.getElementById('access-token-title'); if (el) el.textContent = t('accessToken');
  el = document.getElementById('refresh-token-btn'); if (el) el.textContent = t('refreshToken');
  el = document.getElementById('temp-tokens-title'); if (el) el.textContent = t('tempTokens');
  el = document.getElementById('temp-label'); if (el) el.placeholder = t('labelPlaceholder');
  el = document.getElementById('generate-btn'); if (el) el.textContent = t('generate');
  // Security select options
  var sel = document.getElementById('temp-expires');
  if (sel) {
    sel.options[0].text = t('30min');
    sel.options[1].text = t('1hour');
    sel.options[2].text = t('6hours');
    sel.options[3].text = t('24hours');
    sel.options[4].text = t('7days');
  }
  // Security token status and toggle button (re-apply with current state)
  var tag = document.getElementById('token-status-tag');
  if (tag) {
    var isEnabled = tag.getAttribute('data-enabled') === 'true';
    tag.textContent = isEnabled ? t('enabled') : t('disabled');
  }
  var toggleBtn = document.getElementById('toggle-token-btn');
  if (toggleBtn) {
    var isEnabled2 = toggleBtn.getAttribute('data-enabled') === 'true';
    toggleBtn.textContent = isEnabled2 ? t('disableToken') : t('enableToken');
  }
  // Storage page
  el = document.getElementById('storage-title'); if (el) el.textContent = t('storage');
  el = document.getElementById('upload-dir-label'); if (el) el.textContent = t('uploadDir');
  el = document.getElementById('browse-btn'); if (el) el.textContent = t('browse');
  el = document.getElementById('max-file-size-label'); if (el) el.textContent = t('maxFileSize');
  el = document.getElementById('auto-cleanup-label'); if (el) el.textContent = t('autoCleanup');
  el = document.getElementById('cleanup-hint'); if (el) el.textContent = t('cleanupDisabled');
  el = document.getElementById('save-storage-btn'); if (el) el.textContent = t('save');
  el = document.getElementById('current-usage-label'); if (el) el.textContent = t('currentUsage');
  el = document.getElementById('storage-files-label'); if (el) el.textContent = t('files');
  el = document.getElementById('storage-disk-label'); if (el) el.textContent = t('disk');
  // Network page
  el = document.getElementById('network-title'); if (el) el.textContent = t('network');
  el = document.getElementById('listen-port-label'); if (el) el.textContent = t('listenPort');
  el = document.getElementById('bind-address-label'); if (el) el.textContent = t('bindAddress');
  el = document.getElementById('save-network-btn'); if (el) el.textContent = t('save');
  el = document.getElementById('network-hint'); if (el) el.textContent = t('restartRequired');
  var hostSel = document.getElementById('cfg-host');
  if (hostSel) {
    hostSel.options[0].text = t('localhostOnly');
    hostSel.options[1].text = t('allInterfaces');
  }
  // About page
  el = document.getElementById('about-title'); if (el) el.textContent = t('about');
  el = document.getElementById('about-desc'); if (el) el.textContent = t('aboutDesc');
  el = document.getElementById('about-version-label'); if (el) el.textContent = t('version');
  el = document.getElementById('about-python-label'); if (el) el.textContent = t('python');
  el = document.getElementById('about-platform-label'); if (el) el.textContent = t('platform');
  el = document.getElementById('about-project-label'); if (el) el.textContent = t('project');
  el = document.getElementById('about-license-label'); if (el) el.textContent = t('license');
  el = document.getElementById('about-license-value'); if (el) el.textContent = t('mitLicense');
  // Footer
  el = document.getElementById('footer-text'); if (el) el.textContent = t('footer');
  // Modal
  el = document.getElementById('modal-title'); if (el) el.textContent = t('confirm');
  el = document.getElementById('modal-message'); if (el) el.textContent = t('areYouSure');
  el = document.getElementById('modal-cancel-btn'); if (el) el.textContent = t('cancel');
  el = document.getElementById('modal-confirm-btn'); if (el) el.textContent = t('confirm');
  // Logs page
  el = document.getElementById('logs-title'); if (el) el.textContent = t('logsTitle');
  el = document.getElementById('logs-card-title'); if (el) el.textContent = t('logsCardTitle');
  // Language toggle button
  el = document.getElementById('lang-toggle'); if (el) el.textContent = t('lang');
  // QR modal
  el = document.getElementById('btn-qr-label'); if (el) el.textContent = t('qrCode');
  el = document.getElementById('qr-modal-title'); if (el) el.textContent = t('scanToAccess');
  el = document.getElementById('qr-modal-desc'); if (el) el.textContent = t('scanDesc');
  el = document.getElementById('qr-close-btn'); if (el) el.textContent = t('close');
  // Re-render temp tokens
  if (_lastTempTokens) renderTempTokens(_lastTempTokens);
}

function toggleLanguage() {
  currentLang = currentLang === 'zh' ? 'en' : 'zh';
  if (api) api.set_language(currentLang);
  applyTranslations();
}

let api = window.pywebview ? pywebview.api : null;
let _modalAction = null;
let _statusData = {};
let _lastTempTokens = [];

// Wait for pywebview API ready
function waitForApi() {
  return new Promise(resolve => {
    if (api) return resolve();
    const check = () => {
      if (window.pywebview && pywebview.api) {
        api = pywebview.api;
        resolve();
      } else {
        setTimeout(check, 100);
      }
    };
    check();
  });
}

async function init() {
  await waitForApi();
  // Load saved language preference
  try { currentLang = await api.get_language(); } catch(e) { currentLang = 'zh'; }
  await refreshStatus();
  await refreshConfig();
  applyTranslations();
  setInterval(refreshStatus, 5000);
}

// --- Navigation ---
let _activePage = 'dashboard';
function switchPage(page) {
  _activePage = page;
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
  document.getElementById('page-' + page).classList.add('active');
  document.querySelector('[data-page="' + page + '"]').classList.add('active');
}

// --- Status ---
async function refreshStatus() {
  try {
    const s = await api.get_status();
    _statusData = s;
    document.getElementById('version-label').textContent = 'v' + s.version;
    document.getElementById('status-dot').className = 'status-dot ' + (s.server_running ? 'running' : 'stopped');
    document.getElementById('status-text').textContent = s.server_running ? t('running') : t('stopped');
    document.getElementById('local-url').textContent = s.local_url;
    document.getElementById('network-url').textContent = s.network_url;
    document.getElementById('stat-uptime').textContent = formatUptime(s.uptime);
    document.getElementById('stat-files').textContent = s.file_count;
    document.getElementById('stat-disk').textContent = formatBytes(s.disk_bytes);
    // About
    document.getElementById('about-version').textContent = 'v' + s.version;
    document.getElementById('about-ver').textContent = 'v' + s.version;
    document.getElementById('about-python').textContent = s.python_version;
    document.getElementById('about-platform').textContent = s.platform;
    // Storage stats
    document.getElementById('storage-file-count').textContent = s.file_count;
    document.getElementById('storage-disk').textContent = formatBytes(s.disk_bytes);
  } catch(e) { console.error(e); }
}

// --- Config ---
async function refreshConfig() {
  try {
    const c = await api.get_config();
    // Security
    const sec = c.security || {};
    const tag = document.getElementById('token-status-tag');
    tag.textContent = sec.token_enabled ? t('enabled') : t('disabled');
    tag.setAttribute('data-enabled', sec.token_enabled);
    tag.className = 'tag ' + (sec.token_enabled ? 'tag-success' : 'tag-info');
    const toggleBtn = document.getElementById('toggle-token-btn');
    toggleBtn.textContent = sec.token_enabled ? t('disableToken') : t('enableToken');
    toggleBtn.setAttribute('data-enabled', sec.token_enabled);
    if (sec.has_token) {
      document.getElementById('token-url-row').style.display = 'flex';
      document.getElementById('token-url-display').textContent = _statusData.access_url || '-';
    }
    // Temp tokens
    renderTempTokens(sec.temp_tokens || []);
    // Storage
    const sto = c.storage || {};
    document.getElementById('cfg-upload-dir').value = sto.upload_dir || 'uploads';
    document.getElementById('cfg-max-size').value = sto.max_file_size_mb || 50;
    document.getElementById('max-size-val').textContent = (sto.max_file_size_mb || 50) + ' MB';
    document.getElementById('cfg-cleanup-days').value = sto.auto_cleanup_days || 0;
    // Network
    const net = c.network || {};
    document.getElementById('cfg-port').value = net.port || 5000;
    document.getElementById('cfg-host').value = net.host || '0.0.0.0';
  } catch(e) { console.error(e); }
}

// --- Security actions ---
function toggleToken() {
  const enabled = document.getElementById('toggle-token-btn').getAttribute('data-enabled') === 'true';
  api.toggle_token({enabled: !enabled}).then(r => {
    if (r.success) { showToast(enabled ? t('tokenDisabled') : t('tokenEnabled')); refreshConfig(); }
  });
}

function confirmRefreshToken() {
  showModal(t('refreshToken'), t('refreshConfirm'), () => {
    api.refresh_token().then(r => {
      if (r.success) { showToast(t('tokenRefreshed')); refreshConfig(); refreshStatus(); }
    });
  });
}

function createTempToken() {
  const label = document.getElementById('temp-label').value.trim();
  const minutes = parseInt(document.getElementById('temp-expires').value);
  if (!label) { showToast(t('labelRequired')); return; }
  api.create_temp_token({label: label, expires_minutes: minutes}).then(r => {
    if (r.success) { showToast(t('tokenCreated')); document.getElementById('temp-label').value = ''; refreshConfig(); }
    else { showToast(r.error || t('failed')); }
  });
}

function deleteTempToken(token) {
  showModal(t('deleteToken'), t('deleteConfirm'), () => {
    api.delete_temp_token(token).then(r => { if (r.success) { showToast(t('deleted')); refreshConfig(); } });
  });
}

function renderTempTokens(tokens) {
  _lastTempTokens = tokens;
  const el = document.getElementById('temp-token-list');
  if (!tokens.length) { el.innerHTML = '<div class="empty-state">' + t('noTempTokens') + '</div>'; return; }
  let html = '<table class="token-table"><thead><tr><th>' + t('label') + '</th><th>' + t('token') + '</th><th>' + t('expires') + '</th><th>' + t('status') + '</th><th></th></tr></thead><tbody>';
  const now = Date.now() / 1000;
  for (const t of tokens) {
    const expired = t.expires_at < now;
    html += '<tr>'
      + '<td>' + esc(t.label) + '</td>'
      + '<td><code>' + esc(t.token) + '</code></td>'
      + '<td>' + formatTime(t.expires_at) + '</td>'
      + '<td><span class="tag ' + (expired ? 'tag-danger' : 'tag-success') + '">' + (expired ? t('expired') : t('active')) + '</span></td>'
      + '<td><button class="btn btn-ghost btn-sm" onclick="deleteTempToken(\'' + esc(t.token) + '\')">' + t('delete') + '</button></td>'
      + '</tr>';
  }
  html += '</tbody></table>';
  el.innerHTML = html;
}

// --- Storage / Network save ---
function saveStorageConfig() {
  api.save_config({storage: {
    upload_dir: document.getElementById('cfg-upload-dir').value,
    max_file_size_mb: parseInt(document.getElementById('cfg-max-size').value),
    auto_cleanup_days: parseInt(document.getElementById('cfg-cleanup-days').value),
  }}).then(r => showToast(r.success ? t('save') : t('failed')));
}

async function pickFolder() {
  const r = await api.pick_folder();
  if (r.success) {
    document.getElementById('cfg-upload-dir').value = r.path;
  }
}

function saveNetworkConfig() {
  api.save_config({network: {
    port: parseInt(document.getElementById('cfg-port').value),
    host: document.getElementById('cfg-host').value,
  }}).then(r => showToast(r.success ? t('savedRestartRequired') : t('failed')));
}

// --- Copy ---
function copyUrl(type) {
  let text = '';
  if (type === 'local') text = _statusData.local_url || '';
  else if (type === 'network') text = _statusData.network_url || '';
  else if (type === 'token') text = _statusData.access_url || '';
  else if (type === 'qr-modal') text = _statusData.qr_url || '';
  api.copy_text(text).then(r => showToast(r.success ? t('copied') : t('copyFailed')));
}

function copyMainUrl() {
  api.copy_url().then(r => showToast(r.success ? t('copied') : t('copyFailed')));
}

// --- Logs ---
let _currentLogFilter = 'ALL';
let _cachedLogs = [];
let _logPollTimer = null;

async function refreshLogs() {
  try {
    const raw = await api.get_logs();
    const logs = typeof raw === 'string' ? JSON.parse(raw) : raw;
    _cachedLogs = logs;
    if (_activePage === 'logs') renderLogs(logs);
  } catch(e) { console.error('refreshLogs error:', e); }
}

// Called by Python via window.evaluate_js — primary log update mechanism
window._receiveLogs = function(logs) {
  if (!logs || !Array.isArray(logs)) return;
  _cachedLogs = logs;
  if (_activePage === 'logs') renderLogs(logs);
};

function renderLogs(logs) {
  const container = document.getElementById('log-container');
  const wasAtBottom = container.scrollTop + container.clientHeight >= container.scrollHeight - 20;

  const filtered = _currentLogFilter === 'ALL'
    ? logs
    : logs.filter(line => {
        const level = line.split(' ')[1];
        return level && level.indexOf(_currentLogFilter) === 0;
      });

  if (!filtered.length) {
    container.innerHTML = '<div class="empty-state">' + esc(t('noLogs')) + '</div>';
    return;
  }

  let html = '';
  for (const line of filtered) {
    const level = (line.split(' ')[1] || '').split(':')[0].trim();
    const cls = ['DEBUG','INFO','WARNING','ERROR','CRITICAL'].indexOf(level) >= 0 ? ' log-' + level : '';
    html += '<div class="log-line' + cls + '">' + esc(line) + '</div>';
  }
  container.innerHTML = html;

  if (wasAtBottom) {
    container.scrollTop = container.scrollHeight;
  }
}

function setLogFilter(level, btn) {
  _currentLogFilter = level;
  document.querySelectorAll('.log-filter-btn').forEach(b => b.classList.remove('active'));
  if (btn) btn.classList.add('active');
  renderLogs(_cachedLogs);
}

function copyLogs() {
  const text = _cachedLogs.join('\n');
  api.copy_text(text).then(r => showToast(r.success ? t('logsCopied') : t('copyFailed')));
}

function confirmClearLogs() {
  showModal(t('clearLogs'), t('clearLogsConfirm'), () => {
    api.clear_logs().then(r => {
      if (r.success) { _cachedLogs = []; renderLogs([]); showToast(t('logsCleared')); }
    });
  });
}

// Initial log load — Python pushes updates via _receiveLogs
setTimeout(() => { if (api) refreshLogs(); }, 1500);

// --- Modal ---
function showModal(title, message, onConfirm) {
  document.getElementById('modal-title').textContent = title;
  document.getElementById('modal-message').textContent = message;
  _modalAction = onConfirm;
  document.getElementById('confirm-modal').classList.add('active');
}
function closeModal() { document.getElementById('confirm-modal').classList.remove('active'); _modalAction = null; }
function modalConfirmAction() { if (_modalAction) _modalAction(); closeModal(); }

// --- QR Code Modal ---
async function showQrCode() {
  try {
    const r = await api.get_qr_code();
    if (r.success) {
      document.getElementById('qr-modal-img').src = r.image;
      document.getElementById('qr-modal-url').textContent = r.url;
      _statusData.qr_url = r.url;
      document.getElementById('qr-modal').classList.add('active');
    } else {
      showToast(r.error || t('failed'));
    }
  } catch(e) { showToast(t('failed')); }
}
function closeQrModal() { document.getElementById('qr-modal').classList.remove('active'); }

// --- Toast ---
function showToast(msg) {
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.classList.add('show');
  setTimeout(() => t.classList.remove('show'), 2500);
}

// --- Helpers ---
function esc(s) { const d = document.createElement('div'); d.textContent = s; return d.innerHTML; }
function formatUptime(s) {
  const h = Math.floor(s/3600), m = Math.floor((s%3600)/60), sec = s%60;
  if (h > 0) return h + 'h ' + m + 'm';
  if (m > 0) return m + 'm ' + sec + 's';
  return sec + 's';
}
function formatBytes(b) {
  if (!b) return '0 B';
  const u = ['B','KB','MB','GB']; let i = 0; let v = b;
  while (v >= 1024 && i < u.length - 1) { v /= 1024; i++; }
  return v.toFixed(1) + ' ' + u[i];
}
function formatTime(ts) {
  return new Date(ts * 1000).toLocaleString();
}

// Init
window.addEventListener('pywebviewready', init);
// Fallback in case event already fired
setTimeout(() => { if (!api) init(); }, 500);
</script>
</body>
</html>'''


# ---------------------------------------------------------------------------
#  Main entry
# ---------------------------------------------------------------------------

def run_gui_app(app, host, port, access_token, version='dev'):
    """Start Flask in daemon thread, then open pywebview native window."""

    start_time = time.time()
    api = Api(app, host, port, access_token, version, start_time)

    # Attach log handler for GUI log viewer
    global _log_handler
    _log_handler = _GUILogHandler()
    logging.root.addHandler(_log_handler)
    _log_handler.setLevel(logging.DEBUG)

    # Start Flask
    flask_thread = start_flask_thread(app, host, port)

    # Print banner
    local_ip = _get_local_ip()

    base_url = f"http://127.0.0.1:{port}"
    token_url = f"{base_url}/?token={access_token}"
    network_url = f"http://{local_ip}:{port}/?token={access_token}"

    print()
    print("=" * 56)
    print(f"  DevToolBox v{version}")
    print("=" * 56)
    print(f"  Local:   {token_url}")
    print(f"  Network: {network_url}")
    print("=" * 56)
    print()

    logger.info(f'DevToolBox v{version} started — Local: {base_url} | LAN: http://{local_ip}:{port}')
    logger.info(f'Detected LAN IP: {local_ip} (port {port})')

    # Wait for server
    if not wait_for_server(host, port):
        print("ERROR: Flask server failed to start within timeout")
        os._exit(1)

    api.set_server_running(True)

    # Create native window
    window = webview.create_window(
        f'DevToolBox v{version}',
        html=GUI_HTML,
        js_api=api,
        width=820,
        height=560,
        resizable=True,
        min_size=(640, 460),
    )
    api.set_window(window)

    # Load icon for window if available
    try:
        icon_path = None
        if hasattr(sys, '_MEIPASS'):
            icon_path = os.path.join(sys._MEIPASS, 'icon.png')
        else:
            icon_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                'frontend', 'public', 'icon.png'
            )
        if os.path.exists(icon_path):
            window.set_icon(icon_path)
    except Exception:
        pass

    # Background thread: push logs to JS via evaluate_js every 3 seconds
    def _log_push_thread():
        import re
        ansi_re = re.compile(r'\x1b\[[0-9;]*m')
        time.sleep(3)
        tick = 0
        while True:
            try:
                time.sleep(3)
                tick += 1
                if _log_handler is None:
                    continue

                records = list(_log_handler.records)
                clean = [ansi_re.sub('', line) for line in records]
                window.evaluate_js('_receiveLogs(' + json.dumps(clean) + ')')
            except Exception:
                pass

    threading.Thread(target=_log_push_thread, daemon=True).start()

    webview.start(debug=False)

    # Window closed
    os._exit(0)
