import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { io } from 'socket.io-client'
import { usePeerConnection } from './usePeerConnection.js'

const IDENTITY_KEY = 'im_identity'
const MESSAGES_KEY = 'im_messages'
const PRIVATE_LIMIT = 200
const GROUP_LIMIT = 1200

function logToBackend(level, message) {
  try {
    fetch('/api/frontend-log', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ level, message }),
    }).catch(() => {})
  } catch {}
}

function generateId() {
  return Math.random().toString(36).substring(2) + Date.now().toString(36)
}

function getLimit(convKey) {
  return convKey === 'group' ? GROUP_LIMIT : PRIVATE_LIMIT
}

function trimMessages(arr, convKey) {
  const limit = getLimit(convKey)
  if (arr.length <= limit) return arr
  return arr.slice(arr.length - limit)
}

// ---------------------------------------------------------------------------
// Singleton state — shared across all useIm() calls in the same tab
// ---------------------------------------------------------------------------

const myId = ref('')
const myName = ref('')
const serverIp = ref('')
const connected = ref(false)
const peers = ref([])
const activePeer = ref(null)
const messages = ref({})
const typingPeers = ref({})

let socket = null
let _refCount = 0

// ---------------------------------------------------------------------------
// P2P (WebRTC) integration — singleton instance
// ---------------------------------------------------------------------------

const p2p = usePeerConnection()

// Wire P2P callbacks → message handling
p2p.setOnMessage((fromId, msg) => {
  // Incoming P2P message — use isGroup flag to distinguish private vs group
  const convKey = msg.isGroup ? 'group' : fromId
  const peerName = getPeerName(fromId)
  const m = {
    id: msg.id || generateId(),
    peerId: convKey,
    peerName,
    direction: 'received',
    content: msg.content || '',
    msgType: msg.msgType || 'text',
    attachment: msg.attachment || null,
    timestamp: msg.timestamp || Date.now(),
    secure: true,
  }
  if (!messages.value[convKey]) messages.value[convKey] = []
  messages.value[convKey].push(m)
  persistMessage(convKey)
})

p2p.setOnFileReceived((fromId, transferId, attachment) => {
  // A P2P file transfer completed — add a message for it
  const peerName = getPeerName(fromId)
  // Determine msgType from mime
  let msgType = 'file'
  if (attachment.mime?.startsWith('image/')) msgType = 'image'
  else if (attachment.mime?.startsWith('video/')) msgType = 'video'

  const m = {
    id: transferId,
    peerId: fromId,
    peerName,
    direction: 'received',
    content: msgType === 'file' ? (attachment.filename || '') : '',
    msgType,
    attachment,
    timestamp: Date.now(),
    secure: true,
  }
  if (!messages.value[fromId]) messages.value[fromId] = []
  messages.value[fromId].push(m)
  persistMessage(fromId)
})

p2p.setOnTyping((fromId) => {
  typingPeers.value[fromId] = true
  setTimeout(() => {
    typingPeers.value[fromId] = false
  }, 3000)
})

p2p.setOnRead((fromId) => {
  // Read receipt received via P2P — no UI for now
})

function getPeerName(nodeId) {
  const peer = peers.value.find(p => p.nodeId === nodeId)
  return peer?.name || nodeId
}

// ---------------------------------------------------------------------------
// LocalStorage persistence
// ---------------------------------------------------------------------------

function loadMessagesFromStorage() {
  try {
    const raw = localStorage.getItem(MESSAGES_KEY)
    if (raw) {
      const parsed = JSON.parse(raw)
      const result = {}
      for (const [key, arr] of Object.entries(parsed)) {
        if (Array.isArray(arr)) {
          result[key] = trimMessages(arr, key)
        }
      }
      return result
    }
  } catch {}
  return {}
}

function saveMessagesToStorage() {
  try {
    const toSave = {}
    for (const [key, arr] of Object.entries(messages.value)) {
      if (Array.isArray(arr) && arr.length > 0) {
        toSave[key] = trimMessages(arr, key)
      }
    }
    localStorage.setItem(MESSAGES_KEY, JSON.stringify(toSave))
  } catch (e) {
    logToBackend('error', `Failed to save messages: ${e.message}`)
  }
}

function persistMessage(convKey) {
  if (messages.value[convKey]) {
    messages.value[convKey] = trimMessages(messages.value[convKey], convKey)
  }
  saveMessagesToStorage()
}

// ---------------------------------------------------------------------------
// Identity persistence
// ---------------------------------------------------------------------------

function loadIdentity() {
  try {
    const raw = localStorage.getItem(IDENTITY_KEY)
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
  localStorage.setItem(IDENTITY_KEY, JSON.stringify({
    nodeId: myId.value,
    name: myName.value,
  }))
}

// ---------------------------------------------------------------------------
// SocketIO connection (singleton) — used for signaling + relay fallback
// ---------------------------------------------------------------------------

function connect() {
  if (socket?.connected) return
  loadIdentity()

  logToBackend('info', `[IM] connect() called — myId=${myId.value}, origin=${window.location.origin}`)

  messages.value = loadMessagesFromStorage()

  socket = io({
    transports: ['polling'],
    upgrade: false,
    path: '/socket.io',
    reconnection: true,
    reconnectionAttempts: Infinity,
    reconnectionDelay: 1000,
  })

  logToBackend('info', `[IM] socket.io client created — attempting connection to ${window.location.origin}/socket.io`)

  // Wire P2P signaling through Socket.IO
  p2p.setSignalSender((targetId, signal) => {
    if (socket?.connected) {
      socket.emit('webrtc-signal', { targetId, signal })
    }
  })

  socket.on('connect', () => {
    connected.value = true
    logToBackend('info', `[IM] ✓ SocketIO CONNECTED (sid=${socket.id}, transport=${socket.io.engine?.transport?.name})`)
    socket.emit('join', { nodeId: myId.value, name: myName.value })
  })

  socket.on('joined', (data) => {
    myId.value = data.nodeId
    myName.value = data.name
    if (data.serverIp) serverIp.value = data.serverIp
    saveIdentity()
    const rawPeers = data.peers || []
    peers.value = rawPeers.filter(p => p.nodeId !== myId.value)
    logToBackend('info', `[IM] ✓ JOINED as "${data.name}" (nodeId=${data.nodeId.slice(0,8)}) — server returned ${rawPeers.length} peers, ${peers.value.length} others: [${rawPeers.map(p => p.nodeId.slice(0,8)).join(',')}]`)

    // Safety net: if no peers after joining, retry after a short delay.
    // This handles the race where the server hasn't yet processed other
    // devices' reconnections after a page hard-refresh.
    if (peers.value.length === 0) {
      setTimeout(() => {
        if (socket?.connected && peers.value.length === 0) {
          logToBackend('info', `[IM] Retrying join — still 0 peers after 2s`)
          socket.emit('join', { nodeId: myId.value, name: myName.value })
        }
      }, 2000)
    }

    // Initiate P2P connections to all discovered peers
    p2p.connectToPeers(
      myId.value,
      peers.value.map(p => p.nodeId),
    )
  })

  socket.on('peers', (data) => {
    const newPeers = (data.list || []).filter(p => p.nodeId !== myId.value)
    // Find newly appeared peers and connect P2P
    const existingIds = new Set(peers.value.map(p => p.nodeId))
    const freshIds = newPeers.filter(p => !existingIds.has(p.nodeId)).map(p => p.nodeId)
    peers.value = newPeers
    logToBackend('info', `[IM] "peers" event received — ${newPeers.length} peers: [${newPeers.map(p => p.name).join(',')}]`)
    if (freshIds.length > 0) {
      p2p.connectToPeers(myId.value, freshIds)
    }
  })

  socket.on('leave', (data) => {
    const leftPeer = peers.value.find(p => p.nodeId === data.nodeId)
    const leftName = leftPeer?.name || data.nodeId
    peers.value = peers.value.filter(p => p.nodeId !== data.nodeId)
    if (activePeer.value?.nodeId === data.nodeId) {
      activePeer.value = null
    }
    // Close P2P connection to departed peer
    p2p.closePeerConnection(data.nodeId)
    logToBackend('info', `[IM] peer left: ${leftName}`)
  })

  socket.on('recv-msg', (data) => {
    // Relay fallback message (not P2P)
    const peerId = data.senderId || 'group'
    const peerName = data.senderName || peerId
    const convKey = data.targetId ? peerId : 'group'

    // Deduplicate: if already received via P2P (same id), skip
    if (messages.value[convKey]?.some(m => m.id === data.id)) return

    const msg = {
      id: data.id || generateId(),
      peerId: convKey,
      peerName,
      direction: 'received',
      content: data.content || '',
      msgType: data.msgType || 'text',
      attachment: data.attachment || null,
      timestamp: (data.timestamp || 0) * 1000,
      secure: false,
    }

    if (!messages.value[convKey]) messages.value[convKey] = []
    messages.value[convKey].push(msg)
    persistMessage(convKey)
  })

  socket.on('webrtc-signal', (data) => {
    // Incoming WebRTC signaling from a remote peer
    p2p.handleSignal(myId.value, data.fromId, data.signal)
  })

  socket.on('msg-sent', (data) => {
    const { id, timestamp } = data
    if (!id) return
    for (const key of Object.keys(messages.value)) {
      const arr = messages.value[key]
      const msg = arr.find(m => m.id === id)
      if (msg) {
        msg.timestamp = (timestamp || 0) * 1000
        msg.confirmed = true
        break
      }
    }
    saveMessagesToStorage()
  })

  socket.on('typing', (data) => {
    const peerId = data.from
    if (peerId) {
      typingPeers.value[peerId] = true
      setTimeout(() => {
        typingPeers.value[peerId] = false
      }, 3000)
    }
  })

  socket.on('disconnect', (reason) => {
    connected.value = false
    logToBackend('warning', `[IM] ✗ SocketIO DISCONNECTED: ${reason}`)
  })

  socket.on('connect_error', (err) => {
    connected.value = false
    logToBackend('error', `[IM] ✗ SocketIO CONNECT ERROR: ${err.message}`)
  })
}

function disconnect() {
  p2p.closeAll()
  // Revoke all blob: URLs from P2P file transfers to free memory
  for (const arr of Object.values(messages.value)) {
    for (const msg of arr) {
      if (msg.attachment?._blobUrl && msg.attachment.url?.startsWith('blob:')) {
        URL.revokeObjectURL(msg.attachment.url)
      }
    }
  }
  if (socket) {
    socket.removeAllListeners()
    socket.disconnect()
    socket = null
  }
  connected.value = false
}

// ---------------------------------------------------------------------------
// Sending messages — P2P preferred, Socket.IO fallback
// ---------------------------------------------------------------------------

function sendMsg(content, msgType = 'text', targetPeer = null, attachment = null) {
  if (!socket?.connected) return

  const peerId = targetPeer?.nodeId || 'group'
  const peerName = targetPeer?.name || ''
  const id = generateId()
  const timestamp = Date.now()

  // Try P2P first (only for private messages to a specific peer)
  let sentViaP2P = false
  if (targetPeer && p2p.isP2PReady(peerId)) {
    sentViaP2P = p2p.sendMsgP2P(peerId, { id, content, msgType, timestamp, attachment })
  }

  const msg = {
    id,
    peerId,
    peerName,
    direction: 'sent',
    content,
    msgType,
    attachment,
    timestamp,
    secure: sentViaP2P,
    confirmed: !sentViaP2P, // P2P doesn't get server ACK; mark confirmed for P2P
  }

  if (!messages.value[peerId]) messages.value[peerId] = []
  messages.value[peerId].push(msg)
  persistMessage(peerId)

  // Group message: send P2P to all connected peers, Socket.IO for any not P2P-ready
  if (!targetPeer) {
    const allPeerIds = peers.value.map(p => p.nodeId)
    const p2pReadyIds = allPeerIds.filter(id => p2p.isP2PReady(id))
    const fallbackIds = allPeerIds.filter(id => !p2p.isP2PReady(id))

    // P2P send
    for (const pid of p2pReadyIds) {
      p2p.sendMsgP2P(pid, { id, content, msgType, timestamp, attachment, isGroup: true })
    }

    // If any peers aren't P2P ready, fall back to server relay for them
    if (fallbackIds.length > 0 || p2pReadyIds.length === 0) {
      socket.emit('send-msg', {
        id,
        content,
        msgType,
        attachment,
        targetId: null,
      })
    }
    return
  }

  // Private message: if not sent via P2P, use Socket.IO relay
  if (!sentViaP2P) {
    socket.emit('send-msg', {
      id,
      content,
      msgType,
      attachment,
      targetId: targetPeer?.nodeId || null,
    })
  }
}

// ---------------------------------------------------------------------------
// File upload & transfer — P2P preferred, HTTP fallback
// ---------------------------------------------------------------------------

async function uploadFile(file) {
  const formData = new FormData()
  formData.append('file', file)

  const resp = await fetch('/api/im/upload', {
    method: 'POST',
    body: formData,
  })

  if (!resp.ok) {
    const text = await resp.text().catch(() => '')
    throw new Error(text || `Upload failed (HTTP ${resp.status})`)
  }

  const data = await resp.json()
  if (!data.success) {
    throw new Error(data.error || 'Upload failed')
  }

  return {
    url: data.url,
    filename: data.filename,
    size: data.size,
    mime: data.mime,
    thumbnail: data.thumbnail || null,
  }
}

async function sendImage(file, targetPeer = null) {
  const peerId = targetPeer?.nodeId

  // Try P2P file transfer for private messages
  if (peerId && p2p.isP2PReady(peerId)) {
    try {
      const { transferId, attachment } = await p2p.sendFileP2P(peerId, file)
      // For the sender's local display, create a blob URL from the file
      const localUrl = URL.createObjectURL(file)
      const localAttachment = {
        ...attachment,
        url: localUrl,
        _blobUrl: true,
      }
      sendMsg('', 'image', targetPeer, localAttachment)
      return
    } catch {
      // Fall through to HTTP upload
    }
  }

  // HTTP upload fallback
  const attachment = await uploadFile(file)
  sendMsg('', 'image', targetPeer, attachment)
}

async function sendFile(file, targetPeer = null) {
  const peerId = targetPeer?.nodeId
  const isVideo = file.type?.startsWith('video/')

  // Try P2P file transfer for private messages
  if (peerId && p2p.isP2PReady(peerId)) {
    try {
      const { transferId, attachment } = await p2p.sendFileP2P(peerId, file)
      // For the sender's local display, create a blob URL from the file
      const localUrl = URL.createObjectURL(file)
      const localAttachment = {
        ...attachment,
        url: localUrl,
        _blobUrl: true,
      }
      sendMsg(isVideo ? '' : file.name, isVideo ? 'video' : 'file', targetPeer, localAttachment)
      return
    } catch {
      // Fall through to HTTP upload
    }
  }

  // HTTP upload fallback
  const attachment = await uploadFile(file)
  sendMsg(file.name, isVideo ? 'video' : 'file', targetPeer, attachment)
}

// ---------------------------------------------------------------------------
// Local search
// ---------------------------------------------------------------------------

function searchMessages(query, limit = 20) {
  if (!query) return []
  const q = query.toLowerCase()
  const results = []
  for (const arr of Object.values(messages.value)) {
    for (const msg of arr) {
      if (msg.content && msg.content.toLowerCase().includes(q)) {
        results.push(msg)
      }
      if (results.length >= limit) break
    }
    if (results.length >= limit) break
  }
  return results.sort((a, b) => b.timestamp - a.timestamp).slice(0, limit)
}

// ---------------------------------------------------------------------------
// Typing indicators
// ---------------------------------------------------------------------------

function startTyping(targetPeer = null) {
  const peerId = targetPeer?.nodeId
  if (peerId) {
    // Private typing: prefer P2P
    if (p2p.isP2PReady(peerId)) {
      p2p.sendTypingP2P(peerId)
    } else if (socket?.connected) {
      socket.emit('typing', { from: myId.value, to: peerId })
    }
  } else {
    // Group typing: P2P to all ready peers + Socket.IO for rest
    const allPeerIds = peers.value.map(p => p.nodeId)
    for (const pid of allPeerIds) {
      if (p2p.isP2PReady(pid)) {
        p2p.sendTypingP2P(pid)
      }
    }
    if (socket?.connected) {
      socket.emit('typing', { from: myId.value, to: null })
    }
  }
}

function stopTyping() {}

// ---------------------------------------------------------------------------
// Read receipts
// ---------------------------------------------------------------------------

function markAsRead(peerId) {
  if (p2p.isP2PReady(peerId)) {
    p2p.sendReadP2P(peerId)
  }
  if (socket?.connected) {
    socket.emit('read', { from: peerId, to: myId.value })
  }
}

// ---------------------------------------------------------------------------
// Peer selection
// ---------------------------------------------------------------------------

function selectPeer(peer) {
  activePeer.value = peer
}

function selectGroupChat() {
  activePeer.value = null
}

// ---------------------------------------------------------------------------
// Rename
// ---------------------------------------------------------------------------

function rename(name) {
  myName.value = name
  saveIdentity()
  if (socket?.connected) {
    socket.emit('rename', { nodeId: myId.value, name })
  }
}

// ---------------------------------------------------------------------------
// Message management
// ---------------------------------------------------------------------------

function deleteMessage(msgId, peerId) {
  const arr = messages.value[peerId]
  if (!arr) return
  const idx = arr.findIndex(m => m.id === msgId)
  if (idx !== -1) {
    const msg = arr[idx]
    // Revoke blob: URL if it was a P2P file
    if (msg.attachment?._blobUrl && msg.attachment.url?.startsWith('blob:')) {
      URL.revokeObjectURL(msg.attachment.url)
    }
    arr.splice(idx, 1)
    saveMessagesToStorage()
  }
}

function forwardMessage(msg, targetPeer) {
  sendMsg(msg.content || '', msg.msgType || 'text', targetPeer, msg.attachment || null)
}

// ---------------------------------------------------------------------------
// Computed
// ---------------------------------------------------------------------------

const activeMessages = computed(() => {
  const key = activePeer.value?.nodeId || 'group'
  return messages.value[key] || []
})

/** Per-peer P2P connection state for UI indicators */
const p2pStatus = computed(() => {
  const status = {}
  for (const peer of peers.value) {
    status[peer.nodeId] = p2p.getP2PState(peer.nodeId) || 'none'
  }
  return status
})

// ---------------------------------------------------------------------------
// Public API — singleton with ref-counted lifecycle
// ---------------------------------------------------------------------------

export function useIm() {
  _refCount++

  onMounted(() => {
    if (_refCount > 0 && !socket?.connected) {
      connect()
    }
  })

  onBeforeUnmount(() => {
    _refCount--
    if (_refCount <= 0) {
      _refCount = 0
      disconnect()
    }
  })

  return {
    myId,
    myName,
    serverIp,
    connected,
    peers,
    activePeer,
    messages,
    typingPeers,
    activeMessages,
    connect,
    disconnect,
    sendMsg,
    sendImage,
    sendFile,
    uploadFile,
    searchMessages,
    startTyping,
    stopTyping,
    markAsRead,
    selectPeer,
    selectGroupChat,
    rename,
    deleteMessage,
    forwardMessage,
    // New P2P-related exports (additive, backward-compatible)
    transferProgress: p2p.transferProgress,
    p2pStatus,
  }
}
