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
    <!-- Teleport to body to escape grid stacking context on iOS Safari,
         so the overlay's top bar and bottom input aren't clipped by
         app-header / app-bottom-nav. -->
    <Teleport to="body">
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
                <span v-else-if="p2pStatus[activePeer.nodeId] === 'ready'" class="tg-bar-status tg-bar-status--p2p">{{ t('tools.im.p2pDirect') }}</span>
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
          <div class="tg-messages" ref="messagesContainer" @scroll="onMessagesScroll">
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
                @long-press="onMessageLongPress"
                @preview-file="onPreviewFile"
              />
            </template>
          </div>

          <!-- Scroll-to-bottom floating button -->
          <transition name="scroll-btn-fade">
            <button
              v-if="!isAtBottom"
              class="scroll-to-bottom-btn"
              @click="scrollToBottom"
            >
              <span class="material-symbols-rounded">keyboard_arrow_down</span>
              <span v-if="unreadScrollCount > 0" class="scroll-btn-badge">
                {{ unreadScrollCount > 99 ? '99+' : unreadScrollCount }}
              </span>
            </button>
          </transition>

          <!-- Fixed bottom input -->
          <ImChatInput
            :disabled="!connected"
            @send="onSend"
            @upload-file="onUploadFile"
            @upload-image="onUploadImage"
          />
        </div>
      </transition>
    </Teleport>

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
          <div class="avatar-circle avatar-group"><span class="material-symbols-rounded">groups</span></div>
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
            <div class="avatar-circle small avatar-group"><span class="material-symbols-rounded">groups</span></div>
            <span class="chat-target-name">{{ t('tools.im.groupChat') }}</span>
          </template>
        </div>

        <div class="chat-messages" ref="messagesContainer" @scroll="onMessagesScroll">
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
              @long-press="onMessageLongPress"
              @preview-file="onPreviewFile"
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

  <!-- Mobile action sheet for message actions -->
  <el-drawer
    v-if="deviceStore.isMobile"
    v-model="actionSheetVisible"
    direction="btt"
    :size="'auto'"
    :show-close="false"
    :with-header="false"
    class="msg-action-sheet"
  >
    <div class="action-sheet-list">
      <button class="action-sheet-item" @click="actionCopy">
        <span class="material-symbols-rounded">content_copy</span>
        <span>{{ t('common.copy') }}</span>
      </button>
      <button class="action-sheet-item" @click="actionForward">
        <span class="material-symbols-rounded">forward</span>
        <span>{{ t('tools.im.forward') }}</span>
      </button>
      <button class="action-sheet-item action-sheet-item--danger" @click="actionDelete">
        <span class="material-symbols-rounded">delete</span>
        <span>{{ t('common.delete') }}</span>
      </button>
    </div>
    <button class="action-sheet-cancel" @click="actionSheetVisible = false">
      {{ t('tools.im.cancel') }}
    </button>
  </el-drawer>

  <!-- File preview drawer (md / html / code) -->
  <el-drawer
    v-model="filePreviewVisible"
    :title="filePreviewName"
    direction="btt"
    size="90%"
    class="file-preview-drawer"
  >
    <div v-if="filePreviewType === 'md'" class="file-preview-md" v-html="filePreviewContent"></div>
    <div v-else-if="filePreviewType === 'code'" class="file-preview-code">
      <pre><code class="hljs" v-html="filePreviewContent"></code></pre>
    </div>
    <iframe
      v-else-if="filePreviewType === 'html'"
      :srcdoc="filePreviewContent"
      class="file-preview-iframe"
      sandbox="allow-same-origin"
    ></iframe>
  </el-drawer>
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
import { copyToClipboard } from '@/utils/format.js'
import { marked } from 'marked'
import DOMPurify from 'dompurify'
import hljs from 'highlight.js/lib/core'
import javascript from 'highlight.js/lib/languages/javascript'
import python from 'highlight.js/lib/languages/python'
import css from 'highlight.js/lib/languages/css'
import xml from 'highlight.js/lib/languages/xml'
import json from 'highlight.js/lib/languages/json'
import bash from 'highlight.js/lib/languages/bash'
import sql from 'highlight.js/lib/languages/sql'
import java from 'highlight.js/lib/languages/java'
import cpp from 'highlight.js/lib/languages/cpp'
import csharp from 'highlight.js/lib/languages/csharp'
import go from 'highlight.js/lib/languages/go'
import rust from 'highlight.js/lib/languages/rust'
import yaml from 'highlight.js/lib/languages/yaml'
import ini from 'highlight.js/lib/languages/ini'
import ruby from 'highlight.js/lib/languages/ruby'
import php from 'highlight.js/lib/languages/php'
import typescript from 'highlight.js/lib/languages/typescript'
import plaintext from 'highlight.js/lib/languages/plaintext'
import 'highlight.js/styles/github-dark.min.css'

hljs.registerLanguage('javascript', javascript)
hljs.registerLanguage('js', javascript)
hljs.registerLanguage('typescript', typescript)
hljs.registerLanguage('ts', typescript)
hljs.registerLanguage('python', python)
hljs.registerLanguage('py', python)
hljs.registerLanguage('css', css)
hljs.registerLanguage('html', xml)
hljs.registerLanguage('xml', xml)
hljs.registerLanguage('json', json)
hljs.registerLanguage('bash', bash)
hljs.registerLanguage('shell', bash)
hljs.registerLanguage('sh', bash)
hljs.registerLanguage('sql', sql)
hljs.registerLanguage('java', java)
hljs.registerLanguage('cpp', cpp)
hljs.registerLanguage('c', cpp)
hljs.registerLanguage('csharp', csharp)
hljs.registerLanguage('cs', csharp)
hljs.registerLanguage('go', go)
hljs.registerLanguage('rust', rust)
hljs.registerLanguage('yaml', yaml)
hljs.registerLanguage('yml', yaml)
hljs.registerLanguage('ini', ini)
hljs.registerLanguage('ruby', ruby)
hljs.registerLanguage('rb', ruby)
hljs.registerLanguage('php', php)
hljs.registerLanguage('plaintext', plaintext)
hljs.registerLanguage('text', plaintext)
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
const actionSheetVisible = ref(false)
const actionSheetMsg = ref(null)
const isAtBottom = ref(true)
const unreadScrollCount = ref(0)
const filePreviewVisible = ref(false)
const filePreviewName = ref('')
const filePreviewType = ref('')
const filePreviewContent = ref('')

// Close overlay AND disconnect SocketIO before the page-slide leave transition.
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
    let c = 0
    for (let i = msgs.length - 1; i >= 0; i--) {
      if (msgs[i].direction === 'sent') break
      c++
    }
    return c
  }
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

// --- Mobile long-press action sheet ---
function onMessageLongPress(msg) {
  actionSheetMsg.value = msg
  actionSheetVisible.value = true
}
function actionCopy() {
  if (!actionSheetMsg.value) return
  const text = actionSheetMsg.value.content || ''
  copyToClipboard(text).then(() => {
    ElMessage.success(t('common.copySuccess'))
  })
  actionSheetVisible.value = false
}
function actionForward() {
  if (!actionSheetMsg.value) return
  forwardMessage(actionSheetMsg.value, null)
  ElMessage.success(t('tools.im.forwarded'))
  actionSheetVisible.value = false
}
function actionDelete() {
  if (!actionSheetMsg.value) return
  deleteMessage(actionSheetMsg.value.id, activePeer.value?.nodeId || 'group')
  actionSheetVisible.value = false
}

function openLightboxForImage(msg) {
  const imgs = activeMessages.value
    .filter(m => m.msgType === 'image' && m.attachment?.url)
    .map(m => ({ url: m.attachment.url, thumbnail: m.attachment.thumbnail || '', filename: m.attachment.filename || '' }))
  lightbox.open(imgs, Math.max(0, imgs.findIndex(img => img.url === msg.attachment?.url)))
}
async function onPreviewFile({ url, filename, mime }) {
  const name = (filename || '').toLowerCase()
  const isHtml = name.endsWith('.html') || name.endsWith('.htm') || (mime && mime.includes('html'))
  const isMd = name.endsWith('.md') || name.endsWith('.markdown') || (mime && mime.includes('markdown'))

  filePreviewName.value = filename || 'Preview'
  filePreviewContent.value = ''
  filePreviewType.value = isMd ? 'md' : isHtml ? 'html' : 'code'

  try {
    const resp = await fetch(url)
    const text = await resp.text()
    if (isMd) {
      marked.setOptions({ breaks: true, gfm: true, async: false })
      const html = marked.parse(text)
      filePreviewContent.value = DOMPurify.sanitize(typeof html === 'string' ? html : '')
    } else if (isHtml) {
      filePreviewContent.value = DOMPurify.sanitize(text)
    } else {
      // Code preview: use highlight.js for syntax highlighting
      const ext = name.includes('.') ? name.split('.').pop() : ''
      const langMap = { py: 'python', js: 'javascript', ts: 'typescript', jsx: 'javascript', tsx: 'typescript',
        rb: 'ruby', yml: 'yaml', sh: 'bash', bash: 'bash', zsh: 'bash', rs: 'rust', go: 'go',
        kt: 'java', scala: 'java', conf: 'ini', cfg: 'ini' }
      const lang = langMap[ext] || ext
      if (lang && hljs.getLanguage(lang)) {
        filePreviewContent.value = hljs.highlight(text, { language: lang }).value
      } else {
        filePreviewContent.value = hljs.highlightAuto(text).value
      }
    }
  } catch {
    filePreviewContent.value = isMd ? '*Failed to load file*' : ''
  }
  filePreviewVisible.value = true
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
    isAtBottom.value = true
    unreadScrollCount.value = 0
  }
}
function onMessagesScroll() {
  const el = messagesContainer.value
  if (!el) return
  const threshold = 60
  const atBottom = el.scrollTop + el.clientHeight >= el.scrollHeight - threshold
  if (atBottom && !isAtBottom.value) {
    unreadScrollCount.value = 0
  }
  isAtBottom.value = atBottom
}
watch(activeMessages, (newVal, oldVal) => {
  const newCount = newVal.length - (oldVal?.length || 0)
  if (isAtBottom.value) {
    nextTick(scrollToBottom)
  } else if (newCount > 0) {
    unreadScrollCount.value += newCount
  }
}, { deep: true })
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
  z-index: 9999;
  display: flex;
  flex-direction: column;
  background: var(--dt-bg-page);
  box-sizing: border-box;
  padding-bottom: env(safe-area-inset-bottom, 0px);
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
  background: var(--dt-danger, #f56c6c);
  transition: background 0.3s;
}
.p2p-dot.online {
  background: var(--dt-success, #67c23a);
}
.p2p-dot.online.p2p-ready {
  box-shadow: 0 0 4px var(--dt-success, #67c23a);
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
  padding-top: calc(env(safe-area-inset-top, 0px) + 8px);
  flex-shrink: 0;
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
.tg-bar-status--p2p {
  color: var(--dt-success, #67c23a);
  font-weight: 500;
}

/* Scroll-to-bottom button */
.scroll-to-bottom-btn {
  position: absolute;
  bottom: 70px;
  right: 16px;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: none;
  background: var(--dt-bg-card);
  box-shadow: var(--dt-shadow-md);
  color: var(--dt-text-secondary);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10;
  transition: transform 0.2s ease;
}
.scroll-to-bottom-btn:active {
  transform: scale(0.92);
}
.scroll-to-bottom-btn .material-symbols-rounded {
  font-size: 24px;
}
.scroll-btn-badge {
  position: absolute;
  top: -4px;
  right: -4px;
  min-width: 18px;
  height: 18px;
  background: var(--dt-danger, #f56c6c);
  color: #fff;
  font-size: 11px;
  font-weight: 600;
  border-radius: 9px;
  padding: 0 5px;
  display: flex;
  align-items: center;
  justify-content: center;
  line-height: 1;
}
.scroll-btn-fade-enter-active,
.scroll-btn-fade-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}
.scroll-btn-fade-enter-from,
.scroll-btn-fade-leave-to {
  opacity: 0;
  transform: scale(0.8);
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
.avatar-circle { width: 36px; height: 36px; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: #fff; font-size: 14px; flex-shrink: 0; }
.avatar-circle .material-symbols-rounded { font-size: 20px; }
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

/* ===== Mobile action sheet ===== */
.msg-action-sheet :deep(.el-drawer__body) {
  padding: 0;
  background: var(--dt-bg-card);
}
.action-sheet-list {
  padding: 8px 0;
}
.action-sheet-item {
  display: flex;
  align-items: center;
  gap: 16px;
  width: 100%;
  padding: 14px 20px;
  border: none;
  background: none;
  font-size: 16px;
  color: var(--dt-text-primary);
  cursor: pointer;
  text-align: left;
}
.action-sheet-item:active {
  background: var(--dt-bg-hover);
}
.action-sheet-item .material-symbols-rounded {
  font-size: 22px;
  color: var(--dt-text-secondary);
}
.action-sheet-item--danger {
  color: var(--dt-danger, #f56c6c);
}
.action-sheet-item--danger .material-symbols-rounded {
  color: var(--dt-danger, #f56c6c);
}
.action-sheet-cancel {
  display: block;
  width: calc(100% - 32px);
  margin: 8px 16px 16px;
  padding: 12px;
  border: none;
  border-radius: var(--dt-radius-md);
  background: var(--dt-bg-section);
  color: var(--dt-text-secondary);
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  text-align: center;
}
.action-sheet-cancel:active {
  background: var(--dt-bg-hover);
}

/* ===== File preview drawer ===== */
.file-preview-drawer :deep(.el-drawer__header) {
  margin-bottom: 0;
  padding: 16px 20px;
  border-bottom: 1px solid var(--dt-border-light);
}
.file-preview-drawer :deep(.el-drawer__body) {
  padding: 0;
  background: var(--dt-bg-page);
}
.file-preview-md {
  padding: 20px;
  overflow-y: auto;
  height: 100%;
  font-size: var(--dt-font-size-sm);
  line-height: 1.6;
  color: var(--dt-text-primary);
}
.file-preview-md :deep(h1),
.file-preview-md :deep(h2),
.file-preview-md :deep(h3),
.file-preview-md :deep(h4) {
  margin: 0.8em 0 0.4em;
  font-weight: 600;
}
.file-preview-md :deep(h1) { font-size: 1.4em; }
.file-preview-md :deep(h2) { font-size: 1.2em; }
.file-preview-md :deep(h3) { font-size: 1.1em; }
.file-preview-md :deep(p) { margin: 0.5em 0; }
.file-preview-md :deep(ul),
.file-preview-md :deep(ol) { margin: 0.5em 0; padding-left: 1.5em; }
.file-preview-md :deep(blockquote) {
  margin: 0.5em 0;
  padding: 0.4em 1em;
  border-left: 3px solid var(--dt-primary);
  opacity: 0.85;
}
.file-preview-md :deep(code) {
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 0.9em;
  padding: 0.15em 0.4em;
  border-radius: 3px;
  background: var(--dt-bg-section);
}
.file-preview-md :deep(pre) {
  margin: 0.6em 0;
  border-radius: var(--dt-radius-sm);
  overflow-x: auto;
}
.file-preview-md :deep(pre code) {
  display: block;
  padding: 0.8em;
  background: #1e1e2e;
  color: #cdd6f4;
}
.file-preview-md :deep(table) {
  border-collapse: collapse;
  margin: 0.5em 0;
}
.file-preview-md :deep(th),
.file-preview-md :deep(td) {
  border: 1px solid var(--dt-border-light);
  padding: 0.4em 0.8em;
  text-align: left;
}
.file-preview-md :deep(th) {
  background: var(--dt-bg-section);
  font-weight: 600;
}
.file-preview-md :deep(hr) {
  border: none;
  border-top: 1px solid var(--dt-border-light);
  margin: 1em 0;
}
.file-preview-md :deep(img) {
  max-width: 100%;
  border-radius: var(--dt-radius-sm);
}
.file-preview-iframe {
  width: 100%;
  height: 100%;
  border: none;
  background: #fff;
}
.file-preview-code {
  height: 100%;
  overflow-y: auto;
  background: #1e1e2e;
}
.file-preview-code pre {
  margin: 0;
  padding: 16px;
  min-height: 100%;
}
.file-preview-code pre code {
  font-family: 'Consolas', 'Monaco', 'Fira Code', monospace;
  font-size: var(--dt-font-size-xs);
  line-height: 1.5;
  white-space: pre;
}
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
