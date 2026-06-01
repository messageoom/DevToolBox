<template>
  <div class="file-category-page">
      <el-card>
        <template #header>
          <div class="page-header">
            <el-button @click="goBack" size="small" type="text">
              <el-icon><ArrowLeft /></el-icon>
              返回
            </el-button>
            <h2>{{ categoryTitle }}</h2>
            <span class="file-count">{{ $t('tools.fileUpload.fileCount', { count: filteredFiles.length }) }}</span>
          </div>
        </template>

        <!-- 搜索和筛选区域 -->
        <div class="search-section">
          <el-input
            v-model="searchText"
            :placeholder="$t('tools.fileUpload.searchPlaceholder')"
            clearable
            prefix-icon="Search"
            style="width: 300px; margin-right: 20px;"
          />
          <el-select v-model="sortBy" :placeholder="$t('tools.fileUpload.sortBy')" style="width: 120px;">
            <el-option :label="$t('tools.fileUpload.sortByName')" value="name" />
            <el-option :label="$t('tools.fileUpload.sortBySize')" value="size" />
            <el-option :label="$t('tools.fileUpload.sortByTime')" value="time" />
          </el-select>
          <el-select v-model="sortOrder" :placeholder="$t('tools.fileUpload.sortOrder')" style="width: 120px; margin-left: 10px;">
            <el-option :label="$t('tools.fileUpload.sortAsc')" value="asc" />
            <el-option :label="$t('tools.fileUpload.sortDesc')" value="desc" />
          </el-select>
        </div>

        <!-- 文件列表 -->
        <div class="file-list" v-if="filteredFiles.length > 0">
          <div class="file-item" v-for="file in paginatedFiles" :key="file.name">
            <div class="file-icon-section">
              <div class="file-icon">{{ getFileIcon(file.name) }}</div>
            </div>

            <div class="file-info-section">
              <div class="file-name" :title="file.name">{{ file.name }}</div>
              <div class="file-details">
                <span class="file-size">{{ formatFileSize(file.size) }}</span>
                <span class="file-date">{{ formatDate(file.modified) }}</span>
              </div>
            </div>

            <div class="file-actions-section">
              <el-button size="small" type="primary" @click="downloadFile(file.url, file.name)">
                <el-icon><Download /></el-icon>
                {{ $t('tools.fileUpload.download') }}
              </el-button>
              <el-button size="small" type="danger" @click="deleteFile(file.name)">
                <el-icon><Delete /></el-icon>
                {{ $t('tools.fileUpload.delete') }}
              </el-button>
            </div>
          </div>
        </div>

        <!-- 分页 -->
        <div class="pagination-section" v-if="totalPages > 1">
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50, 100]"
            :total="filteredFiles.length"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
          />
        </div>

        <!-- 空状态 -->
        <div v-else class="empty-state">
          <el-empty
            :description="$t('tools.fileUpload.noFiles')"
            :image-size="80"
          />
        </div>
      </el-card>
  </div>
</template>

<script>
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft, Search, Download, Delete } from '@element-plus/icons-vue'
import axios from 'axios'

export default {
  name: 'FileCategory',
  components: {
    ArrowLeft,
    Search,
    Download,
    Delete
  },
  data() {
    return {
      category: '',
      searchText: '',
      sortBy: 'time',
      sortOrder: 'desc',
      currentPage: 1,
      pageSize: 20,
      allFiles: [],
    }
  },
  computed: {
    categoryTitle() {
      const titles = {
        images: '🖼️ ' + this.$t('tools.fileUpload.imageFiles'),
        documents: '📄 ' + this.$t('tools.fileUpload.documentFiles'),
        data: '📊 ' + this.$t('tools.fileUpload.dataFiles'),
        archives: '📦 ' + this.$t('tools.fileUpload.archiveFiles'),
        media: '🎵 ' + this.$t('tools.fileUpload.mediaFiles'),
        others: '📁 ' + this.$t('tools.fileUpload.otherFiles')
      }
      return titles[this.category] || this.$t('tools.fileUpload.title')
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

  beforeUnmount() {
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
        ElMessage.error(this.$t('tools.fileUpload.loadFail'))
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

    async deleteFile(filename) {
      try {
        await ElMessageBox.confirm(
          this.$t('tools.fileUpload.confirmDelete', { name: filename }),
          this.$t('tools.fileUpload.confirmDeleteTitle'),
          {
            confirmButtonText: this.$t('tools.fileUpload.confirmBtn'),
            cancelButtonText: this.$t('tools.fileUpload.cancelBtn'),
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
          ElMessage.error(this.$t('tools.fileUpload.deleteFail'))
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
      return date.toLocaleString('zh-CN')
    },

    handleSizeChange(newSize) {
      this.pageSize = newSize
      this.currentPage = 1
    },

    handleCurrentChange(newPage) {
      this.currentPage = newPage
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
.file-category-page {
  padding: 20px;
}

.page-header {
  display: flex;
  align-items: center;
  gap: 15px;
}

.page-header h2 {
  margin: 0;
  color: #333;
  font-size: 20px;
  font-weight: 600;
}

.file-count {
  color: #909399;
  font-size: 14px;
  font-weight: normal;
}

/* 搜索区域 */
.search-section {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 8px;
}

/* 文件列表 */
.file-list {
  max-height: 600px;
  overflow-y: auto;
}

.file-item {
  display: flex;
  align-items: center;
  padding: 15px;
  border: 1px solid #e6e6e6;
  border-radius: 8px;
  margin-bottom: 10px;
  background: #fff;
  transition: all 0.3s ease;
}

.file-item:hover {
  border-color: #409eff;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.1);
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
  color: #303133;
  margin-bottom: 5px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.file-details {
  display: flex;
  gap: 20px;
  font-size: 12px;
  color: #909399;
}

.file-size,
.file-date {
  display: flex;
  align-items: center;
}

.file-actions-section {
  flex-shrink: 0;
  display: flex;
  gap: 10px;
  margin-left: 15px;
}

.file-actions-section .el-button {
  height: 32px;
}

/* 分页 */
.pagination-section {
  margin-top: 20px;
  text-align: center;
}

/* 空状态 */
.empty-state {
  text-align: center;
  padding: 40px 0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .search-section {
    flex-direction: column;
    gap: 10px;
    align-items: stretch;
  }

  .search-section .el-input,
  .search-section .el-select {
    width: 100% !important;
    margin-right: 0 !important;
    margin-left: 0 !important;
  }

  .file-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }

  .file-actions-section {
    margin-left: 0;
    align-self: flex-end;
  }

  .file-details {
    flex-direction: column;
    gap: 5px;
  }
}

@media (max-width: 480px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }

  .file-actions-section {
    flex-direction: column;
    width: 100%;
  }

  .file-actions-section .el-button {
    width: 100%;
  }
}
</style>
