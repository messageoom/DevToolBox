<template>
  <div class="file-upload">
    <el-card>
      <template #header>
        <div class="card-header">
          <el-icon class="card-icon"><Upload /></el-icon>
          <span>文件上传</span>
        </div>
      </template>

      <!-- 上传区域 -->
      <div class="upload-area">
        <el-upload
          ref="uploadRef"
          class="upload-demo"
          drag
          :http-request="customUpload"
          :on-change="handleFileChange"
          :file-list="fileList"
          multiple
          :limit="9"
          :auto-upload="false"
          name="files"
        >
          <el-icon class="el-icon--upload"><upload-filled /></el-icon>
          <div class="el-upload__text">
            将文件拖到此处，或<em>点击上传</em>
          </div>
          <template #tip>
            <div class="el-upload__tip">
              支持多种文件格式，单文件最大50MB，最多9个文件
            </div>
          </template>
        </el-upload>

        <div class="upload-actions">
          <el-button @click="clearFiles">清空列表</el-button>
          <el-button type="primary" @click="submitUpload" :loading="uploading">开始上传</el-button>
        </div>
      </div>

      <!-- 已上传文件列表 -->
      <div class="uploaded-files" v-if="Object.keys(categorizedFiles).length > 0">
        <h3>已上传的文件</h3>

        <!-- 图片文件 -->
        <div v-if="displayFiles.images && displayFiles.images.total > 0" class="file-category">
          <div class="category-header">
            <h4>🖼️ 图片文件</h4>
            <span class="file-count">({{ displayFiles.images.total }})</span>
          </div>
          <div class="file-grid" :style="{ gridTemplateColumns: `repeat(${filesPerRow}, 1fr)` }">
            <div v-for="file in displayFiles.images.displayed" :key="file.name" class="file-item">
              <div class="file-preview">
                <img :src="file.url" :alt="file.name" @error="handleImageError">
              </div>
              <div class="file-info">
                <div class="file-name" :title="file.name">{{ file.name }}</div>
                <div class="file-size">{{ formatFileSize(file.size) }}</div>
                <div class="file-actions">
                  <el-button size="small" type="primary" @click="downloadFile(file.url, file.name)">
                    下载
                  </el-button>
                  <el-button size="small" type="danger" @click="deleteFile(file.name)">
                    删除
                  </el-button>
                </div>
              </div>
            </div>
          </div>
          <div v-if="displayFiles.images.hasMore" class="view-more">
            <el-button type="text" @click="viewMoreFiles('images')">
              查看更多 ({{ displayFiles.images.remaining }} 个文件)
              <el-icon class="el-icon--right"><ArrowRight /></el-icon>
            </el-button>
          </div>
        </div>

        <!-- 文档文件 -->
        <div v-if="displayFiles.documents && displayFiles.documents.total > 0" class="file-category">
          <div class="category-header">
            <h4>📄 文档文件</h4>
            <span class="file-count">({{ displayFiles.documents.total }})</span>
          </div>
          <div class="file-grid" :style="{ gridTemplateColumns: `repeat(${filesPerRow}, 1fr)` }">
            <div v-for="file in displayFiles.documents.displayed" :key="file.name" class="file-item">
              <div class="file-preview">
                <div class="file-icon">📄</div>
              </div>
              <div class="file-info">
                <div class="file-name" :title="file.name">{{ file.name }}</div>
                <div class="file-size">{{ formatFileSize(file.size) }}</div>
                <div class="file-actions">
                  <el-button size="small" type="primary" @click="downloadFile(file.url, file.name)">
                    下载
                  </el-button>
                  <el-button size="small" type="danger" @click="deleteFile(file.name)">
                    删除
                  </el-button>
                </div>
              </div>
            </div>
          </div>
          <div v-if="displayFiles.documents.hasMore" class="view-more">
            <el-button type="text" @click="viewMoreFiles('documents')">
              查看更多 ({{ displayFiles.documents.remaining }} 个文件)
              <el-icon class="el-icon--right"><ArrowRight /></el-icon>
            </el-button>
          </div>
        </div>

        <!-- 数据文件 -->
        <div v-if="displayFiles.data && displayFiles.data.total > 0" class="file-category">
          <div class="category-header">
            <h4>📊 数据文件</h4>
            <span class="file-count">({{ displayFiles.data.total }})</span>
          </div>
          <div class="file-grid" :style="{ gridTemplateColumns: `repeat(${filesPerRow}, 1fr)` }">
            <div v-for="file in displayFiles.data.displayed" :key="file.name" class="file-item">
              <div class="file-preview">
                <div class="file-icon">📊</div>
              </div>
              <div class="file-info">
                <div class="file-name" :title="file.name">{{ file.name }}</div>
                <div class="file-size">{{ formatFileSize(file.size) }}</div>
                <div class="file-actions">
                  <el-button size="small" type="primary" @click="downloadFile(file.url, file.name)">
                    下载
                  </el-button>
                  <el-button size="small" type="danger" @click="deleteFile(file.name)">
                    删除
                  </el-button>
                </div>
              </div>
            </div>
          </div>
          <div v-if="displayFiles.data.hasMore" class="view-more">
            <el-button type="text" @click="viewMoreFiles('data')">
              查看更多 ({{ displayFiles.data.remaining }} 个文件)
              <el-icon class="el-icon--right"><ArrowRight /></el-icon>
            </el-button>
          </div>
        </div>

        <!-- 压缩文件 -->
        <div v-if="displayFiles.archives && displayFiles.archives.total > 0" class="file-category">
          <div class="category-header">
            <h4>📦 压缩文件</h4>
            <span class="file-count">({{ displayFiles.archives.total }})</span>
          </div>
          <div class="file-grid" :style="{ gridTemplateColumns: `repeat(${filesPerRow}, 1fr)` }">
            <div v-for="file in displayFiles.archives.displayed" :key="file.name" class="file-item">
              <div class="file-preview">
                <div class="file-icon">📦</div>
              </div>
              <div class="file-info">
                <div class="file-name" :title="file.name">{{ file.name }}</div>
                <div class="file-size">{{ formatFileSize(file.size) }}</div>
                <div class="file-actions">
                  <el-button size="small" type="primary" @click="downloadFile(file.url, file.name)">
                    下载
                  </el-button>
                  <el-button size="small" type="danger" @click="deleteFile(file.name)">
                    删除
                  </el-button>
                </div>
              </div>
            </div>
          </div>
          <div v-if="displayFiles.archives.hasMore" class="view-more">
            <el-button type="text" @click="viewMoreFiles('archives')">
              查看更多 ({{ displayFiles.archives.remaining }} 个文件)
              <el-icon class="el-icon--right"><ArrowRight /></el-icon>
            </el-button>
          </div>
        </div>

        <!-- 媒体文件 -->
        <div v-if="displayFiles.media && displayFiles.media.total > 0" class="file-category">
          <div class="category-header">
            <h4>🎵 媒体文件</h4>
            <span class="file-count">({{ displayFiles.media.total }})</span>
          </div>
          <div class="file-grid" :style="{ gridTemplateColumns: `repeat(${filesPerRow}, 1fr)` }">
            <div v-for="file in displayFiles.media.displayed" :key="file.name" class="file-item">
              <div class="file-preview">
                <div class="file-icon">🎵</div>
              </div>
              <div class="file-info">
                <div class="file-name" :title="file.name">{{ file.name }}</div>
                <div class="file-size">{{ formatFileSize(file.size) }}</div>
                <div class="file-actions">
                  <el-button size="small" type="primary" @click="downloadFile(file.url, file.name)">
                    下载
                  </el-button>
                  <el-button size="small" type="danger" @click="deleteFile(file.name)">
                    删除
                  </el-button>
                </div>
              </div>
            </div>
          </div>
          <div v-if="displayFiles.media.hasMore" class="view-more">
            <el-button type="text" @click="viewMoreFiles('media')">
              查看更多 ({{ displayFiles.media.remaining }} 个文件)
              <el-icon class="el-icon--right"><ArrowRight /></el-icon>
            </el-button>
          </div>
        </div>

        <!-- 其他文件 -->
        <div v-if="displayFiles.others && displayFiles.others.total > 0" class="file-category">
          <div class="category-header">
            <h4>📁 其他文件</h4>
            <span class="file-count">({{ displayFiles.others.total }})</span>
          </div>
          <div class="file-grid" :style="{ gridTemplateColumns: `repeat(${filesPerRow}, 1fr)` }">
            <div v-for="file in displayFiles.others.displayed" :key="file.name" class="file-item">
              <div class="file-preview">
                <div class="file-icon">📁</div>
              </div>
              <div class="file-info">
                <div class="file-name" :title="file.name">{{ file.name }}</div>
                <div class="file-size">{{ formatFileSize(file.size) }}</div>
                <div class="file-actions">
                  <el-button size="small" type="primary" @click="downloadFile(file.url, file.name)">
                    下载
                  </el-button>
                  <el-button size="small" type="danger" @click="deleteFile(file.name)">
                    删除
                  </el-button>
                </div>
              </div>
            </div>
          </div>
          <div v-if="displayFiles.others.hasMore" class="view-more">
            <el-button type="text" @click="viewMoreFiles('others')">
              查看更多 ({{ displayFiles.others.remaining }} 个文件)
              <el-icon class="el-icon--right"><ArrowRight /></el-icon>
            </el-button>
          </div>
        </div>
      </div>

      <!-- 如果没有文件 -->
      <div v-else class="no-files">
        <el-empty description="暂无上传的文件" />
      </div>
    </el-card>
  </div>
</template>

<script>
import { ElMessage, ElMessageBox } from 'element-plus'
import { Upload, UploadFilled } from '@element-plus/icons-vue'
import axios from 'axios'

export default {
  name: 'FileUpload',
  components: {
    Upload,
    UploadFilled
  },
  data() {
    return {
      uploadUrl: '/api/file-upload/upload',
      fileList: [],
      uploadedFiles: [],
      uploading: false,
      screenWidth: window.innerWidth
    }
  },
  computed: {
    categorizedFiles() {
      const categories = {
        images: [],
        documents: [],
        data: [],
        archives: [],
        media: [],
        others: []
      }

      // 文件扩展名分类
      const imageExts = ['png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp', 'svg', 'ico']
      const documentExts = ['txt', 'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx']
      const dataExts = ['csv', 'json', 'xml']
      const archiveExts = ['zip', 'rar', '7z']
      const mediaExts = ['mp3', 'mp4', 'avi', 'mov', 'wmv', 'flac', 'mflac', 'wav', 'aac', 'ogg']

      this.uploadedFiles.forEach(file => {
        const extension = file.name.split('.').pop()?.toLowerCase()

        if (imageExts.includes(extension)) {
          categories.images.push(file)
        } else if (documentExts.includes(extension)) {
          categories.documents.push(file)
        } else if (dataExts.includes(extension)) {
          categories.data.push(file)
        } else if (archiveExts.includes(extension)) {
          categories.archives.push(file)
        } else if (mediaExts.includes(extension)) {
          categories.media.push(file)
        } else {
          categories.others.push(file)
        }
      })

      return categories
    },

    // 动态计算每行显示的文件数量
    filesPerRow() {
      if (this.screenWidth >= 1200) {
        return 6 // 大屏幕显示6个
      } else if (this.screenWidth >= 992) {
        return 5 // 中等屏幕显示5个
      } else if (this.screenWidth >= 768) {
        return 4 // 平板显示4个
      } else if (this.screenWidth >= 576) {
        return 3 // 小屏幕显示3个
      } else {
        return 2 // 超小屏幕显示2个
      }
    },

    // 计算每个分类显示的文件
    displayFiles() {
      const result = {}
      Object.keys(this.categorizedFiles).forEach(category => {
        const files = this.categorizedFiles[category]
        const maxDisplay = this.filesPerRow
        result[category] = {
          displayed: files.slice(0, maxDisplay),
          total: files.length,
          hasMore: files.length > maxDisplay,
          remaining: Math.max(0, files.length - maxDisplay)
        }
      })
      return result
    }
  },
  mounted() {
    this.loadUploadedFiles()
    // 监听窗口大小变化
    window.addEventListener('resize', this.handleResize)
  },

  beforeUnmount() {
    // 移除事件监听器
    window.removeEventListener('resize', this.handleResize)
  },
  methods: {
    customUpload(options) {
      // 自定义上传方法，确保所有文件都能被上传
      const { file, onSuccess, onError } = options

      // 这里我们不直接上传，而是让用户点击"开始上传"按钮
      // 所以我们只需要返回成功状态，让文件显示在列表中
      onSuccess(file)
    },

    beforeUpload(file) {
      // 检查文件大小（限制为50MB）
      const isLt50M = file.size / 1024 / 1024 < 50
      if (!isLt50M) {
        ElMessage.error('上传文件大小不能超过 50MB!')
        return false
      }
      // 不返回false，让文件正常添加到列表中
      return true
    },

    async submitUpload() {
      if (this.fileList.length === 0) {
        ElMessage.warning('请先选择文件')
        return
      }

      this.uploading = true

      try {
        const formData = new FormData()

        // 添加所有选择的文件
        console.log('Building FormData with files:', this.fileList.length)
        this.fileList.forEach((fileItem, index) => {
          // el-upload的文件对象结构
          const file = fileItem.raw || fileItem.originFileObj || fileItem
          if (file && file instanceof File) {
            console.log(`Adding file ${index + 1}:`, file.name, file.size, 'bytes')
            formData.append('files', file)
          } else {
            console.log(`Skipping invalid file ${index + 1}:`, fileItem)
          }
        })

        // 调试信息
        console.log('FileList:', this.fileList)
        console.log('FormData entries count:', Array.from(formData.entries()).length)
        Array.from(formData.entries()).forEach(([key, value], index) => {
          if (value instanceof File) {
            console.log(`FormData entry ${index + 1}: ${key} = File(${value.name}, ${value.size} bytes)`)
          } else {
            console.log(`FormData entry ${index + 1}: ${key} = ${value}`)
          }
        })

        const response = await axios.post(this.uploadUrl, formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        })

        if (response.data.message) {
          ElMessage.success(response.data.message)
          this.fileList = []
          // 清除上传组件的文件列表
          if (this.$refs.uploadRef) {
            this.$refs.uploadRef.clearFiles()
          }
          this.loadUploadedFiles()
        } else {
          ElMessage.error('上传失败')
        }
      } catch (error) {
        console.error('Upload error:', error)
        ElMessage.error('上传失败: ' + (error.response?.data?.error || error.message))
      } finally {
        this.uploading = false
      }
    },

    handleUploadSuccess(response, file, fileList) {
      this.uploading = false
      if (response.message) {
        ElMessage.success(response.message)
        this.fileList = []
        this.loadUploadedFiles()
      } else {
        ElMessage.error('上传失败')
      }
    },

    handleUploadError(err, file, fileList) {
      this.uploading = false
      ElMessage.error('上传失败: ' + err.message)
    },

    handleFileChange(file, fileList) {
      this.fileList = fileList
    },

    clearFiles() {
      this.fileList = []
      // 清除上传组件的文件列表
      if (this.$refs.uploadRef) {
        this.$refs.uploadRef.clearFiles()
      }
    },

    async loadUploadedFiles() {
      try {
        const response = await axios.get('/api/file-upload/files')
        if (response.data.files) {
          this.uploadedFiles = response.data.files
        }
      } catch (error) {
        console.error('加载文件列表失败:', error)
      }
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
          this.loadUploadedFiles()
        }
      } catch (error) {
        if (error !== 'cancel') {
          ElMessage.error('删除失败')
        }
      }
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
      return date.toLocaleString()
    },

    downloadFile(url, filename) {
      // 创建一个临时的a标签来触发下载
      const link = document.createElement('a')
      link.href = url
      link.download = filename
      link.style.display = 'none'
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
    },

    handleImageError(event) {
      // 图片加载失败时显示默认图标
      const img = event.target
      const parent = img.parentElement
      parent.innerHTML = '<div class="file-icon">🖼️</div>'
    },

    viewMoreFiles(category) {
      // 跳转到文件列表页面
      this.$router.push({
        path: `/file-category/${category}`,
        query: {
          from: 'upload'
        }
      })
    },

    handleResize() {
      // 更新屏幕宽度
      this.screenWidth = window.innerWidth
    }
  }
}
</script>

<style scoped>
.file-upload {
  padding: 20px;
}

.upload-area {
  margin-bottom: 30px;
}

.upload-demo {
  width: 100%;
}

.upload-actions {
  margin-top: 20px;
  text-align: center;
}

.upload-actions .el-button {
  margin: 0 10px;
}

.uploaded-files {
  margin-top: 30px;
}

.uploaded-files h3 {
  margin-bottom: 20px;
  color: #333;
}

.card-header {
  display: flex;
  align-items: center;
}

.card-icon {
  margin-right: 8px;
  font-size: 18px;
}

.card-header span {
  font-weight: bold;
}

/* 文件分类样式 */
.file-category {
  margin-bottom: 30px;
}

.category-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 15px;
}

.category-header h4 {
  color: #333;
  font-size: 16px;
  font-weight: 600;
  border-bottom: 2px solid #e6e6e6;
  padding-bottom: 8px;
  margin: 0;
}

.file-count {
  color: #909399;
  font-size: 14px;
  font-weight: normal;
}

/* 查看更多按钮样式 */
.view-more {
  text-align: center;
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid #f0f0f0;
}

.view-more .el-button {
  color: #409eff;
  font-weight: 500;
}

.view-more .el-button:hover {
  color: #66b1ff;
  background-color: #ecf5ff;
}

/* 文件网格布局 */
.file-grid {
  display: grid;
  gap: 20px;
  margin-top: 15px;
}

/* 文件项样式 */
.file-item {
  background: #fff;
  border: 1px solid #e6e6e6;
  border-radius: 8px;
  overflow: hidden;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.file-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
  border-color: #409eff;
}

/* 文件预览区域 */
.file-preview {
  height: 120px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f8f9fa;
  border-bottom: 1px solid #e6e6e6;
  overflow: hidden;
}

.file-preview img {
  max-width: 100%;
  max-height: 100%;
  object-fit: cover;
}

.file-icon {
  font-size: 48px;
  color: #909399;
}

/* 文件信息区域 */
.file-info {
  padding: 12px;
}

.file-name {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
  margin-bottom: 8px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  line-height: 1.4;
}

.file-size {
  font-size: 12px;
  color: #909399;
  margin-bottom: 12px;
}

/* 文件操作按钮 */
.file-actions {
  display: flex;
  gap: 8px;
}

.file-actions .el-button {
  flex: 1;
  height: 28px;
  font-size: 12px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .file-grid {
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    gap: 15px;
  }

  .file-preview {
    height: 100px;
  }

  .file-icon {
    font-size: 36px;
  }

  .file-info {
    padding: 10px;
  }

  .file-name {
    font-size: 13px;
  }
}

@media (max-width: 480px) {
  .file-grid {
    grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
    gap: 10px;
  }

  .file-preview {
    height: 80px;
  }

  .file-icon {
    font-size: 28px;
  }

  .file-info {
    padding: 8px;
  }

  .file-name {
    font-size: 12px;
  }

  .file-actions .el-button {
    height: 24px;
    font-size: 11px;
  }
}

/* 空状态样式 */
.no-files {
  text-align: center;
  margin-top: 40px;
  color: #909399;
}
</style>
