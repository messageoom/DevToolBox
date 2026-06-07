# backend/modules/text_transfer.py
import threading
import random
from flask_socketio import emit

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

        with _nodes_lock:
            connected_nodes[node_id] = {'sid': sid, 'name': name, 'ip': ip}

        emit('joined', {
            'nodeId': node_id,
            'name': name,
            'peers': get_peers_list(),
        })
        socketio.emit('peers', {'list': get_peers_list()}, skip_sid=sid)

    @socketio.on('disconnect')
    def handle_disconnect():
        from flask import request as flask_request
        sid = flask_request.sid
        disconnected_node = None
        with _nodes_lock:
            for nid, info in list(connected_nodes.items()):
                if info['sid'] == sid:
                    disconnected_node = nid
                    del connected_nodes[nid]
                    break
        if disconnected_node:
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
        with _nodes_lock:
            if node_id in connected_nodes and connected_nodes[node_id]['sid'] == sid:
                connected_nodes[node_id]['name'] = new_name
        socketio.emit('peers', {'list': get_peers_list()})

    @socketio.on('offer-text')
    def handle_offer_text(data):
        target_id = data.get('to')
        with _nodes_lock:
            target = connected_nodes.get(target_id)
        if target:
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
        with _nodes_lock:
            target = connected_nodes.get(target_id)
        if target:
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
        import time
        data['timestamp'] = int(time.time())
        with _nodes_lock:
            sids = [info['sid'] for info in connected_nodes.values() if info['sid'] != sid]
        for s in sids:
            socketio.emit('chat', data, room=s)
