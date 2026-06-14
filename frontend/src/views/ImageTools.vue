<template>
  <ToolPage :title="$t('tools.image.title')" :icon="Picture">
    <div class="tool-section">
      <!-- Dropzone (only shown when no image loaded) -->
      <div
        v-if="!imageLoaded"
        class="dropzone"
        :class="{ 'dropzone--active': isDragging }"
        @click="triggerFilePicker"
        @dragover.prevent="isDragging = true"
        @dragleave.prevent="isDragging = false"
        @drop.prevent="onDrop"
        role="button"
        tabindex="0"
      >
        <el-icon class="dropzone-icon"><UploadFilled /></el-icon>
        <div class="dropzone-text">{{ $t('tools.image.labels.dropHere') }}</div>
        <div class="dropzone-hint">{{ $t('tools.image.labels.dropHint') }}</div>
        <input
          ref="fileInput"
          type="file"
          accept="image/*"
          class="file-input"
          @change="onFileChange"
        />
      </div>

      <!-- Loaded view -->
      <template v-else>
        <!-- Original info -->
        <div class="original-bar">
          <div class="original-preview">
            <img :src="originalUrl" alt="preview" />
          </div>
          <div class="original-meta">
            <div class="meta-name">{{ originalFile.name }}</div>
            <div class="meta-stats">
              {{ originalWidth }}×{{ originalHeight }} px · {{ formatSize(originalFile.size) }}
            </div>
          </div>
          <el-button size="small" plain @click="reset">
            <el-icon><RefreshLeft /></el-icon>
            {{ $t('tools.image.action.changeImage') }}
          </el-button>
        </div>

        <el-tabs v-model="activeTab">
          <!-- COMPRESS -->
          <el-tab-pane :label="$t('tools.image.tab.compress')" name="compress">
            <div class="config-row">
              <div class="config-item">
                <div class="field-label">
                  {{ $t('tools.image.labels.quality') }}: {{ compressQuality }}%
                </div>
                <el-slider v-model="compressQuality" :min="10" :max="100" :step="5" />
              </div>
              <div class="config-item">
                <div class="field-label">{{ $t('tools.image.labels.outputFormat') }}</div>
                <el-select v-model="compressFormat" style="width: 100%;">
                  <el-option label="JPEG" value="image/jpeg" />
                  <el-option label="WebP" value="image/webp" />
                </el-select>
              </div>
              <div class="config-item config-switch">
                <el-button type="primary" @click="process('compress')" :loading="processing">
                  {{ $t('tools.image.action.compress') }}
                </el-button>
              </div>
            </div>
          </el-tab-pane>

          <!-- RESIZE -->
          <el-tab-pane :label="$t('tools.image.tab.resize')" name="resize">
            <div class="config-row">
              <div class="config-item">
                <div class="field-label">{{ $t('tools.image.labels.width') }}</div>
                <el-input-number
                  v-model="resizeWidth"
                  :min="1"
                  :max="10000"
                  style="width: 100%;"
                  @change="onWidthChange"
                />
              </div>
              <div class="config-item">
                <div class="field-label">{{ $t('tools.image.labels.height') }}</div>
                <el-input-number
                  v-model="resizeHeight"
                  :min="1"
                  :max="10000"
                  style="width: 100%;"
                  @change="onHeightChange"
                />
              </div>
              <div class="config-item config-switch">
                <div class="field-label">{{ $t('tools.image.labels.lockAspect') }}</div>
                <el-switch v-model="lockAspect" />
              </div>
              <div class="config-item config-switch">
                <el-button type="primary" @click="process('resize')" :loading="processing">
                  {{ $t('tools.image.action.resize') }}
                </el-button>
              </div>
            </div>
          </el-tab-pane>

          <!-- CONVERT -->
          <el-tab-pane :label="$t('tools.image.tab.convert')" name="convert">
            <div class="config-row">
              <div class="config-item">
                <div class="field-label">{{ $t('tools.image.labels.targetFormat') }}</div>
                <el-select v-model="convertFormat" style="width: 100%;">
                  <el-option label="PNG" value="image/png" />
                  <el-option label="JPEG" value="image/jpeg" />
                  <el-option label="WebP" value="image/webp" />
                </el-select>
              </div>
              <div class="config-item config-switch">
                <el-button type="primary" @click="process('convert')" :loading="processing">
                  {{ $t('tools.image.action.convert') }}
                </el-button>
              </div>
            </div>
          </el-tab-pane>
        </el-tabs>

        <!-- Output result -->
        <div class="output-section" v-if="outputUrl">
          <div class="result-header">
            <h4 class="section-title">{{ $t('tools.image.labels.result') }}</h4>
          </div>

          <div class="size-comparison">
            <span class="size-before">{{ formatSize(originalFile.size) }}</span>
            <el-icon class="size-arrow"><Right /></el-icon>
            <span class="size-after">{{ formatSize(outputSize) }}</span>
            <span
              class="size-delta"
              :class="sizeDeltaClass"
            >
              {{ sizeDeltaText }}
            </span>
          </div>

          <div class="output-preview">
            <img :src="outputUrl" alt="result" />
          </div>

          <div class="action-section">
            <el-button type="success" @click="downloadOutput">
              <el-icon><Download /></el-icon>
              {{ $t('tools.image.action.download') }}
            </el-button>
          </div>
        </div>
      </template>
    </div>
  </ToolPage>
</template>

<script>
import { ElMessage } from 'element-plus'
import { Picture, UploadFilled, RefreshLeft, Download, Right } from '@element-plus/icons-vue'
import ToolPage from '@/components/ToolPage.vue'
import { formatFileSize } from '@/utils/format.js'

export default {
  name: 'ImageTools',
  components: {
    Picture,
    UploadFilled,
    RefreshLeft,
    Download,
    Right,
    ToolPage
  },
  data() {
    return {
      isDragging: false,
      imageLoaded: false,
      activeTab: 'compress',
      processing: false,
      // original
      originalFile: null,
      originalUrl: '',
      originalWidth: 0,
      originalHeight: 0,
      originalImageEl: null,
      // compress
      compressQuality: 70,
      compressFormat: 'image/jpeg',
      // resize
      resizeWidth: 100,
      resizeHeight: 100,
      lockAspect: true,
      // convert
      convertFormat: 'image/png',
      // output
      outputUrl: '',
      outputSize: 0,
      outputBlob: null,
      outputExt: ''
    }
  },
  computed: {
    aspectRatio() {
      if (!this.originalHeight) return 1
      return this.originalWidth / this.originalHeight
    },
    sizeDeltaText() {
      if (!this.originalFile || !this.outputSize) return ''
      const diff = this.outputSize - this.originalFile.size
      const pct = this.originalFile.size === 0
        ? 0
        : Math.round((diff / this.originalFile.size) * 100)
      const sign = pct > 0 ? '+' : ''
      return `${sign}${pct}%`
    },
    sizeDeltaClass() {
      if (!this.outputSize || !this.originalFile) return ''
      return this.outputSize <= this.originalFile.size
        ? 'size-delta--down'
        : 'size-delta--up'
    }
  },
  beforeUnmount() {
    this.revokeUrls()
  },
  methods: {
    formatSize(bytes) {
      return formatFileSize(bytes)
    },

    triggerFilePicker() {
      this.$refs.fileInput.click()
    },

    onDrop(e) {
      this.isDragging = false
      const files = e.dataTransfer.files
      if (files && files.length > 0) {
        this.handleFile(files[0])
      }
    },

    onFileChange(e) {
      const files = e.target.files
      if (files && files.length > 0) {
        this.handleFile(files[0])
      }
      // reset so same file can be picked again
      e.target.value = ''
    },

    handleFile(file) {
      if (!file.type.startsWith('image/')) {
        ElMessage.warning(this.$t('tools.image.messages.notAnImage'))
        return
      }

      // revoke previous urls
      this.revokeUrls()

      this.originalFile = file
      this.originalUrl = URL.createObjectURL(file)

      const img = new Image()
      img.onload = () => {
        this.originalWidth = img.naturalWidth
        this.originalHeight = img.naturalHeight
        this.originalImageEl = img
        this.resizeWidth = img.naturalWidth
        this.resizeHeight = img.naturalHeight
        this.imageLoaded = true
      }
      img.onerror = () => {
        ElMessage.warning(this.$t('tools.image.messages.loadFailed'))
      }
      img.src = this.originalUrl
    },

    onWidthChange(val) {
      if (this.lockAspect && val) {
        this.resizeHeight = Math.round(val / this.aspectRatio)
      }
    },

    onHeightChange(val) {
      if (this.lockAspect && val) {
        this.resizeWidth = Math.round(val * this.aspectRatio)
      }
    },

    process(mode) {
      if (!this.originalImageEl) {
        ElMessage.warning(this.$t('tools.image.messages.loadFailed'))
        return
      }

      this.processing = true
      // allow UI to repaint the loading state
      requestAnimationFrame(() => {
        try {
          const source = this.originalImageEl
          let width = source.naturalWidth
          let height = source.naturalHeight
          let mimeType = 'image/png'
          let quality = undefined

          if (mode === 'compress') {
            mimeType = this.compressFormat
            quality = this.compressQuality / 100
          } else if (mode === 'resize') {
            width = this.resizeWidth
            height = this.resizeHeight
            mimeType = this.compressFormat
            quality = this.compressQuality / 100
          } else if (mode === 'convert') {
            mimeType = this.convertFormat
          }

          const canvas = document.createElement('canvas')
          canvas.width = width
          canvas.height = height
          const ctx = canvas.getContext('2d')

          // White background for JPEG (no alpha support)
          if (mimeType === 'image/jpeg') {
            ctx.fillStyle = '#ffffff'
            ctx.fillRect(0, 0, width, height)
          }

          ctx.drawImage(source, 0, 0, width, height)

          canvas.toBlob(
            (blob) => {
              if (!blob) {
                ElMessage.warning(this.$t('tools.image.messages.processFailed'))
                this.processing = false
                return
              }
              // revoke previous output url
              if (this.outputUrl) URL.revokeObjectURL(this.outputUrl)
              this.outputBlob = blob
              this.outputSize = blob.size
              this.outputUrl = URL.createObjectURL(blob)
              this.outputExt = this.extFromMime(mimeType)
              this.processing = false
              ElMessage.success(this.$t('tools.image.messages.processSuccess'))
            },
            mimeType,
            quality
          )
        } catch (e) {
          this.processing = false
          ElMessage.warning(this.$t('tools.image.messages.processFailed'))
        }
      })
    },

    extFromMime(mime) {
      if (mime === 'image/jpeg') return 'jpg'
      if (mime === 'image/webp') return 'webp'
      if (mime === 'image/png') return 'png'
      return 'img'
    },

    downloadOutput() {
      if (!this.outputBlob) return
      const baseName = (this.originalFile.name || 'image').replace(/\.[^.]+$/, '')
      const url = URL.createObjectURL(this.outputBlob)
      const a = document.createElement('a')
      a.href = url
      a.download = `${baseName}.${this.outputExt}`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
    },

    reset() {
      this.revokeUrls()
      this.imageLoaded = false
      this.originalFile = null
      this.originalImageEl = null
      this.originalWidth = 0
      this.originalHeight = 0
      this.outputUrl = ''
      this.outputSize = 0
      this.outputBlob = null
    },

    revokeUrls() {
      if (this.originalUrl) {
        URL.revokeObjectURL(this.originalUrl)
        this.originalUrl = ''
      }
      if (this.outputUrl) {
        URL.revokeObjectURL(this.outputUrl)
        this.outputUrl = ''
      }
    }
  }
}
</script>

<style scoped>
.tool-section {
  display: flex;
  flex-direction: column;
  gap: var(--dt-spacing-md);
}

/* Dropzone */
.dropzone {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: var(--dt-spacing-sm);
  padding: var(--dt-spacing-xl, 48px) var(--dt-spacing-md);
  border: 2px dashed var(--dt-border-light);
  border-radius: var(--dt-radius-md);
  background: var(--dt-bg-section);
  cursor: pointer;
  transition: border-color var(--dt-transition-fast),
    background var(--dt-transition-fast);
}

.dropzone:hover,
.dropzone--active {
  border-color: var(--dt-primary);
  background: var(--dt-bg-hover, var(--dt-bg-section));
}

.dropzone-icon {
  font-size: 48px;
  color: var(--dt-primary);
}

.dropzone-text {
  font-size: var(--dt-font-size-lg);
  font-weight: 600;
  color: var(--dt-text-primary);
}

.dropzone-hint {
  font-size: var(--dt-font-size-sm);
  color: var(--dt-text-secondary);
}

.file-input {
  display: none;
}

/* Original bar */
.original-bar {
  display: flex;
  align-items: center;
  gap: var(--dt-spacing-md);
  padding: var(--dt-spacing-sm);
  background: var(--dt-bg-section);
  border: 1px solid var(--dt-border-light);
  border-radius: var(--dt-radius-md);
}

.original-preview {
  width: 64px;
  height: 64px;
  flex-shrink: 0;
  border: 1px solid var(--dt-border-light);
  border-radius: var(--dt-radius-md);
  overflow: hidden;
  background: var(--dt-bg-card);
}

.original-preview img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.original-meta {
  flex: 1;
  min-width: 0;
}

.meta-name {
  font-size: var(--dt-font-size-base);
  color: var(--dt-text-primary);
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.meta-stats {
  font-size: var(--dt-font-size-sm);
  color: var(--dt-text-secondary);
  margin-top: 4px;
}

/* Config */
.config-row {
  display: flex;
  gap: var(--dt-spacing-md);
  align-items: flex-end;
  flex-wrap: wrap;
}

.config-item {
  flex: 1;
  min-width: 140px;
}

.config-switch {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  min-width: 90px;
}

.field-label {
  font-size: var(--dt-font-size-sm);
  color: var(--dt-text-secondary);
  margin-bottom: var(--dt-spacing-xs);
}

.section-title {
  font-size: var(--dt-font-size-base);
  font-weight: 600;
  color: var(--dt-text-primary);
  margin: 0;
}

/* Output */
.output-section {
  display: flex;
  flex-direction: column;
  gap: var(--dt-spacing-md);
  padding: var(--dt-spacing-md);
  background: var(--dt-bg-section);
  border: 1px solid var(--dt-border-light);
  border-radius: var(--dt-radius-md);
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.size-comparison {
  display: flex;
  align-items: center;
  gap: var(--dt-spacing-sm);
  font-size: var(--dt-font-size-base);
}

.size-before {
  color: var(--dt-text-secondary);
}

.size-arrow {
  color: var(--dt-text-secondary);
}

.size-after {
  color: var(--dt-text-primary);
  font-weight: 600;
}

.size-delta {
  padding: 2px 8px;
  border-radius: var(--dt-radius-md);
  font-size: var(--dt-font-size-sm);
  font-weight: 600;
}

.size-delta--down {
  color: var(--dt-success);
  background: rgba(103, 194, 58, 0.12);
}

.size-delta--up {
  color: var(--dt-danger);
  background: rgba(245, 108, 108, 0.12);
}

.output-preview {
  border: 1px solid var(--dt-border-light);
  border-radius: var(--dt-radius-md);
  overflow: hidden;
  background: var(--dt-bg-card);
  display: flex;
  justify-content: center;
  min-height: 120px;
}

.output-preview img {
  max-width: 100%;
  max-height: 400px;
  object-fit: contain;
}

.action-section {
  display: flex;
  gap: var(--dt-spacing-sm);
}

@media (max-width: 768px) {
  .config-row {
    flex-direction: column;
    gap: var(--dt-spacing-sm);
    align-items: stretch;
  }

  .config-item,
  .config-switch {
    min-width: 100%;
    width: 100%;
  }

  .config-switch {
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
  }

  .config-switch .el-button {
    width: 100%;
  }

  .original-bar {
    flex-wrap: wrap;
  }
}
</style>
