import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { io } from 'socket.io-client'

const HISTORY_KEY = 'text-transfer-history'
const MAX_HISTORY = 200
const IDENTITY_KEY = 'landrop_identity'

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
  const myId = ref('')
  const myName = ref('')
  const serverIp = ref('')

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

  const connected = ref(false)
  const peers = ref([])
  const activePeer = ref(null)
  const messages = ref({})
  const history = ref(loadHistory())
  const sending = ref(false)

  let socket = null

  function connect() {
    if (socket?.connected) return
    loadIdentity()

    socket = io({
      transports: ['polling'],
      path: '/socket.io',
      upgrade: false,
      reconnection: true,
      reconnectionAttempts: Infinity,
      reconnectionDelay: 1000,
    })

    socket.on('connect', () => {
      connected.value = true
      logToBackend('info', `SocketIO connected (sid=${socket.id})`)
      socket.emit('join', { nodeId: myId.value, name: myName.value })
    })

    socket.on('disconnect', (reason) => {
      connected.value = false
      logToBackend('warning', `SocketIO disconnected: ${reason}`)
    })

    socket.on('connect_error', (err) => {
      connected.value = false
      logToBackend('error', `SocketIO connection error: ${err.message}`)
    })

    socket.on('joined', (data) => {
      myId.value = data.nodeId
      myName.value = data.name
      if (data.serverIp) serverIp.value = data.serverIp
      saveIdentity()
      peers.value = data.peers.filter(p => p.nodeId !== myId.value)
      logToBackend('info', `Joined as "${data.name}" — ${peers.value.length} other devices online, server IP: ${data.serverIp || '?'}`)
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
      logToBackend('info', `Device left: ${leftName}`)
    })

    socket.on('offer-text', (data) => {
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

  function sendText(content, targetPeer, secure = false) {
    if (!content.trim() || !socket?.connected) return

    const isGroup = !targetPeer
    const peerName = targetPeer?.name || ''
    const peerId = targetPeer?.nodeId || 'group'

    const target = isGroup ? 'group' : peerName
    logToBackend('info', `Sending text to ${target} (${content.length} chars, ${secure ? 'encrypted' : 'plain'})`)

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

  const rtcConfig = { iceServers: [] }
  let pendingConnections = {}

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

  function rename(newName) {
    myName.value = newName
    saveIdentity()
    socket?.emit('rename', { nodeId: myId.value, name: newName })
  }

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

  onMounted(() => connect())
  onBeforeUnmount(() => disconnect())

  return {
    myId,
    myName,
    serverIp,
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
