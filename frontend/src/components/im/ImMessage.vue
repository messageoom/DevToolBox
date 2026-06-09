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
      }"
    >
      <!-- Group chat: show sender name for received messages -->
      <div v-if="isGroup && msg.direction === 'received'" class="message-sender">
        {{ msg.peerName }}
      </div>

      <!-- Text message -->
      <div v-if="msg.msgType === 'text'" class="message-text" v-html="linkify(msg.content)"></div>

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

    <!-- Copy button (visible on hover) -->
    <button class="msg-action-btn" @click="handleCopy" :title="t('common.copy')">
      <span class="material-symbols-rounded">content_copy</span>
    </button>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import ImCodeBlock from './ImCodeBlock.vue'
import ImImageMessage from './ImImageMessage.vue'
import ImFileCard from './ImFileCard.vue'

const props = defineProps({
  msg: {
    type: Object,
    required: true,
    // { id, content, msgType, attachment, direction, peerName, timestamp, secure }
  },
  isGroup: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['preview-image', 'delete', 'copy', 'forward'])

const { t } = useI18n()

const formattedTime = computed(() => {
  const d = new Date(props.msg.timestamp)
  return `${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2, '0')}`
})

const detectedLanguage = computed(() => {
  if (props.msg.msgType !== 'code') return ''
  const content = props.msg.content || ''
  // Try to detect language from common patterns
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
  // No specific match, let highlight.js auto-detect
  return ''
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

function handleCopy() {
  const text = props.msg.content || ''
  navigator.clipboard.writeText(text).then(() => {
    ElMessage.success(t('common.copySuccess'))
    emit('copy', text)
  })
}

function openVideo() {
  const url = props.msg.attachment?.url
  if (url) window.open(url, '_blank')
}
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
}

.bubble-sent {
  background: var(--dt-primary);
  color: #fff;
  border-bottom-right-radius: var(--dt-radius-sm);
}

.bubble-received {
  background: var(--dt-bg-card);
  color: var(--dt-text-primary);
  border: 1px solid var(--dt-border-lighter);
  border-bottom-left-radius: var(--dt-radius-sm);
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
   Override ImCodeBlock inside sent bubble
   ========================================= */
.bubble-sent :deep(.im-code-block) {
  border: 1px solid rgba(255, 255, 255, 0.1);
}

/* =========================================
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
