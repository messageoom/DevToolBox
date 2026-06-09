<template>
  <div
    class="im-chat-input"
    :class="{ 'im-chat-input--mobile': deviceStore.isMobile, 'im-chat-input--disabled': disabled }"
    @dragenter.prevent.stop="onDragEnter"
    @dragover.prevent.stop="onDragOver"
    @dragleave.prevent.stop="onDragLeave"
    @drop.prevent.stop="onDrop"
  >
    <div class="input-row">
      <div class="action-buttons">
        <button
          class="action-btn"
          :disabled="disabled"
          :title="t('tools.im.uploadFile')"
          @click="triggerFileInput"
        >
          <span class="material-symbols-rounded">attach_file</span>
        </button>
        <button
          class="action-btn"
          :disabled="disabled"
          :title="t('tools.im.uploadImage')"
          @click="triggerImageInput"
        >
          <span class="material-symbols-rounded">image</span>
        </button>
      </div>

      <el-input
        ref="textareaRef"
        v-model="inputText"
        type="textarea"
        :autosize="{ minRows: 1, maxRows: 6 }"
        :placeholder="t('tools.im.inputPlaceholder')"
        :disabled="disabled"
        class="chat-textarea"
        @keydown.enter.exact.prevent="handleSend"
        @paste="onPaste"
      />

      <el-button
        v-if="!deviceStore.isMobile || inputText.trim()"
        type="primary"
        :class="deviceStore.isMobile ? 'send-btn-mobile-inline' : 'send-btn'"
        :disabled="disabled || !inputText.trim()"
        @click="handleSend"
      >
        <span v-if="deviceStore.isMobile" class="material-symbols-rounded">send</span>
        <span v-else>{{ t('tools.im.send') }}</span>
      </el-button>
    </div>

    <!-- Hidden file inputs -->
    <input
      ref="fileInputRef"
      type="file"
      multiple
      class="hidden-input"
      @change="onFileSelected"
    />
    <input
      ref="imageInputRef"
      type="file"
      accept="image/*"
      multiple
      class="hidden-input"
      @change="onImageSelected"
    />

    <!-- Drag overlay -->
    <transition name="overlay-fade">
      <div v-if="isDragging" class="drag-overlay">
        <span class="material-symbols-rounded drag-icon">cloud_upload</span>
        <span class="drag-text">{{ t('tools.im.dropFiles') }}</span>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import { useI18n } from 'vue-i18n'
import { useDeviceStore } from '@/stores/device.js'

const { t } = useI18n()
const deviceStore = useDeviceStore()

const props = defineProps({
  disabled: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['send', 'upload-file', 'upload-image'])

const inputText = ref('')
const isDragging = ref(false)
const dragCounter = ref(0)

const textareaRef = ref(null)
const fileInputRef = ref(null)
const imageInputRef = ref(null)

function detectMsgType(text) {
  const trimmed = text.trim()
  if (/^```[\s\S]*```$/.test(trimmed)) return 'code'
  if (/^[a-zA-Z0-9+/=]{20,}$/.test(trimmed)) return 'code'
  if (/[{}\[\];]/.test(trimmed) && trimmed.split('\n').length > 3) return 'code'
  if (/^https?:\/\//.test(trimmed)) return 'link'
  return 'text'
}

function handleSend() {
  const content = inputText.value
  if (!content.trim() || props.disabled) return

  const msgType = detectMsgType(content)
  emit('send', content, msgType, null)
  inputText.value = ''

  nextTick(() => {
    if (textareaRef.value) {
      textareaRef.value.focus()
    }
  })
}

function triggerFileInput() {
  if (props.disabled) return
  fileInputRef.value?.click()
}

function triggerImageInput() {
  if (props.disabled) return
  imageInputRef.value?.click()
}

function onFileSelected(e) {
  const files = e.target.files
  if (!files || files.length === 0) return

  for (let i = 0; i < files.length; i++) {
    emit('upload-file', files[i])
  }

  // Reset so selecting the same file again triggers the event
  e.target.value = ''
}

function onImageSelected(e) {
  const files = e.target.files
  if (!files || files.length === 0) return

  for (let i = 0; i < files.length; i++) {
    emit('upload-image', files[i])
  }

  e.target.value = ''
}

// --- Drag & Drop ---

function onDragEnter() {
  dragCounter.value++
  isDragging.value = true
}

function onDragOver() {
  // Required to allow drop; nothing else needed
}

function onDragLeave() {
  dragCounter.value--
  if (dragCounter.value <= 0) {
    dragCounter.value = 0
    isDragging.value = false
  }
}

function onDrop(e) {
  dragCounter.value = 0
  isDragging.value = false

  const files = e.dataTransfer?.files
  if (!files || files.length === 0) return

  for (let i = 0; i < files.length; i++) {
    const file = files[i]
    if (file.type.startsWith('image/')) {
      emit('upload-image', file)
    } else {
      emit('upload-file', file)
    }
  }
}

// --- Paste Upload ---

function onPaste(e) {
  const items = e.clipboardData?.items
  if (!items) return

  for (let i = 0; i < items.length; i++) {
    const item = items[i]
    if (item.type.startsWith('image/')) {
      e.preventDefault()
      const file = item.getAsFile()
      if (file) {
        emit('upload-image', file)
      }
      return
    }
  }
  // If no image, let text paste through normally
}
</script>

<style scoped>
.im-chat-input {
  position: relative;
  border-top: 1px solid var(--dt-border-light);
  background: var(--dt-bg-card);
  padding: var(--dt-spacing-sm) var(--dt-spacing-md);
}

.im-chat-input--disabled {
  opacity: 0.5;
  pointer-events: none;
}

/* --- Input Row --- */

.input-row {
  display: flex;
  align-items: flex-end;
  gap: var(--dt-spacing-sm);
}

.action-buttons {
  display: flex;
  gap: 2px;
  flex-shrink: 0;
  padding-bottom: 4px;
}

.action-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border: none;
  background: transparent;
  border-radius: var(--dt-radius-sm);
  cursor: pointer;
  color: var(--dt-text-secondary);
  transition: background 0.15s, color 0.15s;
}

.action-btn:hover:not(:disabled) {
  background: var(--dt-bg-hover);
  color: var(--dt-text-primary);
}

.action-btn:disabled {
  cursor: not-allowed;
  opacity: 0.5;
}

.action-btn .material-symbols-rounded {
  font-size: 20px;
}

/* --- Textarea --- */

.chat-textarea {
  flex: 1;
  min-width: 0;
}

.chat-textarea :deep(.el-textarea__inner) {
  padding: 6px 10px;
  line-height: 1.5;
}

/* --- Send Button --- */

.send-btn {
  flex-shrink: 0;
}

.send-btn-mobile-inline {
  flex-shrink: 0;
  min-width: 36px;
  width: 36px;
  height: 36px;
  padding: 0;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: opacity 0.15s ease, transform 0.15s ease;
}

.send-btn-mobile-inline .material-symbols-rounded {
  font-size: 20px;
}

/* --- Hidden Inputs --- */

.hidden-input {
  display: none;
}

/* --- Drag Overlay --- */

.drag-overlay {
  position: absolute;
  inset: 0;
  z-index: 10;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: var(--dt-spacing-sm);
  background: rgba(0, 0, 0, 0.5);
  border-radius: var(--dt-radius-md);
  pointer-events: none;
}

.drag-icon {
  font-size: 48px;
  color: #fff;
}

.drag-text {
  font-size: var(--dt-font-size-base);
  color: #fff;
  font-weight: 500;
}

/* Overlay transition */
.overlay-fade-enter-active,
.overlay-fade-leave-active {
  transition: opacity 0.2s ease;
}

.overlay-fade-enter-from,
.overlay-fade-leave-to {
  opacity: 0;
}

/* --- Mobile --- */

@media (max-width: 768px) {
  .chat-textarea :deep(.el-textarea__inner) {
    font-size: 16px; /* Prevent iOS zoom */
  }
}
</style>
