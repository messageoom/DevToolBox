<template>
  <!-- Single root wrapper — required for <Transition mode="out-in"> in App.vue -->
  <div class="text-transfer-root">
  <!-- Mobile: conversation list in normal flow, chat view as fixed overlay -->
  <div v-if="deviceStore.isMobile">
    <!-- Connection status banner (inline) -->
    <transition name="banner-slide">
      <div v-if="!connected" class="connection-toast">
        <span class="material-symbols-rounded" style="font-size:14px">wifi_off</span>
        <span>{{ t('tools.im.disconnected') }}</span>
      </div>
    </transition>

    <!-- ===== Conversation List (normal document flow) ===== -->
    <div class="tg-conv-list">
      <!-- Toolbar -->
      <div class="tg-toolbar">
        <img class="tg-self-avatar" :src="generateIdenticon(myId)" />
        <div class="tg-self-info">
          <span class="tg-self-name">{{ myName || t('tools.im.unnamed') }}</span>
          <span class="tg-self-tag">{{ t('tools.im.thisDevice') }}</span>
        </div>
        <span class="tg-appbar-badge">{{ peers.length + 1 }}</span>
        <span class="connect-dot" :class="{ on: connected }"></span>
        <button class="tg-icon-btn" @click="showRenameDialog">
          <span class="material-symbols-rounded">edit</span>
        </button>
      </div>

      <!-- Group chat -->
      <div class="tg-conv-item" @click="openChat(null)">
        <div class="tg-avatar tg-avatar--group"><span class="material-symbols-rounded">groups</span></div>
        <div class="tg-conv-body">
          <div class="tg-conv-row">
            <span class="tg-conv-name">{{ t('tools.im.groupChat') }}</span>
            <span v-if="unreadCount('group') > 0" class="tg-badge">{{ unreadCount('group') > 99 ? '99+' : unreadCount('group') }}</span>
            <span v-else class="tg-conv-time">{{ formatConvTime(lastMsgTime('group')) }}</span>
          </div>
          <div class="tg-conv-row">
            <conv-preview peer-id="group" :messages="messages" />
          </div>
        </div>
      </div>

      <!-- Peer conversations -->
      <div
        v-for="peer in peers"
        :key="peer.nodeId"
        class="tg-conv-item"
        @click="openChat(peer)"
      >
        <img class="tg-avatar" :src="generateIdenticon(peer.nodeId)" />
        <div class="tg-conv-body">
          <div class="tg-conv-row">
            <span class="tg-conv-name">{{ peer.name }}</span>
            <span class="tg-online-dot-inline" :class="p2pDotClass(peer.nodeId)" :title="p2pDotTitle(peer.nodeId)"></span>
            <span v-if="unreadCount(peer.nodeId) > 0" class="tg-badge">{{ unreadCount(peer.nodeId) }}</span>
            <span v-else class="tg-conv-time">{{ formatConvTime(lastMsgTime(peer.nodeId)) }}</span>
          </div>
          <div class="tg-conv-row">
            <conv-preview :peer-id="peer.nodeId" :messages="messages" />
          </div>
        </div>
      </div>

      <!-- Empty state -->
      <div v-if="peers.length === 0" class="tg-empty">
        <span class="material-symbols-rounded tg-empty-icon">devices</span>
        <span class="tg-empty-text">{{ t('tools.im.noDevices') }}</span>
      </div>
    </div>

    <!-- ===== Chat View (fixed full-screen overlay, slides in from right) ===== -->
    <transition name="tg-slide">
      <div v-if="mobileView === 'chat'" class="im-chat-overlay">
        <!-- Chat app bar -->
        <div class="tg-chat-bar">
          <button class="tg-back-btn" @click="mobileView = 'list'">
            <span class="material-symbols-rounded">arrow_back</span>
          </button>
          <template v-if="activePeer">
            <img class="tg-bar-avatar" :src="generateIdenticon(activePeer.nodeId)" />
            <div class="tg-bar-info">
              <span class="tg-bar-name">{{ activePeer.name }}</span>
              <span v-if="activeTyping" class="tg-bar-status tg-bar-status--typing">{{ t('tools.im.typing') }}</span>
              <span v-else class="tg-bar-status">{{ t('tools.im.online') }}</span>
            </div>
          </template>
          <template v-else>
            <div class="tg-bar-avatar tg-bar-avatar--group"><span class="material-symbols-rounded">groups</span></div>
            <div class="tg-bar-info">
              <span class="tg-bar-name">{{ t('tools.im.groupChat') }}</span>
              <span class="tg-bar-status">{{ t('tools.im.memberCount', { count: peers.length + 1 }) }}</span>
            </div>
          </template>
        </div>

        <!-- Messages -->
        <div class="tg-messages" ref="messagesContainer">
          <div v-if="activeMessages.length === 0" class="tg-empty-chat">
            <span class="material-symbols-rounded tg-empty-chat-icon">forum</span>
            <p class="tg-empty-chat-title">{{ t('tools.im.noMessages') }}</p>
            <p class="tg-empty-chat-hint">{{ activePeer ? t('tools.im.hintPeer') : t('tools.im.hintGroup') }}</p>
          </div>

          <template v-for="(msg, idx) in activeMessages" :key="msg.id">
            <div v-if="shouldShowTimeSeparator(activeMessages, idx)" class="tg-time-sep">
              <span>{{ formatTimeSeparator(msg.timestamp) }}</span>
            </div>
            <ImMessage
              :msg="msg"
              :is-group="!activePeer"
              @preview-image="openLightboxForImage"
              @copy="onCopy"
              @delete="onDeleteMessage"
              @forward="onForwardMessage"
            />
          </template>
        </div>

        <!-- Fixed bottom input -->
        <ImChatInput
          :disabled="!connected"
          @send="onSend"
          @upload-file="onUploadFile"
          @upload-image="onUploadImage"
        />
      </div>
    </transition>

    <!-- Rename dialog -->
    <el-dialog
      v-model="renameDialogVisible"
      :title="t('tools.im.renameTitle')"
      width="85%"
      :close-on-click-modal="true"
    >
      <el-input v-model="renameInput" :placeholder="t('tools.im.renamePlaceholder')" maxlength="20" @keydown.enter="confirmRename" />
      <template #footer>
        <el-button @click="renameDialogVisible = false">{{ t('tools.im.cancel') }}</el-button>
        <el-button type="primary" @click="confirmRename">{{ t('tools.im.confirm') }}</el-button>
      </template>
    </el-dialog>
  </div>

  <!-- ===== Desktop: standard ToolPage + sidebar/chat layout ===== -->
  <ToolPage v-else :title="t('tools.im.title')" :icon="ChatDotRound">
    <div class="im-container">
      <!-- Connection banner -->
      <transition name="banner-slide">
        <div v-if="!connected" class="connection-banner">
          <span class="material-symbols-rounded banner-icon">wifi_off</span>
          <span>{{ t('tools.im.disconnected') }}</span>
          <span class="banner-retrying">{{ t('tools.im.retrying') }}</span>
        </div>
      </transition>

      <!-- Left sidebar -->
      <div class="im-sidebar">
        <div class="sidebar-header">
          <span class="sidebar-title">{{ t('tools.im.onlineDevices') }}</span>
          <span class="peer-count">{{ peers.length + 1 }}</span>
          <span class="connect-dot" :class="{ on: connected }"></span>
        </div>

        <div class="peer-list">
          <div class="peer-item self-item" @click="showRenameDialog">
            <img class="avatar-identicon" :src="generateIdenticon(myId)" />
            <div class="peer-info">
              <div class="peer-name">
                {{ myName || t('tools.im.unnamed') }}
                <span class="self-tag">{{ t('tools.im.thisDevice') }}</span>
              </div>
            </div>
            <span class="material-symbols-rounded rename-icon">edit</span>
          </div>

          <div
            v-for="peer in peers"
            :key="peer.nodeId"
            class="peer-item"
            :class="{ active: activePeer?.nodeId === peer.nodeId }"
            @click="selectPeer(peer)"
          >
            <img class="avatar-identicon" :src="generateIdenticon(peer.nodeId)" />
            <div class="peer-info">
              <div class="peer-name">{{ peer.name }}</div>
              <div class="peer-ip">{{ peer.ip }}</div>
            </div>
            <div class="p2p-dot" :class="p2pDotClass(peer.nodeId)" :title="p2pDotTitle(peer.nodeId)"></div>
          </div>
          <div v-if="peers.length === 0" class="empty-peers">
            <span class="material-symbols-rounded empty-peers-icon">devices</span>
            <span>{{ t('tools.im.noDevices') }}</span>
          </div>
        </div>

        <div class="group-chat-entry" :class="{ active: !activePeer }" @click="selectGroupChat()">
          <div class="avatar-circle avatar-group">#</div>
          <div class="peer-info">
            <div class="peer-name">{{ t('tools.im.groupChat') }}</div>
            <div class="peer-ip">{{ t('tools.im.memberCount', { count: peers.length + 1 }) }}</div>
          </div>
        </div>
      </div>

      <!-- Right: chat -->
      <div class="im-chat">
        <div class="chat-header">
          <template v-if="activePeer">
            <img class="avatar-identicon small" :src="generateIdenticon(activePeer.nodeId)" />
            <span class="chat-target-name">{{ activePeer.name }}</span>
            <span v-if="activeTyping" class="typing-hint">{{ t('tools.im.typing') }}</span>
          </template>
          <template v-else>
            <div class="avatar-circle small avatar-group">#</div>
            <span class="chat-target-name">{{ t('tools.im.groupChat') }}</span>
          </template>
        </div>

        <div class="chat-messages" ref="messagesContainer">
          <div v-if="activeMessages.length === 0" class="empty-messages">
            <span class="material-symbols-rounded empty-chat-icon">chat</span>
            <p class="empty-chat-title">{{ t('tools.im.noMessages') }}</p>
            <p class="empty-chat-hint">{{ activePeer ? t('tools.im.hintPeer') : t('tools.im.hintGroup') }}</p>
          </div>

          <template v-for="(msg, idx) in activeMessages" :key="msg.id">
            <div v-if="shouldShowTimeSeparator(activeMessages, idx)" class="time-separator">
              <span>{{ formatTimeSeparator(msg.timestamp) }}</span>
            </div>
            <ImMessage
              :msg="msg"
              :is-group="!activePeer"
              @preview-image="openLightboxForImage"
              @copy="onCopy"
              @delete="onDeleteMessage"
              @forward="onForwardMessage"
            />
          </template>
        </div>

        <ImChatInput
          :disabled="!connected"
          @send="onSend"
          @upload-file="onUploadFile"
          @upload-image="onUploadImage"
        />
      </div>
    </div>
  </ToolPage>

  <!-- Lightbox (shared) -->
  <ImLightbox
    :visible="lightbox.visible.value"
    :images="lightbox.images.value"
    :current-index="lightbox.currentIndex.value"
    @close="lightbox.close()"
    @next="lightbox.next()"
    @prev="lightbox.prev()"
    @go-to="lightbox.goTo($event)"
  />

  <!-- Desktop rename dialog -->
  <el-dialog
    v-if="!deviceStore.isMobile"
    v-model="renameDialogVisible"
    :title="t('tools.im.renameTitle')"
    width="360px"
    :close-on-click-modal="true"
  >
    <el-input v-model="renameInput" :placeholder="t('tools.im.renamePlaceholder')" maxlength="20" @keydown.enter="confirmRename" />
    <template #footer>
      <el-button @click="renameDialogVisible = false">{{ t('tools.im.cancel') }}</el-button>
      <el-button type="primary" @click="confirmRename">{{ t('tools.im.confirm') }}</el-button>
    </template>
  </el-dialog>
  </div><!-- /.text-transfer-root -->
</template>

<script setup>
import { ref, nextTick, watch, computed, onBeforeUnmount } from 'vue'
import { useI18n } from 'vue-i18n'
import { onBeforeRouteLeave } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ChatDotRound } from '@element-plus/icons-vue'
import { useDeviceStore } from '@/stores/device.js'
import { useIm } from '@/composables/useIm.js'
import { useLightbox } from '@/composables/useLightbox.js'
import ImMessage from '@/components/im/ImMessage.vue'
import ImChatInput from '@/components/im/ImChatInput.vue'
import ImLightbox from '@/components/im/ImLightbox.vue'
import { h } from 'vue'

// Inline component: conversation list last-message preview
const ConvPreview = {
  props: {
    peerId: String,
    messages: { type: Object, required: true },
  },
  setup(props) {
    const { t } = useI18n()
    return () => {
      const msgs = props.messages[props.peerId]
      const last = msgs?.length ? msgs[msgs.length - 1] : null
      if (!last) return h('span', { class: 'tg-conv-preview' }, '')

      const name = last.direction === 'sent' ? t('tools.im.you') : (last.peerName || '')
      const prefix = name ? `${name}: ` : ''

      // Media types → text label only
      if (last.msgType === 'image') {
        return h('span', { class: 'tg-conv-preview' }, `${prefix}[${t('tools.im.image')}]`)
      }
      if (last.msgType === 'video') {
        return h('span', { class: 'tg-conv-preview' }, `${prefix}[${t('tools.im.video')}]`)
      }
      if (last.msgType === 'file') {
        const fname = last.attachment?.filename || t('tools.im.file')
        return h('span', { class: 'tg-conv-preview' }, `${prefix}[${t('tools.im.file')}] ${fname}`)
      }

      // Text / code / link — emoji displays naturally
      const text = last.content || ''
      const preview = prefix + (text.length > 30 ? text.slice(0, 30) + '...' : text)
      return h('span', { class: 'tg-conv-preview' }, preview)
    }
  }
}
import ToolPage from '@/components/ToolPage.vue'

const { t } = useI18n()
const deviceStore = useDeviceStore()
const lightbox = useLightbox()

const {
  myId,
  myName,
  connected,
  peers,
  activePeer,
  activeMessages,
  messages,
  typingPeers,
  sendMsg,
  sendImage,
  sendFile,
  selectPeer,
  selectGroupChat,
  rename,
  deleteMessage,
  forwardMessage,
  disconnect,
  p2pStatus,
} = useIm()

const messagesContainer = ref(null)
const renameDialogVisible = ref(false)
const renameInput = ref('')
const mobileView = ref('list')

// Close overlay AND disconnect SocketIO before the page-slide leave transition.
// Without early disconnect, the long-polling connection blocks browser HTTP
// connections and stale event handlers can fire during the 0.2s transition,
// which prevents the next page from rendering ("no content" bug).
onBeforeRouteLeave(() => {
  mobileView.value = 'list'
})

const activeTyping = computed(() => {
  if (!activePeer.value) return false
  return !!typingPeers.value[activePeer.value.nodeId]
})

// --- P2P status helpers ---
function p2pDotClass(nodeId) {
  if (!connected.value) return ''
  const state = p2pStatus.value[nodeId]
  // Online: always green, add glow for P2P direct
  if (state === 'ready') return 'online p2p-ready'
  return 'online'
}
function p2pDotTitle(nodeId) {
  const state = p2pStatus.value[nodeId]
  if (state === 'ready') return t('tools.im.p2pReady')
  if (state === 'connecting') return t('tools.im.p2pConnecting')
  return t('tools.im.p2pRelay')
}

// --- Identicon ---
function hashStr(str) {
  let h = 0
  for (let i = 0; i < str.length; i++) h = str.charCodeAt(i) + ((h << 5) - h)
  return h
}
function hashBytes(str) {
  const bytes = []
  let h = hashStr(str)
  for (let i = 0; i < 20; i++) {
    h = ((h << 5) - h + str.charCodeAt(i % str.length) + i * 31) | 0
    bytes.push(Math.abs(h))
  }
  return bytes
}
const IDENTICON_COLORS = [
  ['#7c3aed','#ede9fe'],['#4f46e5','#e0e7ff'],['#0891b2','#cffafe'],
  ['#059669','#d1fae5'],['#d97706','#fef3c7'],['#dc2626','#fee2e2'],
  ['#db2777','#fce7f3'],['#2563eb','#dbeafe'],['#7c2d12','#ffedd5'],
  ['#475569','#e2e8f0'],['#15803d','#dcfce7'],['#9333ea','#f3e8ff'],
]
function generateIdenticon(id) {
  if (!id) id = 'default'
  const bytes = hashBytes(id)
  const [fg, bg] = IDENTICON_COLORS[Math.abs(bytes[0]) % IDENTICON_COLORS.length]
  const grid = 5, cell = 8, pad = 4, size = grid * cell + pad * 2
  let rects = `<rect width="${size}" height="${size}" fill="${bg}" rx="6"/>`
  for (let row = 0; row < grid; row++) {
    for (let col = 0; col < 3; col++) {
      if (bytes[row * 3 + col + 2] % 2 === 0) continue
      const x = pad + col * cell, y = pad + row * cell
      rects += `<rect x="${x}" y="${y}" width="${cell}" height="${cell}" fill="${fg}"/>`
      if (col < 2) rects += `<rect x="${pad + (grid - 1 - col) * cell}" y="${y}" width="${cell}" height="${cell}" fill="${fg}"/>`
    }
  }
  return `data:image/svg+xml,${encodeURIComponent(`<svg xmlns="http://www.w3.org/2000/svg" width="${size}" height="${size}">${rects}</svg>`)}`
}

// --- Time ---
function formatTimeSeparator(ts) {
  const d = new Date(ts)
  const now = new Date()
  const time = `${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2, '0')}`
  if (d.toDateString() === now.toDateString()) return time
  return `${(d.getMonth() + 1).toString().padStart(2, '0')}/${d.getDate().toString().padStart(2, '0')} ${time}`
}
function shouldShowTimeSeparator(msgs, idx) {
  if (idx === 0) return true
  return msgs[idx].timestamp - msgs[idx - 1].timestamp > 5 * 60 * 1000
}
function formatConvTime(ts) {
  if (!ts) return ''
  const d = new Date(ts)
  const now = new Date()
  const time = `${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2, '0')}`
  if (d.toDateString() === now.toDateString()) return time
  const yd = new Date(now); yd.setDate(yd.getDate() - 1)
  if (d.toDateString() === yd.toDateString()) return t('tools.im.yesterday')
  return `${(d.getMonth() + 1).toString().padStart(2, '0')}/${d.getDate().toString().padStart(2, '0')}`
}

// --- Conv list ---
function getLastMsg(peerId) {
  const msgs = messages.value[peerId]
  return (msgs && msgs.length) ? msgs[msgs.length - 1] : null
}
function lastMsgTime(peerId) {
  const msgs = messages.value[peerId]
  return (!msgs || !msgs.length) ? 0 : msgs[msgs.length - 1].timestamp
}
function getLastMsgPreview(peerId) {
  const msgs = messages.value[peerId]
  if (!msgs || !msgs.length) return ''
  const last = msgs[msgs.length - 1]
  const name = last.direction === 'sent' ? t('tools.im.you') : (last.peerName || '')
  const prefix = name ? `${name}: ` : ''
  if (last.msgType === 'image') return `${prefix}[${t('tools.im.image')}]`
  if (last.msgType === 'file') return `${prefix}[${last.attachment?.filename || t('tools.im.file')}]`
  const text = last.content || ''
  return prefix + (text.length > 30 ? text.slice(0, 30) + '...' : text)
}
// Track last-seen message ID per conversation — persisted to localStorage
const SEEN_IDS_KEY = 'im_seen_ids'

function loadSeenIds() {
  try { return JSON.parse(localStorage.getItem(SEEN_IDS_KEY)) || {} } catch { return {} }
}
function saveSeenIds() {
  try { localStorage.setItem(SEEN_IDS_KEY, JSON.stringify(seenIds.value)) } catch {}
}

const seenIds = ref(loadSeenIds())

function unreadCount(peerId) {
  const msgs = messages.value[peerId]
  if (!msgs || !msgs.length) return 0
  const lastSeenId = seenIds.value[peerId]
  if (!lastSeenId) {
    // No seen record — count trailing received messages
    let c = 0
    for (let i = msgs.length - 1; i >= 0; i--) {
      if (msgs[i].direction === 'sent') break
      c++
    }
    return c
  }
  // Count received messages after the last seen message
  let c = 0
  let found = false
  for (let i = msgs.length - 1; i >= 0; i--) {
    if (msgs[i].id === lastSeenId) { found = true; break }
    if (msgs[i].direction === 'received') c++
  }
  return found ? c : 0
}

// --- Mobile nav ---
function openChat(peer) {
  const peerId = peer ? peer.nodeId : 'group'
  const msgs = messages.value[peerId] || []
  if (msgs.length > 0) {
    seenIds.value[peerId] = msgs[msgs.length - 1].id
    saveSeenIds()
  }
  if (peer) selectPeer(peer)
  else selectGroupChat()
  mobileView.value = 'chat'
  nextTick(scrollToBottom)
}

// --- Actions ---
function onSend(content, msgType, attachment) {
  sendMsg(content, msgType, activePeer.value, attachment)
  nextTick(scrollToBottom)
}
async function onUploadFile(file) {
  try { await sendFile(file, activePeer.value); nextTick(scrollToBottom) }
  catch (e) { ElMessage.error(t('tools.im.uploadFail', { error: e.message })) }
}
async function onUploadImage(file) {
  try { await sendImage(file, activePeer.value); nextTick(scrollToBottom) }
  catch (e) { ElMessage.error(t('tools.im.uploadFail', { error: e.message })) }
}
function onCopy() {}
function onDeleteMessage(msg) {
  deleteMessage(msg.id, activePeer.value?.nodeId || 'group')
}
function onForwardMessage(msg) {
  forwardMessage(msg, null)
  ElMessage.success(t('tools.im.forwarded'))
}
function openLightboxForImage(msg) {
  const imgs = activeMessages.value
    .filter(m => m.msgType === 'image' && m.attachment?.url)
    .map(m => ({ url: m.attachment.url, thumbnail: m.attachment.thumbnail || '', filename: m.attachment.filename || '' }))
  lightbox.open(imgs, Math.max(0, imgs.findIndex(img => img.url === msg.attachment?.url)))
}
function showRenameDialog() {
  renameInput.value = myName.value || ''
  renameDialogVisible.value = true
}
function confirmRename() {
  const name = renameInput.value.trim()
  if (!name) return
  rename(name)
  renameDialogVisible.value = false
}
function scrollToBottom() {
  if (messagesContainer.value) messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
}
watch(activeMessages, () => nextTick(scrollToBottom), { deep: true })
</script>

<style scoped>
/* ==============================================
   MOBILE: Telegram-style full-screen layout
   ============================================== */
.im-chat-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 150;
  display: flex;
  flex-direction: column;
  background: var(--dt-bg-page);
}

/* Connection toast (inline banner) */
.connection-toast {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 6px 12px;
  background: color-mix(in srgb, var(--dt-warning, #e6a23c) 15%, transparent);
  color: var(--dt-warning, #e6a23c);
  font-size: 12px;
  font-weight: 500;
}
.banner-slide-enter-active, .banner-slide-leave-active { transition: all 0.3s ease; }
.banner-slide-enter-from, .banner-slide-leave-to { opacity: 0; transform: translateY(-100%); }

/* ===== Toolbar (inline, in content flow) ===== */
.tg-toolbar {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  background: var(--dt-bg-card);
  border-bottom: 1px solid var(--dt-border-light);
}
.tg-self-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  flex-shrink: 0;
  image-rendering: pixelated;
  object-fit: cover;
}
.tg-self-info {
  flex: 1;
  min-width: 0;
  display: flex;
  align-items: center;
  gap: 6px;
}
.tg-self-name {
  font-size: 15px;
  font-weight: 600;
  color: var(--dt-text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  min-width: 0;
}
.tg-self-tag {
  font-size: 10px;
  font-weight: 500;
  color: var(--dt-primary);
  background: color-mix(in srgb, var(--dt-primary) 12%, transparent);
  padding: 1px 6px;
  border-radius: 4px;
  flex-shrink: 0;
}
.tg-appbar-badge {
  font-size: 13px;
  font-weight: 600;
  color: var(--dt-primary);
  background: color-mix(in srgb, var(--dt-primary) 14%, transparent);
  padding: 2px 8px;
  border-radius: 10px;
}
.tg-icon-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border: none;
  background: none;
  border-radius: 50%;
  cursor: pointer;
  color: var(--dt-text-secondary);
  margin-left: auto;
}
.tg-icon-btn:active { background: var(--dt-bg-hover); }

.connect-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--dt-danger, #f56c6c);
  transition: background 0.3s;
}
.connect-dot.on { background: var(--dt-success, #67c23a); }

/* ===== Conversation list (normal flow) ===== */
.tg-conv-list {
  overflow: hidden;
}

.tg-conv-item {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 12px 16px;
  cursor: pointer;
  transition: background 0.12s;
  border-bottom: 1px solid var(--dt-border-light);
}
.tg-conv-item:active { background: var(--dt-bg-hover); }

.tg-avatar {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  flex-shrink: 0;
  image-rendering: pixelated;
  object-fit: cover;
}
.tg-avatar--group {
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, var(--dt-primary), #a855f7);
  color: #fff;
}
.tg-avatar--group .material-symbols-rounded {
  font-size: 26px;
}

.tg-conv-body { flex: 1; min-width: 0; }
.tg-conv-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}
.tg-conv-row + .tg-conv-row { margin-top: 3px; }

.tg-conv-name {
  font-size: 16px;
  font-weight: 500;
  color: var(--dt-text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  min-width: 0;
}
.tg-conv-time {
  font-size: 12px;
  color: var(--dt-text-secondary);
  flex-shrink: 0;
}
.tg-badge {
  min-width: 18px;
  height: 18px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: var(--dt-primary);
  color: #fff;
  font-size: 11px;
  font-weight: 600;
  border-radius: 9px;
  padding: 0 5px;
  flex-shrink: 0;
  line-height: 1;
}
.tg-online-dot-inline {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--dt-danger, #f56c6c);
  flex-shrink: 0;
  transition: background 0.3s;
}
.tg-online-dot-inline.online {
  background: var(--dt-success, #67c23a);
}
.tg-online-dot-inline.online.p2p-ready {
  box-shadow: 0 0 4px var(--dt-success, #67c23a);
}
/* P2P connection status dot (desktop sidebar) */
.p2p-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
  background: var(--dt-text-placeholder, #c0c4cc);
  transition: background 0.3s;
}
.p2p-dot.p2p-ready {
  background: var(--dt-success, #67c23a);
}
.p2p-dot.p2p-connecting {
  background: var(--dt-warning, #e6a23c);
  animation: p2p-pulse 1.2s ease-in-out infinite;
}
@keyframes p2p-pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}

.tg-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  gap: 10px;
}
.tg-empty-icon { font-size: 48px; color: var(--dt-primary); opacity: 0.15; }
.tg-empty-text { font-size: 15px; color: var(--dt-text-secondary); }

/* ===== Chat view ===== */
.tg-chat {
  display: flex;
  flex-direction: column;
  height: 100%;
}

/* Chat bar */
.tg-chat-bar {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 6px;
  background: var(--dt-bg-card);
  border-bottom: 1px solid var(--dt-border-light);
  flex-shrink: 0;
}
.tg-back-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border: none;
  background: none;
  border-radius: 50%;
  cursor: pointer;
  color: var(--dt-primary);
}
.tg-back-btn:active { background: var(--dt-bg-hover); }

.tg-bar-avatar {
  width: 38px;
  height: 38px;
  border-radius: 50%;
  flex-shrink: 0;
  object-fit: cover;
  image-rendering: pixelated;
}
.tg-bar-avatar--group {
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, var(--dt-primary), #a855f7);
  color: #fff;
}
.tg-bar-avatar--group .material-symbols-rounded {
  font-size: 20px;
}
.tg-bar-info { display: flex; flex-direction: column; }
.tg-bar-name {
  font-size: 16px;
  font-weight: 600;
  color: var(--dt-text-primary);
  line-height: 1.2;
}
.tg-bar-status {
  font-size: 12px;
  color: var(--dt-text-secondary);
  line-height: 1.2;
}
.tg-bar-status--typing {
  color: var(--dt-primary);
  font-style: italic;
}

/* Messages */
.tg-messages {
  flex: 1;
  overflow-y: auto;
  padding: 10px 12px;
  display: flex;
  flex-direction: column;
  gap: 4px;
  -webkit-overflow-scrolling: touch;
}

.tg-time-sep {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 8px 0;
}
.tg-time-sep span {
  font-size: 12px;
  color: var(--dt-text-secondary);
  background: color-mix(in srgb, var(--dt-bg-card) 80%, transparent);
  padding: 3px 10px;
  border-radius: 12px;
}

.tg-empty-chat {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  flex: 1;
  padding: 40px 20px;
  text-align: center;
}
.tg-empty-chat-icon { font-size: 48px; color: var(--dt-primary); opacity: 0.15; margin-bottom: 8px; }
.tg-empty-chat-title { font-size: 16px; font-weight: 500; color: var(--dt-text-secondary); margin: 0 0 4px; }
.tg-empty-chat-hint { font-size: 14px; color: var(--dt-text-placeholder); margin: 0; }

/* Slide animation */
.tg-slide-enter-active, .tg-slide-leave-active { transition: transform 0.28s cubic-bezier(0.4, 0, 0.2, 1); }
.tg-slide-enter-from { transform: translateX(100%); }
.tg-slide-leave-to { transform: translateX(30%); opacity: 0.7; }

/* ==============================================
   DESKTOP: Standard layout
   ============================================== */
.im-container {
  display: flex;
  height: calc(100vh - 160px);
  min-height: 400px;
  border: 1px solid var(--dt-border-light);
  border-radius: var(--dt-radius-md);
  overflow: hidden;
  background: var(--dt-bg-card);
  position: relative;
}

.connection-banner {
  position: absolute;
  top: 0; left: 0; right: 0;
  z-index: 10;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 8px 16px;
  background: color-mix(in srgb, var(--dt-warning, #e6a23c) 15%, transparent);
  border-bottom: 1px solid color-mix(in srgb, var(--dt-warning, #e6a23c) 30%, transparent);
  color: var(--dt-warning, #e6a23c);
  font-size: 13px;
  font-weight: 500;
}
.banner-icon { font-size: 16px; }
.banner-retrying { font-size: 11px; opacity: 0.7; }

/* Sidebar */
.im-sidebar {
  width: 260px;
  min-width: 260px;
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
.sidebar-title { font-weight: 600; font-size: var(--dt-font-size-sm); color: var(--dt-text-primary); }
.peer-count {
  font-size: var(--dt-font-size-xs);
  color: var(--dt-primary);
  background: color-mix(in srgb, var(--dt-primary) 12%, transparent);
  padding: 1px 6px;
  border-radius: 10px;
}

.self-item {
  background: color-mix(in srgb, var(--dt-primary) 6%, transparent);
  border-left: 3px solid var(--dt-primary);
}
.self-item:hover { background: color-mix(in srgb, var(--dt-primary) 10%, transparent); }
.self-tag {
  font-size: 10px; font-weight: 500; color: var(--dt-primary);
  background: color-mix(in srgb, var(--dt-primary) 12%, transparent);
  padding: 1px 6px; border-radius: 4px; margin-left: 6px; vertical-align: middle;
}
.rename-icon { font-size: 14px; color: var(--dt-text-placeholder); opacity: 0; transition: opacity 0.15s; }
.peer-item:hover .rename-icon { opacity: 1; }

.peer-list { flex: 1; overflow-y: auto; padding: var(--dt-spacing-xs); }
.peer-item {
  display: flex; align-items: center; gap: var(--dt-spacing-sm);
  padding: var(--dt-spacing-sm); border-radius: var(--dt-radius-sm);
  cursor: pointer; transition: background 0.15s; border-left: 3px solid transparent;
}
.peer-item:hover { background: var(--dt-bg-hover); }
.peer-item.active { background: color-mix(in srgb, var(--dt-primary) 10%, transparent); border-left-color: var(--dt-primary); }

.empty-peers { display: flex; flex-direction: column; align-items: center; gap: 6px; color: var(--dt-text-secondary); font-size: var(--dt-font-size-sm); padding: var(--dt-spacing-xl); }
.empty-peers-icon { font-size: 28px; opacity: 0.3; }

.group-chat-entry {
  display: flex; align-items: center; gap: var(--dt-spacing-sm);
  padding: var(--dt-spacing-sm); border-top: 1px solid var(--dt-border-light);
  cursor: pointer; border-left: 3px solid transparent; transition: background 0.15s;
}
.group-chat-entry:hover { background: var(--dt-bg-hover); }
.group-chat-entry.active { background: color-mix(in srgb, var(--dt-primary) 10%, transparent); border-left-color: var(--dt-primary); }

/* Shared avatar/peer-info */
.avatar-identicon { width: 36px; height: 36px; border-radius: 6px; flex-shrink: 0; image-rendering: pixelated; }
.avatar-identicon.small { width: 28px; height: 28px; }
.avatar-circle { width: 36px; height: 36px; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: #fff; font-size: 14px; font-weight: 600; flex-shrink: 0; }
.avatar-group { background: linear-gradient(135deg, var(--dt-primary), #a855f7) !important; }
.peer-info { flex: 1; min-width: 0; }
.peer-name { font-size: var(--dt-font-size-sm); font-weight: 500; color: var(--dt-text-primary); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.peer-ip { font-size: var(--dt-font-size-xs); color: var(--dt-text-secondary); }
.online-dot { width: 8px; height: 8px; border-radius: 50%; background: var(--dt-success, #67c23a); flex-shrink: 0; }

/* Chat area */
.im-chat { flex: 1; display: flex; flex-direction: column; min-width: 0; }
.chat-header { padding: var(--dt-spacing-sm) var(--dt-spacing-md); border-bottom: 1px solid var(--dt-border-light); display: flex; align-items: center; gap: var(--dt-spacing-sm); background: var(--dt-bg-card); }
.chat-target-name { font-weight: 600; font-size: var(--dt-font-size-sm); color: var(--dt-text-primary); }
.typing-hint { font-size: var(--dt-font-size-xs); color: var(--dt-text-secondary); font-style: italic; animation: typing-pulse 1.5s ease-in-out infinite; }
@keyframes typing-pulse { 0%, 100% { opacity: 0.4; } 50% { opacity: 1; } }

.chat-messages { flex: 1; overflow-y: auto; padding: var(--dt-spacing-md); display: flex; flex-direction: column; gap: var(--dt-spacing-xs); background: var(--dt-bg-page); }
.chat-messages::-webkit-scrollbar { width: 5px; }
.chat-messages::-webkit-scrollbar-thumb { background: var(--dt-border-lighter); border-radius: 3px; }

.empty-messages { display: flex; flex-direction: column; align-items: center; justify-content: center; flex: 1; padding: var(--dt-spacing-2xl, 48px); text-align: center; }
.empty-chat-icon { font-size: 56px; color: var(--dt-primary); opacity: 0.2; margin-bottom: 12px; }
.empty-chat-title { font-size: 14px; font-weight: 500; color: var(--dt-text-secondary); margin: 0 0 4px; }
.empty-chat-hint { font-size: 13px; color: var(--dt-text-placeholder); margin: 0; }

.time-separator { display: flex; align-items: center; justify-content: center; padding: 8px 0; }
.time-separator span { font-size: 11px; color: var(--dt-text-placeholder); background: var(--dt-bg-page); padding: 2px 10px; border-radius: 10px; }
</style>

<!-- ConvPreview uses render function — scoped styles don't apply, so these must be unscoped -->
<style>
.tg-conv-preview {
  font-size: 14px;
  color: var(--dt-text-secondary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  line-height: 1.4;
}
</style>
