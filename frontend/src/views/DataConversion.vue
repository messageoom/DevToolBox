<template>
  <div class="data-conversion">
    <el-card>
      <template #header>
        <div class="card-header">
          <el-icon class="card-icon"><DocumentCopy /></el-icon>
          <span>数据互转</span>
        </div>
      </template>

      <el-tabs v-model="activeTab">
        <el-tab-pane label="Markdown转HTML" name="md-to-html">
          <div class="tool-section">
            <div class="input-section">
              <h4>输入Markdown文本</h4>
              <el-input
                v-model="markdownInput"
                type="textarea"
                :rows="8"
                placeholder="请输入Markdown文本..."
                style="width: 100%;"
              />
            </div>
            <div class="action-section">
              <el-button type="primary" @click="convertMdToHtml" :loading="converting">
                转换
              </el-button>
              <el-button @click="clearAll">清空</el-button>
            </div>
            <div class="output-section" v-if="htmlOutput">
              <h4>HTML输出</h4>
              <el-input
                v-model="htmlOutput"
                type="textarea"
                :rows="8"
                readonly
                style="width: 100%;"
              />
              <div class="stats" v-if="conversionStats">
                <el-descriptions :column="2" size="small" border>
                  <el-descriptions-item label="原始长度">
                    {{ conversionStats.original_length }} 字符
                  </el-descriptions-item>
                  <el-descriptions-item label="输出长度">
                    {{ conversionStats.html_length }} 字符
                  </el-descriptions-item>
                </el-descriptions>
              </div>
            </div>
          </div>
        </el-tab-pane>

        <el-tab-pane label="HTML转Markdown" name="html-to-md">
          <div class="tool-section">
            <div class="input-section">
              <h4>输入HTML文本</h4>
              <el-input
                v-model="htmlInput"
                type="textarea"
                :rows="8"
                placeholder="请输入HTML文本..."
                style="width: 100%;"
              />
            </div>
            <div class="action-section">
              <el-button type="primary" @click="convertHtmlToMd" :loading="converting">
                转换
              </el-button>
              <el-button @click="clearAll">清空</el-button>
            </div>
            <div class="output-section" v-if="markdownOutput">
              <h4>Markdown输出</h4>
              <el-input
                v-model="markdownOutput"
                type="textarea"
                :rows="8"
                readonly
                style="width: 100%;"
              />
              <div class="stats" v-if="conversionStats">
                <el-descriptions :column="2" size="small" border>
                  <el-descriptions-item label="原始长度">
                    {{ conversionStats.original_length }} 字符
                  </el-descriptions-item>
                  <el-descriptions-item label="输出长度">
                    {{ conversionStats.markdown_length }} 字符
                  </el-descriptions-item>
                </el-descriptions>
              </div>
            </div>
          </div>
        </el-tab-pane>

        <el-tab-pane label="Markdown转PDF" name="md-to-pdf">
          <div class="tool-section">
            <div class="input-section">
              <h4>输入Markdown文本</h4>
              <el-input
                v-model="markdownInput"
                type="textarea"
                :rows="8"
                placeholder="请输入Markdown文本..."
                style="width: 100%;"
              />
            </div>
            <div class="action-section">
              <el-button type="primary" @click="convertMdToPdf" :loading="converting">
                生成PDF
              </el-button>
              <el-button @click="clearAll">清空</el-button>
            </div>
            <div class="output-section" v-if="pdfUrl">
              <h4>PDF生成成功</h4>
              <el-alert
                title="PDF已生成"
                type="success"
                :description="`文件大小: ${pdfSize} bytes`"
                show-icon
                style="margin-bottom: 20px;"
              />
              <el-button type="primary" @click="downloadPdf">
                下载PDF
              </el-button>
            </div>
          </div>
        </el-tab-pane>

        <el-tab-pane label="PDF转Markdown" name="pdf-to-md">
          <div class="tool-section">
            <div class="input-section">
              <h4>上传PDF文件</h4>
              <el-upload
                ref="uploadRef"
                class="upload-demo"
                drag
                :action="uploadUrl"
                :on-success="handleUploadSuccess"
                :on-error="handleUploadError"
                :before-upload="beforeUpload"
                :file-list="fileList"
                accept=".pdf"
                :limit="1"
              >
                <el-icon class="el-icon--upload"><upload-filled /></el-icon>
                <div class="el-upload__text">
                  将PDF文件拖到此处，或<em>点击上传</em>
                </div>
                <template #tip>
                  <div class="el-upload__tip">只能上传PDF文件，且不超过10MB</div>
                </template>
              </el-upload>
            </div>
            <div class="action-section">
              <el-button type="primary" @click="convertPdfToMd" :loading="converting" :disabled="!uploadedFile">
                转换
              </el-button>
              <el-button @click="clearAll">清空</el-button>
            </div>
            <div class="output-section" v-if="markdownFromPdf">
              <h4>Markdown输出</h4>
              <el-input
                v-model="markdownFromPdf"
                type="textarea"
                :rows="8"
                readonly
                style="width: 100%;"
              />
              <div class="stats" v-if="pdfConversionStats">
                <el-descriptions :column="2" size="small" border>
                  <el-descriptions-item label="页数">
                    {{ pdfConversionStats.pages }} 页
                  </el-descriptions-item>
                  <el-descriptions-item label="字符数">
                    {{ pdfConversionStats.characters }} 字符
                  </el-descriptions-item>
                </el-descriptions>
              </div>
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script>
import { ElMessage } from 'element-plus'
import { DocumentCopy, UploadFilled } from '@element-plus/icons-vue'
import axios from 'axios'

export default {
  name: 'DataConversion',
  components: {
    DocumentCopy,
    UploadFilled
  },
  data() {
    return {
      activeTab: 'md-to-html',

      // Markdown转HTML
      markdownInput: '',
      htmlOutput: '',

      // HTML转Markdown
      htmlInput: '',
      markdownOutput: '',

      // PDF相关
      fileList: [],
      uploadedFile: null,
      pdfUrl: '',
      pdfSize: 0,
      markdownFromPdf: '',

      // 通用
      converting: false,
      conversionStats: null,
      pdfConversionStats: null,

      uploadUrl: '/api/data-conversion/upload-pdf'
    }
  },
  methods: {
    async convertMdToHtml() {
      if (!this.markdownInput) {
        ElMessage.warning('请输入Markdown文本')
        return
      }

      this.converting = true
      try {
        const response = await axios.post('/api/data-conversion/md-to-html', {
          markdown_text: this.markdownInput
        })

        if (response.data.success) {
          this.htmlOutput = response.data.html
          this.conversionStats = {
            original_length: response.data.original_length,
            html_length: response.data.html_length
          }
          ElMessage.success('转换成功')
        } else {
          ElMessage.error(response.data.error)
        }
      } catch (error) {
        ElMessage.error('转换失败: ' + error.response?.data?.error || error.message)
      } finally {
        this.converting = false
      }
    },

    async convertHtmlToMd() {
      if (!this.htmlInput) {
        ElMessage.warning('请输入HTML文本')
        return
      }

      this.converting = true
      try {
        const response = await axios.post('/api/data-conversion/html-to-md', {
          html_text: this.htmlInput
        })

        if (response.data.success) {
          this.markdownOutput = response.data.markdown
          this.conversionStats = {
            original_length: response.data.original_length,
            markdown_length: response.data.markdown_length
          }
          ElMessage.success('转换成功')
        } else {
          ElMessage.error(response.data.error)
        }
      } catch (error) {
        ElMessage.error('转换失败: ' + error.response?.data?.error || error.message)
      } finally {
        this.converting = false
      }
    },

    async convertMdToPdf() {
      if (!this.markdownInput) {
        ElMessage.warning('请输入Markdown文本')
        return
      }

      this.converting = true
      try {
        const response = await axios.post('/api/data-conversion/md-to-pdf', {
          markdown_text: this.markdownInput
        }, {
          responseType: 'blob'
        })

        if (response.status === 200) {
          const blob = new Blob([response.data], { type: 'application/pdf' })
          this.pdfUrl = URL.createObjectURL(blob)
          this.pdfSize = response.data.size
          ElMessage.success('PDF生成成功')
        } else {
          ElMessage.error('PDF生成失败')
        }
      } catch (error) {
        ElMessage.error('PDF生成失败: ' + error.message)
      } finally {
        this.converting = false
      }
    },

    downloadPdf() {
      if (this.pdfUrl) {
        const link = document.createElement('a')
        link.href = this.pdfUrl
        link.download = 'converted.pdf'
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
      }
    },

    handleUploadSuccess(response, file, fileList) {
      if (response.success) {
        this.uploadedFile = response.filename
        this.fileList = fileList
        ElMessage.success('文件上传成功')
      } else {
        ElMessage.error(response.error || '上传失败')
      }
    },

    handleUploadError(err, file, fileList) {
      ElMessage.error('上传失败: ' + err.message)
    },

    beforeUpload(file) {
      const isPdf = file.type === 'application/pdf'
      const isLt10M = file.size / 1024 / 1024 < 10

      if (!isPdf) {
        ElMessage.error('只能上传PDF文件!')
        return false
      }
      if (!isLt10M) {
        ElMessage.error('上传文件大小不能超过10MB!')
        return false
      }
      return true
    },

    async convertPdfToMd() {
      if (!this.uploadedFile) {
        ElMessage.warning('请先上传PDF文件')
        return
      }

      this.converting = true
      try {
        const response = await axios.post('/api/data-conversion/pdf-to-md', {
          filename: this.uploadedFile
        })

        if (response.data.success) {
          this.markdownFromPdf = response.data.markdown
          this.pdfConversionStats = {
            pages: response.data.pages,
            characters: response.data.characters
          }
          ElMessage.success('转换成功')
        } else {
          ElMessage.error(response.data.error)
        }
      } catch (error) {
        ElMessage.error('转换失败: ' + error.response?.data?.error || error.message)
      } finally {
        this.converting = false
      }
    },

    clearAll() {
      this.markdownInput = ''
      this.htmlOutput = ''
      this.htmlInput = ''
      this.markdownOutput = ''
      this.fileList = []
      this.uploadedFile = null
      this.pdfUrl = ''
      this.pdfSize = 0
      this.markdownFromPdf = ''
      this.conversionStats = null
      this.pdfConversionStats = null
    }
  }
}
</script>

<style scoped>
.data-conversion {
  padding: 20px;
}

.tool-section {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.input-section, .output-section {
  flex: 1;
}

.input-section h4, .output-section h4 {
  margin-bottom: 10px;
  color: #333;
  font-weight: bold;
}

.action-section {
  text-align: center;
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

.stats {
  margin-top: 15px;
}

.upload-demo {
  width: 100%;
}
</style>
