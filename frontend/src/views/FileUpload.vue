<template>
  <div class="tool-page">
    <!-- Upload area -->
    <div class="upload-section">
      <el-upload
        ref="uploadRef"
        class="upload-dropzone"
        drag
        v-model:file-list="fileList"
        multiple
        :limit="9"
        :auto-upload="false"
      >
        <div class="dropzone-content">
          <span class="material-symbols-rounded dropzone-icon">cloud_upload</span>
          <p class="dropzone-text">{{ t('tools.fileUpload.dropzone') }}</p>
          <p class="dropzone-hint">{{ t('tools.fileUpload.hint') }}</p>
        </div>
      </el-upload>

      <div v-if="fileList.length" class="upload-actions">
        <div class="upload-progress-wrap" v-if="uploading">
          <div class="upload-progress-bar">
            <div class="upload-progress-fill" :style="{ width: uploadProgress + '%' }"></div>
          </div>
          <span class="upload-progress-text">{{ uploadProgress }}%</span>
        </div>
        <template v-else>
          <span class="file-count-label">{{ t('tools.fileUpload.fileCount', { count: fileList.length }) }}</span>
        </template>
        <div class="action-buttons">
          <el-button @click="clearFiles" :disabled="uploading">{{ t('tools.fileUpload.clearList') }}</el-button>
          <el-button type="primary" @click="submitUpload" :loading="uploading">
            <span class="material-symbols-rounded btn-icon" v-if="!uploading">upload</span>
            {{ t('tools.fileUpload.startUpload') }}
          </el-button>
        </div>
      </div>
    </div>

    <!-- Uploaded files -->
    <div class="files-section" v-if="uploadedFiles.length > 0">
      <div class="section-header">
        <h3>{{ t('tools.fileUpload.uploadedFiles') }}</h3>
        <div class="section-header-right">
          <el-input
            v-model="searchQuery"
            :placeholder="t('tools.fileUpload.searchPlaceholder')"
            clearable
            size="small"
            class="search-input"
          >
            <template #prefix>
              <span class="material-symbols-rounded search-icon">search</span>
            </template>
          </el-input>
          <span class="total-count">{{ formatFileSize(totalSize) }}</span>
        </div>
      </div>

      <div v-for="cat in categorizedFiles" :key="cat.id" class="file-category">
        <div class="category-header" @click="toggleCategory(cat.id)">
          <div class="category-label">
            <span class="material-symbols-rounded category-icon">{{ cat.icon }}</span>
            <span>{{ cat.label }}</span>
            <span class="category-count">{{ cat.files.length }}</span>
          </div>
          <span class="material-symbols-rounded expand-icon" :class="{ rotated: expandedCategories[cat.id] }">expand_more</span>
        </div>

        <transition name="grid-collapse">
          <div v-show="expandedCategories[cat.id]" class="file-grid">
            <div
              v-for="file in cat.files"
              :key="file.name"
              class="file-card"
              :class="{ highlighted: highlightedFiles.has(file.name) }"
            >
              <div class="file-preview" :class="previewClass(cat.id, file)">
                <img v-if="cat.id === 'images'" :src="file.url" :alt="file.name" @error="handleImageError($event)" />
                <img v-else-if="file.coverUrl" :src="file.coverUrl" :alt="file.title || file.name" class="ebook-cover" @error="handleImageError($event)" />
                <span v-else class="material-symbols-rounded file-type-icon">{{ cat.icon }}</span>
              </div>
              <div class="file-info">
                <div class="file-name" :title="file.title || file.name">{{ file.title || file.name }}</div>
                <div class="file-size">{{ formatFileSize(file.size) }}</div>
              </div>
              <div class="file-actions">
                <button class="action-btn" @click="downloadFile(file.url, file.name)" :title="t('tools.fileUpload.download')">
                  <span class="material-symbols-rounded">download</span>
                </button>
                <button class="action-btn action-btn--danger" @click="deleteFile(file.name)" :title="t('tools.fileUpload.delete')">
                  <span class="material-symbols-rounded">delete</span>
                </button>
              </div>
            </div>
          </div>
        </transition>
      </div>
    </div>

    <!-- Empty state -->
    <div v-else class="empty-state">
      <div class="empty-card">
        <span class="material-symbols-rounded empty-icon">cloud_upload</span>
        <p class="empty-title">{{ t('tools.fileUpload.noFiles') }}</p>
        <p class="empty-hint">{{ t('tools.fileUpload.emptyHint') }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from 'axios'

const { t } = useI18n()

const uploadRef = ref(null)
const fileList = ref([])
const uploadedFiles = ref([])
const uploading = ref(false)
const uploadProgress = ref(0)
const searchQuery = ref('')
const expandedCategories = reactive({})
const highlightedFiles = reactive(new Set())

const CATEGORY_META = {
  images:    { icon: 'image',            exts: ['png','jpg','jpeg','gif','bmp','webp','svg','ico'] },
  documents: { icon: 'description',      exts: ['txt','pdf','doc','docx','xls','xlsx','ppt','pptx'] },
  ebooks:    { icon: 'menu_book',        exts: ['epub'] },
  data:      { icon: 'table_chart',      exts: ['csv','json','xml'] },
  archives:  { icon: 'folder_zip',       exts: ['zip','rar','7z'] },
  media:     { icon: 'music_note',       exts: ['mp3','mp4','avi','mov','wmv','flac','mflac','wav','aac','ogg'] },
  others:    { icon: 'insert_drive_file', exts: [] },
}

const CATEGORY_LABELS = {
  images:    'imageFiles',
  documents: 'documentFiles',
  ebooks:    'ebookFiles',
  data:      'dataFiles',
  archives:  'archiveFiles',
  media:     'mediaFiles',
  others:    'otherFiles',
}

function toggleCategory(id) {
  expandedCategories[id] = !expandedCategories[id]
}

function previewClass(catId, file) {
  if (catId === 'images') return 'preview-image'
  if (file.coverUrl) return 'preview-ebook'
  return 'preview-default'
}

const filteredUploadedFiles = computed(() => {
  const q = searchQuery.value.trim().toLowerCase()
  if (!q) return uploadedFiles.value
  return uploadedFiles.value.filter(f =>
    (f.title || f.name || '').toLowerCase().includes(q) ||
    (f.name || '').toLowerCase().includes(q)
  )
})

const categorizedFiles = computed(() => {
  const groups = {}
  for (const id of Object.keys(CATEGORY_META)) groups[id] = []

  filteredUploadedFiles.value.forEach(file => {
    const ext = (file.name || '').split('.').pop()?.toLowerCase() || ''
    let matched = false
    for (const [id, meta] of Object.entries(CATEGORY_META)) {
      if (id === 'others') continue
      if (meta.exts.includes(ext)) {
        groups[id].push(file)
        matched = true
        break
      }
    }
    if (!matched) groups.others.push(file)
  })

  const result = []
  for (const [id, files] of Object.entries(groups)) {
    if (files.length === 0) continue
    if (expandedCategories[id] === undefined) expandedCategories[id] = true
    result.push({
      id,
      icon: CATEGORY_META[id].icon,
      label: t(`tools.fileUpload.${CATEGORY_LABELS[id]}`),
      files,
    })
  }
  return result
})

const totalSize = computed(() =>
  uploadedFiles.value.reduce((sum, f) => sum + (f.size || 0), 0)
)

function clearFiles() {
  fileList.value = []
  uploadRef.value?.clearFiles()
}

async function submitUpload() {
  if (!fileList.value.length) {
    ElMessage.warning(t('tools.fileUpload.selectFileFirst'))
    return
  }
  uploading.value = true
  uploadProgress.value = 0
  try {
    const formData = new FormData()
    fileList.value.forEach(item => {
      const raw = item.raw
      if (raw && raw instanceof File) {
        formData.append('files', raw)
      }
    })

    if (!Array.from(formData.entries()).length) {
      ElMessage.error(t('tools.fileUpload.uploadFail'))
      uploading.value = false
      return
    }

    const { data } = await axios.post('/api/file-upload/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: e => {
        if (e.total) uploadProgress.value = Math.round(e.loaded / e.total * 100)
      },
    })
    if (data.message) {
      ElMessage.success(data.message)
      // Highlight newly uploaded files
      if (data.files) {
        data.files.forEach(f => highlightedFiles.add(f.unique_name))
        setTimeout(() => {
          data.files.forEach(f => highlightedFiles.delete(f.unique_name))
        }, 3000)
      }
      fileList.value = []
      uploadRef.value?.clearFiles()
      await loadUploadedFiles()
    } else {
      ElMessage.error(t('tools.fileUpload.uploadFail'))
    }
  } catch (err) {
    ElMessage.error(t('tools.fileUpload.uploadFail') + ': ' + (err.response?.data?.error || err.message))
  } finally {
    uploading.value = false
    uploadProgress.value = 0
  }
}

async function loadUploadedFiles() {
  try {
    const { data } = await axios.get('/api/file-upload/files')
    if (data.files) uploadedFiles.value = data.files
  } catch {}
}

async function deleteFile(filename) {
  try {
    await ElMessageBox.confirm(
      t('tools.fileUpload.confirmDelete', { name: filename }),
      t('tools.fileUpload.confirmDeleteTitle'),
      { confirmButtonText: t('tools.fileUpload.confirmBtn'), cancelButtonText: t('tools.fileUpload.cancelBtn'), type: 'warning' }
    )
    const { data } = await axios.delete(`/api/file-upload/files/${filename}`)
    if (data.message) {
      ElMessage.success(data.message)
      loadUploadedFiles()
    }
  } catch {}
}

function downloadFile(url, filename) {
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

function handleImageError(event) {
  event.target.style.display = 'none'
}

function formatFileSize(bytes) {
  if (!bytes) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
}

onMounted(loadUploadedFiles)
</script>

<style scoped>
/* =========================================
   Upload dropzone
   ========================================= */
.upload-section {
  margin-bottom: 24px;
}

.upload-dropzone :deep(.el-upload-dragger) {
  border: 2px dashed var(--dt-border-base);
  border-radius: var(--dt-radius-lg);
  background: var(--dt-bg-card);
  padding: 40px 20px;
  transition: all 0.25s ease;
}

.upload-dropzone :deep(.el-upload-dragger:hover) {
  border-color: var(--dt-primary);
}

.upload-dropzone :deep(.el-upload-dragger.is-dragover) {
  border-color: var(--dt-primary);
  background: color-mix(in srgb, var(--dt-primary) 8%, transparent);
}

.upload-dropzone :deep(.el-upload-dragger.is-dragover) .dropzone-icon {
  transform: scale(1.15);
  animation: dropPulse 1s ease-in-out infinite;
}

@keyframes dropPulse {
  0%, 100% { opacity: 0.7; }
  50% { opacity: 1; }
}

.dropzone-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.dropzone-icon {
  font-size: 48px;
  color: var(--dt-primary);
  opacity: 0.6;
  transition: transform 0.25s ease, opacity 0.25s ease;
}

.dropzone-text {
  font-size: 15px;
  color: var(--dt-text-regular);
  margin: 0;
}

.dropzone-hint {
  font-size: 12px;
  color: var(--dt-text-secondary);
  margin: 0;
}

/* Pending file actions */
.upload-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 16px;
  padding: 12px 16px;
  background: var(--dt-bg-section);
  border-radius: var(--dt-radius-md);
}

.file-count-label {
  font-size: 13px;
  color: var(--dt-text-secondary);
}

.action-buttons {
  display: flex;
  gap: 8px;
}

.btn-icon {
  font-size: 16px;
  vertical-align: middle;
  margin-right: 4px;
}

/* Upload progress bar */
.upload-progress-wrap {
  display: flex;
  align-items: center;
  gap: 10px;
  flex: 1;
  min-width: 0;
}

.upload-progress-bar {
  flex: 1;
  height: 6px;
  background: var(--dt-border-lighter);
  border-radius: 3px;
  overflow: hidden;
}

.upload-progress-fill {
  height: 100%;
  background: var(--dt-primary);
  border-radius: 3px;
  transition: width 0.2s ease;
}

.upload-progress-text {
  font-size: 12px;
  font-weight: 600;
  color: var(--dt-primary);
  min-width: 36px;
  text-align: right;
}

/* =========================================
   Uploaded files section
   ========================================= */
.files-section {
  margin-top: 8px;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
  gap: 16px;
}

.section-header h3 {
  font-size: 16px;
  font-weight: 600;
  margin: 0;
  color: var(--dt-text-primary);
  white-space: nowrap;
}

.section-header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.search-input {
  width: 200px;
}

.search-icon {
  font-size: 16px;
  color: var(--dt-text-placeholder);
}

.total-count {
  font-size: 13px;
  color: var(--dt-text-secondary);
  white-space: nowrap;
}

/* Category blocks */
.file-category {
  margin-bottom: 16px;
}

.category-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 12px;
  background: var(--dt-bg-section);
  border-radius: var(--dt-radius-md);
  cursor: pointer;
  user-select: none;
  transition: background 0.15s;
}

.category-header:hover {
  background: var(--dt-bg-hover);
}

.category-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 500;
  color: var(--dt-text-primary);
}

.category-icon {
  font-size: 18px;
  color: var(--dt-primary);
}

.category-count {
  font-size: 12px;
  color: var(--dt-text-secondary);
  background: var(--dt-bg-card);
  padding: 1px 8px;
  border-radius: 99px;
}

.expand-icon {
  font-size: 20px;
  color: var(--dt-text-secondary);
  transition: transform 0.3s ease;
}

.expand-icon.rotated {
  transform: rotate(180deg);
}

/* Grid collapse transition */
.grid-collapse-enter-active,
.grid-collapse-leave-active {
  transition: all 0.3s ease;
  overflow: hidden;
}

.grid-collapse-enter-from,
.grid-collapse-leave-to {
  opacity: 0;
  max-height: 0;
  padding-top: 0;
  padding-bottom: 0;
}

.grid-collapse-enter-to,
.grid-collapse-leave-from {
  opacity: 1;
  max-height: 2000px;
}

/* File grid */
.file-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: 12px;
  padding: 12px 0;
}

.file-card {
  background: var(--dt-bg-card);
  border: 1px solid var(--dt-border-lighter);
  border-radius: var(--dt-radius-md);
  overflow: hidden;
  transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
}

.file-card:hover {
  border-color: var(--dt-primary);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  transform: translateY(-2px);
}

/* New file highlight */
.file-card.highlighted {
  animation: highlightPulse 2s ease-out;
}

@keyframes highlightPulse {
  0% {
    box-shadow: 0 0 0 0 color-mix(in srgb, var(--dt-primary) 40%, transparent);
    transform: scale(1);
  }
  30% {
    box-shadow: 0 0 0 4px color-mix(in srgb, var(--dt-primary) 20%, transparent);
    transform: scale(1.02);
  }
  100% {
    box-shadow: 0 0 0 0 transparent;
    transform: scale(1);
  }
}

/* File preview - adaptive height */
.file-preview {
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--dt-bg-section);
  overflow: hidden;
}

.file-preview.preview-default {
  height: 100px;
}

.file-preview.preview-image {
  min-height: 100px;
  aspect-ratio: 4 / 3;
}

.file-preview.preview-ebook {
  min-height: 120px;
  aspect-ratio: 2 / 3;
}

.file-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.file-preview img.ebook-cover {
  width: auto;
  height: 100%;
  max-width: 100%;
  object-fit: contain;
}

.file-type-icon {
  font-size: 36px;
  color: var(--dt-text-placeholder);
}

.file-info {
  padding: 10px 12px 6px;
}

.file-name {
  font-size: 13px;
  font-weight: 500;
  color: var(--dt-text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.file-size {
  font-size: 11px;
  color: var(--dt-text-secondary);
  margin-top: 2px;
}

.file-actions {
  display: flex;
  border-top: 1px solid var(--dt-border-lighter);
}

.action-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 8px;
  border: none;
  background: transparent;
  cursor: pointer;
  color: var(--dt-text-secondary);
  transition: all 0.15s;
}

.action-btn:hover {
  background: var(--dt-bg-hover);
  color: var(--dt-primary);
}

.action-btn--danger:hover {
  color: var(--dt-danger);
  background: color-mix(in srgb, var(--dt-danger) 8%, transparent);
}

.action-btn .material-symbols-rounded {
  font-size: 18px;
}

/* =========================================
   Empty state
   ========================================= */
.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 48px 20px;
}

.empty-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 40px 32px;
  background: var(--dt-bg-card);
  border: 1px dashed var(--dt-border-lighter);
  border-radius: var(--dt-radius-lg);
  max-width: 360px;
}

.empty-icon {
  font-size: 64px;
  color: var(--dt-primary);
  opacity: 0.35;
  margin-bottom: 16px;
  animation: emptyFloat 3s ease-in-out infinite;
}

@keyframes emptyFloat {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-8px); }
}

.empty-title {
  font-size: 15px;
  font-weight: 500;
  color: var(--dt-text-regular);
  margin: 0 0 6px;
}

.empty-hint {
  font-size: 13px;
  color: var(--dt-text-placeholder);
  margin: 0;
}

/* =========================================
   Responsive
   ========================================= */
@media (max-width: 768px) {
  .file-grid {
    grid-template-columns: repeat(auto-fill, minmax(130px, 1fr));
    gap: 8px;
  }

  .file-preview.preview-default {
    height: 80px;
  }

  .file-preview.preview-image {
    min-height: 80px;
  }

  .file-preview.preview-ebook {
    min-height: 100px;
  }

  .upload-dropzone :deep(.el-upload-dragger) {
    padding: 24px 16px;
  }

  .dropzone-icon {
    font-size: 36px;
  }

  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }

  .section-header-right {
    width: 100%;
  }

  .search-input {
    flex: 1;
  }

  .empty-card {
    padding: 32px 20px;
  }
}
</style>
