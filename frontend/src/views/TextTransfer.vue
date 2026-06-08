<template>
  <ToolPage :title="t('tools.im.title')" :icon="ChatDotRound">
    <div class="im-container" :class="{ 'im-mobile': deviceStore.isMobile }">

      <!-- Connection status banner -->
      <transition name="banner-slide">
        <div v-if="!connected" class="connection-banner">
          <span class="material-symbols-rounded banner-icon">wifi_off</span>
          <span>{{ t('tools.im.disconnected') }}</span>
          <span class="banner-retrying">{{ t('tools.im.retrying') }}</span>
        </div>
      </transition>

      <!-- Mobile: horizontal device strip -->
      <div v-if="deviceStore.isMobile" class="mobile-device-strip">
        <div
          v-for="peer in peers"
          :key="peer.nodeId"
          class="mobile-device-avatar"
          :class="{ active: activePeer?.nodeId === peer.nodeId }"
          @click="selectPeer(peer)"
        >
          <img class="avatar-identicon" :src="generateIdenticon(peer.nodeId)" />
          <span class="mobile-avatar-name">{{ peer.name }}</span>
        </div>
        <div
          class="mobile-device-avatar"
          :class="{ active: !activePeer }"
          @click="selectGroupChat()"
        >
          <div class="avatar-circle avatar-group">#</div>
          <span class="mobile-avatar-name">{{ t('tools.im.groupChat') }}</span>
        </div>
      </div>

      <!-- Desktop: left sidebar -->
      <div v-if="!deviceStore.isMobile" class="im-sidebar">
        <div class="sidebar-header">
          <span class="sidebar-title">{{ t('tools.im.onlineDevices') }}</span>
          <span class="peer-count">{{ peers.length + 1 }}</span>
          <span class="connect-dot" :class="{ on: connected }"></span>
        </div>

        <div class="peer-list">
          <!-- Self -->
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

          <!-- Other peers -->
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
            <div class="online-dot"></div>
          </div>
          <div v-if="peers.length === 0" class="empty-peers">
            <span class="material-symbols-rounded empty-peers-icon">devices</span>
            <span>{{ t('tools.im.noDevices') }}</span>
          </div>
        </div>

        <!-- Group chat entry -->
        <div class="group-chat-entry" :class="{ active: !activePeer }" @click="selectGroupChat()">
          <div class="avatar-circle avatar-group">#</div>
          <div class="peer-info">
            <div class="peer-name">{{ t('tools.im.groupChat') }}</div>
            <div class="peer-ip">{{ t('tools.im.memberCount', { count: peers.length + 1 }) }}</div>
          </div>
        </div>
      </div>

      <!-- Right panel: chat area -->
      <div class="im-chat">
        <!-- Chat header -->
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

        <!-- Messages -->
        <div class="chat-messages" ref="messagesContainer">
          <!-- Empty state -->
          <div v-if="activeMessages.length === 0" class="empty-messages">
            <span class="material-symbols-rounded empty-chat-icon">chat</span>
            <p class="empty-chat-title">{{ t('tools.im.noMessages') }}</p>
            <p class="empty-chat-hint">{{ activePeer ? t('tools.im.hintPeer') : t('tools.im.hintGroup') }}</p>
          </div>

          <template v-for="(msg, idx) in activeMessages" :key="msg.id">
            <!-- Time separator -->
            <div v-if="shouldShowTimeSeparator(activeMessages, idx)" class="time-separator">
              <span>{{ formatTimeSeparator(msg.timestamp) }}</span>
            </div>

            <!-- Message -->
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

        <!-- Input area -->
        <ImChatInput
          :disabled="!connected"
          @send="onSend"
          @upload-file="onUploadFile"
          @upload-image="onUploadImage"
        />
      </div>
    </div>

    <!-- Rename dialog -->
    <el-dialog
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

    <!-- Image lightbox -->
    <ImLightbox
      :visible="lightbox.visible.value"
      :images="lightbox.images.value"
      :current-index="lightbox.currentIndex.value"
      @close="lightbox.close()"
      @next="lightbox.next()"
      @prev="lightbox.prev()"
      @go-to="lightbox.goTo($event)"
    />
  </ToolPage>
</template>

<script setup>
import { ref, nextTick, watch, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import { ChatDotRound } from '@element-plus/icons-vue'
import { useDeviceStore } from '@/stores/device.js'
import { useIm } from '@/composables/useIm.js'
import { useLightbox } from '@/composables/useLightbox.js'
import ImMessage from '@/components/im/ImMessage.vue'
import ImChatInput from '@/components/im/ImChatInput.vue'
import ImLightbox from '@/components/im/ImLightbox.vue'

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
  typingPeers,
  sendMsg,
  sendImage,
  sendFile,
  selectPeer,
  selectGroupChat,
  rename,
  deleteMessage,
  forwardMessage,
} = useIm()

const messagesContainer = ref(null)
const renameDialogVisible = ref(false)
const renameInput = ref('')

// Typing indicator for current peer
const activeTyping = computed(() => {
  if (!activePeer.value) return false
  return !!typingPeers.value[activePeer.value.nodeId]
})

// --- Identicon generation ---
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
  const grid = 5, cell = 8, pad = 4
  const size = grid * cell + pad * 2
  let rects = `<rect width="${size}" height="${size}" fill="${bg}" rx="6"/>`
  for (let row = 0; row < grid; row++) {
    for (let col = 0; col < 3; col++) {
      if (bytes[row * 3 + col + 2] % 2 === 0) continue
      const x = pad + col * cell, y = pad + row * cell
      rects += `<rect x="${x}" y="${y}" width="${cell}" height="${cell}" fill="${fg}"/>`
      if (col < 2) {
        rects += `<rect x="${pad + (grid - 1 - col) * cell}" y="${y}" width="${cell}" height="${cell}" fill="${fg}"/>`
      }
    }
  }
  return `data:image/svg+xml,${encodeURIComponent(`<svg xmlns="http://www.w3.org/2000/svg" width="${size}" height="${size}">${rects}</svg>`)}`
}

// --- Time formatting ---
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

// --- Actions ---
function onSend(content, msgType, attachment) {
  sendMsg(content, msgType, activePeer.value, attachment)
  nextTick(scrollToBottom)
}

async function onUploadFile(file) {
  try {
    await sendFile(file, activePeer.value)
    nextTick(scrollToBottom)
  } catch (e) {
    ElMessage.error(t('tools.im.uploadFail', { error: e.message }))
  }
}

async function onUploadImage(file) {
  try {
    await sendImage(file, activePeer.value)
    nextTick(scrollToBottom)
  } catch (e) {
    ElMessage.error(t('tools.im.uploadFail', { error: e.message }))
  }
}

function onCopy() { /* ImMessage handles clipboard + toast */ }

function onDeleteMessage(msg) {
  const peerId = activePeer.value?.nodeId || 'group'
  deleteMessage(msg.id, peerId)
}

function onForwardMessage(msg) {
  // For now, forward to group. A picker UI could be added later.
  forwardMessage(msg, null)
  ElMessage.success(t('tools.im.forwarded'))
}

function openLightboxForImage(msg) {
  const peerId = activePeer.value?.nodeId || 'group'
  const msgs = activeMessages.value
  // Collect all image messages in current conversation for lightbox navigation
  const images = msgs
    .filter(m => m.msgType === 'image' && m.attachment?.url)
    .map(m => ({ url: m.attachment.url, thumbnail: m.attachment.thumbnail || '', filename: m.attachment.filename || '' }))
  const startIndex = images.findIndex(img => img.url === msg.attachment?.url)
  lightbox.open(images, Math.max(0, startIndex))
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
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

watch(activeMessages, () => nextTick(scrollToBottom), { deep: true })
</script>

<style scoped>
/* =========================================
   Layout
   ========================================= */
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

.im-mobile {
  flex-direction: column;
  height: calc(100vh - 140px);
}

/* =========================================
   Connection banner
   ========================================= */
.connection-banner {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
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

.banner-slide-enter-active,
.banner-slide-leave-active { transition: all 0.3s ease; }
.banner-slide-enter-from,
.banner-slide-leave-to { opacity: 0; transform: translateY(-100%); }

/* =========================================
   Mobile device strip
   ========================================= */
.mobile-device-strip {
  display: flex;
  gap: var(--dt-spacing-md);
  padding: var(--dt-spacing-sm) var(--dt-spacing-md);
  border-bottom: 1px solid var(--dt-border-light);
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: none;
  background: var(--dt-bg-section);
}

.mobile-device-strip::-webkit-scrollbar { display: none; }

.mobile-device-avatar {
  cursor: pointer;
  flex-shrink: 0;
  opacity: 0.6;
  transition: opacity 0.2s;
  min-width: 44px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
}

.mobile-device-avatar.active { opacity: 1; }

.mobile-avatar-name {
  font-size: 10px;
  color: var(--dt-text-secondary);
  max-width: 56px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  text-align: center;
}

/* =========================================
   Sidebar (desktop)
   ========================================= */
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

.sidebar-title {
  font-weight: 600;
  font-size: var(--dt-font-size-sm);
  color: var(--dt-text-primary);
}

.peer-count {
  font-size: var(--dt-font-size-xs);
  color: var(--dt-primary);
  background: color-mix(in srgb, var(--dt-primary) 12%, transparent);
  padding: 1px 6px;
  border-radius: 10px;
}

.connect-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--dt-danger, #f56c6c);
  margin-left: auto;
  transition: background 0.3s;
}

.connect-dot.on { background: var(--dt-success, #67c23a); }

/* Self item */
.self-item {
  background: color-mix(in srgb, var(--dt-primary) 6%, transparent);
  border-left: 3px solid var(--dt-primary);
}

.self-item:hover { background: color-mix(in srgb, var(--dt-primary) 10%, transparent); }

.self-tag {
  font-size: 10px;
  font-weight: 500;
  color: var(--dt-primary);
  background: color-mix(in srgb, var(--dt-primary) 12%, transparent);
  padding: 1px 6px;
  border-radius: 4px;
  margin-left: 6px;
  vertical-align: middle;
}

.rename-icon {
  font-size: 14px;
  color: var(--dt-text-placeholder);
  opacity: 0;
  transition: opacity 0.15s;
}

.peer-item:hover .rename-icon { opacity: 1; }

/* Peer list */
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

.peer-item:hover { background: var(--dt-bg-hover); }
.peer-item.active {
  background: color-mix(in srgb, var(--dt-primary) 10%, transparent);
  border-left-color: var(--dt-primary);
}

.empty-peers {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  color: var(--dt-text-secondary);
  font-size: var(--dt-font-size-sm);
  padding: var(--dt-spacing-xl);
}

.empty-peers-icon { font-size: 28px; opacity: 0.3; }

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

.group-chat-entry:hover { background: var(--dt-bg-hover); }
.group-chat-entry.active {
  background: color-mix(in srgb, var(--dt-primary) 10%, transparent);
  border-left-color: var(--dt-primary);
}

/* =========================================
   Shared: avatar + peer-info
   ========================================= */
.avatar-identicon {
  width: 36px;
  height: 36px;
  border-radius: 6px;
  flex-shrink: 0;
  image-rendering: pixelated;
}

.avatar-identicon.small { width: 28px; height: 28px; }

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

.avatar-group { background: linear-gradient(135deg, var(--dt-primary), #a855f7) !important; }

.peer-info { flex: 1; min-width: 0; }

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
  background: var(--dt-success, #67c23a);
  flex-shrink: 0;
}

/* =========================================
   Chat area
   ========================================= */
.im-chat {
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

.typing-hint {
  font-size: var(--dt-font-size-xs);
  color: var(--dt-text-secondary);
  font-style: italic;
  animation: typing-pulse 1.5s ease-in-out infinite;
}

@keyframes typing-pulse {
  0%, 100% { opacity: 0.4; }
  50% { opacity: 1; }
}

/* Messages */
.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: var(--dt-spacing-md);
  display: flex;
  flex-direction: column;
  gap: var(--dt-spacing-xs);
  background: var(--dt-bg-page);
}

.chat-messages::-webkit-scrollbar { width: 5px; }
.chat-messages::-webkit-scrollbar-thumb {
  background: var(--dt-border-lighter);
  border-radius: 3px;
}

/* Empty state */
.empty-messages {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  flex: 1;
  padding: var(--dt-spacing-2xl, 48px);
  text-align: center;
}

.empty-chat-icon {
  font-size: 56px;
  color: var(--dt-primary);
  opacity: 0.2;
  margin-bottom: 12px;
}

.empty-chat-title {
  font-size: 14px;
  font-weight: 500;
  color: var(--dt-text-secondary);
  margin: 0 0 4px;
}

.empty-chat-hint {
  font-size: 13px;
  color: var(--dt-text-placeholder);
  margin: 0;
}

/* Time separator */
.time-separator {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 8px 0;
}

.time-separator span {
  font-size: 11px;
  color: var(--dt-text-placeholder);
  background: var(--dt-bg-page);
  padding: 2px 10px;
  border-radius: 10px;
}

/* =========================================
   Responsive
   ========================================= */
@media (max-width: 768px) {
  .empty-chat-icon { font-size: 40px; }
}
</style>
