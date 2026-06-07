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
