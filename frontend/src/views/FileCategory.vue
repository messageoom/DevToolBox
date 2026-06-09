<template>
  <div class="file-category-page" :class="{ 'is-mobile': deviceStore.isMobile }">
    <!-- Header -->
    <div class="page-header">
      <button class="back-btn" @click="goBack">
        <span class="material-symbols-rounded">arrow_back</span>
      </button>
      <div class="header-info">
        <h2 class="header-title">{{ categoryTitle }}</h2>
        <span class="file-count">{{ $t('tools.fileUpload.fileCount', { count: filteredFiles.length }) }}</span>
      </div>
    </div>

    <!-- Search & Sort bar -->
    <div class="toolbar">
      <div class="search-box">
        <span class="material-symbols-rounded search-icon">search</span>
        <input
          v-model="searchText"
          :placeholder="$t('tools.fileUpload.searchPlaceholder')"
          type="text"
          class="search-input"
        />
        <button v-if="searchText" class="clear-btn" @click="searchText = ''">
          <span class="material-symbols-rounded">close</span>
        </button>
      </div>
      <button class="sort-btn" @click="cycleSort" :title="sortLabel">
        <span class="material-symbols-rounded">{{ sortIcon }}</span>
      </button>
    </div>

    <!-- ==================== Image grid mode ==================== -->
    <template v-if="isImageCategory">
      <div class="image-grid" v-if="paginatedFiles.length > 0">
        <div
          v-for="(file, idx) in paginatedFiles"
          :key="file.name"
          class="image-card"
          @click="openLightbox((currentPage - 1) * pageSize + idx)"
          @touchstart.passive="onTouchStart($event, file)"
          @touchend="onTouchEnd"
          @touchmove.passive="onTouchMove"
        >
          <div class="image-thumb-wrap">
            <img
              :src="file.url"
              :alt="file.name"
              class="image-thumb"
              loading="lazy"
              @error="onImageError($event)"
            />
            <div class="image-overlay">
              <span class="image-name">{{ file.name }}</span>
              <span class="image-meta">{{ formatFileSize(file.size) }}</span>
            </div>
            <!-- Desktop hover actions -->
            <div class="image-actions" v-if="!deviceStore.isMobile">
              <button class="img-action-btn" @click.stop="downloadFile(file.url, file.name)" :title="$t('tools.fileUpload.download')">
                <span class="material-symbols-rounded">download</span>
              </button>
              <button class="img-action-btn img-action-btn--danger" @click.stop="deleteFile(file.name)" :title="$t('tools.fileUpload.delete')">
                <span class="material-symbols-rounded">delete</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Load more (mobile) / Pagination (desktop) -->
      <div class="load-more-section" v-if="hasMore && deviceStore.isMobile">
        <button class="load-more-btn" @click="loadMore">
          <span class="material-symbols-rounded">expand_more</span>
          {{ $t('tools.im.expandText') || '加载更多' }}
        </button>
      </div>
      <div class="pagination-section" v-else-if="totalPages > 1 && !deviceStore.isMobile">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[30, 60, 120]"
          :total="filteredFiles.length"
          layout="total, sizes, prev, pager, next"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </template>

    <!-- ==================== List mode (non-image categories) ==================== -->
    <template v-else>
      <div class="file-list" v-if="filteredFiles.length > 0">
        <div class="file-item" v-for="file in paginatedFiles" :key="file.name">
          <div class="file-icon-section">
            <span class="material-symbols-rounded file-type-icon">{{ getFileIcon(file.name) }}</span>
          </div>
          <div class="file-info-section">
            <div class="file-name" :title="file.name">{{ file.name }}</div>
            <div class="file-details">
              <span>{{ formatFileSize(file.size) }}</span>
              <span>{{ formatDate(file.modified) }}</span>
            </div>
          </div>
          <div class="file-actions-section">
            <button class="action-btn" @click="downloadFile(file.url, file.name)">
              <span class="material-symbols-rounded">download</span>
            </button>
            <button class="action-btn action-btn--danger" @click="deleteFile(file.name)">
              <span class="material-symbols-rounded">delete</span>
            </button>
          </div>
        </div>
      </div>
      <div class="pagination-section" v-if="totalPages > 1">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="filteredFiles.length"
          layout="total, sizes, prev, pager, next"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </template>

    <!-- Empty state -->
    <div v-if="filteredFiles.length === 0" class="empty-state">
      <span class="material-symbols-rounded empty-icon">folder_off</span>
      <p>{{ $t('tools.fileUpload.noFiles') }}</p>
    </div>

    <!-- ==================== Lightbox ==================== -->
    <Teleport to="body">
      <Transition name="lightbox-fade">
        <div v-if="lightboxOpen" class="lightbox" @click.self="closeLightbox">
          <!-- Top bar -->
          <div class="lb-top">
            <span class="lb-counter">{{ lightboxIndex + 1 }} / {{ filteredFiles.length }}</span>
            <div class="lb-top-actions">
              <button class="lb-btn" @click="downloadCurrent" :title="$t('tools.fileUpload.download')">
                <span class="material-symbols-rounded">download</span>
              </button>
              <button class="lb-btn" @click="closeLightbox" title="Close">
                <span class="material-symbols-rounded">close</span>
              </button>
            </div>
          </div>
          <!-- Nav arrows -->
          <button v-if="lightboxIndex > 0" class="lb-nav lb-prev" @click.stop="lightboxIndex--">
            <span class="material-symbols-rounded">chevron_left</span>
          </button>
          <button v-if="lightboxIndex < filteredFiles.length - 1" class="lb-nav lb-next" @click.stop="lightboxIndex++">
            <span class="material-symbols-rounded">chevron_right</span>
          </button>
          <!-- Stage -->
          <div class="lb-stage" @touchstart.passive="onLbTouchStart" @touchend="onLbTouchEnd">
            <img :src="currentLightboxUrl" class="lb-image" />
          </div>
          <!-- Bottom strip -->
          <div v-if="filteredFiles.length > 1" class="lb-strip">
            <div
              v-for="(f, i) in filteredFiles"
              :key="f.name"
              class="lb-thumb"
              :class="{ active: i === lightboxIndex }"
              @click.stop="lightboxIndex = i"
            >
              <img :src="f.url" :alt="f.name" />
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script>
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from 'axios'
import { useDeviceStore } from '@/stores/device.js'

export default {
  name: 'FileCategory',
  data() {
    return {
      category: '',
      searchText: '',
      sortBy: 'time',
      sortOrder: 'desc',
      currentPage: 1,
      pageSize: 30,
      allFiles: [],
      // Lightbox
      lightboxOpen: false,
      lightboxIndex: 0,
      // Long press (mobile delete)
      _lpTimer: null,
      _lpFile: null,
      // Lightbox touch swipe
      _lbTouchX: 0,
    }
  },
  setup() {
    const deviceStore = useDeviceStore()
    return { deviceStore }
  },
  computed: {
    isImageCategory() {
      return this.category === 'images'
    },

    categoryTitle() {
      const titles = {
        images: this.$t('tools.fileUpload.imageFiles'),
        documents: this.$t('tools.fileUpload.documentFiles'),
        ebooks: this.$t('tools.fileUpload.ebookFiles'),
        data: this.$t('tools.fileUpload.dataFiles'),
        archives: this.$t('tools.fileUpload.archiveFiles'),
        media: this.$t('tools.fileUpload.mediaFiles'),
        others: this.$t('tools.fileUpload.otherFiles'),
      }
      return titles[this.category] || this.$t('tools.fileUpload.title')
    },

    sortIcon() {
      if (this.sortBy === 'name') return 'sort_by_alpha'
      if (this.sortBy === 'size') return 'hard_drive'
      return 'schedule'
    },

    sortLabel() {
      const labels = { name: 'Name', size: 'Size', time: 'Time' }
      const dir = this.sortOrder === 'asc' ? '↑' : '↓'
      return (labels[this.sortBy] || 'Time') + ' ' + dir
    },

    filteredFiles() {
      let files = [...this.allFiles]
      if (this.searchText.trim()) {
        const search = this.searchText.toLowerCase()
        files = files.filter(f => f.name.toLowerCase().includes(search))
      }
      files.sort((a, b) => {
        let av, bv
        switch (this.sortBy) {
          case 'name': av = a.name.toLowerCase(); bv = b.name.toLowerCase(); break
          case 'size': av = a.size; bv = b.size; break
          default: av = a.modified; bv = b.modified
        }
        return this.sortOrder === 'asc' ? (av > bv ? 1 : -1) : (av < bv ? 1 : -1)
      })
      return files
    },

    paginatedFiles() {
      if (this.isImageCategory && this.deviceStore.isMobile) {
        // Mobile image: show pageSize items (load more pattern)
        return this.filteredFiles.slice(0, this.currentPage * this.pageSize)
      }
      const start = (this.currentPage - 1) * this.pageSize
      return this.filteredFiles.slice(start, start + this.pageSize)
    },

    totalPages() {
      return Math.ceil(this.filteredFiles.length / this.pageSize)
    },

    hasMore() {
      return this.isImageCategory && this.paginatedFiles.length < this.filteredFiles.length
    },

    currentLightboxUrl() {
      const f = this.filteredFiles[this.lightboxIndex]
      return f ? f.url : ''
    },
  },

  mounted() {
    this.category = this.$route.params.category
    if (!this.isImageCategory) this.pageSize = 20
    this.loadFiles()
    window.addEventListener('keydown', this.onKeydown)
  },

  beforeUnmount() {
    window.removeEventListener('keydown', this.onKeydown)
    if (this._lpTimer) clearTimeout(this._lpTimer)
  },

  methods: {
    async loadFiles() {
      try {
        const resp = await axios.get('/api/file-upload/files')
        if (resp.data.files) {
          this.allFiles = this.filterFilesByCategory(resp.data.files, this.category)
        }
      } catch {
        ElMessage.error(this.$t('tools.fileUpload.loadFail'))
      }
    },

    filterFilesByCategory(files, category) {
      const exts = {
        images: ['png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp', 'svg', 'ico'],
        documents: ['txt', 'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx'],
        ebooks: ['epub'],
        data: ['csv', 'json', 'xml'],
        archives: ['zip', 'rar', '7z'],
        media: ['mp3', 'mp4', 'avi', 'mov', 'wmv', 'flac', 'mflac', 'wav', 'aac', 'ogg'],
      }
      if (category === 'others') {
        const all = Object.values(exts).flat()
        return files.filter(f => !all.includes(f.name.split('.').pop()?.toLowerCase()))
      }
      const catExts = exts[category] || []
      return files.filter(f => catExts.includes(f.name.split('.').pop()?.toLowerCase()))
    },

    getFileIcon(filename) {
      const ext = filename.split('.').pop()?.toLowerCase()
      if (['png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp', 'svg', 'ico'].includes(ext)) return 'image'
      if (['txt', 'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx'].includes(ext)) return 'description'
      if (['epub'].includes(ext)) return 'menu_book'
      if (['csv', 'json', 'xml'].includes(ext)) return 'database'
      if (['zip', 'rar', '7z'].includes(ext)) return 'folder_zip'
      if (['mp3', 'mp4', 'avi', 'mov', 'wmv', 'flac', 'mflac', 'wav', 'aac', 'ogg'].includes(ext)) return 'audiotrack'
      return 'draft'
    },

    cycleSort() {
      const cycle = [
        { by: 'time', order: 'desc' },
        { by: 'time', order: 'asc' },
        { by: 'name', order: 'asc' },
        { by: 'size', order: 'desc' },
      ]
      const cur = cycle.findIndex(c => c.by === this.sortBy && c.order === this.sortOrder)
      const next = cycle[(cur + 1) % cycle.length]
      this.sortBy = next.by
      this.sortOrder = next.order
    },

    goBack() {
      this.$router.go(-1)
    },

    async deleteFile(filename) {
      try {
        await ElMessageBox.confirm(
          this.$t('tools.fileUpload.confirmDelete', { name: filename }),
          this.$t('tools.fileUpload.confirmDeleteTitle'),
          { confirmButtonText: this.$t('tools.fileUpload.confirmBtn'), cancelButtonText: this.$t('tools.fileUpload.cancelBtn'), type: 'warning' }
        )
        const resp = await axios.delete(`/api/file-upload/files/${filename}`)
        if (resp.data.message) {
          ElMessage.success(resp.data.message)
          this.loadFiles()
        }
      } catch (e) {
        if (e !== 'cancel') ElMessage.error(this.$t('tools.fileUpload.deleteFail'))
      }
    },

    downloadFile(url, filename) {
      const a = document.createElement('a')
      a.href = url
      a.download = filename
      a.style.display = 'none'
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
    },

    downloadCurrent() {
      const f = this.filteredFiles[this.lightboxIndex]
      if (f) this.downloadFile(f.url, f.name)
    },

    formatFileSize(bytes) {
      if (bytes === 0) return '0 B'
      const k = 1024
      const sizes = ['B', 'KB', 'MB', 'GB']
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
    },

    formatDate(ts) {
      return new Date(ts * 1000).toLocaleString('zh-CN')
    },

    handleSizeChange(s) { this.pageSize = s; this.currentPage = 1 },
    handleCurrentChange(p) { this.currentPage = p },
    loadMore() { this.currentPage++ },

    // --- Image error fallback ---
    onImageError(e) {
      e.target.src = ''
      e.target.style.display = 'none'
      e.target.parentElement.classList.add('image-error')
    },

    // --- Lightbox ---
    openLightbox(index) {
      this.lightboxIndex = index
      this.lightboxOpen = true
    },
    closeLightbox() {
      this.lightboxOpen = false
    },
    onKeydown(e) {
      if (!this.lightboxOpen) return
      if (e.key === 'Escape') this.closeLightbox()
      if (e.key === 'ArrowLeft' && this.lightboxIndex > 0) this.lightboxIndex--
      if (e.key === 'ArrowRight' && this.lightboxIndex < this.filteredFiles.length - 1) this.lightboxIndex++
    },

    // --- Lightbox touch swipe ---
    onLbTouchStart(e) {
      this._lbTouchX = e.touches[0].clientX
    },
    onLbTouchEnd(e) {
      const dx = e.changedTouches[0].clientX - this._lbTouchX
      if (Math.abs(dx) > 60) {
        if (dx < 0 && this.lightboxIndex < this.filteredFiles.length - 1) this.lightboxIndex++
        if (dx > 0 && this.lightboxIndex > 0) this.lightboxIndex--
      }
    },

    // --- Long press for mobile delete ---
    onTouchStart(e, file) {
      if (!this.deviceStore.isMobile) return
      this._lpFile = file
      this._lpTimer = setTimeout(() => {
        this.deleteFile(file.name)
      }, 500)
    },
    onTouchEnd() {
      if (this._lpTimer) { clearTimeout(this._lpTimer); this._lpTimer = null }
    },
    onTouchMove() {
      if (this._lpTimer) { clearTimeout(this._lpTimer); this._lpTimer = null }
    },
  },

  watch: {
    '$route.params.category'(cat) {
      this.category = cat
      this.currentPage = 1
      this.pageSize = cat === 'images' ? 30 : 20
      this.loadFiles()
    },
  },
}
</script>

<style scoped>
/* =========================================
   Page layout
   ========================================= */
.file-category-page {
  padding: var(--dt-spacing-md);
  min-height: 100%;
}

/* =========================================
   Header
   ========================================= */
.page-header {
  display: flex;
  align-items: center;
  gap: var(--dt-spacing-sm);
  margin-bottom: var(--dt-spacing-md);
}

.back-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border: none;
  border-radius: var(--dt-radius-md);
  background: var(--dt-bg-section);
  color: var(--dt-text-regular);
  cursor: pointer;
  transition: background var(--dt-transition-fast);
}
.back-btn:active { background: var(--dt-bg-hover) }

.header-info { display: flex; align-items: baseline; gap: var(--dt-spacing-sm); }

.header-title {
  margin: 0;
  font-size: var(--dt-font-size-xl);
  font-weight: 600;
  color: var(--dt-text-primary);
}

.file-count {
  font-size: var(--dt-font-size-xs);
  color: var(--dt-text-secondary);
}

/* =========================================
   Toolbar
   ========================================= */
.toolbar {
  display: flex;
  gap: var(--dt-spacing-sm);
  margin-bottom: var(--dt-spacing-md);
}

.search-box {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 0 12px;
  height: 40px;
  background: var(--dt-bg-card);
  border: 1px solid var(--dt-border-light);
  border-radius: var(--dt-radius-lg);
  transition: border-color var(--dt-transition-fast);
}
.search-box:focus-within { border-color: var(--dt-primary) }

.search-icon { font-size: 20px; color: var(--dt-text-placeholder) }

.search-input {
  flex: 1;
  border: none;
  outline: none;
  background: transparent;
  font-size: var(--dt-font-size-sm);
  color: var(--dt-text-primary);
  font-family: inherit;
}
.search-input::placeholder { color: var(--dt-text-placeholder) }

.clear-btn {
  display: flex;
  align-items: center;
  border: none;
  background: none;
  color: var(--dt-text-placeholder);
  cursor: pointer;
  padding: 2px;
}
.clear-btn .material-symbols-rounded { font-size: 18px }

.sort-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border: 1px solid var(--dt-border-light);
  border-radius: var(--dt-radius-md);
  background: var(--dt-bg-card);
  color: var(--dt-text-secondary);
  cursor: pointer;
  transition: all var(--dt-transition-fast);
}
.sort-btn:active { background: var(--dt-bg-hover); color: var(--dt-primary) }

/* =========================================
   Image Grid
   ========================================= */
.image-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: var(--dt-spacing-sm);
}

.image-card {
  cursor: pointer;
  -webkit-tap-highlight-color: transparent;
}

.image-thumb-wrap {
  position: relative;
  aspect-ratio: 1;
  border-radius: var(--dt-radius-md);
  overflow: hidden;
  background: var(--dt-bg-section);
  box-shadow: var(--dt-shadow-sm);
}

.image-thumb {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  transition: transform 0.2s ease;
}

.image-card:active .image-thumb { transform: scale(0.97) }

/* Error placeholder */
.image-error::before {
  content: 'image_not_supported';
  font-family: 'Material Symbols Rounded';
  font-size: 32px;
  color: var(--dt-text-placeholder);
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* Bottom overlay with name */
.image-overlay {
  position: absolute;
  left: 0; right: 0; bottom: 0;
  padding: 24px 8px 6px;
  background: linear-gradient(transparent, rgba(0,0,0,0.6));
  color: #fff;
  pointer-events: none;
}

.image-name {
  display: block;
  font-size: 11px;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  line-height: 1.3;
}

.image-meta {
  font-size: 10px;
  opacity: 0.75;
}

/* Desktop hover actions */
.image-actions {
  position: absolute;
  top: 6px;
  right: 6px;
  display: flex;
  gap: 4px;
  opacity: 0;
  transition: opacity var(--dt-transition-fast);
}
.image-card:hover .image-actions { opacity: 1 }

.img-action-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 30px;
  height: 30px;
  border: none;
  border-radius: var(--dt-radius-sm);
  background: rgba(0,0,0,0.5);
  color: #fff;
  cursor: pointer;
  transition: background var(--dt-transition-fast);
}
.img-action-btn:hover { background: rgba(0,0,0,0.7) }
.img-action-btn--danger:hover { background: var(--dt-danger) }

/* =========================================
   Load more (mobile)
   ========================================= */
.load-more-section {
  text-align: center;
  margin-top: var(--dt-spacing-md);
}

.load-more-btn {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 10px 24px;
  border: 1px solid var(--dt-border-light);
  border-radius: var(--dt-radius-lg);
  background: var(--dt-bg-card);
  color: var(--dt-text-secondary);
  font-size: var(--dt-font-size-sm);
  cursor: pointer;
  transition: all var(--dt-transition-fast);
}
.load-more-btn:active { background: var(--dt-bg-hover); color: var(--dt-primary) }

/* =========================================
   List mode (non-image categories)
   ========================================= */
.file-list {
  display: flex;
  flex-direction: column;
  gap: var(--dt-spacing-xs);
}

.file-item {
  display: flex;
  align-items: center;
  gap: var(--dt-spacing-sm);
  padding: var(--dt-spacing-sm) var(--dt-spacing-md);
  background: var(--dt-bg-card);
  border: 1px solid var(--dt-border-lighter);
  border-radius: var(--dt-radius-md);
  transition: border-color var(--dt-transition-fast), box-shadow var(--dt-transition-fast);
}
.file-item:hover {
  border-color: var(--dt-primary);
  box-shadow: 0 1px 4px color-mix(in srgb, var(--dt-primary) 15%, transparent);
}

.file-type-icon {
  font-size: 24px;
  color: var(--dt-primary);
}

.file-info-section { flex: 1; min-width: 0 }

.file-name {
  font-size: var(--dt-font-size-sm);
  font-weight: 500;
  color: var(--dt-text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.file-details {
  display: flex;
  gap: var(--dt-spacing-sm);
  font-size: var(--dt-font-size-xs);
  color: var(--dt-text-secondary);
  margin-top: 2px;
}

.file-actions-section { display: flex; gap: 6px }

.action-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border: none;
  border-radius: var(--dt-radius-sm);
  background: var(--dt-bg-section);
  color: var(--dt-text-secondary);
  cursor: pointer;
  transition: all var(--dt-transition-fast);
}
.action-btn:hover { background: var(--dt-bg-hover); color: var(--dt-primary) }
.action-btn--danger:hover { background: var(--dt-danger-light); color: var(--dt-danger) }
.action-btn .material-symbols-rounded { font-size: 18px }

/* =========================================
   Pagination
   ========================================= */
.pagination-section {
  margin-top: var(--dt-spacing-md);
  display: flex;
  justify-content: center;
}

/* =========================================
   Empty state
   ========================================= */
.empty-state {
  text-align: center;
  padding: 60px 0;
  color: var(--dt-text-placeholder);
}
.empty-icon {
  font-size: 48px;
  display: block;
  margin-bottom: 12px;
  opacity: 0.5;
}
.empty-state p {
  font-size: var(--dt-font-size-sm);
  margin: 0;
}

/* =========================================
   Lightbox
   ========================================= */
.lightbox {
  position: fixed;
  inset: 0;
  z-index: 2000;
  background: rgba(0,0,0,0.88);
  display: flex;
  align-items: center;
  justify-content: center;
}

.lb-top {
  position: absolute;
  top: 0; left: 0; right: 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  z-index: 1;
}

.lb-counter {
  font-size: 13px;
  color: rgba(255,255,255,0.6);
  background: rgba(0,0,0,0.4);
  padding: 4px 10px;
  border-radius: 12px;
}

.lb-top-actions { display: flex; gap: 8px }

.lb-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border: none;
  border-radius: 50%;
  background: rgba(255,255,255,0.12);
  color: #fff;
  cursor: pointer;
  transition: background var(--dt-transition-fast);
}
.lb-btn:hover { background: rgba(255,255,255,0.25) }
.lb-btn .material-symbols-rounded { font-size: 22px }

.lb-nav {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  display: flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  border: none;
  border-radius: 50%;
  background: rgba(255,255,255,0.1);
  color: #fff;
  cursor: pointer;
  z-index: 1;
  transition: background var(--dt-transition-fast);
}
.lb-nav:hover { background: rgba(255,255,255,0.25) }
.lb-nav .material-symbols-rounded { font-size: 28px }
.lb-prev { left: 12px }
.lb-next { right: 12px }

.lb-stage {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  padding: 60px 56px 80px;
}

.lb-image {
  max-width: 90vw;
  max-height: 75vh;
  object-fit: contain;
  border-radius: 4px;
  user-select: none;
}

.lb-strip {
  position: absolute;
  bottom: 0;
  left: 0; right: 0;
  display: flex;
  justify-content: center;
  gap: 6px;
  padding: 10px 16px;
  background: linear-gradient(transparent, rgba(0,0,0,0.5));
  overflow-x: auto;
  scrollbar-width: none;
}
.lb-strip::-webkit-scrollbar { display: none }

.lb-thumb {
  width: 40px;
  height: 40px;
  flex-shrink: 0;
  border-radius: var(--dt-radius-sm);
  overflow: hidden;
  border: 2px solid transparent;
  cursor: pointer;
  opacity: 0.5;
  transition: opacity var(--dt-transition-fast), border-color var(--dt-transition-fast);
}
.lb-thumb.active { border-color: var(--dt-primary); opacity: 1 }
.lb-thumb:hover { opacity: 0.8 }
.lb-thumb img { width: 100%; height: 100%; object-fit: cover }

/* Lightbox transition */
.lightbox-fade-enter-active,
.lightbox-fade-leave-active {
  transition: opacity 0.2s ease;
}
.lightbox-fade-enter-from,
.lightbox-fade-leave-to {
  opacity: 0;
}

/* =========================================
   Mobile responsive
   ========================================= */
@media (max-width: 768px) {
  .file-category-page {
    padding: var(--dt-spacing-sm);
  }

  .image-grid {
    grid-template-columns: repeat(3, 1fr);
    gap: 6px;
  }

  .image-name { font-size: 10px }
  .image-meta { display: none }

  .file-item {
    padding: var(--dt-spacing-sm);
  }

  .file-details { flex-direction: column; gap: 2px }

  .file-actions-section {
    flex-direction: column;
    gap: 4px;
  }
}

@media (max-width: 480px) {
  .image-grid {
    grid-template-columns: repeat(3, 1fr);
    gap: 4px;
  }

  .image-thumb-wrap { border-radius: var(--dt-radius-sm) }

  .lb-stage { padding: 56px 8px 72px }
  .lb-nav { display: none }
}
</style>
