"""
System tray integration for DevToolBox.
Uses pystray for cross-platform tray icon support.
"""

import os
import sys
import time
import socket
import threading
import webbrowser
import logging

logger = logging.getLogger(__name__)


def get_tray_icon_image():
    """Load tray icon image from bundled or dev location."""
    try:
        from PIL import Image

        # Try PyInstaller bundle path first
        if hasattr(sys, '_MEIPASS'):
            icon_path = os.path.join(sys._MEIPASS, 'icon.png')
        else:
            # Dev mode: relative to project root
            icon_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                'frontend', 'public', 'icon.png'
            )

        if os.path.exists(icon_path):
            img = Image.open(icon_path)
            return img.resize((64, 64), Image.LANCZOS)
    except Exception:
        pass

    # Fallback: simple colored square
    try:
        from PIL import Image
        img = Image.new('RGBA', (64, 64), (0, 113, 227, 255))
        return img
    except Exception:
        return None


def wait_for_server(host, port, timeout=15):
    """Poll until Flask server is ready to accept connections."""
    start = time.time()
    while time.time() - start < timeout:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            sock.connect((host.replace('0.0.0.0', '127.0.0.1'), port))
            sock.close()
            return True
        except (ConnectionRefusedError, OSError):
            time.sleep(0.3)
    return False


def start_flask_thread(app, host, port):
    """Start Flask (or SocketIO) in a daemon thread."""
    def run():
        socketio = app.config.get('SOCKETIO')
        if socketio:
            socketio.run(app, host=host, port=port, debug=False, allow_unsafe_werkzeug=True)
        else:
            app.run(host=host, port=port, debug=False, use_reloader=False)

    thread = threading.Thread(target=run, daemon=True)
    thread.start()
    return thread


def _copy_to_clipboard(text):
    """Copy text to clipboard cross-platform."""
    try:
        import pyperclip
        pyperclip.copy(text)
        return True
    except Exception:
        # Fallback for Windows without pyperclip
        if sys.platform == 'win32':
            try:
                import subprocess
                process = subprocess.Popen(['clip'], stdin=subprocess.PIPE)
                process.communicate(text.encode('utf-8'))
                return True
            except Exception:
                pass
    return False


def run_tray_app(app, host, port, access_token, version='2.0.0'):
    """Main entry: start Flask in background, run system tray in main thread."""
    import pystray

    base_url = f"http://127.0.0.1:{port}"
    token_url = f"{base_url}/?token={access_token}"

    # Start Flask in background
    flask_thread = start_flask_thread(app, host, port)

    # Print banner
    hostname = socket.gethostname()
    try:
        local_ip = socket.gethostbyname(hostname)
    except Exception:
        local_ip = '127.0.0.1'

    network_url = f"http://{local_ip}:{port}/?token={access_token}"

    print()
    print("=" * 56)
    print(f"  DevToolBox v{version}")
    print("=" * 56)
    print(f"  Local:   {token_url}")
    print(f"  Network: {network_url}")
    print("=" * 56)
    print()

    # Wait for server
    if not wait_for_server(host, port):
        print("ERROR: Flask server failed to start within timeout")
        os._exit(1)

    # Auto-open browser
    try:
        webbrowser.open(token_url)
    except Exception:
        pass

    # Create tray icon
    image = get_tray_icon_image()

    def on_open(icon, item):
        webbrowser.open(token_url)

    def on_copy(icon, item):
        _copy_to_clipboard(token_url)
        icon.notify("Access URL copied to clipboard", "DevToolBox")

    def on_exit(icon, item):
        icon.stop()

    menu = pystray.Menu(
        pystray.MenuItem("Open in Browser", on_open, default=True),
        pystray.MenuItem("Copy Access URL", on_copy),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Exit", on_exit),
    )

    if image:
        icon = pystray.Icon("DevToolBox", image, f"DevToolBox v{version}", menu)
    else:
        icon = pystray.Icon("DevToolBox", menu=menu)

    icon.title = f"DevToolBox v{version}"

    def on_icon_stopped(icon):
        os._exit(0)

    icon.on_exit = on_icon_stopped

    try:
        icon.run()
    except Exception:
        # If tray fails, fall back to blocking Flask
        flask_thread.join()


def run_console_app(app, host, port, access_token, version='2.0.0'):
    """Fallback: run without tray, just console output + Flask blocking."""
    base_url = f"http://127.0.0.1:{port}"
    token_url = f"{base_url}/?token={access_token}"

    hostname = socket.gethostname()
    try:
        local_ip = socket.gethostbyname(hostname)
    except Exception:
        local_ip = '127.0.0.1'

    network_url = f"http://{local_ip}:{port}/?token={access_token}"

    print()
    print("=" * 56)
    print(f"  DevToolBox v{version}")
    print("=" * 56)
    print(f"  Local:   {token_url}")
    print(f"  Network: {network_url}")
    print("=" * 56)
    print()

    try:
        webbrowser.open(token_url)
    except Exception:
        pass

    socketio = app.config.get('SOCKETIO')
    if socketio:
        socketio.run(app, host=host, port=port, debug=False, allow_unsafe_werkzeug=True)
    else:
        app.run(host=host, port=port, debug=False, use_reloader=False)
