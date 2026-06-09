<template>
  <div class="im-file-card">
    <div class="file-icon-wrap">
      <span class="material-symbols-rounded file-icon">{{ fileIcon }}</span>
    </div>
    <div class="file-info">
      <div class="file-name" :title="filename">{{ filename }}</div>
      <div class="file-size">{{ formattedSize }}</div>
      <!-- P2P transfer progress bar -->
      <div v-if="progress != null && progress < 1" class="file-progress">
        <div class="file-progress-bar" :style="{ width: (progress * 100) + '%' }"></div>
      </div>
    </div>
    <button
      v-if="canPreview && url && (progress == null || progress >= 1)"
      class="file-action-btn file-preview-btn"
      @click="$emit('preview-file', { url, filename, mime })"
      :title="t('tools.im.preview')"
    >
      <span class="material-symbols-rounded">visibility</span>
    </button>
    <a
      v-if="url && (progress == null || progress >= 1)"
      class="file-action-btn file-download-btn"
      :href="url"
      target="_blank"
      rel="noopener noreferrer"
      :title="t('tools.im.download')"
    >
      <span class="material-symbols-rounded">download</span>
    </a>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

const PREVIEW_EXTENSIONS = [
  '.md', '.markdown', '.html', '.htm',
  '.txt', '.log', '.csv', '.tsv',
  '.py', '.js', '.ts', '.jsx', '.tsx', '.vue', '.svelte',
  '.java', '.c', '.cpp', '.h', '.hpp',
  '.go', '.rs', '.rb', '.php', '.swift', '.kt', '.scala',
  '.sh', '.bash', '.zsh', '.bat', '.ps1',
  '.json', '.yaml', '.yml', '.toml', '.ini', '.cfg', '.conf',
  '.xml', '.sql', '.css', '.scss', '.less', '.sass',
  '.env', '.gitignore', '.dockerignore', '.editorconfig',
  '.dockerfile', '.makefile',
]

const PREVIEW_MIMES = [
  'text/', 'application/json', 'application/xml', 'application/javascript',
  'application/x-yaml', 'application/yaml',
]

const props = defineProps({
  filename: { type: String, default: '' },
  size: { type: Number, default: 0 },
  mime: { type: String, default: '' },
  url: { type: String, default: '' },
  progress: { type: Number, default: null },
})

defineEmits(['preview-file'])

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

const canPreview = computed(() => {
  const name = props.filename.toLowerCase()
  if (PREVIEW_EXTENSIONS.some(ext => name.endsWith(ext))) return true
  const mime = props.mime.toLowerCase()
  if (PREVIEW_MIMES.some(m => mime.startsWith(m) || mime === m)) return true
  return false
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

.file-action-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: var(--dt-radius-sm);
  border: none;
  cursor: pointer;
  color: var(--dt-text-secondary);
  text-decoration: none;
  transition: all 0.15s ease;
  flex-shrink: 0;
  background: none;
}

.file-action-btn:hover {
  background: color-mix(in srgb, var(--dt-primary) 10%, transparent);
  color: var(--dt-primary);
}

.file-action-btn .material-symbols-rounded {
  font-size: 20px;
}

/* P2P transfer progress */
.file-progress {
  height: 3px;
  background: var(--dt-border-lighter);
  border-radius: 2px;
  margin-top: 4px;
  overflow: hidden;
}
.file-progress-bar {
  height: 100%;
  background: var(--dt-primary);
  border-radius: 2px;
  transition: width 0.15s ease;
}
</style>
