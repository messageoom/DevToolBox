# Text Transfer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add LAN text transfer to DevToolBox using WebSocket signaling + WebRTC P2P, with an IM-style chat UI.

**Architecture:** Flask-SocketIO handles signaling (device discovery, SDP/ICE exchange, chat relay). WebRTC DataChannel provides E2E-encrypted P2P text delivery. Frontend is a single `TextTransfer.vue` page with a composable `useTextTransfer.js` encapsulating all real-time logic.

**Tech Stack:** Flask-SocketIO (Python), socket.io-client + WebRTC API (browser-native, no npm WebRTC lib needed)

---

## File Structure

**New files:**
- `backend/modules/text_transfer.py` — SocketIO event handlers, device registry, name generator
- `frontend/src/views/TextTransfer.vue` — IM-style dual-panel chat page
- `frontend/src/composables/useTextTransfer.js` — SocketIO client + WebRTC + state management

**Modified files:**
- `backend/app.py` — Initialize SocketIO, register text_transfer events
- `requirements.txt` — Add flask-socketio, python-engineio
- `frontend/package.json` — Add socket.io-client (via npm install)
- `frontend/src/router/index.js` — Add /text-transfer route
- `frontend/src/App.vue` — Add sidebar entry, mobile nav entry, import ChatDotRound icon
- `frontend/src/data/toolCategories.js` — Add transfer category
- `frontend/src/locales/zh.json` — Add i18n keys
- `frontend/src/locales/en.json` — Add i18n keys

---

### Task 1: Install Dependencies

**Files:**
- Modify: `requirements.txt`
- Modify: `frontend/package.json` (via npm)

- [ ] **Step 1: Add Python dependencies**

Append to `requirements.txt`:

```
Flask-SocketIO==5.3.6
python-engineio==4.9.0
```

- [ ] **Step 2: Install Python dependencies**

Run: `pip install Flask-SocketIO==5.3.6 python-engineio==4.9.0`
Expected: Successfully installed

- [ ] **Step 3: Install socket.io-client**

Run: `cd frontend && npm install socket.io-client@4.7.5`
Expected: added 1 package

- [ ] **Step 4: Commit**

```bash
git add requirements.txt frontend/package.json frontend/package-lock.json
git commit -m "chore: add flask-socketio and socket.io-client dependencies"
```

---

### Task 2: Backend — Device Registry and Name Generator

**Files:**
- Create: `backend/modules/text_transfer.py`

- [ ] **Step 1: Create text_transfer.py with device registry and name generator**

```python
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
        from flask import request as flask_request
        data['from'] = data.get('from')
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
```

- [ ] **Step 2: Commit**

```bash
git add backend/modules/text_transfer.py
git commit -m "feat(text-transfer): add backend signaling with device registry"
```

---

### Task 3: Backend — Integrate SocketIO into Flask App

**Files:**
- Modify: `backend/app.py`

- [ ] **Step 1: Add SocketIO imports and initialization in create_app()**

At the top of `backend/app.py`, add import after the existing imports (after line 57):

```python
try:
    from flask_socketio import SocketIO
except ImportError:
    SocketIO = None
```

Inside `create_app()`, after the `CORS(...)` call (after line 86) and before `@app.before_request`, add:

```python
    # SocketIO initialization
    socketio = None
    if SocketIO is not None:
        socketio = SocketIO(
            app,
            cors_allowed_origins=allowed_origins,
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
```

- [ ] **Step 2: Update the app runner at the bottom of app.py**

Replace the last block (lines 229-231):

```python
    if not access_token:
        # Dev mode: no token, no gui, no tray
        debug = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
        app.run(host=host, port=port, debug=debug)
```

With:

```python
    if not access_token:
        # Dev mode: no token, no gui, no tray
        debug = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
        socketio = app.config.get('SOCKETIO')
        if socketio:
            socketio.run(app, host=host, port=port, debug=debug, allow_unsafe_werkzeug=True)
        else:
            app.run(host=host, port=port, debug=debug)
```

- [ ] **Step 3: Also update the tray/console runners to use socketio**

In the tray/console app runner paths, the `run_gui_app` and `run_tray_app`/`run_console_app` functions likely call `app.run()` internally. We need to pass `socketio` through so they can use `socketio.run()` instead. Find where those utility functions are defined and check if they already support this, or add the socketio reference to app config (which we already do above) so they can detect it.

For now, since `app.config['SOCKETIO']` is set, the tray/console utilities can access it. We'll handle this in integration testing.

- [ ] **Step 4: Commit**

```bash
git add backend/app.py
git commit -m "feat(text-transfer): integrate Flask-SocketIO into create_app"
```

---

### Task 4: Frontend — useTextTransfer Composable

**Files:**
- Create: `frontend/src/composables/useTextTransfer.js`

- [ ] **Step 1: Create the composable**

```javascript
// frontend/src/composables/useTextTransfer.js
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { io } from 'socket.io-client'

const HISTORY_KEY = 'text-transfer-history'
const MAX_HISTORY = 200
const IDENTITY_KEY = 'landrop_identity'

function generateId() {
  return Math.random().toString(36).substring(2) + Date.now().toString(36)
}

function loadHistory() {
  try {
    const raw = localStorage.getItem(HISTORY_KEY)
    return raw ? JSON.parse(raw) : []
  } catch { return [] }
}

function saveHistory(items) {
  const trimmed = items.slice(-MAX_HISTORY)
  localStorage.setItem(HISTORY_KEY, JSON.stringify(trimmed))
}

function detectType(text) {
  if (!text) return 'text'
  const trimmed = text.trim()
  if (/^https?:\/\//.test(trimmed)) return 'url'
  if (/[{}\[\];]/.test(trimmed) && trimmed.split('\n').length > 3) return 'code'
  return 'text'
}

export function useTextTransfer() {
  // --- Identity ---
  const myId = ref('')
  const myName = ref('')

  function loadIdentity() {
    try {
      const raw = sessionStorage.getItem(IDENTITY_KEY)
      if (raw) {
        const parsed = JSON.parse(raw)
        myId.value = parsed.nodeId || generateId()
        myName.value = parsed.name || ''
        return
      }
    } catch {}
    myId.value = generateId()
  }

  function saveIdentity() {
    sessionStorage.setItem(IDENTITY_KEY, JSON.stringify({
      nodeId: myId.value,
      name: myName.value,
    }))
  }

  // --- State ---
  const connected = ref(false)
  const peers = ref([])
  const activePeer = ref(null)  // { nodeId, name, ip } or null (group chat)
  const messages = ref({})  // { peerId: [msg, ...] }  -- 'group' key for group chat
  const history = ref(loadHistory())
  const sending = ref(false)

  // --- SocketIO ---
  let socket = null

  function connect() {
    if (socket?.connected) return
    loadIdentity()

    const protocol = window.location.protocol === 'https:' ? 'https:' : 'http:'
    const url = `${protocol}//${window.location.hostname}:${window.location.port || (window.location.protocol === 'https:' ? '443' : '80')}`

    socket = io(url, {
      transports: ['websocket', 'polling'],
      reconnection: true,
      reconnectionAttempts: Infinity,
      reconnectionDelay: 1000,
    })

    socket.on('connect', () => {
      connected.value = true
      socket.emit('join', { nodeId: myId.value, name: myName.value })
    })

    socket.on('disconnect', () => {
      connected.value = false
    })

    socket.on('joined', (data) => {
      myId.value = data.nodeId
      myName.value = data.name
      saveIdentity()
      peers.value = data.peers.filter(p => p.nodeId !== myId.value)
    })

    socket.on('peers', (data) => {
      peers.value = (data.list || []).filter(p => p.nodeId !== myId.value)
    })

    socket.on('leave', (data) => {
      peers.value = peers.value.filter(p => p.nodeId !== data.nodeId)
      if (activePeer.value?.nodeId === data.nodeId) {
        activePeer.value = null
      }
    })

    socket.on('offer-text', (data) => {
      // Incoming text from peer
      const peerId = data.from
      const peerInfo = peers.value.find(p => p.nodeId === peerId)
      const peerName = peerInfo?.name || peerId
      const msg = {
        id: generateId(),
        peerId,
        peerName,
        direction: 'received',
        content: data.content,
        timestamp: Date.now(),
        secure: data.secure || false,
        type: detectType(data.content),
      }
      if (!messages.value[peerId]) messages.value[peerId] = []
      messages.value[peerId].push(msg)
      history.value.push({ ...msg })
      saveHistory(history.value)
    })

    socket.on('chat', (data) => {
      const peerId = data.from
      const peerName = data.fromName || peerId
      const msg = {
        id: generateId(),
        peerId,
        peerName,
        direction: 'received',
        content: data.content,
        timestamp: data.timestamp ? data.timestamp * 1000 : Date.now(),
        secure: false,
        type: 'group',
      }
      if (!messages.value['group']) messages.value['group'] = []
      messages.value['group'].push(msg)
      history.value.push({ ...msg })
      saveHistory(history.value)
    })

    socket.on('sdp-offer', async (data) => {
      await handleRemoteSdpOffer(data)
    })

    socket.on('sdp-answer', async (data) => {
      await handleRemoteSdpAnswer(data)
    })

    socket.on('ice-candidate', (data) => {
      handleRemoteIceCandidate(data)
    })
  }

  function disconnect() {
    if (socket) {
      socket.disconnect()
      socket = null
    }
    connected.value = false
  }

  // --- Sending ---
  function sendText(content, targetPeer, secure = false) {
    if (!content.trim() || !socket?.connected) return

    const isGroup = !targetPeer
    const peerName = targetPeer?.name || ''
    const peerId = targetPeer?.nodeId || 'group'

    const msg = {
      id: generateId(),
      peerId,
      peerName,
      direction: 'sent',
      content,
      timestamp: Date.now(),
      secure,
      type: isGroup ? 'group' : detectType(content),
    }

    if (!messages.value[peerId]) messages.value[peerId] = []
    messages.value[peerId].push(msg)
    history.value.push({ ...msg })
    saveHistory(history.value)

    if (isGroup) {
      socket.emit('chat', { content, from: myId.value, fromName: myName.value })
    } else {
      socket.emit('offer-text', {
        to: targetPeer.nodeId,
        from: myId.value,
        content,
        secure,
      })
    }
  }

  // --- WebRTC (E2E) ---
  const rtcConfig = { iceServers: [] }
  let pendingConnections = {}  // { peerId: RTCPeerConnection }

  async function handleRemoteSdpOffer(data) {
    const fromId = data.from
    const pc = new RTCPeerConnection(rtcConfig)
    pendingConnections[fromId] = pc

    pc.ondatachannel = (e) => {
      const dc = e.channel
      dc.onmessage = (ev) => {
        try {
          const payload = JSON.parse(ev.data)
          if (payload.type === 'text') {
            const peerInfo = peers.value.find(p => p.nodeId === fromId)
            const msg = {
              id: generateId(),
              peerId: fromId,
              peerName: peerInfo?.name || fromId,
              direction: 'received',
              content: payload.content,
              timestamp: Date.now(),
              secure: true,
              type: detectType(payload.content),
            }
            if (!messages.value[fromId]) messages.value[fromId] = []
            messages.value[fromId].push(msg)
            history.value.push({ ...msg })
            saveHistory(history.value)
            dc.send(JSON.stringify({ type: 'received' }))
          }
        } catch {}
      }
    }

    pc.onicecandidate = (e) => {
      if (e.candidate) {
        socket.emit('ice-candidate', { to: fromId, from: myId.value, candidate: e.candidate })
      }
    }

    await pc.setRemoteDescription(new RTCSessionDescription(data.sdp))
    const answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)
    socket.emit('sdp-answer', { to: fromId, from: myId.value, sdp: answer })

    setTimeout(() => { delete pendingConnections[fromId] }, 30000)
  }

  async function handleRemoteSdpAnswer(data) {
    const pc = pendingConnections[data.from]
    if (pc) {
      await pc.setRemoteDescription(new RTCSessionDescription(data.sdp))
    }
  }

  function handleRemoteIceCandidate(data) {
    const pc = pendingConnections[data.from]
    if (pc && data.candidate) {
      pc.addIceCandidate(new RTCIceCandidate(data.candidate))
    }
  }

  // --- Rename ---
  function rename(newName) {
    myName.value = newName
    saveIdentity()
    socket?.emit('rename', { nodeId: myId.value, name: newName })
  }

  // --- Selection ---
  const activeMessages = computed(() => {
    if (!activePeer.value) return messages.value['group'] || []
    return messages.value[activePeer.value.nodeId] || []
  })

  function selectPeer(peer) {
    activePeer.value = peer
  }

  function selectGroupChat() {
    activePeer.value = null
  }

  // --- Lifecycle ---
  onMounted(() => connect())
  onBeforeUnmount(() => disconnect())

  return {
    myId,
    myName,
    connected,
    peers,
    activePeer,
    activeMessages,
    history,
    sending,
    sendText,
    rename,
    selectPeer,
    selectGroupChat,
    connect,
    disconnect,
  }
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/composables/useTextTransfer.js
git commit -m "feat(text-transfer): add useTextTransfer composable with SocketIO + WebRTC"
```

---

### Task 5: Frontend — TextTransfer Vue Page

**Files:**
- Create: `frontend/src/views/TextTransfer.vue`

- [ ] **Step 1: Create the TextTransfer.vue page**

```vue
<template>
  <ToolPage :title="t('tools.transfer.title')" :icon="ChatDotRound">
    <div class="transfer-container" :class="{ 'transfer-mobile': deviceStore.isMobile }">
      <!-- Mobile: horizontal device strip -->
      <div v-if="deviceStore.isMobile" class="mobile-device-strip">
        <div
          v-for="peer in peers"
          :key="peer.nodeId"
          class="mobile-device-avatar"
          :class="{ active: activePeer?.nodeId === peer.nodeId }"
          @click="selectPeer(peer)"
        >
          <div class="avatar-circle" :style="{ background: getAvatarColor(peer.nodeId) }">
            {{ peer.name.charAt(0) }}
          </div>
        </div>
        <div
          class="mobile-device-avatar"
          :class="{ active: !activePeer }"
          @click="selectGroupChat()"
        >
          <div class="avatar-circle avatar-group">#</div>
        </div>
      </div>

      <!-- Desktop: left panel -->
      <div v-if="!deviceStore.isMobile" class="transfer-sidebar">
        <div class="sidebar-header">
          <span class="sidebar-title">{{ t('tools.transfer.onlineDevices') }}</span>
          <span class="peer-count">{{ peers.length }}</span>
          <span class="connect-dot" :class="{ on: connected }"></span>
        </div>
        <div class="peer-list">
          <div
            v-for="peer in peers"
            :key="peer.nodeId"
            class="peer-item"
            :class="{ active: activePeer?.nodeId === peer.nodeId }"
            @click="selectPeer(peer)"
          >
            <div class="avatar-circle" :style="{ background: getAvatarColor(peer.nodeId) }">
              {{ peer.name.charAt(0) }}
            </div>
            <div class="peer-info">
              <div class="peer-name">{{ peer.name }}</div>
              <div class="peer-ip">{{ peer.ip }}</div>
            </div>
            <div class="online-dot"></div>
          </div>
          <div v-if="peers.length === 0" class="empty-peers">
            {{ t('tools.transfer.noDevices') }}
          </div>
        </div>
        <div class="group-chat-entry" :class="{ active: !activePeer }" @click="selectGroupChat()">
          <div class="avatar-circle avatar-group">#</div>
          <div class="peer-info">
            <div class="peer-name">{{ t('tools.transfer.groupChat') }}</div>
            <div class="peer-ip">{{ t('tools.transfer.memberCount', { count: peers.length + 1 }) }}</div>
          </div>
        </div>
      </div>

      <!-- Right panel: chat area -->
      <div class="transfer-chat">
        <!-- Chat header -->
        <div class="chat-header">
          <template v-if="activePeer">
            <div class="avatar-circle small" :style="{ background: getAvatarColor(activePeer.nodeId) }">
              {{ activePeer.name.charAt(0) }}
            </div>
            <span class="chat-target-name">{{ activePeer.name }}</span>
          </template>
          <template v-else>
            <div class="avatar-circle small avatar-group">#</div>
            <span class="chat-target-name">{{ t('tools.transfer.groupChat') }}</span>
          </template>
        </div>

        <!-- Messages -->
        <div class="chat-messages" ref="messagesContainer">
          <div v-if="activeMessages.length === 0" class="empty-messages">
            {{ t('tools.transfer.noMessages') }}
          </div>
          <div
            v-for="msg in activeMessages"
            :key="msg.id"
            class="message-row"
            :class="{ 'message-sent': msg.direction === 'sent', 'message-received': msg.direction === 'received' }"
          >
            <div class="message-bubble" :class="{ 'bubble-sent': msg.direction === 'sent', 'bubble-received': msg.direction === 'received' }">
              <div v-if="msg.direction === 'received'" class="message-sender">{{ msg.peerName }}</div>
              <div v-if="msg.type === 'code'" class="message-code">
                <pre><code>{{ msg.content }}</code></pre>
              </div>
              <div v-else class="message-text">{{ msg.content }}</div>
              <div class="message-meta">
                <span class="message-time">{{ formatTime(msg.timestamp) }}</span>
                <span v-if="msg.secure" class="secure-badge">E2E</span>
                <span v-if="msg.direction === 'sent'" class="sent-check">✓✓</span>
              </div>
            </div>
            <el-button
              v-if="msg.direction === 'received'"
              class="copy-btn"
              link
              size="small"
              @click="copyText(msg.content)"
            >
              {{ t('common.copy') }}
            </el-button>
          </div>
        </div>

        <!-- Input area -->
        <div class="chat-input">
          <el-input
            v-model="inputText"
            type="textarea"
            :autosize="{ minRows: 1, maxRows: 6 }"
            :placeholder="t('tools.transfer.inputPlaceholder')"
            @keydown.enter.exact.prevent="handleSend"
          />
          <div class="input-actions">
            <el-switch
              v-model="useEncryption"
              active-text="🔒"
              inactive-text=""
              inline-prompt
              size="small"
            />
            <el-button
              type="primary"
              :loading="sending"
              :disabled="!inputText.trim()"
              @click="handleSend"
            >
              {{ t('tools.transfer.send') }}
            </el-button>
          </div>
        </div>
      </div>
    </div>
  </ToolPage>
</template>

<script setup>
import { ref, nextTick, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import { ChatDotRound } from '@element-plus/icons-vue'
import { useDeviceStore } from '@/stores/device.js'
import { useTextTransfer } from '@/composables/useTextTransfer.js'

const { t } = useI18n()
const deviceStore = useDeviceStore()

const {
  myName,
  connected,
  peers,
  activePeer,
  activeMessages,
  sending,
  sendText,
  rename,
  selectPeer,
  selectGroupChat,
} = useTextTransfer()

const inputText = ref('')
const useEncryption = ref(false)
const messagesContainer = ref(null)

const AVATAR_COLORS = [
  '#7c3aed', '#4f46e5', '#0891b2', '#059669',
  '#d97706', '#dc2626', '#db2777', '#7c3aed',
]

function getAvatarColor(id) {
  let hash = 0
  for (let i = 0; i < id.length; i++) hash = id.charCodeAt(i) + ((hash << 5) - hash)
  return AVATAR_COLORS[Math.abs(hash) % AVATAR_COLORS.length]
}

function formatTime(ts) {
  const d = new Date(ts)
  return `${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2, '0')}`
}

function copyText(text) {
  navigator.clipboard.writeText(text).then(() => {
    ElMessage.success(t('common.copySuccess'))
  })
}

function handleSend() {
  if (!inputText.value.trim()) return
  sendText(inputText.value, activePeer.value, useEncryption.value)
  inputText.value = ''
  nextTick(scrollToBottom)
}

function scrollToBottom() {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

watch(activeMessages, () => nextTick(scrollToBottom), { deep: true })
</script>

<style scoped>
.transfer-container {
  display: flex;
  height: calc(100vh - 160px);
  min-height: 400px;
  border: 1px solid var(--dt-border-light);
  border-radius: var(--dt-radius-md);
  overflow: hidden;
  background: var(--dt-bg-card);
}

.transfer-mobile {
  flex-direction: column;
  height: calc(100vh - 140px);
}

/* === Mobile device strip === */
.mobile-device-strip {
  display: flex;
  gap: var(--dt-spacing-sm);
  padding: var(--dt-spacing-sm);
  border-bottom: 1px solid var(--dt-border-light);
  overflow-x: auto;
  background: var(--dt-bg-section);
}

.mobile-device-avatar {
  cursor: pointer;
  flex-shrink: 0;
  opacity: 0.6;
  transition: opacity 0.2s;
}

.mobile-device-avatar.active {
  opacity: 1;
}

/* === Left sidebar (desktop) === */
.transfer-sidebar {
  width: 280px;
  min-width: 280px;
  border-right: 1px solid var(--dt-border-light);
  display: flex;
  flex-direction: column;
  background: var(--dt-bg-section);
}

.sidebar-header {
  padding: var(--dt-spacing-md);
  border-bottom: 1px solid var(--dt-border-light);
  display: flex;
  align-items: center;
  gap: var(--dt-spacing-sm);
}

.sidebar-title {
  font-weight: 600;
  font-size: var(--dt-font-size-sm);
  color: var(--dt-text-primary);
}

.peer-count {
  font-size: var(--dt-font-size-xs);
  color: var(--dt-primary);
  background: var(--dt-primary-light);
  padding: 1px 6px;
  border-radius: 10px;
}

.connect-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--dt-danger);
  margin-left: auto;
  transition: background 0.3s;
}

.connect-dot.on {
  background: var(--dt-success);
}

/* === Peer list === */
.peer-list {
  flex: 1;
  overflow-y: auto;
  padding: var(--dt-spacing-xs);
}

.peer-item {
  display: flex;
  align-items: center;
  gap: var(--dt-spacing-sm);
  padding: var(--dt-spacing-sm);
  border-radius: var(--dt-radius-sm);
  cursor: pointer;
  transition: background 0.15s;
  border-left: 3px solid transparent;
}

.peer-item:hover {
  background: var(--dt-bg-hover);
}

.peer-item.active {
  background: var(--dt-primary-light);
  border-left-color: var(--dt-primary);
}

.group-chat-entry {
  display: flex;
  align-items: center;
  gap: var(--dt-spacing-sm);
  padding: var(--dt-spacing-sm);
  border-top: 1px solid var(--dt-border-light);
  cursor: pointer;
  border-left: 3px solid transparent;
  transition: background 0.15s;
}

.group-chat-entry:hover {
  background: var(--dt-bg-hover);
}

.group-chat-entry.active {
  background: var(--dt-primary-light);
  border-left-color: var(--dt-primary);
}

.avatar-circle {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 14px;
  font-weight: 600;
  flex-shrink: 0;
}

.avatar-circle.small {
  width: 28px;
  height: 28px;
  font-size: 12px;
}

.avatar-circle.mobile-avatar {
  width: 32px;
  height: 32px;
  font-size: 12px;
}

.avatar-group {
  background: linear-gradient(135deg, var(--dt-primary), #a855f7) !important;
}

.peer-info {
  flex: 1;
  min-width: 0;
}

.peer-name {
  font-size: var(--dt-font-size-sm);
  font-weight: 500;
  color: var(--dt-text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.peer-ip {
  font-size: var(--dt-font-size-xs);
  color: var(--dt-text-secondary);
}

.online-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--dt-success);
  flex-shrink: 0;
}

.empty-peers {
  text-align: center;
  color: var(--dt-text-secondary);
  font-size: var(--dt-font-size-sm);
  padding: var(--dt-spacing-xl);
}

/* === Chat area === */
.transfer-chat {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.chat-header {
  padding: var(--dt-spacing-sm) var(--dt-spacing-md);
  border-bottom: 1px solid var(--dt-border-light);
  display: flex;
  align-items: center;
  gap: var(--dt-spacing-sm);
  background: var(--dt-bg-card);
}

.chat-target-name {
  font-weight: 600;
  font-size: var(--dt-font-size-sm);
  color: var(--dt-text-primary);
}

/* === Messages === */
.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: var(--dt-spacing-md);
  display: flex;
  flex-direction: column;
  gap: var(--dt-spacing-sm);
  background: var(--dt-bg-page);
}

.empty-messages {
  text-align: center;
  color: var(--dt-text-secondary);
  font-size: var(--dt-font-size-sm);
  padding-top: var(--dt-spacing-2xl);
}

.message-row {
  display: flex;
  align-items: flex-end;
  gap: var(--dt-spacing-xs);
}

.message-sent {
  flex-direction: row-reverse;
}

.message-bubble {
  max-width: 70%;
  padding: var(--dt-spacing-sm) var(--dt-spacing-md);
  border-radius: 12px;
  font-size: var(--dt-font-size-sm);
  line-height: 1.5;
  word-break: break-word;
}

.bubble-sent {
  background: var(--dt-primary);
  color: #fff;
  border-bottom-right-radius: 4px;
}

.bubble-received {
  background: var(--dt-bg-card);
  color: var(--dt-text-primary);
  border: 1px solid var(--dt-border-lighter);
  border-bottom-left-radius: 4px;
}

.message-sender {
  font-size: var(--dt-font-size-xs);
  color: var(--dt-text-secondary);
  margin-bottom: 2px;
}

.message-text {
  white-space: pre-wrap;
}

.message-code {
  background: rgba(0, 0, 0, 0.05);
  border-radius: var(--dt-radius-sm);
  padding: var(--dt-spacing-sm);
  overflow-x: auto;
}

.message-code pre {
  margin: 0;
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: var(--dt-font-size-xs);
  line-height: 1.4;
}

.message-code code {
  font-family: inherit;
}

.message-meta {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 2px;
}

.message-time {
  font-size: 10px;
  opacity: 0.6;
}

.secure-badge {
  font-size: 10px;
  background: rgba(124, 58, 237, 0.2);
  color: #7c3aed;
  padding: 0 4px;
  border-radius: 4px;
}

.sent-check {
  font-size: 10px;
  opacity: 0.6;
}

.copy-btn {
  opacity: 0;
  transition: opacity 0.15s;
  flex-shrink: 0;
}

.message-row:hover .copy-btn {
  opacity: 1;
}

/* === Input area === */
.chat-input {
  padding: var(--dt-spacing-sm) var(--dt-spacing-md);
  border-top: 1px solid var(--dt-border-light);
  background: var(--dt-bg-card);
}

.input-actions {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: var(--dt-spacing-sm);
  margin-top: var(--dt-spacing-sm);
}
</style>
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/views/TextTransfer.vue
git commit -m "feat(text-transfer): add TextTransfer page with IM-style chat UI"
```

---

### Task 6: Frontend — Router and Navigation Integration

**Files:**
- Modify: `frontend/src/router/index.js`
- Modify: `frontend/src/App.vue`
- Modify: `frontend/src/data/toolCategories.js`

- [ ] **Step 1: Add route to router/index.js**

Add a new lazy import after the DiffTool import (around line 29):

```javascript
const TextTransfer = () => import(/* webpackChunkName: "transfer-tools" */ '../views/TextTransfer.vue')
```

Add route entry in the routes array (before the closing `]`):

```javascript
  { path: '/text-transfer', name: 'TextTransfer', component: TextTransfer },
```

- [ ] **Step 2: Add sidebar entry in App.vue**

In the `categoryToolMap` computed (around line 159), add a new category after `generator`:

```javascript
    transfer: [
      { label: t('sidebar.textTransfer'), route: '/text-transfer' },
    ],
```

In the imports at top of `<script setup>`, add `ChatDotRound` to the icon imports:

```javascript
import {
  HomeFilled,
  FolderOpened,
  DocumentCopy,
  Key,
  Lock,
  Clock,
  Expand,
  Fold,
  Crop,
  MagicStick,
  Upload,
  Grid,
  ChatDotRound,
} from '@element-plus/icons-vue'
```

In the `getIcon` function, add `ChatDotRound` to the map:

```javascript
function getIcon(iconName) {
  const iconMap = {
    FolderOpened,
    DocumentCopy,
    Key,
    Lock,
    Clock,
    Crop,
    ChatDotRound,
  }
  return iconMap[iconName] || DocumentCopy
}
```

In the `mobileNavTabs` computed, add a new tab entry (after the `qr` tab):

```javascript
  { label: t('mobileNav.transfer'), route: '/text-transfer', icon: ChatDotRound, matchPrefix: '/text-transfer' },
```

- [ ] **Step 3: Add category entry in toolCategories.js**

Add a new category to the `toolCategories` array:

```javascript
  {
    id: 'transfer',
    icon: 'ChatDotRound',
    route: '/text-transfer',
    tools: ['textTransfer']
  }
```

- [ ] **Step 4: Commit**

```bash
git add frontend/src/router/index.js frontend/src/App.vue frontend/src/data/toolCategories.js
git commit -m "feat(text-transfer): add route, sidebar, and navigation entries"
```

---

### Task 7: Frontend — i18n

**Files:**
- Modify: `frontend/src/locales/zh.json`
- Modify: `frontend/src/locales/en.json`

- [ ] **Step 1: Add Chinese translations**

In `zh.json`, add to the `"sidebar"` object:

```json
    "textTransfer": "文本传输"
```

Add to the `"mobileNav"` object:

```json
    "transfer": "传输"
```

Add a new category to `"categories"`:

```json
    "transfer": { "name": "文本传输", "description": "局域网设备间文本传输与群聊", "tools": { "textTransfer": "文本传输" } }
```

Add a new section to `"tools"`:

```json
    "transfer": {
      "title": "文本传输",
      "onlineDevices": "在线设备",
      "noDevices": "暂无其他设备在线",
      "groupChat": "群聊广播",
      "memberCount": "{count} 位成员",
      "noMessages": "暂无消息，开始发送吧",
      "inputPlaceholder": "输入文本，Enter 发送...",
      "send": "发送",
      "copied": "已复制"
    }
```

- [ ] **Step 2: Add English translations**

In `en.json`, add to the `"sidebar"` object:

```json
    "textTransfer": "Text Transfer"
```

Add to the `"mobileNav"` object:

```json
    "transfer": "Transfer"
```

Add a new category to `"categories"`:

```json
    "transfer": { "name": "Text Transfer", "description": "LAN text transfer and group chat", "tools": { "textTransfer": "Text Transfer" } }
```

Add a new section to `"tools"`:

```json
    "transfer": {
      "title": "Text Transfer",
      "onlineDevices": "Online Devices",
      "noDevices": "No other devices online",
      "groupChat": "Group Chat",
      "memberCount": "{count} members",
      "noMessages": "No messages yet. Start sending!",
      "inputPlaceholder": "Type a message, Enter to send...",
      "send": "Send",
      "copied": "Copied"
    }
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/locales/zh.json frontend/src/locales/en.json
git commit -m "feat(text-transfer): add i18n translations for text transfer"
```

---

### Task 8: Integration Test — Verify Signaling Works

**Files:** No new files

- [ ] **Step 1: Start the backend**

Run: `cd D:/github_app/DevToolBox && DEVTOOLBOX_NO_TOKEN=1 python -m backend.app`
Expected: Server starts on port 5000 with SocketIO support, no errors in output

- [ ] **Step 2: Start the frontend**

Run: `cd D:/github_app/DevToolBox/frontend && npm run dev`
Expected: Vite dev server starts on port 5173

- [ ] **Step 3: Open two browser tabs**

Open `http://localhost:5173/text-transfer` in two browser tabs.
Expected: Both tabs show the text transfer page. Each sees the other device in the left panel.

- [ ] **Step 4: Test group chat**

In Tab 1, click "Group Chat" in the sidebar. Type a message and press Enter.
Expected: The message appears in Tab 2's group chat view.

- [ ] **Step 5: Test private text**

In Tab 1, click on the device from Tab 2 in the left panel. Type a message and send.
Expected: The message appears in Tab 2 as an incoming message from Tab 1's device.

- [ ] **Step 6: Test copy button**

Hover over a received message and click "Copy".
Expected: "Copied to clipboard" toast appears.

- [ ] **Step 7: Fix any issues found, then commit**

```bash
git add -A
git commit -m "fix(text-transfer): integration test fixes"
```

---

## Self-Review

**Spec coverage:**
- Device discovery: Task 2 (backend join/peers/leave), Task 4 (frontend connect/peers state)
- Private text transfer: Task 2 (offer-text signaling), Task 4 (sendText), Task 5 (chat UI)
- E2E encrypted transfer: Task 4 (WebRTC DataChannel handlers)
- Group chat broadcast: Task 2 (chat handler), Task 4 (chat emit/receive), Task 5 (group view)
- History records: Task 4 (localStorage save/load, 200 item cap)
- IM-style dual-panel layout: Task 5 (full Vue component with sidebar + chat)
- Mobile adaptation: Task 5 (horizontal device strip, full-screen chat)
- i18n: Task 7
- Navigation integration: Task 6

**Placeholder scan:** No TBD/TODO found. All code blocks contain complete implementations.

**Type consistency:** `nodeId`, `peerName`, `content`, `secure`, `type` used consistently across backend events, composable state, and Vue template. `activePeer` is `{ nodeId, name, ip } | null` throughout. `messages` dict keyed by peerId (string) throughout.
