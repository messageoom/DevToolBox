import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { io } from 'socket.io-client'

const IDENTITY_KEY = 'im_identity'

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

export function useIm() {
  const myId = ref('')
  const myName = ref('')
  const serverIp = ref('')
  const connected = ref(false)
  const peers = ref([])
  const activePeer = ref(null) // null = group chat
  const messages = ref({})     // { peerId: [msg...], 'group': [msg...] }
  const typingPeers = ref({})  // { peerId: true/false }

  let socket = null

  // ---------------------------------------------------------------------------
  // Identity persistence
  // ---------------------------------------------------------------------------

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

  // ---------------------------------------------------------------------------
  // SocketIO connection
  // ---------------------------------------------------------------------------

  function connect() {
    if (socket?.connected) return
    loadIdentity()

    socket = io({
      transports: ['polling', 'websocket'],
      path: '/socket.io',
      reconnection: true,
      reconnectionAttempts: Infinity,
      reconnectionDelay: 1000,
    })

    socket.on('connect', () => {
      connected.value = true
      logToBackend('info', `IM SocketIO connected (sid=${socket.id})`)
      socket.emit('join', { nodeId: myId.value, name: myName.value })
    })

    socket.on('joined', (data) => {
      myId.value = data.nodeId
      myName.value = data.name
      if (data.serverIp) serverIp.value = data.serverIp
      saveIdentity()
      peers.value = (data.peers || []).filter(p => p.nodeId !== myId.value)
      logToBackend('info', `IM joined as "${data.name}" — ${peers.value.length} peers online`)

      // Handle unread messages from server
      if (data.unreadMessages && data.unreadMessages.length > 0) {
        for (const msg of data.unreadMessages) {
          const peerId = msg.senderId || msg.targetId || 'group'
          const normalised = {
            id: msg.id || generateId(),
            peerId,
            peerName: msg.senderName || peerId,
            direction: 'received',
            content: msg.content || '',
            msgType: msg.msgType || 'text',
            attachment: msg.attachment || null,
            timestamp: (msg.timestamp || 0) * 1000,
            secure: false,
          }
          if (!messages.value[peerId]) messages.value[peerId] = []
          messages.value[peerId].push(normalised)
        }
      }
    })

    socket.on('peers', (data) => {
      peers.value = (data.list || []).filter(p => p.nodeId !== myId.value)
    })

    socket.on('leave', (data) => {
      const leftPeer = peers.value.find(p => p.nodeId === data.nodeId)
      const leftName = leftPeer?.name || data.nodeId
      peers.value = peers.value.filter(p => p.nodeId !== data.nodeId)
      if (activePeer.value?.nodeId === data.nodeId) {
        activePeer.value = null
      }
      logToBackend('info', `IM peer left: ${leftName}`)
    })

    // Incoming real-time message (renamed from 'new-msg' to 'recv-msg' to match backend)
    socket.on('recv-msg', (data) => {
      const peerId = data.senderId || 'group'
      const peerName = data.senderName || peerId
      const msg = {
        id: data.id || generateId(),
        peerId,
        peerName,
        direction: 'received',
        content: data.content || '',
        msgType: data.msgType || 'text',
        attachment: data.attachment || null,
        timestamp: (data.timestamp || 0) * 1000,
        secure: false,
      }

      // For private messages, store under the conversation key (peer's id).
      // For group (targetId is null), store under 'group'.
      const convKey = data.targetId ? peerId : 'group'
      if (!messages.value[convKey]) messages.value[convKey] = []
      messages.value[convKey].push(msg)
    })

    socket.on('msg-sent', (data) => {
      // Server confirmed our message — update the optimistic local copy.
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
    })

    socket.on('typing', (data) => {
      const peerId = data.from
      if (peerId) {
        typingPeers.value[peerId] = true
        // Auto-expire after 3 seconds
        setTimeout(() => {
          typingPeers.value[peerId] = false
        }, 3000)
      }
    })

    socket.on('disconnect', (reason) => {
      connected.value = false
      logToBackend('warning', `IM SocketIO disconnected: ${reason}`)
    })

    socket.on('connect_error', (err) => {
      connected.value = false
      logToBackend('error', `IM SocketIO connection error: ${err.message}`)
    })
  }

  function disconnect() {
    if (socket) {
      socket.disconnect()
      socket = null
    }
    connected.value = false
  }

  // ---------------------------------------------------------------------------
  // Sending messages
  // ---------------------------------------------------------------------------

  function sendMsg(content, msgType = 'text', targetPeer = null, attachment = null) {
    if (!socket?.connected) return

    const isGroup = !targetPeer
    const peerId = targetPeer?.nodeId || 'group'
    const peerName = targetPeer?.name || ''
    const id = generateId()

    const msg = {
      id,
      peerId,
      peerName,
      direction: 'sent',
      content,
      msgType,
      attachment,
      timestamp: Date.now(),
      secure: false,
      confirmed: false,
    }

    if (!messages.value[peerId]) messages.value[peerId] = []
    messages.value[peerId].push(msg)

    socket.emit('send-msg', {
      id,
      content,
      msgType,
      attachment,
      targetId: targetPeer?.nodeId || null,
    })
  }

  // ---------------------------------------------------------------------------
  // File upload
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
    const attachment = await uploadFile(file)
    sendMsg('', 'image', targetPeer, attachment)
  }

  async function sendFile(file, targetPeer = null) {
    const attachment = await uploadFile(file)
    sendMsg(file.name, 'file', targetPeer, attachment)
  }

  // ---------------------------------------------------------------------------
  // History & search
  // ---------------------------------------------------------------------------

  async function loadHistory(peerId = 'group', limit = 50, before = null) {
    const params = new URLSearchParams({ peer: peerId, limit: String(limit) })
    if (before) params.set('before', String(before))

    const resp = await fetch(`/api/im/history?${params}`)
    if (!resp.ok) return

    const data = await resp.json()
    if (!data.success) return

    const loaded = (data.messages || []).map(msg => ({
      id: msg.id || generateId(),
      peerId: msg.senderId === myId.value ? (msg.targetId || 'group') : (msg.senderId || 'group'),
      peerName: msg.senderName || msg.senderId || '',
      direction: msg.senderId === myId.value ? 'sent' : 'received',
      content: msg.content || '',
      msgType: msg.msg_type || msg.msgType || 'text',
      attachment: msg.attachment || null,
      timestamp: (msg.timestamp || 0) * 1000,
      secure: false,
      confirmed: true,
    }))

    if (before) {
      // Prepend older messages
      messages.value[peerId] = [...loaded, ...(messages.value[peerId] || [])]
    } else {
      // Replace current view
      messages.value[peerId] = loaded
    }
  }

  async function searchMessages(query, limit = 20) {
    const params = new URLSearchParams({ q: query, limit: String(limit) })
    const resp = await fetch(`/api/im/search?${params}`)
    if (!resp.ok) return []
    const data = await resp.json()
    if (!data.success) return []
    return (data.messages || []).map(msg => ({
      id: msg.id || generateId(),
      peerId: msg.senderId === myId.value ? (msg.targetId || 'group') : (msg.senderId || 'group'),
      peerName: msg.senderName || msg.senderId || '',
      direction: msg.senderId === myId.value ? 'sent' : 'received',
      content: msg.content || '',
      msgType: msg.msg_type || msg.msgType || 'text',
      attachment: msg.attachment || null,
      timestamp: (msg.timestamp || 0) * 1000,
      secure: false,
      confirmed: true,
    }))
  }

  // ---------------------------------------------------------------------------
  // Typing indicators
  // ---------------------------------------------------------------------------

  function startTyping(targetPeer = null) {
    if (!socket?.connected) return
    socket.emit('typing', { from: myId.value, to: targetPeer?.nodeId || null })
  }

  function stopTyping() {
    // Typing indicators auto-expire; this is a no-op for now.
  }

  // ---------------------------------------------------------------------------
  // Read receipts
  // ---------------------------------------------------------------------------

  function markAsRead(peerId) {
    if (!socket?.connected) return
    socket.emit('read', { from: peerId, to: myId.value })
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
    if (idx !== -1) arr.splice(idx, 1)
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

  // ---------------------------------------------------------------------------
  // Lifecycle
  // ---------------------------------------------------------------------------

  onMounted(() => connect())
  onBeforeUnmount(() => disconnect())

  return {
    // State
    myId,
    myName,
    serverIp,
    connected,
    peers,
    activePeer,
    messages,
    typingPeers,

    // Computed
    activeMessages,

    // Connection
    connect,
    disconnect,

    // Messaging
    sendMsg,
    sendImage,
    sendFile,
    uploadFile,

    // History
    loadHistory,
    searchMessages,

    // Typing
    startTyping,
    stopTyping,

    // Read receipts
    markAsRead,

    // Peer management
    selectPeer,
    selectGroupChat,
    rename,

    // Message management
    deleteMessage,
    forwardMessage,
  }
}
