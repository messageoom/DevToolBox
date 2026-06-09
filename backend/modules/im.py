# backend/modules/im.py
"""
IM (Instant Messaging) module for DevToolBox.
Real-time message relay via SocketIO, file upload with thumbnails.
Messages are stored client-side (localStorage); server only relays.
No server-side database.
"""

import os
import threading
import time
import uuid
import logging

from flask import Blueprint, request, jsonify, send_file
from werkzeug.utils import secure_filename
from werkzeug.security import safe_join
from flask_socketio import emit

logger = logging.getLogger(__name__)

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB
THUMB_MAX_SIZE = (200, 200)

# ---------------------------------------------------------------------------
# Upload directory helpers
# ---------------------------------------------------------------------------

def _get_project_root():
    import sys
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _get_upload_dir():
    try:
        from utils.config_manager import load_config, get_upload_dir
    except ImportError:
        try:
            from backend.utils.config_manager import load_config, get_upload_dir
        except ImportError:
            from ..utils.config_manager import load_config, get_upload_dir

    config = load_config()
    upload_base = get_upload_dir(config)
    im_dir = os.path.join(upload_base, 'im')
    os.makedirs(im_dir, exist_ok=True)
    return im_dir


# ---------------------------------------------------------------------------
# Device registry — in-memory only, supports multiple tabs per device
# ---------------------------------------------------------------------------
connected_devices = {}  # {nodeId: {'name': str, 'sessions': {sid: ip}}}
sid_to_node = {}        # {sid: nodeId}
_devices_lock = threading.RLock()


def _peers_list():
    with _devices_lock:
        result = []
        for nid, info in connected_devices.items():
            ips = list(info['sessions'].values())
            result.append({'nodeId': nid, 'name': info['name'], 'ip': ips[-1] if ips else ''})
        return result


def _all_sids_except(exclude_sid):
    with _devices_lock:
        return [s for info in connected_devices.values() for s in info['sessions'] if s != exclude_sid]


def _device_sids(node_id):
    with _devices_lock:
        dev = connected_devices.get(node_id)
        return list(dev['sessions'].keys()) if dev else []


# ---------------------------------------------------------------------------
# Blueprint — file upload / serve
# ---------------------------------------------------------------------------
im_bp = Blueprint('im', __name__)


@im_bp.route('/status', methods=['GET'])
def im_status():
    """Diagnostic endpoint: check Socket.IO availability and connected devices."""
    with _devices_lock:
        devices = []
        for nid, info in connected_devices.items():
            devices.append({
                'nodeId': nid,
                'name': info['name'],
                'sessions': len(info['sessions']),
            })
    return jsonify({
        'success': True,
        'socketio_registered': socketio_registered,
        'device_count': len(devices),
        'devices': devices,
    })


socketio_registered = False  # set to True by register_im_events()


@im_bp.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file provided'}), 400

    f = request.files['file']
    if not f.filename:
        return jsonify({'success': False, 'error': 'Empty filename'}), 400

    f.seek(0, os.SEEK_END)
    size = f.tell()
    f.seek(0)
    if size > MAX_FILE_SIZE:
        return jsonify({'success': False, 'error': 'File too large (max 50 MB)'}), 400

    basename = secure_filename(f.filename) or 'file'
    ext = os.path.splitext(basename)[1]
    unique_name = f"{uuid.uuid4().hex}{ext}"

    upload_dir = _get_upload_dir()
    filepath = os.path.join(upload_dir, unique_name)
    f.save(filepath)

    mime = f.mimetype or 'application/octet-stream'
    file_id = uuid.uuid4().hex
    file_url = f"/api/im/files/{unique_name}"
    thumbnail_url = None

    if mime.startswith('image/'):
        try:
            from PIL import Image
            thumb_name = f"thumb_{unique_name}.webp"
            thumb_path = os.path.join(upload_dir, thumb_name)
            with Image.open(filepath) as img:
                img.thumbnail(THUMB_MAX_SIZE)
                img.save(thumb_path, 'WEBP', quality=80)
            thumbnail_url = f"/api/im/thumbs/{unique_name}"
        except Exception:
            logger.warning('Failed to generate thumbnail for %s', unique_name, exc_info=True)

    elif mime.startswith('video/'):
        try:
            import subprocess
            thumb_name = f"thumb_{unique_name}.webp"
            thumb_path = os.path.join(upload_dir, thumb_name)
            result = subprocess.run(
                ['ffmpeg', '-i', filepath, '-ss', '00:00:01',
                 '-frames:v', '1', '-y',
                 '-vf', 'scale=200:200:force_original_aspect_ratio=decrease,pad=200:200:(ow-iw)/2:(oh-ih)/2:white',
                 thumb_path],
                capture_output=True, timeout=15,
            )
            if os.path.isfile(thumb_path):
                thumbnail_url = f"/api/im/thumbs/{unique_name}"
        except Exception:
            pass

    return jsonify({
        'success': True, 'id': file_id, 'url': file_url,
        'filename': f.filename, 'size': size, 'mime': mime, 'thumbnail': thumbnail_url,
    })


@im_bp.route('/files/<path:filename>')
def serve_file(filename):
    upload_dir = _get_upload_dir()
    safe_path = safe_join(upload_dir, filename)
    if safe_path is None or not os.path.isfile(safe_path):
        return jsonify({'success': False, 'error': 'File not found'}), 404
    return send_file(safe_path)


@im_bp.route('/thumbs/<path:filename>')
def serve_thumb(filename):
    upload_dir = _get_upload_dir()
    thumb_name = f"thumb_{filename}.webp"
    safe_path = safe_join(upload_dir, thumb_name)

    # Thumbnail exists — serve directly
    if safe_path and os.path.isfile(safe_path):
        return send_file(safe_path, mimetype='image/webp')

    # Thumbnail missing — try to regenerate from original file
    original_path = safe_join(upload_dir, filename)
    if original_path and os.path.isfile(original_path):
        try:
            from PIL import Image
            with Image.open(original_path) as img:
                img.thumbnail(THUMB_MAX_SIZE)
                img.save(safe_path, 'WEBP', quality=80)
            return send_file(safe_path, mimetype='image/webp')
        except Exception:
            logger.warning('Failed to regenerate thumbnail for %s', filename, exc_info=True)

    # No thumbnail and no original — return the original file as fallback
    if original_path and os.path.isfile(original_path):
        return send_file(original_path)

    return jsonify({'success': False, 'error': 'Thumbnail not found'}), 404


# ---------------------------------------------------------------------------
# SocketIO — real-time relay, no persistence
# ---------------------------------------------------------------------------

def register_im_events(socketio):
    global socketio_registered
    socketio_registered = True
    logger.info('Socket.IO IM events registered — real-time messaging ENABLED')

    @socketio.on('join')
    def handle_join(data):
        from flask import request as flask_request
        sid = flask_request.sid
        node_id = data.get('nodeId')
        name = data.get('name', '').strip() or f'Device-{node_id[:6]}'
        ip = flask_request.headers.get('X-Forwarded-For', flask_request.remote_addr or '0.0.0.0')

        with _devices_lock:
            if node_id not in connected_devices:
                connected_devices[node_id] = {'name': name, 'sessions': {}}
            connected_devices[node_id]['name'] = name
            connected_devices[node_id]['sessions'][sid] = ip
            sid_to_node[sid] = node_id
            current_peers = _peers_list()

        logger.info('IM join: %s (%s) from %s — %d devices, %d sessions',
                     name, node_id[:8], ip, len(connected_devices),
                     len(connected_devices[node_id]['sessions']))

        logger.info('IM join → emitting "joined" to %s with %d peers: %s',
                     sid[:8], len(current_peers),
                     [p['nodeId'][:8] for p in current_peers])

        emit('joined', {
            'nodeId': node_id,
            'name': name,
            'peers': current_peers,
        })
        socketio.emit('peers', {'list': current_peers}, skip_sid=sid)

    @socketio.on('disconnect')
    def handle_disconnect():
        from flask import request as flask_request
        sid = flask_request.sid

        with _devices_lock:
            node_id = sid_to_node.pop(sid, None)
            if node_id and node_id in connected_devices:
                connected_devices[node_id]['sessions'].pop(sid, None)
                if not connected_devices[node_id]['sessions']:
                    name = connected_devices[node_id]['name']
                    del connected_devices[node_id]
                    logger.info('IM leave: %s (%s) — %d remaining', name, node_id[:8], len(connected_devices))
                    socketio.emit('leave', {'nodeId': node_id})
                    socketio.emit('peers', {'list': _peers_list()})
                else:
                    logger.info('IM session closed (sid=%s)', sid[:8])

    @socketio.on('rename')
    def handle_rename(data):
        from flask import request as flask_request
        sid = flask_request.sid
        node_id = data.get('nodeId')
        new_name = data.get('name', '').strip()
        if not new_name:
            return
        with _devices_lock:
            if node_id in connected_devices and sid in connected_devices[node_id]['sessions']:
                connected_devices[node_id]['name'] = new_name
        logger.info('IM rename: %s', new_name)
        socketio.emit('peers', {'list': _peers_list()})

    @socketio.on('send-msg')
    def handle_send_msg(data):
        from flask import request as flask_request
        sid = flask_request.sid

        with _devices_lock:
            sender_id = sid_to_node.get(sid)
            if not sender_id or sender_id not in connected_devices:
                sender_id = None
            sender_name = connected_devices[sender_id]['name'] if sender_id else '?'

        if sender_id is None:
            emit('msg-error', {'error': 'Not registered'})
            return

        msg_id = data.get('id') or uuid.uuid4().hex
        content = data.get('content', '')
        msg_type = data.get('msgType', 'text')
        attachment = data.get('attachment')
        target_id = data.get('targetId')

        outgoing = {
            'id': msg_id,
            'senderId': sender_id,
            'senderName': sender_name,
            'targetId': target_id,
            'content': content,
            'msgType': msg_type,
            'attachment': attachment,
            'timestamp': int(time.time()),
        }

        if target_id:
            for s in _device_sids(target_id):
                socketio.emit('recv-msg', outgoing, room=s)
            logger.info('IM private: %s -> %s [%s]', sender_name, target_id[:8], msg_type)
        else:
            other_sids = _all_sids_except(sid)
            for s in other_sids:
                socketio.emit('recv-msg', outgoing, room=s)
            logger.info('IM group: %s [%s] to %d', sender_name, msg_type, len(other_sids))

        emit('msg-sent', {'id': msg_id, 'timestamp': outgoing['timestamp']})

    @socketio.on('typing')
    def handle_typing(data):
        from flask import request as flask_request
        sid = flask_request.sid
        sender_id = data.get('from')
        target_id = data.get('to')

        if not target_id:
            for s in _all_sids_except(sid):
                socketio.emit('typing', {'from': sender_id}, room=s)
        else:
            for s in _device_sids(target_id):
                socketio.emit('typing', {'from': sender_id}, room=s)

    @socketio.on('read')
    def handle_read(data):
        reader_id = data.get('to')
        sender_id = data.get('from')
        if not reader_id or not sender_id:
            return
        for s in _device_sids(sender_id):
            socketio.emit('read', {'from': reader_id, 'to': sender_id}, room=s)

    # ------------------------------------------------------------------
    # WebRTC signaling relay — dumb forward, no payload inspection
    # ------------------------------------------------------------------
    @socketio.on('webrtc-signal')
    def handle_webrtc_signal(data):
        from flask import request as flask_request
        sid = flask_request.sid

        with _devices_lock:
            sender_id = sid_to_node.get(sid)

        if not sender_id:
            return

        target_id = data.get('targetId')
        signal = data.get('signal')
        if not target_id or not signal:
            return

        # Relay to all sessions of the target device
        for s in _device_sids(target_id):
            socketio.emit('webrtc-signal', {
                'fromId': sender_id,
                'signal': signal,
            }, room=s)
