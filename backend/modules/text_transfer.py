# backend/modules/text_transfer.py
import threading
import random
import logging
import time
from flask_socketio import emit

logger = logging.getLogger(__name__)

# --- LAN IP detection (reuses project's VPN-bypass logic) ---
_server_lan_ip = None
_server_lan_ip_lock = threading.Lock()


def _get_server_lan_ip():
    """Get the server's real LAN IP, bypassing VPN/proxy.
    Cached after first call.
    """
    global _server_lan_ip
    with _server_lan_ip_lock:
        if _server_lan_ip is not None:
            return _server_lan_ip
    import socket
    import sys
    import ipaddress

    def _is_private(ip):
        try:
            return ipaddress.ip_address(ip).is_private
        except ValueError:
            return False

    # Method 1: UDP socket — fast, works when no VPN
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        if _is_private(ip) and not ip.startswith('198.'):
            _server_lan_ip = ip
            return ip
    except Exception:
        pass

    # Method 2: Parse OS routing table (bypasses VPN/proxy)
    try:
        import subprocess
        if sys.platform == 'win32':
            out = subprocess.check_output('route print 0.0.0.0', shell=True, text=True, timeout=3)
            for line in out.splitlines():
                parts = line.split()
                if (len(parts) >= 5 and parts[0] == '0.0.0.0' and parts[1] == '0.0.0.0'
                        and parts[2] != parts[3] and _is_private(parts[2])
                        and not parts[3].startswith('198.')):
                    _server_lan_ip = parts[3]
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
                        _server_lan_ip = ip
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
                        _server_lan_ip = ip
                        return ip
    except Exception:
        pass

    # Method 3: hostname resolution
    try:
        ip = socket.gethostbyname(socket.gethostname())
        _server_lan_ip = ip
        return ip
    except Exception:
        _server_lan_ip = '127.0.0.1'
        return '127.0.0.1'


# --- Device Registry ---
connected_nodes = {}  # {nodeId: {sid, name, ip}}
_nodes_lock = threading.Lock()

ADJECTIVES = [
    '敏捷的', '勇敢的', '智慧的', '温柔的', '快乐的',
    '酷酷的', '灵巧的', '淡定的', '可爱的', '霸气的',
    '优雅的', '热情的', '安静的', '沉稳的', '呆萌的',
]

ANIMALS = [
    '猫咪', '企鹅', '狐狸', '兔子', '老虎',
    '熊猫', '海豚', '鹦鹉', '仓鼠', '考拉',
    '柴犬', '浣熊', '水獭', '猫头鹰', '龙猫',
]


def generate_name():
    return f"{random.choice(ADJECTIVES)}{random.choice(ANIMALS)}{random.randint(1, 99)}"


def get_peers_list():
    with _nodes_lock:
        return [
            {'nodeId': nid, 'name': info['name'], 'ip': info['ip']}
            for nid, info in connected_nodes.items()
        ]


def register_socketio_events(socketio):
    @socketio.on('join')
    def handle_join(data):
        from flask import request as flask_request
        sid = flask_request.sid
        node_id = data.get('nodeId')
        name = data.get('name') or generate_name()
        ip = flask_request.headers.get('X-Forwarded-For', flask_request.remote_addr or '0.0.0.0')

        lan_ip = _get_server_lan_ip()

        with _nodes_lock:
            connected_nodes[node_id] = {'sid': sid, 'name': name, 'ip': ip}

        logger.info(f'Device joined: {name} ({node_id[:8]}...) from {ip} — {len(connected_nodes)} online')

        emit('joined', {
            'nodeId': node_id,
            'name': name,
            'peers': get_peers_list(),
            'serverIp': lan_ip,
        })
        socketio.emit('peers', {'list': get_peers_list()}, skip_sid=sid)

    @socketio.on('disconnect')
    def handle_disconnect():
        from flask import request as flask_request
        sid = flask_request.sid
        disconnected_node = None
        disconnected_name = ''
        with _nodes_lock:
            for nid, info in list(connected_nodes.items()):
                if info['sid'] == sid:
                    disconnected_node = nid
                    disconnected_name = info['name']
                    del connected_nodes[nid]
                    break
        if disconnected_node:
            logger.info(f'Device left: {disconnected_name} ({disconnected_node[:8]}...) — {len(connected_nodes)} remaining')
            socketio.emit('leave', {'nodeId': disconnected_node})
            socketio.emit('peers', {'list': get_peers_list()})

    @socketio.on('rename')
    def handle_rename(data):
        from flask import request as flask_request
        sid = flask_request.sid
        node_id = data.get('nodeId')
        new_name = data.get('name', '').strip()
        if not new_name:
            return
        old_name = ''
        with _nodes_lock:
            if node_id in connected_nodes and connected_nodes[node_id]['sid'] == sid:
                old_name = connected_nodes[node_id]['name']
                connected_nodes[node_id]['name'] = new_name
        if old_name:
            logger.info(f'Renamed: {old_name} -> {new_name}')
        socketio.emit('peers', {'list': get_peers_list()})

    @socketio.on('offer-text')
    def handle_offer_text(data):
        target_id = data.get('to')
        from_id = data.get('from', '?')
        secure = data.get('secure', False)
        with _nodes_lock:
            target = connected_nodes.get(target_id)
        if target:
            mode = 'secure' if secure else 'plain'
            logger.info(f'Text ({mode}): {from_id[:8]}... -> {target["name"]}')
            socketio.emit('offer-text', data, room=target['sid'])

    @socketio.on('accept-text')
    def handle_accept_text(data):
        target_id = data.get('to')
        with _nodes_lock:
            target = connected_nodes.get(target_id)
        if target:
            socketio.emit('accept-text', data, room=target['sid'])

    @socketio.on('reject-text')
    def handle_reject_text(data):
        target_id = data.get('to')
        with _nodes_lock:
            target = connected_nodes.get(target_id)
        if target:
            socketio.emit('reject-text', data, room=target['sid'])

    @socketio.on('sdp-offer')
    def handle_sdp_offer(data):
        target_id = data.get('to')
        from_id = data.get('from', '?')
        with _nodes_lock:
            target = connected_nodes.get(target_id)
        if target:
            logger.info(f'WebRTC SDP offer: {from_id[:8]}... -> {target["name"]}')
            socketio.emit('sdp-offer', data, room=target['sid'])

    @socketio.on('sdp-answer')
    def handle_sdp_answer(data):
        target_id = data.get('to')
        with _nodes_lock:
            target = connected_nodes.get(target_id)
        if target:
            socketio.emit('sdp-answer', data, room=target['sid'])

    @socketio.on('ice-candidate')
    def handle_ice_candidate(data):
        target_id = data.get('to')
        with _nodes_lock:
            target = connected_nodes.get(target_id)
        if target:
            socketio.emit('ice-candidate', data, room=target['sid'])

    @socketio.on('chat')
    def handle_chat(data):
        from flask import request as flask_request
        sid = flask_request.sid
        data['timestamp'] = int(time.time())
        from_name = data.get('fromName', '?')
        with _nodes_lock:
            sids = [info['sid'] for info in connected_nodes.values() if info['sid'] != sid]
        logger.info(f'Group chat from {from_name} to {len(sids)} peers')
        for s in sids:
            socketio.emit('chat', data, room=s)
