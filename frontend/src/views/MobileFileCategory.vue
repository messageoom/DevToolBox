<template>
  <div class="mobile-file-category-page">
    <!-- 顶部导航栏 -->
    <div class="mobile-header">
      <el-button @click="goBack" size="small" type="text" class="back-button">
        <el-icon><ArrowLeft /></el-icon>
      </el-button>
      <h2 class="category-title">{{ categoryTitle }}</h2>
      <div class="header-spacer"></div>
    </div>

    <!-- 搜索区域 -->
    <div class="mobile-search-section">
      <el-input
        v-model="searchText"
        placeholder="搜索文件名..."
        clearable
        prefix-icon="Search"
        size="small"
      />
      <el-button @click="toggleFilter" size="small" class="filter-button">
        <el-icon><Filter /></el-icon>
      </el-button>
    </div>

    <!-- 筛选面板 -->
    <div v-if="showFilter" class="filter-panel">
      <div class="filter-row">
        <span class="filter-label">排序方式</span>
        <el-select v-model="sortBy" size="small" class="filter-select">
          <el-option label="按名称" value="name" />
          <el-option label="按大小" value="size" />
          <el-option label="按时间" value="time" />
        </el-select>
      </div>
      <div class="filter-row">
        <span class="filter-label">排序顺序</span>
        <el-select v-model="sortOrder" size="small" class="filter-select">
          <el-option label="升序" value="asc" />
          <el-option label="降序" value="desc" />
        </el-select>
      </div>
    </div>

    <!-- 文件列表 -->
    <div class="mobile-file-list" v-if="filteredFiles.length > 0">
      <div 
        class="mobile-file-item" 
        v-for="file in paginatedFiles" 
        :key="file.name"
      >
        <div class="file-icon-section" @click="handleFileClick(file)">
          <div class="file-icon">{{ getFileIcon(file.name) }}</div>
        </div>

        <div class="file-info-section" @click="handleFileClick(file)">
          <div class="file-name" :title="file.name">{{ file.name }}</div>
          <div class="file-details">
            <span class="file-size">{{ formatFileSize(file.size) }}</span>
            <span class="file-date">{{ formatDate(file.modified) }}</span>
          </div>
        </div>

        <div class="file-actions-section">
          <el-button size="small" type="primary" @click.stop="downloadFile(file.url, file.name)">
            <el-icon><Download /></el-icon>
          </el-button>
          <el-button size="small" type="danger" @click.stop="deleteFile(file.name)">
            <el-icon><Delete /></el-icon>
          </el-button>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-else class="mobile-empty-state">
      <el-empty
        :description="`暂无${categoryTitle}`"
        :image-size="60"
      />
    </div>

    <!-- 底部操作栏 -->
    <div class="mobile-footer-bar" v-if="filteredFiles.length > 0">
      <div class="file-count">共 {{ filteredFiles.length }} 个文件</div>
      <div class="pagination-controls">
        <el-button 
          size="small" 
          :disabled="currentPage === 1"
          @click="prevPage"
        >
          <el-icon><ArrowLeft /></el-icon>
        </el-button>
        <span class="page-info">{{ currentPage }} / {{ totalPages }}</span>
        <el-button 
          size="small" 
          :disabled="currentPage === totalPages"
          @click="nextPage"
        >
          <el-icon><ArrowRight /></el-icon>
        </el-button>
      </div>
    </div>

    <!-- 文件操作菜单 -->
    <div v-if="showActionSheet" class="mobile-action-sheet">
      <div class="action-sheet-mask" @click="showActionSheet = false"></div>
      <div class="action-sheet-content">
        <div class="action-sheet-item" @click="downloadFile(selectedFile.url, selectedFile.name)">
          下载
        </div>
        <div class="action-sheet-item" @click="deleteFile(selectedFile.name)">
          删除
        </div>
        <div class="action-sheet-cancel" @click="showActionSheet = false">
          取消
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft, ArrowRight, Search, Download, Filter, Delete } from '@element-plus/icons-vue'
import axios from 'axios'

export default {
  name: 'MobileFileCategory',
  components: {
    ArrowLeft,
    ArrowRight,
    Search,
    Download,
    Filter,
    Delete
  },
  data() {
    return {
      category: '',
      searchText: '',
      sortBy: 'time',
      sortOrder: 'desc',
      currentPage: 1,
      pageSize: 10,
      allFiles: [],
      showFilter: false,
      showActionSheet: false,
      selectedFile: null,
      actions: [
        { name: '下载', value: 'download' },
        { name: '删除', value: 'delete' }
      ]
    }
  },
  computed: {
    categoryTitle() {
      const titles = {
        images: '🖼️ 图片文件',
        documents: '📄 文档文件',
        data: '📊 数据文件',
        archives: '📦 压缩文件',
        media: '🎵 媒体文件',
        others: '📁 其他文件'
      }
      return titles[this.category] || '文件列表'
    },

    filteredFiles() {
      let files = [...this.allFiles]

      // 搜索过滤
      if (this.searchText.trim()) {
        const search = this.searchText.toLowerCase()
        files = files.filter(file =>
          file.name.toLowerCase().includes(search)
        )
      }

      // 排序
      files.sort((a, b) => {
        let aValue, bValue

        switch (this.sortBy) {
          case 'name':
            aValue = a.name.toLowerCase()
            bValue = b.name.toLowerCase()
            break
          case 'size':
            aValue = a.size
            bValue = b.size
            break
          case 'time':
            aValue = a.modified
            bValue = b.modified
            break
          default:
            return 0
        }

        if (this.sortOrder === 'asc') {
          return aValue > bValue ? 1 : -1
        } else {
          return aValue < bValue ? 1 : -1
        }
      })

      return files
    },

    paginatedFiles() {
      const start = (this.currentPage - 1) * this.pageSize
      const end = start + this.pageSize
      return this.filteredFiles.slice(start, end)
    },

    totalPages() {
      return Math.ceil(this.filteredFiles.length / this.pageSize)
    }
  },

  mounted() {
    this.category = this.$route.params.category
    this.loadFiles()
  },

  methods: {
    async loadFiles() {
      try {
        const response = await axios.get('/api/file-upload/files')
        if (response.data.files) {
          // 根据分类过滤文件
          this.allFiles = this.filterFilesByCategory(response.data.files, this.category)
        }
      } catch (error) {
        console.error('加载文件列表失败:', error)
        ElMessage.error('加载文件列表失败')
      }
    },

    filterFilesByCategory(files, category) {
      const extensions = {
        images: ['png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp', 'svg', 'ico'],
        documents: ['txt', 'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx'],
        data: ['csv', 'json', 'xml'],
        archives: ['zip', 'rar', '7z'],
        media: ['mp3', 'mp4', 'avi', 'mov', 'wmv', 'flac', 'mflac', 'wav', 'aac', 'ogg'],
        others: []
      }

      if (category === 'others') {
        // 其他文件：不属于上述任何分类的文件
        const allExtensions = Object.values(extensions).flat()
        return files.filter(file => {
          const ext = file.name.split('.').pop()?.toLowerCase()
          return !allExtensions.includes(ext)
        })
      } else {
        // 特定分类的文件
        const categoryExtensions = extensions[category] || []
        return files.filter(file => {
          const ext = file.name.split('.').pop()?.toLowerCase()
          return categoryExtensions.includes(ext)
        })
      }
    },

    getFileIcon(filename) {
      const ext = filename.split('.').pop()?.toLowerCase()

      if (['png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp', 'svg', 'ico'].includes(ext)) {
        return '🖼️'
      } else if (['txt', 'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx'].includes(ext)) {
        return '📄'
      } else if (['csv', 'json', 'xml'].includes(ext)) {
        return '📊'
      } else if (['zip', 'rar', '7z'].includes(ext)) {
        return '📦'
      } else if (['mp3', 'mp4', 'avi', 'mov', 'wmv', 'flac', 'mflac', 'wav', 'aac', 'ogg'].includes(ext)) {
        return '🎵'
      } else {
        return '📁'
      }
    },

    goBack() {
      this.$router.go(-1)
    },

    toggleFilter() {
      this.showFilter = !this.showFilter
    },

    handleFileClick(file) {
      this.selectedFile = file
      this.showActionSheet = true
    },

    async deleteFile(filename) {
      try {
        await ElMessageBox.confirm(
          `确定要删除文件 "${filename}" 吗？`,
          '确认删除',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning',
          }
        )

        const response = await axios.delete(`/api/file-upload/files/${filename}`)
        if (response.data.message) {
          ElMessage.success(response.data.message)
          this.loadFiles()
        }
      } catch (error) {
        if (error !== 'cancel') {
          ElMessage.error('删除失败')
        }
      }
    },

    downloadFile(url, filename) {
      const link = document.createElement('a')
      link.href = url
      link.download = filename
      link.style.display = 'none'
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
    },

    formatFileSize(bytes) {
      if (bytes === 0) return '0 B'
      const k = 1024
      const sizes = ['B', 'KB', 'MB', 'GB']
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
    },

    formatDate(timestamp) {
      const date = new Date(timestamp * 1000)
      return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      })
    },

    prevPage() {
      if (this.currentPage > 1) {
        this.currentPage--
      }
    },

    nextPage() {
      if (this.currentPage < this.totalPages) {
        this.currentPage++
      }
    }
  },

  watch: {
    '$route.params.category'(newCategory) {
      this.category = newCategory
      this.loadFiles()
    }
  }
}
</script>

<style scoped>
.mobile-file-category-page {
  padding: 0;
  background-color: #f5f5f5;
  min-height: 100vh;
}

/* 顶部导航栏 */
.mobile-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 15px;
  background-color: #409eff;
  color: white;
  position: sticky;
  top: 0;
  z-index: 100;
}

.back-button {
  color: white;
  font-size: 18px;
}

.category-title {
  margin: 0;
  font-size: 18px;
  font-weight: 500;
  flex: 1;
  text-align: center;
  padding: 0 10px;
}

.header-spacer {
  width: 32px; /* 与返回按钮宽度相同 */
}

/* 搜索区域 */
.mobile-search-section {
  display: flex;
  padding: 10px 15px;
  background-color: white;
  border-bottom: 1px solid #e6e6e6;
}

.mobile-search-section .el-input {
  flex: 1;
  margin-right: 10px;
}

.filter-button {
  width: 40px;
  height: 40px;
  padding: 0;
}

/* 筛选面板 */
.filter-panel {
  padding: 15px;
  background-color: white;
  border-bottom: 1px solid #e6e6e6;
}

.filter-row {
  display: flex;
  align-items: center;
  margin-bottom: 15px;
}

.filter-row:last-child {
  margin-bottom: 0;
}

.filter-label {
  width: 80px;
  font-size: 14px;
  color: #666;
}

.filter-select {
  flex: 1;
}

/* 文件列表 */
.mobile-file-list {
  padding: 10px 15px;
}

.mobile-file-item {
  display: flex;
  align-items: center;
  padding: 15px;
  background: white;
  border-radius: 8px;
  margin-bottom: 10px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.mobile-file-item:active {
  background-color: #f0f0f0;
}

.file-icon-section {
  flex-shrink: 0;
  margin-right: 15px;
}

.file-icon {
  font-size: 32px;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f5f5;
  border-radius: 6px;
}

.file-info-section {
  flex: 1;
  min-width: 0;
}

.file-name {
  font-size: 16px;
  font-weight: 500;
  color: #333;
  margin-bottom: 5px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.file-details {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #999;
}

.file-size,
.file-date {
  flex: 1;
}

/* 空状态 */
.mobile-empty-state {
  padding: 40px 15px;
  text-align: center;
}

/* 底部操作栏 */
.mobile-footer-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 15px;
  background-color: white;
  border-top: 1px solid #e6e6e6;
  z-index: 100;
}

.file-count {
  font-size: 14px;
  color: #666;
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: 10px;
}

.page-info {
  font-size: 14px;
  color: #666;
  min-width: 60px;
  text-align: center;
}

.pagination-controls .el-button {
  padding: 8px 12px;
}

/* 文件操作菜单 */
.mobile-action-sheet {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 2000;
}

.action-sheet-mask {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.3);
}

.action-sheet-content {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background-color: #f5f5f5;
  border-top-left-radius: 10px;
  border-top-right-radius: 10px;
  padding: 10px 0;
}

.action-sheet-item {
  padding: 15px 20px;
  background-color: white;
  font-size: 16px;
  text-align: center;
  border-bottom: 1px solid #e6e6e6;
  cursor: pointer;
}

.action-sheet-item:last-child {
  border-bottom: none;
}

.action-sheet-item:active {
  background-color: #f0f0f0;
}

.action-sheet-cancel {
  margin-top: 10px;
  padding: 15px 20px;
  background-color: white;
  font-size: 16px;
  text-align: center;
  border-radius: 10px;
  cursor: pointer;
}

.action-sheet-cancel:active {
  background-color: #f0f0f0;
}

/* 响应式设计 */
@media (max-width: 375px) {
  .mobile-header {
    padding: 10px 10px;
  }
  
  .mobile-search-section {
    padding: 10px;
  }
  
  .mobile-file-list {
    padding: 10px;
  }
  
  .mobile-file-item {
    padding: 12px;
  }
  
  .mobile-footer-bar {
    padding: 10px;
  }
}
</style>
