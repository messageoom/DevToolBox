<template>
  <div class="im-file-card">
    <div class="file-icon-wrap">
      <span class="material-symbols-rounded file-icon">{{ fileIcon }}</span>
    </div>
    <div class="file-info">
      <div class="file-name" :title="filename">{{ filename }}</div>
      <div class="file-size">{{ formattedSize }}</div>
    </div>
    <a
      v-if="url"
      class="file-download-btn"
      :href="url"
      target="_blank"
      rel="noopener noreferrer"
      title="Download"
    >
      <span class="material-symbols-rounded">download</span>
    </a>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  filename: {
    type: String,
    default: '',
  },
  size: {
    type: Number,
    default: 0,
  },
  mime: {
    type: String,
    default: '',
  },
  url: {
    type: String,
    default: '',
  },
})

const fileIcon = computed(() => {
  const mime = props.mime.toLowerCase()
  if (mime.startsWith('image/')) return 'image'
  if (mime.startsWith('video/')) return 'videocam'
  if (mime.startsWith('audio/')) return 'audiotrack'
  if (mime === 'application/pdf') return 'picture_as_pdf'
  if (mime === 'application/zip' || mime.startsWith('application/x-')) return 'folder_zip'
  if (mime.startsWith('text/')) return 'description'
  return 'draft'
})

const formattedSize = computed(() => {
  const bytes = props.size
  if (bytes < 1024) {
    return `${bytes} B`
  }
  if (bytes < 1024 * 1024) {
    return `${(bytes / 1024).toFixed(1)} KB`
  }
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
})
</script>

<style scoped>
.im-file-card {
  display: flex;
  align-items: center;
  gap: var(--dt-spacing-sm);
  padding: var(--dt-spacing-sm) var(--dt-spacing-md);
  background: var(--dt-bg-section);
  border: 1px solid var(--dt-border-lighter);
  border-radius: var(--dt-radius-md);
  min-width: 220px;
  max-width: 320px;
  transition: background 0.15s ease;
}

.im-file-card:hover {
  background: var(--dt-bg-hover);
}

.file-icon-wrap {
  width: 40px;
  height: 40px;
  border-radius: var(--dt-radius-sm);
  background: color-mix(in srgb, var(--dt-primary) 10%, transparent);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.file-icon {
  font-size: 22px;
  color: var(--dt-primary);
}

.file-info {
  flex: 1;
  min-width: 0;
}

.file-name {
  font-size: var(--dt-font-size-sm);
  font-weight: 500;
  color: var(--dt-text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.file-size {
  font-size: var(--dt-font-size-xs);
  color: var(--dt-text-secondary);
  margin-top: 2px;
}

.file-download-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: var(--dt-radius-sm);
  color: var(--dt-text-secondary);
  text-decoration: none;
  transition: all 0.15s ease;
  flex-shrink: 0;
}

.file-download-btn:hover {
  background: color-mix(in srgb, var(--dt-primary) 10%, transparent);
  color: var(--dt-primary);
}

.file-download-btn .material-symbols-rounded {
  font-size: 20px;
}
</style>
