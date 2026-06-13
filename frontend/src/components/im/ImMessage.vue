<template>
  <div
    class="message-row"
    :class="{
      'message-sent': msg.direction === 'sent',
      'message-received': msg.direction === 'received',
    }"
  >
    <div
      class="message-bubble"
      :class="{
        'bubble-sent': msg.direction === 'sent',
        'bubble-received': msg.direction === 'received',
        'bubble-media': msg.msgType === 'image' || msg.msgType === 'video',
        'bubble-file': msg.msgType === 'file',
        'bubble-code': msg.msgType === 'code',
        'long-pressing': isLongPressing,
      }"
      @touchstart.passive="onTouchStart"
      @touchend="onTouchEnd"
      @touchmove.passive="onTouchMove"
    >
      <!-- Group chat: show sender name for received messages -->
      <div v-if="isGroup && msg.direction === 'received'" class="message-sender">
        {{ msg.peerName }}
      </div>

      <!-- Text message -->
      <!-- Text message -->
      <div v-if="msg.msgType === 'text'" class="message-text-wrapper">
        <div class="message-text" :class="{ 'text-collapsed': isTextCollapsed }" ref="textRef" v-html="linkify(msg.content)"></div>
        <button v-if="textNeedsCollapse" class="text-expand-btn" @click="isTextCollapsed = !isTextCollapsed">
          <span class="material-symbols-rounded">{{ isTextCollapsed ? 'expand_more' : 'expand_less' }}</span>
          {{ isTextCollapsed ? t('tools.im.expandText') : t('tools.im.collapseText') }}
        </button>
      </div>

      <!-- Markdown message -->
      <div v-else-if="msg.msgType === 'markdown'" class="message-markdown" v-html="renderedMarkdown"></div>

      <!-- Code message -->
      <ImCodeBlock
        v-else-if="msg.msgType === 'code'"
        :code="msg.content"
        :language="detectedLanguage"
      />

      <!-- Image message -->
      <ImImageMessage
        v-else-if="msg.msgType === 'image'"
        :url="msg.attachment?.url || ''"
        :thumbnail="msg.attachment?.thumbnail || ''"
        :filename="msg.attachment?.filename || ''"
        @preview="$emit('preview-image', msg)"
      />

      <!-- Video message -->
      <div v-else-if="msg.msgType === 'video'" class="video-message" @click="openVideo">
        <div class="video-thumb-wrap">
          <img
            v-if="msg.attachment?.thumbnail"
            :src="msg.attachment.thumbnail"
            class="video-thumb"
            loading="lazy"
          />
          <div v-else class="video-thumb video-thumb--placeholder">
            <span class="material-symbols-rounded">movie</span>
          </div>
          <div class="video-play-overlay">
            <span class="material-symbols-rounded video-play-btn">play_arrow</span>
          </div>
        </div>
        <div v-if="msg.content" class="video-caption">{{ msg.content }}</div>
      </div>

      <!-- File message -->
      <ImFileCard
        v-else-if="msg.msgType === 'file'"
        :filename="msg.attachment?.filename || ''"
        :size="msg.attachment?.size || 0"
        :mime="msg.attachment?.mime || ''"
        :url="msg.attachment?.url || ''"
        :direction="msg.direction"
        @preview-file="$emit('preview-file', $event)"
      />

      <!-- Link message -->
      <div v-else-if="msg.msgType === 'link'" class="message-text" v-html="linkify(msg.content)"></div>

      <!-- Fallback: plain text -->
      <div v-else class="message-text" v-html="linkify(msg.content)"></div>

      <!-- Message meta -->
      <div class="message-meta">
        <span class="message-time">{{ formattedTime }}</span>
        <span v-if="msg.secure" class="secure-badge">E2E</span>
      </div>
    </div>

    <!-- Copy button (visible on hover, desktop only) -->
    <button v-if="!deviceStore.isMobile" class="msg-action-btn" @click="handleCopy" :title="t('common.copy')">
      <span class="material-symbols-rounded">content_copy</span>
    </button>
  </div>
</template>

<script setup>
import { computed, ref, onBeforeUnmount, onMounted, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import { useDeviceStore } from '@/stores/device.js'
import { marked } from 'marked'
import DOMPurify from 'dompurify'
import { copyToClipboard } from '@/utils/format.js'
import ImCodeBlock from './ImCodeBlock.vue'
import ImImageMessage from './ImImageMessage.vue'
import ImFileCard from './ImFileCard.vue'

const props = defineProps({
  msg: {
    type: Object,
    required: true,
  },
  isGroup: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['preview-image', 'delete', 'copy', 'forward', 'long-press', 'preview-file'])

const { t } = useI18n()
const deviceStore = useDeviceStore()

const formattedTime = computed(() => {
  const d = new Date(props.msg.timestamp)
  return `${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2, '0')}`
})

const detectedLanguage = computed(() => {
  if (props.msg.msgType !== 'code') return ''
  const content = props.msg.content || ''
  if (/^#!/.test(content)) return 'bash'
  if (/^import\s/.test(content) && /from\s+['"]/.test(content)) return 'python'
  if (/^(const|let|var|import|export|function|class)\s/.test(content)) return 'javascript'
  if (/^<\?xml/.test(content)) return 'xml'
  if (/^<!DOCTYPE\s+html/.test(content) || /^<html/i.test(content)) return 'html'
  if (/^[\{\[]"/.test(content)) return 'json'
  if (/^(SELECT|INSERT|UPDATE|DELETE|CREATE|ALTER|DROP)\s/i.test(content)) return 'sql'
  if (/^---\s/.test(content) || /^\w+:\s/.test(content.split('\n')[0])) return 'yaml'
  if (/^(#include|using\s+namespace|int\s+main)/.test(content)) return 'cpp'
  if (/^(package|import|public\s+class)/.test(content)) return 'java'
  if (/^func\s/.test(content) && /package\s/.test(content)) return 'go'
  if (/^(fn\s|let\s|pub\s|use\s|mod\s)/.test(content)) return 'rust'
  if (/^(using|namespace|public\s+class)/.test(content)) return 'csharp'
  return ''
})

const renderedMarkdown = computed(() => {
  if (props.msg.msgType !== 'markdown' || !props.msg.content) return ''
  marked.setOptions({ breaks: true, gfm: true, async: false })
  const html = marked.parse(props.msg.content)
  return DOMPurify.sanitize(typeof html === 'string' ? html : '')
})

function linkify(text) {
  if (!text) return ''
  const escaped = text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
  return escaped.replace(
    /(https?:\/\/[^\s<]+)/g,
    '<a href="$1" target="_blank" rel="noopener noreferrer" class="chat-link">$1</a>'
  )
}

// --- Long text collapse ---
const TEXT_MAX_HEIGHT = 200
const textRef = ref(null)
const textNeedsCollapse = ref(false)
const isTextCollapsed = ref(true)

function checkTextHeight() {
  if (textRef.value) {
    textNeedsCollapse.value = textRef.value.scrollHeight > TEXT_MAX_HEIGHT
  }
}

onMounted(() => {
  checkTextHeight()
})

watch(() => props.msg.content, () => {
  isTextCollapsed.value = true
  setTimeout(checkTextHeight, 0)
})

function handleCopy() {
  const text = props.msg.content || ''
  copyToClipboard(text).then(() => {
    ElMessage.success(t('common.copySuccess'))
    emit('copy', text)
  })
}

function openVideo() {
  const url = props.msg.attachment?.url
  if (url) window.open(url, '_blank')
}

// --- Long-press detection (mobile only) ---
const LONG_PRESS_DURATION = 400
const longPressTimer = ref(null)
const isLongPressing = ref(false)

function onTouchStart() {
  if (!deviceStore.isMobile) return
  longPressTimer.value = setTimeout(() => {
    isLongPressing.value = true
    emit('long-press', props.msg)
  }, LONG_PRESS_DURATION)
}

function onTouchEnd() {
  if (longPressTimer.value) {
    clearTimeout(longPressTimer.value)
    longPressTimer.value = null
  }
  setTimeout(() => { isLongPressing.value = false }, 100)
}

function onTouchMove() {
  if (longPressTimer.value) {
    clearTimeout(longPressTimer.value)
    longPressTimer.value = null
  }
}

onBeforeUnmount(() => {
  if (longPressTimer.value) clearTimeout(longPressTimer.value)
})
</script>

<style scoped>
/* =========================================
   Message Row
   ========================================= */
.message-row {
  display: flex;
  align-items: flex-end;
  gap: var(--dt-spacing-xs);
  position: relative;
}

.message-sent {
  flex-direction: row-reverse;
}

/* =========================================
   Message Bubble
   ========================================= */
.message-bubble {
  max-width: 70%;
  padding: var(--dt-spacing-sm) var(--dt-spacing-md);
  border-radius: var(--dt-radius-lg);
  font-size: var(--dt-font-size-sm);
  line-height: 1.5;
  word-break: break-word;
  transition: transform 0.1s ease, opacity 0.1s ease;
}

.message-bubble.long-pressing {
  transform: scale(0.97);
  opacity: 0.85;
}

.bubble-sent {
  background: linear-gradient(135deg, color-mix(in srgb, var(--dt-primary) 85%, #6366f1), color-mix(in srgb, var(--dt-primary) 92%, #0ea5e9));
  color: #fff;
  border-bottom-right-radius: var(--dt-radius-sm);
  box-shadow: 0 1px 3px color-mix(in srgb, var(--dt-primary) 20%, transparent);
}

.bubble-received {
  background: var(--dt-bg-card);
  color: var(--dt-text-primary);
  border: 1px solid var(--dt-border-lighter);
  border-bottom-left-radius: var(--dt-radius-sm);
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
}

/* Media bubbles: no background, no padding — image IS the content */
.bubble-media {
  background: transparent !important;
  border: none !important;
  padding: 0 !important;
  box-shadow: none !important;
}
.bubble-media .message-meta {
  padding: 2px 4px 0;
}

/* File bubbles: transparent wrapper — file card provides its own visual identity */
.bubble-file {
  background: transparent !important;
  border: none !important;
  padding: 0 !important;
  box-shadow: none !important;
}
.bubble-file .message-meta {
  padding: 2px 4px 0;
}
/* In sent direction, keep meta text legible */
.bubble-file.message-bubble .message-time {
  color: var(--dt-text-secondary);
  opacity: 0.7;
}

/* Code bubbles: transparent wrapper — code block has its own dark bg */
.bubble-code {
  background: transparent !important;
  border: none !important;
  padding: 0 !important;
  box-shadow: none !important;
}
.bubble-code .message-meta {
  padding: 2px 4px 0;
}
.bubble-code.message-bubble .message-time {
  color: var(--dt-text-secondary);
  opacity: 0.7;
}

/* =========================================
   Message Sender (group chat)
   ========================================= */
.message-sender {
  font-size: var(--dt-font-size-xs);
  color: var(--dt-text-secondary);
  font-weight: 500;
  margin-bottom: 4px;
}

/* =========================================
   Message Text
   ========================================= */
.message-text-wrapper {
  min-width: 0;
}

.message-text {
  white-space: pre-wrap;
  overflow-wrap: anywhere;
  overflow: hidden;
  transition: max-height 0.25s ease;
}

.message-text.text-collapsed {
  max-height: 200px;
  overflow-y: auto;
  -webkit-overflow-scrolling: touch;
}

.text-expand-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-top: 6px;
  padding: 4px 8px;
  border: none;
  border-radius: var(--dt-radius-sm);
  background: rgba(0, 0, 0, 0.06);
  color: var(--dt-text-secondary);
  font-size: 12px;
  cursor: pointer;
  transition: background 0.15s;
}

.text-expand-btn:hover {
  background: rgba(0, 0, 0, 0.1);
}

.text-expand-btn .material-symbols-rounded {
  font-size: 16px;
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

/* =========================================
   Markdown Content
   ========================================= */
.message-markdown {
  font-size: var(--dt-font-size-sm);
  line-height: 1.6;
  overflow-wrap: anywhere;
  word-break: break-word;
}
.message-markdown :deep(h1),
.message-markdown :deep(h2),
.message-markdown :deep(h3),
.message-markdown :deep(h4) {
  margin: 0.5em 0 0.3em;
  font-weight: 600;
  line-height: 1.3;
}
.message-markdown :deep(h1) { font-size: 1.3em; }
.message-markdown :deep(h2) { font-size: 1.15em; }
.message-markdown :deep(h3) { font-size: 1.05em; }
.message-markdown :deep(p) {
  margin: 0.4em 0;
}
.message-markdown :deep(ul),
.message-markdown :deep(ol) {
  margin: 0.4em 0;
  padding-left: 1.5em;
}
.message-markdown :deep(li) {
  margin: 0.15em 0;
}
.message-markdown :deep(blockquote) {
  margin: 0.5em 0;
  padding: 0.3em 0.8em;
  border-left: 3px solid var(--dt-primary);
  opacity: 0.85;
}
.message-markdown :deep(code) {
  font-family: 'Consolas', 'Monaco', 'Fira Code', monospace;
  font-size: 0.9em;
  padding: 0.15em 0.4em;
  border-radius: 3px;
  background: rgba(0, 0, 0, 0.15);
}
.bubble-received .message-markdown :deep(code) {
  background: var(--dt-bg-section);
}
.message-markdown :deep(pre) {
  margin: 0.5em 0;
  border-radius: var(--dt-radius-sm);
  overflow-x: auto;
}
.message-markdown :deep(pre code) {
  display: block;
  padding: 0.6em 0.8em;
  background: #1e1e2e;
  color: #cdd6f4;
  font-size: var(--dt-font-size-xs);
  line-height: 1.5;
}
.message-markdown :deep(hr) {
  border: none;
  border-top: 1px solid var(--dt-border-light);
  margin: 0.6em 0;
}
.message-markdown :deep(table) {
  border-collapse: collapse;
  margin: 0.5em 0;
  font-size: 0.9em;
}
.message-markdown :deep(th),
.message-markdown :deep(td) {
  border: 1px solid var(--dt-border-light);
  padding: 0.3em 0.6em;
  text-align: left;
}
.message-markdown :deep(th) {
  background: rgba(0, 0, 0, 0.06);
  font-weight: 600;
}
.message-markdown :deep(strong) {
  font-weight: 600;
}
.message-markdown :deep(em) {
  font-style: italic;
}
.message-markdown :deep(a) {
  color: inherit;
  text-decoration: underline;
}

/* =========================================
   Message Meta
   ========================================= */
.message-meta {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 4px;
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
  border-radius: var(--dt-radius-sm);
}

.bubble-sent .secure-badge {
  background: rgba(255, 255, 255, 0.2);
  color: rgba(255, 255, 255, 0.8);
}

/* =========================================
   Copy Action Button
   ========================================= */
.msg-action-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border: none;
  background: none;
  border-radius: var(--dt-radius-sm);
  cursor: pointer;
  color: var(--dt-text-placeholder);
  opacity: 0;
  transition: opacity 0.15s ease, background 0.15s ease, color 0.15s ease;
  flex-shrink: 0;
}

.message-row:hover .msg-action-btn {
  opacity: 1;
}

.msg-action-btn:hover {
  background: var(--dt-bg-hover);
  color: var(--dt-text-secondary);
}

.msg-action-btn .material-symbols-rounded {
  font-size: 16px;
}

/* =========================================
   Video message
   Video message
   ========================================= */
.video-message {
  cursor: pointer;
  max-width: 280px;
}
.video-thumb-wrap {
  position: relative;
  border-radius: 8px;
  overflow: hidden;
}
.video-thumb {
  width: 100%;
  max-height: 200px;
  object-fit: cover;
  display: block;
  border-radius: 8px;
}
.video-thumb--placeholder {
  height: 120px;
  background: var(--dt-bg-hover, #2a2a2a);
  display: flex;
  align-items: center;
  justify-content: center;
}
.video-thumb--placeholder .material-symbols-rounded {
  font-size: 40px;
  color: var(--dt-text-secondary);
  opacity: 0.5;
}
.video-play-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0,0,0,0.3);
  transition: background 0.15s;
}
.video-message:hover .video-play-overlay {
  background: rgba(0,0,0,0.45);
}
.video-play-btn {
  font-size: 40px;
  color: #fff;
}
.video-caption {
  font-size: 13px;
  color: var(--dt-text-secondary);
  margin-top: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* =========================================
   Responsive
   ========================================= */
@media (max-width: 768px) {
  .message-bubble {
    max-width: 88%;
  }
}
</style>
