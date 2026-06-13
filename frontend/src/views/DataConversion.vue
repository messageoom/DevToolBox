<template>
  <ToolPage :title="$t('tools.dataConversion.title')" :icon="Switch">
    <el-tabs v-model="activeTab">
      <el-tab-pane :label="$t('tools.dataConversion.tab.mdToHtml')" name="md-to-html">
        <div class="tool-section">
          <div class="input-section">
            <h4 class="section-title">{{ $t('tools.dataConversion.label.inputMarkdown') }}</h4>
            <el-input
              v-model="markdownInput"
              type="textarea"
              :rows="8"
              :placeholder="$t('tools.dataConversion.label.inputMarkdown')"
              style="width: 100%;"
              @input="updateMdPreview"
            />
            <div class="field-toolbar">
              <span class="field-stats" v-if="markdownInput">
                {{ markdownInput.length }} {{ $t('tools.dataConversion.label.chars') }} · {{ lineCount(markdownInput) }} {{ $t('tools.dataConversion.label.lines') }}
              </span>
              <div class="toolbar-actions">
                <el-button link size="small" @click="loadSample('markdown')">{{ $t('tools.dataConversion.label.sample') }}</el-button>
              </div>
            </div>
          </div>
          <div class="preview-toggle">
            <el-checkbox v-model="showMdPreview">{{ $t('tools.dataConversion.label.showPreview') }}</el-checkbox>
          </div>
          <div v-if="showMdPreview" class="preview-section">
            <h4 class="section-title">{{ $t('tools.dataConversion.label.preview') }}</h4>
            <!-- eslint-disable-next-line vue/no-v-html -->
            <div class="preview-content" v-html="sanitizedMdPreviewHtml"></div>
          </div>
          <div class="action-section">
            <el-button type="primary" @click="convertMdToHtml" :loading="converting">
              {{ $t('tools.dataConversion.label.convert') }}
            </el-button>
            <el-button @click="clearAll">{{ $t('tools.dataConversion.label.clear') }}</el-button>
          </div>
          <div class="output-section" v-if="htmlOutput">
            <h4 class="section-title">{{ $t('tools.dataConversion.label.htmlOutput') }}</h4>
            <el-input
              v-model="htmlOutput"
              type="textarea"
              :rows="8"
              readonly
              style="width: 100%;"
            />
            <div class="field-toolbar">
              <span class="field-stats" v-if="htmlOutput">
                {{ htmlOutput.length }} {{ $t('tools.dataConversion.label.chars') }}
              </span>
              <div class="toolbar-actions">
                <el-button link size="small" type="primary" @click="copyText(htmlOutput)">
                  <el-icon><CopyDocument /></el-icon> {{ $t('tools.dataConversion.label.copy') }}
                </el-button>
              </div>
            </div>
            <div class="stats" v-if="conversionStats">
              <el-descriptions :column="2" size="small" border>
                <el-descriptions-item :label="$t('tools.dataConversion.label.originalLength')">
                  {{ conversionStats.original_length }} {{ $t('tools.dataConversion.label.chars') }}
                </el-descriptions-item>
                <el-descriptions-item :label="$t('tools.dataConversion.label.outputLength')">
                  {{ conversionStats.html_length }} {{ $t('tools.dataConversion.label.chars') }}
                </el-descriptions-item>
              </el-descriptions>
            </div>
            <div class="action-section" style="margin-top: 15px;">
              <el-button type="primary" @click="downloadHtml">
                {{ $t('tools.dataConversion.label.downloadHtml') }}
              </el-button>
            </div>
          </div>
        </div>
      </el-tab-pane>

      <el-tab-pane :label="$t('tools.dataConversion.tab.htmlToMd')" name="html-to-md">
        <div class="tool-section">
          <div class="input-section">
            <h4 class="section-title">{{ $t('tools.dataConversion.label.inputHtml') }}</h4>
            <el-input
              v-model="htmlInput"
              type="textarea"
              :rows="8"
              :placeholder="$t('tools.dataConversion.label.inputHtml')"
              style="width: 100%;"
              @input="updateHtmlPreview"
            />
            <div class="field-toolbar">
              <span class="field-stats" v-if="htmlInput">
                {{ htmlInput.length }} {{ $t('tools.dataConversion.label.chars') }} · {{ lineCount(htmlInput) }} {{ $t('tools.dataConversion.label.lines') }}
              </span>
              <div class="toolbar-actions">
                <el-button link size="small" @click="loadSample('html')">{{ $t('tools.dataConversion.label.sample') }}</el-button>
              </div>
            </div>
          </div>
          <div class="preview-toggle">
            <el-checkbox v-model="showHtmlPreview">{{ $t('tools.dataConversion.label.showPreview') }}</el-checkbox>
          </div>
          <div v-if="showHtmlPreview" class="preview-section">
            <h4 class="section-title">{{ $t('tools.dataConversion.label.preview') }}</h4>
            <!-- eslint-disable-next-line vue/no-v-html -->
            <div class="preview-content" v-html="sanitizedHtmlPreviewHtml"></div>
          </div>
          <div class="action-section">
            <el-button type="primary" @click="convertHtmlToMd" :loading="converting">
              {{ $t('tools.dataConversion.label.convert') }}
            </el-button>
            <el-button @click="clearAll">{{ $t('tools.dataConversion.label.clear') }}</el-button>
          </div>
          <div class="output-section" v-if="markdownOutput">
            <h4 class="section-title">{{ $t('tools.dataConversion.label.markdownOutput') }}</h4>
            <el-input
              v-model="markdownOutput"
              type="textarea"
              :rows="8"
              readonly
              style="width: 100%;"
            />
            <div class="field-toolbar">
              <span class="field-stats" v-if="markdownOutput">
                {{ markdownOutput.length }} {{ $t('tools.dataConversion.label.chars') }}
              </span>
              <div class="toolbar-actions">
                <el-button link size="small" type="primary" @click="copyText(markdownOutput)">
                  <el-icon><CopyDocument /></el-icon> {{ $t('tools.dataConversion.label.copy') }}
                </el-button>
              </div>
            </div>
            <div class="stats" v-if="conversionStats">
              <el-descriptions :column="2" size="small" border>
                <el-descriptions-item :label="$t('tools.dataConversion.label.originalLength')">
                  {{ conversionStats.original_length }} {{ $t('tools.dataConversion.label.chars') }}
                </el-descriptions-item>
                <el-descriptions-item :label="$t('tools.dataConversion.label.outputLength')">
                  {{ conversionStats.markdown_length }} {{ $t('tools.dataConversion.label.chars') }}
                </el-descriptions-item>
              </el-descriptions>
            </div>
            <div class="action-section" style="margin-top: 15px;">
              <el-button type="primary" @click="downloadMarkdown">
                {{ $t('tools.dataConversion.label.downloadMarkdown') }}
              </el-button>
            </div>
          </div>
        </div>
      </el-tab-pane>

      <el-tab-pane :label="$t('tools.dataConversion.tab.mdToPdf')" name="md-to-pdf">
        <div class="tool-section">
          <div class="input-section">
            <h4 class="section-title">{{ $t('tools.dataConversion.label.inputMarkdown') }}</h4>
            <el-input
              v-model="markdownInput"
              type="textarea"
              :rows="8"
              :placeholder="$t('tools.dataConversion.label.inputMarkdown')"
              style="width: 100%;"
            />
            <div class="field-toolbar">
              <span class="field-stats" v-if="markdownInput">
                {{ markdownInput.length }} {{ $t('tools.dataConversion.label.chars') }} · {{ lineCount(markdownInput) }} {{ $t('tools.dataConversion.label.lines') }}
              </span>
              <div class="toolbar-actions">
                <el-button link size="small" @click="loadSample('markdown')">{{ $t('tools.dataConversion.label.sample') }}</el-button>
              </div>
            </div>
          </div>
          <div class="action-section">
            <el-button type="primary" @click="convertMdToPdf" :loading="converting">
              {{ $t('tools.dataConversion.label.generatePdf') }}
            </el-button>
            <el-button @click="clearAll">{{ $t('tools.dataConversion.label.clear') }}</el-button>
          </div>
          <div class="output-section" v-if="pdfUrl">
            <h4 class="section-title">{{ $t('tools.dataConversion.label.pdfGenerated') }}</h4>
            <el-alert
              :title="$t('tools.dataConversion.label.pdfGenerated')"
              type="success"
              :description="`${$t('tools.dataConversion.label.fileSize')}: ${pdfSize} bytes`"
              show-icon
              style="margin-bottom: 20px;"
            />
            <el-button type="primary" @click="downloadPdf">
              {{ $t('tools.dataConversion.label.downloadPdf') }}
            </el-button>
          </div>
        </div>
      </el-tab-pane>

      <el-tab-pane :label="$t('tools.dataConversion.tab.pdfToMd')" name="pdf-to-md">
        <div class="tool-section">
          <div class="input-section">
            <h4 class="section-title">{{ $t('tools.dataConversion.label.uploadPdf') }}</h4>
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
                {{ $t('tools.dataConversion.label.pdfDropzone') }}<em>{{ $t('tools.dataConversion.label.pdfUploadHint') }}</em>
              </div>
              <template #tip>
                <div class="el-upload__tip">{{ $t('tools.dataConversion.message.onlyPdfAllowed') }}</div>
              </template>
            </el-upload>
          </div>
          <div class="action-section">
            <el-button type="primary" @click="convertPdfToMd" :loading="converting" :disabled="!uploadedFile">
              {{ $t('tools.dataConversion.label.convert') }}
            </el-button>
            <el-button @click="clearAll">{{ $t('tools.dataConversion.label.clear') }}</el-button>
          </div>
          <div class="output-section" v-if="markdownFromPdf">
            <h4 class="section-title">{{ $t('tools.dataConversion.label.markdownOutput') }}</h4>
            <el-input
              v-model="markdownFromPdf"
              type="textarea"
              :rows="8"
              readonly
              style="width: 100%;"
            />
            <div class="field-toolbar">
              <span class="field-stats" v-if="markdownFromPdf">
                {{ markdownFromPdf.length }} {{ $t('tools.dataConversion.label.chars') }}
              </span>
              <div class="toolbar-actions">
                <el-button link size="small" type="primary" @click="copyText(markdownFromPdf)">
                  <el-icon><CopyDocument /></el-icon> {{ $t('tools.dataConversion.label.copy') }}
                </el-button>
              </div>
            </div>
            <div class="stats" v-if="pdfConversionStats">
              <el-descriptions :column="2" size="small" border>
                <el-descriptions-item :label="$t('tools.dataConversion.label.pageCount')">
                  {{ pdfConversionStats.pages }} {{ $t('tools.dataConversion.label.pageUnit') }}
                </el-descriptions-item>
                <el-descriptions-item :label="$t('tools.dataConversion.label.chars')">
                  {{ pdfConversionStats.characters }} {{ $t('tools.dataConversion.label.chars') }}
                </el-descriptions-item>
              </el-descriptions>
            </div>
            <div class="action-section" style="margin-top: 15px;">
              <el-button type="primary" @click="downloadPdfToMdResult">
                {{ $t('tools.dataConversion.label.downloadMarkdown') }}
              </el-button>
            </div>
          </div>
        </div>
      </el-tab-pane>

      <el-tab-pane :label="$t('tools.dataConversion.tab.htmlToPdf')" name="html-to-pdf">
        <div class="tool-section">
          <div class="input-section">
            <h4 class="section-title">{{ $t('tools.dataConversion.label.inputHtml') }}</h4>
            <el-input
              v-model="htmlInput"
              type="textarea"
              :rows="8"
              :placeholder="$t('tools.dataConversion.label.inputHtml')"
              style="width: 100%;"
            />
            <div class="field-toolbar">
              <span class="field-stats" v-if="htmlInput">
                {{ htmlInput.length }} {{ $t('tools.dataConversion.label.chars') }} · {{ lineCount(htmlInput) }} {{ $t('tools.dataConversion.label.lines') }}
              </span>
              <div class="toolbar-actions">
                <el-button link size="small" @click="loadSample('html')">{{ $t('tools.dataConversion.label.sample') }}</el-button>
              </div>
            </div>
          </div>
          <div class="action-section">
            <el-button type="primary" @click="convertHtmlToPdf" :loading="converting">
              {{ $t('tools.dataConversion.label.generatePdf') }}
            </el-button>
            <el-button @click="clearAll">{{ $t('tools.dataConversion.label.clear') }}</el-button>
          </div>
          <div class="output-section" v-if="pdfUrl">
            <h4 class="section-title">{{ $t('tools.dataConversion.label.pdfGenerated') }}</h4>
            <el-alert
              :title="$t('tools.dataConversion.label.pdfGenerated')"
              type="success"
              :description="`${$t('tools.dataConversion.label.fileSize')}: ${pdfSize} bytes`"
              show-icon
              style="margin-bottom: 20px;"
            />
            <el-button type="primary" @click="downloadPdf">
              {{ $t('tools.dataConversion.label.downloadPdf') }}
            </el-button>
          </div>
        </div>
      </el-tab-pane>
    </el-tabs>

    <!-- PDF Error Dialog -->
    <PdfErrorDialog
      v-model="pdfErrorDialogVisible"
      :error-message="pdfErrorMessage"
      @view-solution="viewPdfSolution"
    />
  </ToolPage>
</template>

<script>
import { ElMessage } from 'element-plus'
import { Switch, UploadFilled, CopyDocument } from '@element-plus/icons-vue'
import axios from 'axios'
import { marked } from 'marked'

// DOMPurify import - sanitize HTML to prevent XSS attacks via v-html
// If dompurify is not installed, run: npm install dompurify
import DOMPurify from 'dompurify'

import PdfErrorDialog from '@/components/PdfErrorDialog.vue'
import { useRouter } from 'vue-router'
import ToolPage from '@/components/ToolPage.vue'
import { useDeviceStore } from '@/stores/device.js'
import { copyToClipboard } from '@/utils/format.js'

const SAMPLES = {
  markdown: `# DevToolBox 使用指南

## 简介

**DevToolBox** 是一款功能强大的开发者工具箱。

## 功能特性

- JSON/YAML 工具
- Markdown 编辑器
- 文件管理
- 文本传输

### 代码示例

\`\`\`python
def hello():
    print("Hello, DevToolBox!")
\`\`\`

> 让开发更高效！

| 工具 | 状态 |
|------|------|
| JSON | ✅ |
| YAML | ✅ |`,
  html: `<h1>DevToolBox</h1>
<h2>功能列表</h2>
<ul>
  <li><strong>JSON工具</strong> — 格式化、压缩、验证</li>
  <li><strong>YAML工具</strong> — 格式化、转换</li>
  <li><strong>Markdown工具</strong> — 转换、统计</li>
</ul>
<blockquote>
  <p>DevToolBox 让开发更高效！</p>
</blockquote>
<table>
  <tr><th>工具</th><th>状态</th></tr>
  <tr><td>JSON</td><td>✅</td></tr>
  <tr><td>YAML</td><td>✅</td></tr>
</table>`
}

export default {
  name: 'DataConversion',
  components: {
    Switch,
    UploadFilled,
    CopyDocument,
    PdfErrorDialog,
    ToolPage
  },
  setup() {
    const router = useRouter()

    return {
      router
    }
  },
  data() {
    const deviceStore = useDeviceStore()
    return {
      deviceStore,
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
  computed: {
    sanitizedMdPreviewHtml() {
      return DOMPurify.sanitize(this.mdPreviewHtml)
    },
    sanitizedHtmlPreviewHtml() {
      return DOMPurify.sanitize(this.htmlPreviewHtml)
    }
  },
  methods: {
    lineCount(text) {
      if (!text) return 0
      return text.split('\n').length
    },

    async copyText(text) {
      try {
        await copyToClipboard(text)
        ElMessage.success(this.$t('tools.dataConversion.message.copied'))
      } catch {
        ElMessage.error(this.$t('common.copyFail'))
      }
    },

    loadSample(type) {
      const sample = SAMPLES[type]
      if (!sample) return
      switch (type) {
        case 'markdown': this.markdownInput = sample; break
        case 'html': this.htmlInput = sample; break
      }
    },

    updateMdPreview() {
      if (this.markdownInput) {
        try {
          this.mdPreviewHtml = marked.parse(this.markdownInput)
        } catch (e) {
          this.mdPreviewHtml = '<p class="error">' + this.$t('tools.dataConversion.message.previewParseError') + ': ' + e.message + '</p>'
        }
      } else {
        this.mdPreviewHtml = '<p class="empty-preview">' + this.$t('tools.dataConversion.label.emptyMdPreview') + '</p>'
      }
    },

    updateHtmlPreview() {
      this.htmlPreviewHtml = this.htmlInput || '<p class="empty-preview">' + this.$t('tools.dataConversion.label.emptyHtmlPreview') + '</p>'
    },

    async convertMdToHtml() {
      if (!this.markdownInput) {
        ElMessage.warning(this.$t('tools.dataConversion.message.inputMarkdownRequired'))
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
          ElMessage.success(this.$t('tools.dataConversion.message.convertSuccess'))
        } else {
          ElMessage.error(response.data.error)
        }
      } catch (error) {
        ElMessage.error(this.$t('tools.dataConversion.message.convertFail') + ': ' + error.response?.data?.error || error.message)
      } finally {
        this.converting = false
      }
    },

    async convertHtmlToMd() {
      if (!this.htmlInput) {
        ElMessage.warning(this.$t('tools.dataConversion.message.inputHtmlRequired'))
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
          ElMessage.success(this.$t('tools.dataConversion.message.convertSuccess'))
        } else {
          ElMessage.error(response.data.error)
        }
      } catch (error) {
        ElMessage.error(this.$t('tools.dataConversion.message.convertFail') + ': ' + error.response?.data?.error || error.message)
      } finally {
        this.converting = false
      }
    },

    async convertMdToPdf() {
      if (!this.markdownInput) {
        ElMessage.warning(this.$t('tools.dataConversion.message.inputMarkdownRequired'))
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
          ElMessage.success(this.$t('tools.dataConversion.message.pdfSuccess'))
        } else {
          this.pdfErrorMessage = this.$t('tools.dataConversion.message.pdfFailStatus') + ' ' + response.status
          this.pdfErrorDialogVisible = true
          ElMessage.error(this.$t('tools.dataConversion.message.pdfFail'))
        }
      } catch (error) {
        let errorMessage = this.$t('tools.dataConversion.message.pdfFail')
        if (error.response) {
          if (error.response.status) {
            errorMessage = this.$t('tools.dataConversion.message.pdfFailStatus') + `: ${error.response.status} ${error.response.statusText}`
          } else {
            errorMessage = this.$t('tools.dataConversion.message.pdfFailResponse')
          }
        } else if (error.request) {
          errorMessage = this.$t('tools.dataConversion.message.pdfFailNetwork')
        } else {
          errorMessage = this.$t('tools.dataConversion.message.pdfFailWithError') + ': ' + (error.message || '')
        }

        this.pdfErrorMessage = errorMessage
        this.pdfErrorDialogVisible = true
        ElMessage.error(this.$t('tools.dataConversion.message.pdfFail'))
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
        ElMessage.success(this.$t('tools.dataConversion.message.fileUploadSuccess'))
      } else {
        ElMessage.error(response.error || this.$t('tools.dataConversion.message.uploadFail'))
      }
    },

    handleUploadError(err, file, fileList) {
      ElMessage.error(this.$t('tools.dataConversion.message.uploadFail') + ': ' + err.message)
    },

    beforeUpload(file) {
      const isPdf = file.type === 'application/pdf'
      const isLt10M = file.size / 1024 / 1024 < 10

      if (!isPdf) {
        ElMessage.error(this.$t('tools.dataConversion.message.onlyPdfAllowed'))
        return false
      }
      if (!isLt10M) {
        ElMessage.error(this.$t('tools.dataConversion.message.pdfSizeExceeded'))
        return false
      }
      return true
    },

    async convertPdfToMd() {
      if (!this.uploadedFile) {
        ElMessage.warning(this.$t('tools.dataConversion.message.uploadPdfFirst'))
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
          ElMessage.success(this.$t('tools.dataConversion.message.convertSuccess'))
        } else {
          ElMessage.error(response.data.error)
        }
      } catch (error) {
        ElMessage.error(this.$t('tools.dataConversion.message.convertFail') + ': ' + error.response?.data?.error || error.message)
      } finally {
        this.converting = false
      }
    },

    async convertHtmlToPdf() {
      if (!this.htmlInput) {
        ElMessage.warning(this.$t('tools.dataConversion.message.inputHtmlRequired'))
        return
      }

      this.converting = true
      try {
        const response = await axios.post('/api/data-conversion/html-to-pdf', {
          html_text: this.htmlInput
        }, {
          responseType: 'blob'
        })

        if (response.status === 200) {
          const blob = new Blob([response.data], { type: 'application/pdf' })
          this.pdfUrl = URL.createObjectURL(blob)
          this.pdfSize = response.data.size
          ElMessage.success(this.$t('tools.dataConversion.message.pdfSuccess'))
        } else {
          this.pdfErrorMessage = this.$t('tools.dataConversion.message.pdfFailStatus') + ' ' + response.status
          this.pdfErrorDialogVisible = true
          ElMessage.error(this.$t('tools.dataConversion.message.pdfFail'))
        }
      } catch (error) {
        let errorMessage = this.$t('tools.dataConversion.message.pdfFail')
        if (error.response) {
          if (error.response.status) {
            errorMessage = this.$t('tools.dataConversion.message.pdfFailStatus') + `: ${error.response.status} ${error.response.statusText}`
          } else {
            errorMessage = this.$t('tools.dataConversion.message.pdfFailResponse')
          }
        } else if (error.request) {
          errorMessage = this.$t('tools.dataConversion.message.pdfFailNetwork')
        } else {
          errorMessage = this.$t('tools.dataConversion.message.pdfFailWithError') + ': ' + (error.message || '')
        }

        this.pdfErrorMessage = errorMessage
        this.pdfErrorDialogVisible = true
        ElMessage.error(this.$t('tools.dataConversion.message.pdfFail'))
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
      this.mdPreviewHtml = ''
      this.htmlPreviewHtml = ''
    },

    downloadHtml() {
      if (this.htmlOutput) {
        let htmlContent = this.htmlOutput;
        if (!htmlContent.trim().startsWith('<!DOCTYPE')) {
          htmlContent = `<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Markdown Conversion Result</title>
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
        h1 { font-size: 2em; border-bottom: 1px solid #eaecef; padding-bottom: 0.3em; }
        h2 { font-size: 1.5em; border-bottom: 1px solid #eaecef; padding-bottom: 0.3em; }
        h3 { font-size: 1.25em; }
        p { margin-top: 0; margin-bottom: 16px; }
        a { color: #0366d6; text-decoration: none; }
        a:hover { text-decoration: underline; }
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
        pre code { padding: 0; margin: 0; overflow: visible; font-size: 100%; word-wrap: normal; background-color: transparent; border: 0; }
        blockquote { padding: 0 1em; color: #6a737d; border-left: 0.25em solid #dfe2e5; }
        ul, ol { padding-left: 2em; }
        li { margin-bottom: 0.25em; }
        table { display: block; width: 100%; overflow: auto; border-collapse: collapse; }
        table th, table td { padding: 6px 13px; border: 1px solid #dfe2e5; }
        table tr:nth-child(2n) { background-color: #f6f8fa; }
        hr { height: 0.25em; padding: 0; margin: 24px 0; background-color: #e1e4e8; border: 0; }
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
.field-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 6px;
  min-height: 24px;
}

.field-stats {
  font-size: 12px;
  color: var(--dt-text-secondary);
  line-height: 24px;
}

.toolbar-actions {
  display: flex;
  gap: 4px;
  align-items: center;
}

.stats {
  margin-top: var(--dt-spacing-md);
}

.upload-demo {
  width: 100%;
}

.preview-toggle {
  text-align: right;
  padding: var(--dt-spacing-sm) 0;
}

.preview-content {
  border: 1px solid var(--dt-border-light);
  border-radius: var(--dt-radius-sm);
  padding: var(--dt-spacing-md);
  min-height: 100px;
  background-color: var(--dt-bg-card);
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
  color: var(--dt-text-primary);
}

.preview-content :deep(h1) {
  font-size: 2em;
  border-bottom: 1px solid var(--dt-border-lighter);
  padding-bottom: 0.3em;
}

.preview-content :deep(h2) {
  font-size: 1.5em;
  border-bottom: 1px solid var(--dt-border-lighter);
  padding-bottom: 0.3em;
}

.preview-content :deep(p) {
  margin: 1em 0;
}

.preview-content :deep(code) {
  background-color: var(--dt-bg-section);
  padding: 0.2em 0.4em;
  border-radius: 3px;
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 0.9em;
}

.preview-content :deep(pre) {
  background-color: var(--dt-bg-section);
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
  border-left: 4px solid var(--dt-border-base);
  padding-left: 16px;
  margin: 1em 0;
  color: var(--dt-text-regular);
}

.preview-content :deep(table) {
  border-collapse: collapse;
  width: 100%;
  margin: 1em 0;
}

.preview-content :deep(th),
.preview-content :deep(td) {
  border: 1px solid var(--dt-border-base);
  padding: 8px 12px;
  text-align: left;
}

.preview-content :deep(th) {
  background-color: var(--dt-bg-section);
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
  color: var(--dt-primary);
  text-decoration: none;
}

.preview-content :deep(a:hover) {
  text-decoration: underline;
}

.preview-content :deep(img) {
  max-width: 100%;
  height: auto;
  border-radius: var(--dt-radius-sm);
}

.empty-preview {
  text-align: center;
  color: var(--dt-text-secondary);
  font-style: italic;
  margin: 2em 0;
}

.error {
  color: var(--dt-danger);
  font-style: italic;
}

/* PDF错误对话框样式 */
.error-dialog {
  text-align: center;
}

.error-icon {
  font-size: 48px;
  color: var(--dt-danger);
  margin-bottom: 20px;
}

.error-content h3 {
  margin: 0 0 10px 0;
  color: var(--dt-text-primary);
}

.error-message {
  color: var(--dt-text-regular);
  margin-bottom: 20px;
}

.solution {
  background-color: var(--dt-bg-page);
  border-radius: var(--dt-radius-sm);
  padding: 15px;
  text-align: left;
}

.solution h4 {
  margin: 0 0 10px 0;
  color: var(--dt-text-primary);
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
  font-size: var(--dt-font-size-base);
  color: var(--dt-text-secondary);
}
</style>
