# backend/modules/im.py
"""
Complete IM (Instant Messaging) module for DevToolBox.
Provides chat history persistence via SQLite, file upload with thumbnails,
message search, and SocketIO-based real-time messaging.
"""

import os
import sqlite3
import threading
import time
import uuid
import json
import logging

from flask import Blueprint, request, jsonify, send_file
from werkzeug.utils import secure_filename
from werkzeug.security import safe_join
from flask_socketio import emit

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB
THUMB_MAX_SIZE = (200, 200)

# ---------------------------------------------------------------------------
# Upload directory helpers
# ---------------------------------------------------------------------------

def _get_project_root():
    """Return the project root directory."""
    import sys
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    # This file is at backend/modules/im.py -> root is 3 levels up
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _get_upload_dir():
    """Return the IM upload directory, creating it if needed."""
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
# SQLite database
# ---------------------------------------------------------------------------
_db_path = None
_db_lock = threading.Lock()


def _get_db_path():
    """Return the SQLite database path, initialising the data directory once."""
    global _db_path
    if _db_path is not None:
        return _db_path
    root = _get_project_root()
    data_dir = os.path.join(root, 'data')
    os.makedirs(data_dir, exist_ok=True)
    _db_path = os.path.join(data_dir, 'im.db')
    return _db_path


def _get_conn():
    """Return a new sqlite3 Connection for the IM database."""
    conn = sqlite3.connect(_get_db_path(), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db():
    """Create tables if they don't exist yet."""
    conn = _get_conn()
    try:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS messages (
                id TEXT PRIMARY KEY,
                sender_id TEXT NOT NULL,
                sender_name TEXT NOT NULL,
                target_id TEXT,
                content TEXT NOT NULL,
                msg_type TEXT NOT NULL DEFAULT 'text',
                attachment TEXT,
                timestamp INTEGER NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_msg_target ON messages(target_id, timestamp);
            CREATE INDEX IF NOT EXISTS idx_msg_sender ON messages(sender_id, timestamp);

            CREATE TABLE IF NOT EXISTS devices (
                node_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                last_seen INTEGER NOT NULL
            );
        """)
        conn.commit()
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Device registry (in-memory, same pattern as text_transfer)
# ---------------------------------------------------------------------------
connected_devices = {}  # {nodeId: {sid, name, ip}}
_devices_lock = threading.Lock()


def _peers_list():
    with _devices_lock:
        return [
            {'nodeId': nid, 'name': info['name'], 'ip': info['ip']}
            for nid, info in connected_devices.items()
        ]


# ---------------------------------------------------------------------------
# Blueprint — REST endpoints
# ---------------------------------------------------------------------------
im_bp = Blueprint('im', __name__)


@im_bp.route('/upload', methods=['POST'])
def upload_file():
    """Upload a file for IM attachments.  Multipart form with 'file' field."""
    init_db()

    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file provided'}), 400

    f = request.files['file']
    if not f.filename:
        return jsonify({'success': False, 'error': 'Empty filename'}), 400

    # Size check
    f.seek(0, os.SEEK_END)
    size = f.tell()
    f.seek(0)
    if size > MAX_FILE_SIZE:
        return jsonify({'success': False, 'error': 'File too large (max 50 MB)'}), 400

    # Unique filename
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

    # Generate thumbnail for images
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

    return jsonify({
        'success': True,
        'id': file_id,
        'url': file_url,
        'filename': f.filename,
        'size': size,
        'mime': mime,
        'thumbnail': thumbnail_url,
    })


@im_bp.route('/files/<path:filename>')
def serve_file(filename):
    """Serve an uploaded file."""
    upload_dir = _get_upload_dir()
    safe_path = safe_join(upload_dir, filename)
    if safe_path is None or not os.path.isfile(safe_path):
        return jsonify({'success': False, 'error': 'File not found'}), 404
    return send_file(safe_path)


@im_bp.route('/thumbs/<path:filename>')
def serve_thumb(filename):
    """Serve a thumbnail image."""
    upload_dir = _get_upload_dir()
    thumb_name = f"thumb_{filename}.webp"
    safe_path = safe_join(upload_dir, thumb_name)
    if safe_path is None or not os.path.isfile(safe_path):
        return jsonify({'success': False, 'error': 'Thumbnail not found'}), 404
    return send_file(safe_path, mimetype='image/webp')


@im_bp.route('/history')
def get_history():
    """Get chat history.

    Query params:
        peer   — peer node_id or 'group' (default 'group')
        limit  — max messages to return (default 50, max 200)
        before — timestamp for cursor-based pagination
    """
    init_db()

    peer = request.args.get('peer', 'group')
    limit = min(int(request.args.get('limit', 50)), 200)
    before = request.args.get('before', type=int)

    conn = _get_conn()
    try:
        if peer == 'group':
            # Group messages have NULL target_id
            if before:
                rows = conn.execute(
                    "SELECT * FROM messages WHERE target_id IS NULL AND timestamp < ? ORDER BY timestamp DESC LIMIT ?",
                    (before, limit),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM messages WHERE target_id IS NULL ORDER BY timestamp DESC LIMIT ?",
                    (limit,),
                ).fetchall()
        else:
            # Private messages: either direction between current user and peer
            # We don't know who "current user" is from a pure REST call,
            # so return messages where target_id = peer (directed to that peer)
            # plus messages where sender_id = peer AND target_id != NULL (sent by peer privately)
            if before:
                rows = conn.execute(
                    """SELECT * FROM messages
                       WHERE (target_id = ? OR (sender_id = ? AND target_id IS NOT NULL))
                         AND timestamp < ?
                       ORDER BY timestamp DESC LIMIT ?""",
                    (peer, peer, before, limit),
                ).fetchall()
            else:
                rows = conn.execute(
                    """SELECT * FROM messages
                       WHERE target_id = ? OR (sender_id = ? AND target_id IS NOT NULL)
                       ORDER BY timestamp DESC LIMIT ?""",
                    (peer, peer, limit),
                ).fetchall()

        messages = []
        for r in rows:
            msg = dict(r)
            if msg.get('attachment'):
                try:
                    msg['attachment'] = json.loads(msg['attachment'])
                except (json.JSONDecodeError, TypeError):
                    pass
            messages.append(msg)

        # Return in chronological order (oldest first)
        messages.reverse()
        return jsonify({'success': True, 'messages': messages})
    except Exception as e:
        logger.error('Failed to fetch history: %s', e, exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        conn.close()


@im_bp.route('/search')
def search_messages():
    """Search messages by keyword.

    Query params:
        q     — search keyword (required)
        limit — max results (default 20, max 100)
    """
    init_db()

    q = request.args.get('q', '').strip()
    if not q:
        return jsonify({'success': False, 'error': 'Missing query parameter "q"'}), 400

    limit = min(int(request.args.get('limit', 20)), 100)

    conn = _get_conn()
    try:
        rows = conn.execute(
            "SELECT * FROM messages WHERE content LIKE ? ORDER BY timestamp DESC LIMIT ?",
            (f'%{q}%', limit),
        ).fetchall()

        messages = []
        for r in rows:
            msg = dict(r)
            if msg.get('attachment'):
                try:
                    msg['attachment'] = json.loads(msg['attachment'])
                except (json.JSONDecodeError, TypeError):
                    pass
            messages.append(msg)

        return jsonify({'success': True, 'messages': messages})
    except Exception as e:
        logger.error('Failed to search messages: %s', e, exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# SocketIO event registration
# ---------------------------------------------------------------------------

def register_im_events(socketio):
    """Register all IM-related SocketIO events on the given socketio instance."""
    init_db()

    @socketio.on('join')
    def handle_join(data):
        from flask import request as flask_request
        sid = flask_request.sid
        node_id = data.get('nodeId')
        name = data.get('name', '').strip() or f'Device-{node_id[:6]}'
        ip = flask_request.headers.get('X-Forwarded-For', flask_request.remote_addr or '0.0.0.0')

        with _devices_lock:
            connected_devices[node_id] = {'sid': sid, 'name': name, 'ip': ip}

        # Update / create device row for last_seen
        now = int(time.time())
        conn = _get_conn()
        try:
            # Fetch previous last_seen before updating
            row = conn.execute("SELECT last_seen FROM devices WHERE node_id = ?", (node_id,)).fetchone()
            prev_last_seen = row['last_seen'] if row else 0

            conn.execute(
                "INSERT INTO devices (node_id, name, last_seen) VALUES (?, ?, ?) "
                "ON CONFLICT(node_id) DO UPDATE SET name=?, last_seen=?",
                (node_id, name, now, name, now),
            )
            conn.commit()
        finally:
            conn.close()

        # Collect unread messages (messages targeting this device since its last_seen)
        unread = []
        if prev_last_seen:
            conn = _get_conn()
            try:
                rows = conn.execute(
                    "SELECT * FROM messages WHERE target_id = ? AND timestamp > ? ORDER BY timestamp ASC",
                    (node_id, prev_last_seen),
                ).fetchall()
                for r in rows:
                    msg = dict(r)
                    if msg.get('attachment'):
                        try:
                            msg['attachment'] = json.loads(msg['attachment'])
                        except (json.JSONDecodeError, TypeError):
                            pass
                    unread.append(msg)
            finally:
                conn.close()

        logger.info('IM join: %s (%s) from %s — %d devices online, %d unread',
                     name, node_id[:8], ip, len(connected_devices), len(unread))

        emit('joined', {
            'nodeId': node_id,
            'name': name,
            'peers': _peers_list(),
            'unreadMessages': unread,
        })
        socketio.emit('peers', {'list': _peers_list()}, skip_sid=sid)

    @socketio.on('disconnect')
    def handle_disconnect():
        from flask import request as flask_request
        sid = flask_request.sid
        disconnected_node = None
        disconnected_name = ''
        with _devices_lock:
            for nid, info in list(connected_devices.items()):
                if info['sid'] == sid:
                    disconnected_node = nid
                    disconnected_name = info['name']
                    del connected_devices[nid]
                    break
        if disconnected_node:
            logger.info('IM leave: %s (%s) — %d remaining',
                        disconnected_name, disconnected_node[:8], len(connected_devices))
            socketio.emit('leave', {'nodeId': disconnected_node})
            socketio.emit('peers', {'list': _peers_list()})

    @socketio.on('rename')
    def handle_rename(data):
        from flask import request as flask_request
        sid = flask_request.sid
        node_id = data.get('nodeId')
        new_name = data.get('name', '').strip()
        if not new_name:
            return
        old_name = ''
        with _devices_lock:
            if node_id in connected_devices and connected_devices[node_id]['sid'] == sid:
                old_name = connected_devices[node_id]['name']
                connected_devices[node_id]['name'] = new_name
        if old_name:
            logger.info('IM rename: %s -> %s', old_name, new_name)
            # Persist name change
            conn = _get_conn()
            try:
                conn.execute("UPDATE devices SET name=? WHERE node_id=?", (new_name, node_id))
                conn.commit()
            finally:
                conn.close()
        socketio.emit('peers', {'list': _peers_list()})

    @socketio.on('send-msg')
    def handle_send_msg(data):
        from flask import request as flask_request
        sid = flask_request.sid
        now = int(time.time())

        # Identify sender
        sender_id = None
        sender_name = '?'
        with _devices_lock:
            for nid, info in connected_devices.items():
                if info['sid'] == sid:
                    sender_id = nid
                    sender_name = info['name']
                    break

        if sender_id is None:
            emit('msg-error', {'error': 'Not registered'})
            return

        msg_id = data.get('id') or uuid.uuid4().hex
        content = data.get('content', '')
        msg_type = data.get('msgType', 'text')
        attachment = data.get('attachment')
        target_id = data.get('targetId')  # None for group chat

        # Serialise attachment as JSON string for storage
        attachment_json = json.dumps(attachment) if attachment else None

        # Persist to SQLite
        conn = _get_conn()
        try:
            conn.execute(
                "INSERT INTO messages (id, sender_id, sender_name, target_id, content, msg_type, attachment, timestamp) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (msg_id, sender_id, sender_name, target_id, content, msg_type, attachment_json, now),
            )
            conn.commit()
        finally:
            conn.close()

        outgoing = {
            'id': msg_id,
            'senderId': sender_id,
            'senderName': sender_name,
            'targetId': target_id,
            'content': content,
            'msgType': msg_type,
            'attachment': attachment,
            'timestamp': now,
        }

        if target_id:
            # Private message — forward to target peer only
            with _devices_lock:
                target_info = connected_devices.get(target_id)
            if target_info:
                socketio.emit('recv-msg', outgoing, room=target_info['sid'])
                logger.info('IM private: %s -> %s [%s]', sender_name, target_id[:8], msg_type)
            else:
                logger.info('IM private: %s -> %s (offline) [%s]', sender_name, target_id[:8], msg_type)
        else:
            # Group message — broadcast to all except sender
            with _devices_lock:
                sids = [info['sid'] for info in connected_devices.values() if info['sid'] != sid]
            logger.info('IM group: %s [%s] to %d peers', sender_name, msg_type, len(sids))
            for s in sids:
                socketio.emit('recv-msg', outgoing, room=s)

        # Acknowledge to sender
        emit('msg-sent', {
            'id': msg_id,
            'timestamp': now,
        })

    @socketio.on('typing')
    def handle_typing(data):
        from flask import request as flask_request
        sid = flask_request.sid
        sender_id = data.get('from')
        target_id = data.get('to')

        if not target_id:
            # Group typing — broadcast to everyone else
            with _devices_lock:
                sids = [info['sid'] for info in connected_devices.values() if info['sid'] != sid]
            for s in sids:
                socketio.emit('typing', {'from': sender_id}, room=s)
        else:
            # Private typing — forward to target
            with _devices_lock:
                target_info = connected_devices.get(target_id)
            if target_info:
                socketio.emit('typing', {'from': sender_id}, room=target_info['sid'])

    @socketio.on('read')
    def handle_read(data):
        """Mark messages as read and notify the original sender.

        Expected data: { from: <senderNodeId>, to: <readerNodeId> }
        The reader tells the server that they have read messages from 'from'.
        """
        reader_id = data.get('to')  # who is reading
        sender_id = data.get('from')  # whose messages were read

        if not reader_id or not sender_id:
            return

        now = int(time.time())

        # Update last_seen for the reader
        conn = _get_conn()
        try:
            conn.execute(
                "UPDATE devices SET last_seen=? WHERE node_id=?",
                (now, reader_id),
            )
            conn.commit()
        finally:
            conn.close()

        # Notify the original sender that their messages were read
        with _devices_lock:
            sender_info = connected_devices.get(sender_id)
        if sender_info:
            socketio.emit('read', {'from': reader_id, 'to': sender_id}, room=sender_info['sid'])
