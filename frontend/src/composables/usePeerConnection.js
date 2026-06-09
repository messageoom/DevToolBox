import { ref } from 'vue'

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const CHUNK_SIZE = 16 * 1024 // 16KB per DataChannel chunk
const BUFFER_THRESHOLD = 1024 * 1024 // 1MB backpressure threshold

// ---------------------------------------------------------------------------
// Singleton state
// ---------------------------------------------------------------------------

/** @type {Record<string, { pc: RTCPeerConnection, control: RTCDataChannel|null, data: RTCDataChannel|null, state: 'connecting'|'ready'|'failed' }>} */
const connections = ref({})

/** In-progress inbound file transfers: transferId → { metadata, chunks[], received } */
const inboundTransfers = {}

/** Outbound file transfer progress: transferId → { progress, state } */
const transferProgress = ref({})

/** Callbacks injected by useIm */
let _signalSender = null // (targetId, signal) => void
let _onMessage = null // (fromId, msg) => void
let _onFileReceived = null // (fromId, transferId, attachment) => void
let _onTyping = null // (fromId) => void
let _onRead = null // (fromId) => void

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function generateId() {
  return Math.random().toString(36).substring(2) + Date.now().toString(36)
}

function shouldInitiate(myNodeId, peerNodeId) {
  return myNodeId < peerNodeId
}

/** Convert ArrayBuffer to base64 string */
function ab2b64(buffer) {
  const bytes = new Uint8Array(buffer)
  let binary = ''
  for (let i = 0; i < bytes.length; i++) {
    binary += String.fromCharCode(bytes[i])
  }
  return btoa(binary)
}

/** Convert base64 string to ArrayBuffer */
function b642ab(base64) {
  const binary = atob(base64)
  const bytes = new Uint8Array(binary.length)
  for (let i = 0; i < binary.length; i++) {
    bytes[i] = binary.charCodeAt(i)
  }
  return bytes.buffer
}

/** Wait for DataChannel buffer to drain below threshold */
function waitForBufferDrain(dc) {
  return new Promise((resolve) => {
    if (!dc || dc.readyState !== 'open' || dc.bufferedAmount <= BUFFER_THRESHOLD) {
      resolve()
      return
    }
    const check = () => {
      if (dc.bufferedAmount <= BUFFER_THRESHOLD) {
        resolve()
      } else {
        setTimeout(check, 20)
      }
    }
    setTimeout(check, 20)
  })
}

/** Generate client-side image thumbnail via canvas */
function generateThumbnail(file, maxW = 200, maxH = 200) {
  return new Promise((resolve) => {
    if (!file.type.startsWith('image/')) {
      resolve(null)
      return
    }
    const img = new Image()
    const url = URL.createObjectURL(file)
    img.onload = () => {
      try {
        const canvas = document.createElement('canvas')
        const ratio = Math.min(maxW / img.width, maxH / img.height, 1)
        canvas.width = Math.round(img.width * ratio)
        canvas.height = Math.round(img.height * ratio)
        canvas.getContext('2d').drawImage(img, 0, 0, canvas.width, canvas.height)
        const dataUrl = canvas.toDataURL('image/webp', 0.7)
        resolve(dataUrl)
      } catch {
        resolve(null)
      } finally {
        URL.revokeObjectURL(url)
      }
    }
    img.onerror = () => {
      URL.revokeObjectURL(url)
      resolve(null)
    }
    img.src = url
  })
}

// ---------------------------------------------------------------------------
// RTC Configuration (LAN — no STUN/TURN needed)
// ---------------------------------------------------------------------------

const RTC_CONFIG = {
  iceServers: [],
  iceCandidatePoolSize: 0,
}

// ---------------------------------------------------------------------------
// Connection lifecycle
// ---------------------------------------------------------------------------

/**
 * Create RTCPeerConnection for a peer and set up DataChannel handlers.
 * Does NOT create an offer — the caller decides whether to initiate.
 */
function createPeerConnection(nodeId) {
  if (connections.value[nodeId]?.pc) {
    // Already exists — skip
    return connections.value[nodeId]
  }

  const pc = new RTCPeerConnection(RTC_CONFIG)
  const entry = { pc, control: null, data: null, state: 'connecting' }
  connections.value[nodeId] = entry

  // ICE candidate → send to remote peer via signaling
  pc.onicecandidate = (e) => {
    if (e.candidate) {
      sendSignal(nodeId, { type: 'ice-candidate', payload: e.candidate.toJSON() })
    }
  }

  // Connection state changes
  pc.onconnectionstatechange = () => {
    const state = pc.connectionState
    if (state === 'connected') {
      entry.state = 'ready'
    } else if (state === 'failed' || state === 'disconnected') {
      entry.state = 'failed'
    }
  }

  // Remote peer created DataChannels (answering side receives them)
  pc.ondatachannel = (e) => {
    const dc = e.channel
    if (dc.label === 'control') {
      entry.control = dc
      setupControlChannel(dc, nodeId)
    } else if (dc.label === 'data') {
      entry.data = dc
      setupDataChannel(dc, nodeId)
    }
  }

  pc.oniceconnectionstatechange = () => {
    if (pc.iceConnectionState === 'failed') {
      entry.state = 'failed'
    }
  }

  return entry
}

/**
 * Initiate P2P connection: create offer and send via signaling.
 * Only called by the peer with the lexicographically smaller nodeId.
 */
async function initiateConnection(myNodeId, peerNodeId) {
  const entry = createPeerConnection(peerNodeId)

  // Create DataChannels (initiator creates, responder receives via ondatachannel)
  const controlDc = entry.pc.createDataChannel('control', { ordered: true })
  const dataDc = entry.pc.createDataChannel('data', { ordered: true })
  entry.control = controlDc
  entry.data = dataDc
  setupControlChannel(controlDc, peerNodeId)
  setupDataChannel(dataDc, peerNodeId)

  try {
    const offer = await entry.pc.createOffer()
    await entry.pc.setLocalDescription(offer)
    sendSignal(peerNodeId, { type: 'offer', payload: offer })
  } catch (err) {
    console.error(`[WebRTC] Failed to create offer for ${peerNodeId}:`, err)
    entry.state = 'failed'
  }
}

/**
 * Process incoming signaling message (offer / answer / ice-candidate).
 */
async function handleSignal(myNodeId, fromId, signal) {
  const { type, payload } = signal

  if (type === 'offer') {
    // Remote peer is offering — create connection (if not exists) and answer
    const entry = createPeerConnection(fromId)
    try {
      await entry.pc.setRemoteDescription(new RTCSessionDescription(payload))
      const answer = await entry.pc.createAnswer()
      await entry.pc.setLocalDescription(answer)
      sendSignal(fromId, { type: 'answer', payload: answer })
    } catch (err) {
      console.error(`[WebRTC] Failed to handle offer from ${fromId}:`, err)
      entry.state = 'failed'
    }
  } else if (type === 'answer') {
    const entry = connections.value[fromId]
    if (entry?.pc) {
      try {
        await entry.pc.setRemoteDescription(new RTCSessionDescription(payload))
      } catch (err) {
        console.error(`[WebRTC] Failed to set remote answer from ${fromId}:`, err)
        entry.state = 'failed'
      }
    }
  } else if (type === 'ice-candidate') {
    const entry = connections.value[fromId]
    if (entry?.pc) {
      try {
        await entry.pc.addIceCandidate(new RTCIceCandidate(payload))
      } catch (err) {
        // ICE candidate might arrive before remote description — safe to ignore
      }
    }
  }
}

// ---------------------------------------------------------------------------
// DataChannel setup
// ---------------------------------------------------------------------------

function setupControlChannel(dc, peerNodeId) {
  dc.onopen = () => {
    const entry = connections.value[peerNodeId]
    if (entry) entry.state = 'ready'
  }
  dc.onclose = () => {
    const entry = connections.value[peerNodeId]
    if (entry) entry.state = 'failed'
  }
  dc.onmessage = (e) => {
    try {
      const msg = JSON.parse(e.data)
      handleControlMessage(peerNodeId, msg)
    } catch {}
  }
}

function setupDataChannel(dc, peerNodeId) {
  dc.onclose = () => {
    // DataChannel closed — file transfers will fail
  }
  dc.onmessage = (e) => {
    try {
      const msg = JSON.parse(e.data)
      handleDataMessage(peerNodeId, msg)
    } catch {}
  }
}

// ---------------------------------------------------------------------------
// Incoming message handlers
// ---------------------------------------------------------------------------

function handleControlMessage(fromId, msg) {
  switch (msg.type) {
    case 'msg':
      if (_onMessage) {
        _onMessage(fromId, {
          id: msg.id,
          content: msg.content,
          msgType: msg.msgType || 'text',
          timestamp: msg.timestamp,
          attachment: msg.attachment || null,
          isGroup: !!msg.isGroup,
          secure: true,
        })
      }
      break
    case 'typing':
      if (_onTyping) _onTyping(fromId)
      break
    case 'read':
      if (_onRead) _onRead(fromId)
      break
  }
}

function handleDataMessage(fromId, msg) {
  switch (msg.type) {
    case 'file-offer': {
      inboundTransfers[msg.transferId] = {
        fromId,
        metadata: {
          filename: msg.filename,
          size: msg.size,
          mime: msg.mime,
          thumbnail: msg.thumbnail || null,
        },
        totalChunks: msg.totalChunks,
        chunks: new Array(msg.totalChunks),
        received: 0,
      }
      transferProgress.value[msg.transferId] = { progress: 0, state: 'receiving' }
      break
    }
    case 'file-chunk': {
      const transfer = inboundTransfers[msg.transferId]
      if (!transfer) return
      const chunkBuf = b642ab(msg.data)
      transfer.chunks[msg.seq] = new Uint8Array(chunkBuf)
      transfer.received++
      const progress = transfer.received / transfer.totalChunks
      transferProgress.value[msg.transferId] = { progress, state: 'receiving' }
      break
    }
    case 'file-done': {
      const transfer = inboundTransfers[msg.transferId]
      if (!transfer) return
      // Reassemble
      const blob = new Blob(transfer.chunks.filter(Boolean), { type: transfer.metadata.mime })
      const url = URL.createObjectURL(blob)
      const attachment = {
        url,
        filename: transfer.metadata.filename,
        size: transfer.metadata.size,
        mime: transfer.metadata.mime,
        thumbnail: transfer.metadata.thumbnail || null,
        _blobUrl: true, // flag for cleanup
      }
      if (_onFileReceived) {
        _onFileReceived(fromId, msg.transferId, attachment)
      }
      transferProgress.value[msg.transferId] = { progress: 1, state: 'done' }
      delete inboundTransfers[msg.transferId]
      // Send ACK via control channel
      sendControl(fromId, { type: 'file-ack', transferId: msg.transferId })
      break
    }
    case 'file-ack': {
      transferProgress.value[msg.transferId] = { progress: 1, state: 'done' }
      break
    }
  }
}

// ---------------------------------------------------------------------------
// Sending helpers
// ---------------------------------------------------------------------------

function sendSignal(targetId, signal) {
  if (_signalSender) {
    _signalSender(targetId, signal)
  }
}

function sendControl(peerNodeId, msg) {
  const entry = connections.value[peerNodeId]
  if (entry?.control?.readyState === 'open') {
    entry.control.send(JSON.stringify(msg))
    return true
  }
  return false
}

function sendData(peerNodeId, msg) {
  const entry = connections.value[peerNodeId]
  if (entry?.data?.readyState === 'open') {
    entry.data.send(JSON.stringify(msg))
    return true
  }
  return false
}

/**
 * Send a text/code/link message via P2P DataChannel.
 * Returns true if sent via P2P, false if not available.
 */
function sendMsgP2P(peerNodeId, { id, content, msgType, timestamp, attachment, isGroup }) {
  return sendControl(peerNodeId, {
    type: 'msg',
    id,
    content,
    msgType,
    timestamp,
    attachment: attachment || null,
    isGroup: !!isGroup,
  })
}

/**
 * Send a file via P2P DataChannel with chunking and backpressure.
 * Returns the transferId on success.
 */
async function sendFileP2P(peerNodeId, file) {
  const entry = connections.value[peerNodeId]
  if (!entry?.data || entry.data.readyState !== 'open') {
    throw new Error('P2P data channel not ready')
  }

  const transferId = generateId()
  const buffer = await file.arrayBuffer()
  const totalChunks = Math.ceil(buffer.byteLength / CHUNK_SIZE)

  // Generate thumbnail for images
  let thumbnail = null
  if (file.type.startsWith('image/')) {
    thumbnail = await generateThumbnail(file)
  }

  // Send file offer
  sendControl(peerNodeId, {
    type: 'file-offer',
    transferId,
    filename: file.name,
    size: file.size,
    mime: file.type || 'application/octet-stream',
    totalChunks,
    thumbnail,
  })

  transferProgress.value[transferId] = { progress: 0, state: 'sending' }

  // Stream chunks
  for (let seq = 0; seq < totalChunks; seq++) {
    const start = seq * CHUNK_SIZE
    const end = Math.min(start + CHUNK_SIZE, buffer.byteLength)
    const chunk = buffer.slice(start, end)

    sendData(peerNodeId, {
      type: 'file-chunk',
      transferId,
      seq,
      data: ab2b64(chunk),
    })

    // Backpressure
    await waitForBufferDrain(entry.data)

    const progress = (seq + 1) / totalChunks
    transferProgress.value[transferId] = { progress, state: 'sending' }
  }

  // Signal completion
  sendControl(peerNodeId, { type: 'file-done', transferId })

  return {
    transferId,
    attachment: {
      url: `p2p://${transferId}`, // placeholder — actual data lives at receiver
      filename: file.name,
      size: file.size,
      mime: file.type || 'application/octet-stream',
      thumbnail,
      _p2pLocal: true, // flag: sender's local file
    },
  }
}

function sendTypingP2P(peerNodeId) {
  return sendControl(peerNodeId, { type: 'typing' })
}

function sendReadP2P(peerNodeId) {
  return sendControl(peerNodeId, { type: 'read' })
}

// ---------------------------------------------------------------------------
// Connection management
// ---------------------------------------------------------------------------

/**
 * Initialize P2P connections for a list of peer nodeIds.
 * Only initiates if we should (lexicographic rule).
 */
function connectToPeers(myNodeId, peerNodeIds) {
  for (const peerId of peerNodeIds) {
    if (connections.value[peerId]?.pc) continue // already connected/connecting
    if (shouldInitiate(myNodeId, peerId)) {
      initiateConnection(myNodeId, peerId)
    }
    // If we shouldn't initiate, the other peer will send us an offer
  }
}

function closePeerConnection(nodeId) {
  const entry = connections.value[nodeId]
  if (!entry) return
  try {
    entry.control?.close()
  } catch {}
  try {
    entry.data?.close()
  } catch {}
  try {
    entry.pc.close()
  } catch {}
  delete connections.value[nodeId]
}

function closeAll() {
  for (const nodeId of Object.keys(connections.value)) {
    closePeerConnection(nodeId)
  }
}

// ---------------------------------------------------------------------------
// Query helpers
// ---------------------------------------------------------------------------

function isP2PReady(nodeId) {
  return connections.value[nodeId]?.state === 'ready'
}

function getP2PState(nodeId) {
  return connections.value[nodeId]?.state || null
}

// ---------------------------------------------------------------------------
// Callback registration (called by useIm)
// ---------------------------------------------------------------------------

function setSignalSender(fn) { _signalSender = fn }
function setOnMessage(fn) { _onMessage = fn }
function setOnFileReceived(fn) { _onFileReceived = fn }
function setOnTyping(fn) { _onTyping = fn }
function setOnRead(fn) { _onRead = fn }

// ---------------------------------------------------------------------------
// Public API — singleton
// ---------------------------------------------------------------------------

export function usePeerConnection() {
  return {
    connections,
    transferProgress,
    // Lifecycle
    connectToPeers,
    handleSignal,
    closePeerConnection,
    closeAll,
    // Sending
    sendMsgP2P,
    sendFileP2P,
    sendTypingP2P,
    sendReadP2P,
    // Query
    isP2PReady,
    getP2PState,
    // Callback registration
    setSignalSender,
    setOnMessage,
    setOnFileReceived,
    setOnTyping,
    setOnRead,
  }
}
