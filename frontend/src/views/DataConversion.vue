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
                @input="updateMdPreview"
              />
            </div>
            <div class="preview-toggle">
              <el-checkbox v-model="showMdPreview">显示预览</el-checkbox>
            </div>
            <div v-if="showMdPreview" class="preview-section">
              <h4>预览效果</h4>
              <div class="preview-content" v-html="mdPreviewHtml"></div>
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
              <div class="action-section" style="margin-top: 15px;">
                <el-button type="primary" @click="downloadHtml">
                  下载HTML文件
                </el-button>
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
                @input="updateHtmlPreview"
              />
            </div>
            <div class="preview-toggle">
              <el-checkbox v-model="showHtmlPreview">显示预览</el-checkbox>
            </div>
            <div v-if="showHtmlPreview" class="preview-section">
              <h4>预览效果</h4>
              <div class="preview-content" v-html="htmlPreviewHtml"></div>
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
              <div class="action-section" style="margin-top: 15px;">
                <el-button type="primary" @click="downloadMarkdown">
                  下载Markdown文件
                </el-button>
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
              <div class="action-section" style="margin-top: 15px;">
                <el-button type="primary" @click="downloadPdfToMdResult">
                  下载Markdown文件
                </el-button>
              </div>
            </div>
          </div>
        </el-tab-pane>

        <el-tab-pane label="HTML转PDF" name="html-to-pdf">
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
              <el-button type="primary" @click="convertHtmlToPdf" :loading="converting">
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
      </el-tabs>
    </el-card>
    
    <!-- 添加PDF错误对话框 -->
    <PdfErrorDialog 
      v-model="pdfErrorDialogVisible"
      :error-message="pdfErrorMessage"
      @view-solution="viewPdfSolution"
    />
  </div>
</template>

<script>
import { ElMessage } from 'element-plus'
import { DocumentCopy, UploadFilled } from '@element-plus/icons-vue'
import axios from 'axios'
import { marked } from 'marked'

// 导入PDF错误对话框组件
import PdfErrorDialog from '@/components/PdfErrorDialog.vue'
import { useRouter } from 'vue-router'

export default {
  name: 'DataConversion',
  components: {
    DocumentCopy,
    UploadFilled,
    PdfErrorDialog
  },
  setup() {
    const router = useRouter()
    
    return {
      router
    }
  },
  data() {
    return {
      activeTab: 'md-to-html',

      // Markdown转HTML
      markdownInput: '',
      htmlOutput: '',
      showMdPreview: true,
      mdPreviewHtml: '',

      // HTML转Markdown
      htmlInput: '',
      markdownOutput: '',
      showHtmlPreview: true,
      htmlPreviewHtml: '',

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

      uploadUrl: '/api/data-conversion/upload-pdf',
      pdfErrorDialogVisible: false,
      pdfErrorMessage: ''
    }
  },
  methods: {
    updateMdPreview() {
      if (this.markdownInput) {
        try {
          this.mdPreviewHtml = marked.parse(this.markdownInput)
        } catch (e) {
          this.mdPreviewHtml = '<p class="error">预览解析错误: ' + e.message + '</p>'
        }
      } else {
        this.mdPreviewHtml = '<p class="empty-preview">暂无内容，请输入 Markdown 内容</p>'
      }
    },

    updateHtmlPreview() {
      this.htmlPreviewHtml = this.htmlInput || '<p class="empty-preview">暂无内容，请输入 HTML 内容</p>'
    },

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
          // 处理非200状态码的错误
          this.pdfErrorMessage = 'PDF生成失败: 服务器返回错误状态码 ' + response.status
          this.pdfErrorDialogVisible = true
          ElMessage.error('PDF生成失败，请查看错误详情')
        }
      } catch (error) {
        // 处理网络错误或异常
        console.error('PDF生成异常:', error)
        let errorMessage = 'PDF生成失败'
        if (error.response) {
          // 服务器响应了错误状态码
          if (error.response.status) {
            errorMessage = `PDF生成失败: ${error.response.status} ${error.response.statusText}`
          } else {
            errorMessage = 'PDF生成失败: 服务器响应错误'
          }
        } else if (error.request) {
          // 请求已发出但没有收到响应
          errorMessage = 'PDF生成失败: 无法连接到服务器'
        } else {
          // 其他错误
          errorMessage = 'PDF生成失败: ' + (error.message || '未知错误')
        }

        this.pdfErrorMessage = errorMessage
        this.pdfErrorDialogVisible = true
        ElMessage.error('PDF生成失败，请查看错误详情')
      } finally {
        // 确保总是重置加载状态
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

    async convertHtmlToPdf() {
      if (!this.htmlInput) {
        ElMessage.warning('请输入HTML文本')
        return
      }

      this.converting = true
      try {
        // 直接将HTML发送到后端生成PDF
        const response = await axios.post('/api/data-conversion/html-to-pdf', {
          html_text: this.htmlInput
        }, {
          responseType: 'blob'
        })

        if (response.status === 200) {
          const blob = new Blob([response.data], { type: 'application/pdf' })
          this.pdfUrl = URL.createObjectURL(blob)
          this.pdfSize = response.data.size
          ElMessage.success('PDF生成成功')
        } else {
          // 处理非200状态码的错误
          this.pdfErrorMessage = 'PDF生成失败: 服务器返回错误状态码 ' + response.status
          this.pdfErrorDialogVisible = true
          ElMessage.error('PDF生成失败，请查看错误详情')
        }
      } catch (error) {
        // 处理网络错误或异常
        console.error('HTML转PDF生成异常:', error)
        let errorMessage = 'PDF生成失败'
        if (error.response) {
          // 服务器响应了错误状态码
          if (error.response.status) {
            errorMessage = `PDF生成失败: ${error.response.status} ${error.response.statusText}`
          } else {
            errorMessage = 'PDF生成失败: 服务器响应错误'
          }
        } else if (error.request) {
          // 请求已发出但没有收到响应
          errorMessage = 'PDF生成失败: 无法连接到服务器'
        } else {
          // 其他错误
          errorMessage = 'PDF生成失败: ' + (error.message || '未知错误')
        }

        this.pdfErrorMessage = errorMessage
        this.pdfErrorDialogVisible = true
        ElMessage.error('PDF生成失败，请查看错误详情')
      } finally {
        // 确保总是重置加载状态
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
      this.mdPreviewHtml = ''
      this.htmlPreviewHtml = ''
    },

    downloadHtml() {
      if (this.htmlOutput) {
        // 确保下载的是完整的HTML文档
        let htmlContent = this.htmlOutput;
        if (!htmlContent.trim().startsWith('<!DOCTYPE')) {
          // 如果不是完整的HTML文档，包装成完整的文档
          htmlContent = `<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Markdown转换结果</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }
        h1, h2, h3, h4, h5, h6 {
            margin-top: 24px;
            margin-bottom: 16px;
            font-weight: 600;
            line-height: 1.25;
        }
        h1 {
            font-size: 2em;
            border-bottom: 1px solid #eaecef;
            padding-bottom: 0.3em;
        }
        h2 {
            font-size: 1.5em;
            border-bottom: 1px solid #eaecef;
            padding-bottom: 0.3em;
        }
        h3 {
            font-size: 1.25em;
        }
        p {
            margin-top: 0;
            margin-bottom: 16px;
        }
        a {
            color: #0366d6;
            text-decoration: none;
        }
        a:hover {
            text-decoration: underline;
        }
        code {
            padding: 0.2em 0.4em;
            margin: 0;
            font-size: 85%;
            background-color: rgba(27,31,35,0.05);
            border-radius: 3px;
            font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
        }
        pre {
            padding: 16px;
            overflow: auto;
            font-size: 85%;
            line-height: 1.45;
            background-color: #f6f8fa;
            border-radius: 3px;
        }
        pre code {
            padding: 0;
            margin: 0;
            overflow: visible;
            font-size: 100%;
            word-wrap: normal;
            background-color: transparent;
            border: 0;
        }
        blockquote {
            padding: 0 1em;
            color: #6a737d;
            border-left: 0.25em solid #dfe2e5;
        }
        ul, ol {
            padding-left: 2em;
        }
        li {
            margin-bottom: 0.25em;
        }
        table {
            display: block;
            width: 100%;
            overflow: auto;
            border-collapse: collapse;
        }
        table th, table td {
            padding: 6px 13px;
            border: 1px solid #dfe2e5;
        }
        table tr:nth-child(2n) {
            background-color: #f6f8fa;
        }
        hr {
            height: 0.25em;
            padding: 0;
            margin: 24px 0;
            background-color: #e1e4e8;
            border: 0;
        }
    </style>
</head>
<body>
    ${this.htmlOutput}
</body>
</html>`;
        }
        
        const blob = new Blob([htmlContent], { type: 'text/html;charset=utf-8' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = 'converted.html';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
      }
    },

    downloadPdfToMdResult() {
      if (this.markdownFromPdf) {
        const blob = new Blob([this.markdownFromPdf], { type: 'text/markdown;charset=utf-8' })
        const url = URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.download = 'pdf_converted.md'
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        URL.revokeObjectURL(url)
      }
    },

    downloadMarkdown() {
      if (this.markdownOutput) {
        const blob = new Blob([this.markdownOutput], { type: 'text/markdown;charset=utf-8' })
        const url = URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.download = 'converted.md'
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        URL.revokeObjectURL(url)
      }
    },

    viewPdfSolution() {
      // 跳转到PDF帮助页面
      this.router.push('/pdf-help')
    }
  },
  watch: {
    markdownInput: {
      handler() {
        if (this.showMdPreview) {
          this.updateMdPreview()
        }
      },
      immediate: true
    },
    htmlInput: {
      handler() {
        if (this.showHtmlPreview) {
          this.updateHtmlPreview()
        }
      },
      immediate: true
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

.input-section, .output-section, .preview-section {
  flex: 1;
}

.input-section h4, .output-section h4, .preview-section h4 {
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

.preview-toggle {
  text-align: right;
  padding: 10px 0;
}

.preview-content {
  border: 1px solid #e6e6e6;
  border-radius: 4px;
  padding: 16px;
  min-height: 100px;
  background-color: #fff;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  line-height: 1.6;
}

.preview-content :deep(h1),
.preview-content :deep(h2),
.preview-content :deep(h3),
.preview-content :deep(h4),
.preview-content :deep(h5),
.preview-content :deep(h6) {
  margin-top: 1.5em;
  margin-bottom: 0.5em;
  color: #333;
}

.preview-content :deep(h1) {
  font-size: 2em;
  border-bottom: 1px solid #eee;
  padding-bottom: 0.3em;
}

.preview-content :deep(h2) {
  font-size: 1.5em;
  border-bottom: 1px solid #eee;
  padding-bottom: 0.3em;
}

.preview-content :deep(p) {
  margin: 1em 0;
}

.preview-content :deep(code) {
  background-color: #f6f8fa;
  padding: 0.2em 0.4em;
  border-radius: 3px;
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 0.9em;
}

.preview-content :deep(pre) {
  background-color: #f6f8fa;
  padding: 16px;
  border-radius: 6px;
  overflow-x: auto;
  margin: 1em 0;
}

.preview-content :deep(pre code) {
  background-color: transparent;
  padding: 0;
}

.preview-content :deep(blockquote) {
  border-left: 4px solid #ddd;
  padding-left: 16px;
  margin: 1em 0;
  color: #666;
}

.preview-content :deep(table) {
  border-collapse: collapse;
  width: 100%;
  margin: 1em 0;
}

.preview-content :deep(th),
.preview-content :deep(td) {
  border: 1px solid #ddd;
  padding: 8px 12px;
  text-align: left;
}

.preview-content :deep(th) {
  background-color: #f8f9fa;
  font-weight: bold;
}

.preview-content :deep(ul),
.preview-content :deep(ol) {
  margin: 1em 0;
  padding-left: 2em;
}

.preview-content :deep(li) {
  margin: 0.5em 0;
}

.preview-content :deep(a) {
  color: #409eff;
  text-decoration: none;
}

.preview-content :deep(a:hover) {
  text-decoration: underline;
}

.preview-content :deep(img) {
  max-width: 100%;
  height: auto;
  border-radius: 4px;
}

.empty-preview {
  text-align: center;
  color: #999;
  font-style: italic;
  margin: 2em 0;
}

.error {
  color: #f56c6c;
  font-style: italic;
}

/* 添加PDF错误对话框样式 */
.error-dialog {
  text-align: center;
}

.error-icon {
  font-size: 48px;
  color: #F56C6C;
  margin-bottom: 20px;
}

.error-content h3 {
  margin: 0 0 10px 0;
  color: #333;
}

.error-message {
  color: #666;
  margin-bottom: 20px;
}

.solution {
  background-color: #f5f7fa;
  border-radius: 4px;
  padding: 15px;
  text-align: left;
}

.solution h4 {
  margin: 0 0 10px 0;
  color: #333;
}

.solution ol {
  margin: 0 0 15px 20px;
  padding: 0;
}

.solution li {
  margin-bottom: 8px;
  line-height: 1.5;
}

.solution p {
  margin: 0;
  font-size: 14px;
  color: #999;
}
</style>
