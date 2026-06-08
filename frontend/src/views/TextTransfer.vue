<template>
  <ToolPage :title="t('tools.transfer.title')" :icon="ChatDotRound">
    <div class="transfer-container" :class="{ 'transfer-mobile': deviceStore.isMobile }">

      <!-- Connection status banner -->
      <transition name="banner-slide">
        <div v-if="!connected" class="connection-banner">
          <span class="material-symbols-rounded banner-icon">wifi_off</span>
          <span>{{ t('tools.transfer.disconnected') }}</span>
          <span class="banner-retrying">{{ t('tools.transfer.retrying') }}</span>
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
          <span class="peer-count">{{ peers.length + 1 }}</span>
          <span class="connect-dot" :class="{ on: connected }"></span>
        </div>

        <div class="peer-list">
          <!-- Self (current device) -->
          <div class="peer-item self-item" @click="showRenameDialog">
            <img class="avatar-identicon" :src="generateIdenticon(myId)" />
            <div class="peer-info">
              <div class="peer-name">
                {{ myName || t('tools.transfer.unnamed') }}
                <span class="self-tag">{{ t('tools.transfer.thisDevice') }}</span>
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
            <div class="online-dot"></div>
          </div>
          <div v-if="peers.length === 0" class="empty-peers">
            <span class="material-symbols-rounded empty-peers-icon">devices</span>
            <span>{{ t('tools.transfer.noDevices') }}</span>
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
            <img class="avatar-identicon small" :src="generateIdenticon(activePeer.nodeId)" />
            <span class="chat-target-name">{{ activePeer.name }}</span>
          </template>
          <template v-else>
            <div class="avatar-circle small avatar-group">#</div>
            <span class="chat-target-name">{{ t('tools.transfer.groupChat') }}</span>
          </template>
        </div>

        <!-- Messages -->
        <div class="chat-messages" ref="messagesContainer">
          <!-- Empty state -->
          <div v-if="activeMessages.length === 0" class="empty-messages">
            <span class="material-symbols-rounded empty-chat-icon">chat</span>
            <p class="empty-chat-title">{{ t('tools.transfer.noMessages') }}</p>
            <p class="empty-chat-hint">{{ activePeer ? t('tools.transfer.hintPeer') : t('tools.transfer.hintGroup') }}</p>
          </div>

          <template v-for="(msg, idx) in activeMessages" :key="msg.id">
            <!-- Time separator -->
            <div
              v-if="shouldShowTimeSeparator(activeMessages, idx)"
              class="time-separator"
            >
              <span>{{ formatTimeSeparator(msg.timestamp) }}</span>
            </div>

            <!-- Message -->
            <transition name="msg-pop" appear>
              <div
                class="message-row"
                :class="{ 'message-sent': msg.direction === 'sent', 'message-received': msg.direction === 'received' }"
              >
                <div class="message-bubble" :class="{ 'bubble-sent': msg.direction === 'sent', 'bubble-received': msg.direction === 'received' }">
                  <div v-if="msg.direction === 'received'" class="message-sender">{{ msg.peerName }}</div>
                  <div v-if="msg.type === 'code'" class="message-code">
                    <pre><code>{{ msg.content }}</code></pre>
                  </div>
                  <div v-else class="message-text" v-html="linkify(msg.content)"></div>
                  <div class="message-meta">
                    <span class="message-time">{{ formatTime(msg.timestamp) }}</span>
                    <span v-if="msg.secure" class="secure-badge">E2E</span>
                    <span v-if="msg.direction === 'sent'" class="sent-check">✓✓</span>
                  </div>
                </div>
                <el-button
                  class="copy-btn"
                  link
                  size="small"
                  @click="copyText(msg.content)"
                >
                  {{ t('common.copy') }}
                </el-button>
              </div>
            </transition>
          </template>
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

    <!-- Rename dialog -->
    <el-dialog
      v-model="renameDialogVisible"
      :title="t('tools.transfer.renameTitle')"
      width="360px"
      :close-on-click-modal="true"
    >
      <el-input v-model="renameInput" :placeholder="t('tools.transfer.renamePlaceholder')" maxlength="20" @keydown.enter="confirmRename" />
      <template #footer>
        <el-button @click="renameDialogVisible = false">{{ t('tools.transfer.cancel') }}</el-button>
        <el-button type="primary" @click="confirmRename">{{ t('tools.transfer.confirm') }}</el-button>
      </template>
    </el-dialog>
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
  myId,
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
const renameDialogVisible = ref(false)
const renameInput = ref('')

const AVATAR_COLORS = [
  '#7c3aed', '#4f46e5', '#0891b2', '#059669',
  '#d97706', '#dc2626', '#db2777', '#2563eb',
]

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
  const grid = 5
  const cell = 8
  const pad = 4
  const size = grid * cell + pad * 2

  let rects = `<rect width="${size}" height="${size}" fill="${bg}" rx="6"/>`

  // 5x5 symmetric grid: only compute left 3 columns, mirror
  for (let row = 0; row < grid; row++) {
    for (let col = 0; col < 3; col++) {
      const byteIdx = row * 3 + col
      if (bytes[byteIdx + 2] % 2 === 0) continue
      const x = pad + col * cell
      const y = pad + row * cell
      rects += `<rect x="${x}" y="${y}" width="${cell}" height="${cell}" fill="${fg}"/>`
      // Mirror (skip center column)
      if (col < 2) {
        const mx = pad + (grid - 1 - col) * cell
        rects += `<rect x="${mx}" y="${y}" width="${cell}" height="${cell}" fill="${fg}"/>`
      }
    }
  }

  return `data:image/svg+xml,${encodeURIComponent(`<svg xmlns="http://www.w3.org/2000/svg" width="${size}" height="${size}">${rects}</svg>`)}`
}

function formatTime(ts) {
  const d = new Date(ts)
  return `${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2, '0')}`
}

function formatTimeSeparator(ts) {
  const d = new Date(ts)
  const now = new Date()
  const isToday = d.toDateString() === now.toDateString()
  const time = `${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2, '0')}`
  if (isToday) return time
  return `${(d.getMonth() + 1).toString().padStart(2, '0')}/${d.getDate().toString().padStart(2, '0')} ${time}`
}

function shouldShowTimeSeparator(msgs, idx) {
  if (idx === 0) return true
  const prev = msgs[idx - 1].timestamp
  const curr = msgs[idx].timestamp
  return curr - prev > 5 * 60 * 1000 // 5 min gap
}

function linkify(text) {
  const escaped = text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
  return escaped.replace(
    /(https?:\/\/[^\s<]+)/g,
    '<a href="$1" target="_blank" rel="noopener noreferrer" class="chat-link">$1</a>'
  )
}

function copyText(text) {
  navigator.clipboard.writeText(text).then(() => {
    ElMessage.success(t('common.copySuccess'))
  })
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
/* =========================================
   Layout
   ========================================= */
.transfer-container {
  display: flex;
  height: calc(100vh - 160px);
  min-height: 400px;
  border: 1px solid var(--dt-border-light);
  border-radius: var(--dt-radius-md);
  overflow: hidden;
  background: var(--dt-bg-card);
  position: relative;
}

.transfer-mobile {
  flex-direction: column;
  height: calc(100vh - 140px);
}

/* =========================================
   Connection status banner
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
  background: color-mix(in srgb, var(--dt-warning) 15%, transparent);
  border-bottom: 1px solid color-mix(in srgb, var(--dt-warning) 30%, transparent);
  color: var(--dt-warning);
  font-size: 13px;
  font-weight: 500;
}

.banner-icon {
  font-size: 16px;
}

.banner-retrying {
  font-size: 11px;
  opacity: 0.7;
}

.banner-slide-enter-active,
.banner-slide-leave-active {
  transition: all 0.3s ease;
}

.banner-slide-enter-from,
.banner-slide-leave-to {
  opacity: 0;
  transform: translateY(-100%);
}

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

.mobile-device-strip::-webkit-scrollbar {
  display: none;
}

.mobile-device-avatar {
  cursor: pointer;
  flex-shrink: 0;
  opacity: 0.6;
  transition: opacity 0.2s;
  min-width: 44px;
  min-height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.mobile-device-avatar.active {
  opacity: 1;
}

/* =========================================
   Sidebar (desktop)
   ========================================= */
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
  background: color-mix(in srgb, var(--dt-primary) 12%, transparent);
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

/* Self info + rename */
.self-item {
  background: color-mix(in srgb, var(--dt-primary) 6%, transparent);
  border-left: 3px solid var(--dt-primary);
}

.self-item:hover {
  background: color-mix(in srgb, var(--dt-primary) 10%, transparent);
}

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

.peer-item:hover .rename-icon {
  opacity: 1;
}

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

.peer-item:hover {
  background: var(--dt-bg-hover);
}

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

.empty-peers-icon {
  font-size: 28px;
  opacity: 0.3;
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

.avatar-identicon.small {
  width: 28px;
  height: 28px;
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

/* =========================================
   Chat area
   ========================================= */
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

.chat-messages::-webkit-scrollbar {
  width: 5px;
}

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
  padding: var(--dt-spacing-2xl);
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

/* Message rows */
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

/* Links in messages */
.message-text :deep(.chat-link) {
  color: inherit;
  text-decoration: underline;
  text-decoration-color: rgba(255, 255, 255, 0.4);
  text-underline-offset: 2px;
}

.bubble-received .message-text :deep(.chat-link) {
  color: var(--dt-primary);
  text-decoration-color: color-mix(in srgb, var(--dt-primary) 40%, transparent);
}

.message-code {
  background: rgba(0, 0, 0, 0.06);
  border-radius: var(--dt-radius-sm);
  padding: var(--dt-spacing-sm);
  overflow-x: auto;
}

.bubble-sent .message-code {
  background: rgba(255, 255, 255, 0.1);
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

.bubble-sent .secure-badge {
  background: rgba(255, 255, 255, 0.2);
  color: rgba(255, 255, 255, 0.8);
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

/* Message pop animation */
.msg-pop-enter-active {
  transition: all 0.25s ease-out;
}

.msg-pop-leave-active {
  transition: all 0.15s ease-in;
}

.msg-pop-enter-from {
  opacity: 0;
  transform: translateY(8px) scale(0.96);
}

.msg-pop-leave-to {
  opacity: 0;
  transform: scale(0.96);
}

/* =========================================
   Input area
   ========================================= */
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

/* =========================================
   Responsive
   ========================================= */
@media (max-width: 768px) {
  .message-bubble {
    max-width: 88%;
  }

  .empty-chat-icon {
    font-size: 40px;
  }

  .chat-input :deep(.el-textarea__inner) {
    font-size: 16px;
  }

  .input-actions .el-button {
    min-height: 40px;
  }
}
</style>
