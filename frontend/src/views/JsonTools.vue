<template>
  <ToolPage :title="$t('tools.json.title')" :icon="DocumentCopy">
    <el-tabs v-model="activeTab">
      <!-- 格式化 -->
      <el-tab-pane :label="$t('tools.json.tab.format')" name="format">
        <ToolSection
          :input-label="$t('tools.json.label.inputJson')"
          :output-label="$t('tools.json.label.formatResult')"
          :action-text="$t('tools.json.action.format')"
          :loading="formatting"
          @submit="formatJson"
        >
          <template #input>
            <el-input
              v-model="formatInput"
              type="textarea"
              :rows="10"
              :placeholder="$t('tools.json.placeholder.inputJson')"
              clearable
            />
            <div class="field-toolbar">
              <span class="field-stats" v-if="formatInput">
                {{ formatInput.length }} {{ $t('tools.json.stats.chars') }} · {{ lineCount(formatInput) }} {{ $t('tools.json.stats.lines') }}
              </span>
              <div class="toolbar-actions">
                <el-button link size="small" @click="loadSample('format')">{{ $t('tools.json.action.sample') }}</el-button>
                <el-button link size="small" v-if="formatInput || formatOutput" @click="clearFields('format')">{{ $t('tools.json.action.clear') }}</el-button>
              </div>
            </div>
          </template>
          <template #output>
            <el-input
              v-model="formatOutput"
              type="textarea"
              :rows="10"
              readonly
              :placeholder="$t('tools.json.placeholder.formatResult')"
            />
            <div class="field-toolbar" v-if="formatOutput">
              <span class="field-stats">
                {{ formatOutput.length }} {{ $t('tools.json.stats.chars') }} · {{ lineCount(formatOutput) }} {{ $t('tools.json.stats.lines') }}
              </span>
              <el-button link size="small" type="primary" @click="copyText(formatOutput)">
                <el-icon><CopyDocument /></el-icon> {{ $t('tools.json.action.copy') }}
              </el-button>
            </div>
          </template>
        </ToolSection>
      </el-tab-pane>

      <!-- 压缩 -->
      <el-tab-pane :label="$t('tools.json.tab.minify')" name="minify">
        <ToolSection
          :input-label="$t('tools.json.label.inputJson')"
          :output-label="$t('tools.json.label.minifyResult')"
          :action-text="$t('tools.json.action.minify')"
          :loading="minifying"
          @submit="minifyJson"
        >
          <template #input>
            <el-input
              v-model="minifyInput"
              type="textarea"
              :rows="10"
              :placeholder="$t('tools.json.placeholder.inputJson')"
              clearable
            />
            <div class="field-toolbar">
              <span class="field-stats" v-if="minifyInput">
                {{ minifyInput.length }} {{ $t('tools.json.stats.chars') }} · {{ lineCount(minifyInput) }} {{ $t('tools.json.stats.lines') }}
              </span>
              <div class="toolbar-actions">
                <el-button link size="small" @click="loadSample('minify')">{{ $t('tools.json.action.sample') }}</el-button>
                <el-button link size="small" v-if="minifyInput || minifyOutput" @click="clearFields('minify')">{{ $t('tools.json.action.clear') }}</el-button>
              </div>
            </div>
          </template>
          <template #output>
            <el-input
              v-model="minifyOutput"
              type="textarea"
              :rows="10"
              readonly
              :placeholder="$t('tools.json.placeholder.minifyResult')"
            />
            <div class="field-toolbar" v-if="minifyOutput">
              <span class="field-stats">
                {{ minifyOutput.length }} {{ $t('tools.json.stats.chars') }} · {{ lineCount(minifyOutput) }} {{ $t('tools.json.stats.lines') }}
              </span>
              <el-button link size="small" type="primary" @click="copyText(minifyOutput)">
                <el-icon><CopyDocument /></el-icon> {{ $t('tools.json.action.copy') }}
              </el-button>
            </div>
          </template>
        </ToolSection>
      </el-tab-pane>

      <!-- 验证 -->
      <el-tab-pane :label="$t('tools.json.tab.validate')" name="validate">
        <ToolSection
          :input-label="$t('tools.json.label.inputJson')"
          :output-label="$t('tools.json.label.validateResult')"
          :action-text="$t('tools.json.action.validate')"
          :loading="validating"
          :has-output="!!validationResult"
          @submit="validateJson"
        >
          <template #input>
            <el-input
              v-model="validateInput"
              type="textarea"
              :rows="10"
              :placeholder="$t('tools.json.placeholder.inputJson')"
              clearable
            />
            <div class="field-toolbar">
              <span class="field-stats" v-if="validateInput">
                {{ validateInput.length }} {{ $t('tools.json.stats.chars') }} · {{ lineCount(validateInput) }} {{ $t('tools.json.stats.lines') }}
              </span>
              <div class="toolbar-actions">
                <el-button link size="small" @click="loadSample('validate')">{{ $t('tools.json.action.sample') }}</el-button>
                <el-button link size="small" v-if="validateInput || validationResult" @click="validateInput = ''; validationResult = null">{{ $t('tools.json.action.clear') }}</el-button>
              </div>
            </div>
          </template>
          <template #output>
            <div class="validation-result">
              <el-alert
                :title="validationResult.valid ? $t('tools.json.message.validateSuccess') : $t('tools.json.message.validateFail')"
                :type="validationResult.valid ? 'success' : 'error'"
                :description="validationResult.message || validationResult.error"
                show-icon
              />
              <div v-if="validationResult.parsed_data" class="parsed-data-wrapper">
                <div class="field-toolbar">
                  <span class="field-stats">{{ JSON.stringify(validationResult.parsed_data).length }} {{ $t('tools.json.stats.chars') }}</span>
                  <el-button link size="small" type="primary" @click="copyText(JSON.stringify(validationResult.parsed_data, null, 2))">
                    <el-icon><CopyDocument /></el-icon> {{ $t('tools.json.action.copy') }}
                  </el-button>
                </div>
                <pre class="parsed-data">{{ JSON.stringify(validationResult.parsed_data, null, 2) }}</pre>
              </div>
            </div>
          </template>
        </ToolSection>
      </el-tab-pane>

      <!-- 转义 -->
      <el-tab-pane :label="$t('tools.json.tab.escape')" name="escape">
        <ToolSection
          :input-label="$t('tools.json.label.inputText')"
          :output-label="$t('tools.json.label.escapeResult')"
          :action-text="$t('tools.json.action.escape')"
          :loading="escaping"
          @submit="escapeJson"
        >
          <template #input>
            <el-input
              v-model="escapeInput"
              type="textarea"
              :rows="10"
              :placeholder="$t('tools.json.placeholder.inputText')"
              clearable
            />
            <div class="field-toolbar">
              <span class="field-stats" v-if="escapeInput">
                {{ escapeInput.length }} {{ $t('tools.json.stats.chars') }} · {{ lineCount(escapeInput) }} {{ $t('tools.json.stats.lines') }}
              </span>
              <div class="toolbar-actions">
                <el-button link size="small" @click="loadSample('escape')">{{ $t('tools.json.action.sample') }}</el-button>
                <el-button link size="small" v-if="escapeInput || escapeOutput" @click="clearFields('escape')">{{ $t('tools.json.action.clear') }}</el-button>
              </div>
            </div>
          </template>
          <template #output>
            <el-input
              v-model="escapeOutput"
              type="textarea"
              :rows="10"
              readonly
              :placeholder="$t('tools.json.placeholder.escapeResult')"
            />
            <div class="field-toolbar" v-if="escapeOutput">
              <span class="field-stats">
                {{ escapeOutput.length }} {{ $t('tools.json.stats.chars') }} · {{ lineCount(escapeOutput) }} {{ $t('tools.json.stats.lines') }}
              </span>
              <el-button link size="small" type="primary" @click="copyText(escapeOutput)">
                <el-icon><CopyDocument /></el-icon> {{ $t('tools.json.action.copy') }}
              </el-button>
            </div>
          </template>
        </ToolSection>
      </el-tab-pane>

      <!-- 反转义 -->
      <el-tab-pane :label="$t('tools.json.tab.unescape')" name="unescape">
        <ToolSection
          :input-label="$t('tools.json.label.inputJsonString')"
          :output-label="$t('tools.json.label.unescapeResult')"
          :action-text="$t('tools.json.action.unescape')"
          :loading="unescaping"
          @submit="unescapeJson"
        >
          <template #input>
            <el-input
              v-model="unescapeInput"
              type="textarea"
              :rows="10"
              :placeholder="$t('tools.json.placeholder.inputJson')"
              clearable
            />
            <div class="field-toolbar">
              <span class="field-stats" v-if="unescapeInput">
                {{ unescapeInput.length }} {{ $t('tools.json.stats.chars') }} · {{ lineCount(unescapeInput) }} {{ $t('tools.json.stats.lines') }}
              </span>
              <div class="toolbar-actions">
                <el-button link size="small" @click="loadSample('unescape')">{{ $t('tools.json.action.sample') }}</el-button>
                <el-button link size="small" v-if="unescapeInput || unescapeOutput" @click="clearFields('unescape')">{{ $t('tools.json.action.clear') }}</el-button>
              </div>
            </div>
          </template>
          <template #output>
            <el-input
              v-model="unescapeOutput"
              type="textarea"
              :rows="10"
              readonly
              :placeholder="$t('tools.json.placeholder.unescapeResult')"
            />
            <div class="field-toolbar" v-if="unescapeOutput">
              <span class="field-stats">
                {{ unescapeOutput.length }} {{ $t('tools.json.stats.chars') }} · {{ lineCount(unescapeOutput) }} {{ $t('tools.json.stats.lines') }}
              </span>
              <el-button link size="small" type="primary" @click="copyText(unescapeOutput)">
                <el-icon><CopyDocument /></el-icon> {{ $t('tools.json.action.copy') }}
              </el-button>
            </div>
          </template>
        </ToolSection>
      </el-tab-pane>
    </el-tabs>
  </ToolPage>
</template>

<script>
import { ElMessage } from 'element-plus'
import { DocumentCopy, CopyDocument } from '@element-plus/icons-vue'
import axios from 'axios'
import ToolPage from '@/components/ToolPage.vue'
import ToolSection from '@/components/ToolSection.vue'
import { useDeviceStore } from '@/stores/device.js'

const SAMPLES = {
  format: JSON.stringify({
    name: "DevToolBox",
    version: "1.0.0",
    description: "A developer toolbox with multiple utilities",
    features: ["json-tools", "yaml-tools", "markdown-editor", "file-upload", "text-transfer"],
    config: { theme: "auto", language: "zh-CN", maxFileSize: "20GB" },
    stats: { downloads: 15000, stars: 2300, contributors: 12 }
  }, null, 0),
  minify: JSON.stringify({
    name: "DevToolBox",
    version: "1.0.0",
    description: "A developer toolbox with multiple utilities",
    features: ["json-tools", "yaml-tools", "markdown-editor", "file-upload", "text-transfer"],
    config: { theme: "auto", language: "zh-CN", maxFileSize: "20GB" },
    stats: { downloads: 15000, stars: 2300, contributors: 12 }
  }, null, 2),
  validate: JSON.stringify({
    server: { host: "localhost", port: 5000, debug: true },
    database: { engine: "sqlite", path: "/data/app.db" },
    auth: { enabled: true, tokenExpiry: 3600 },
    logging: { level: "info", file: "app.log" }
  }, null, 2),
  escape: '{"message": "Hello\\nWorld!\\tThis is a \\"test\\"."}',
  unescape: '"{\\\"name\\\":\\\"test\\\",\\\"value\\\":\\\"hello\\\\nworld\\\"}"'
}

export default {
  name: 'JsonTools',
  components: {
    DocumentCopy,
    CopyDocument,
    ToolPage,
    ToolSection
  },
  data() {
    const deviceStore = useDeviceStore()
    return {
      deviceStore,
      activeTab: 'format',
      formatInput: '',
      formatOutput: '',
      formatting: false,
      minifyInput: '',
      minifyOutput: '',
      minifying: false,
      validateInput: '',
      validationResult: null,
      validating: false,
      escapeInput: '',
      escapeOutput: '',
      escaping: false,
      unescapeInput: '',
      unescapeOutput: '',
      unescaping: false
    }
  },
  methods: {
    lineCount(text) {
      if (!text) return 0
      return text.split('\n').length
    },

    loadSample(tab) {
      const sample = SAMPLES[tab]
      if (!sample) return
      switch (tab) {
        case 'format': this.formatInput = sample; break
        case 'minify': this.minifyInput = sample; break
        case 'validate': this.validateInput = sample; break
        case 'escape': this.escapeInput = sample; break
        case 'unescape': this.unescapeInput = sample; break
      }
    },

    clearFields(tab) {
      switch (tab) {
        case 'format': this.formatInput = ''; this.formatOutput = ''; break
        case 'minify': this.minifyInput = ''; this.minifyOutput = ''; break
        case 'escape': this.escapeInput = ''; this.escapeOutput = ''; break
        case 'unescape': this.unescapeInput = ''; this.unescapeOutput = ''; break
      }
    },

    async copyText(text) {
      try {
        await navigator.clipboard.writeText(text)
        ElMessage.success(this.$t('tools.json.message.copied'))
      } catch {
        const ta = document.createElement('textarea')
        ta.value = text
        ta.style.position = 'fixed'
        ta.style.opacity = '0'
        document.body.appendChild(ta)
        ta.select()
        document.execCommand('copy')
        document.body.removeChild(ta)
        ElMessage.success(this.$t('tools.json.message.copied'))
      }
    },

    async formatJson() {
      if (!this.formatInput.trim()) {
        ElMessage.warning(this.$t('tools.json.message.inputRequired'))
        return
      }
      this.formatting = true
      try {
        const response = await axios.post('/api/json-tools/format', {
          json_text: this.formatInput
        })
        if (response.data.success) {
          this.formatOutput = response.data.formatted_json
          ElMessage.success(this.$t('tools.json.message.formatSuccess'))
        } else {
          ElMessage.error(response.data.error)
        }
      } catch (error) {
        ElMessage.error(this.$t('tools.json.message.formatFail') + ': ' + error.response?.data?.error || error.message)
      } finally {
        this.formatting = false
      }
    },

    async minifyJson() {
      if (!this.minifyInput.trim()) {
        ElMessage.warning(this.$t('tools.json.message.inputRequired'))
        return
      }
      this.minifying = true
      try {
        const response = await axios.post('/api/json-tools/minify', {
          json_text: this.minifyInput
        })
        if (response.data.success) {
          this.minifyOutput = response.data.minified_json
          ElMessage.success(this.$t('tools.json.message.minifySuccess'))
        } else {
          ElMessage.error(response.data.error)
        }
      } catch (error) {
        ElMessage.error(this.$t('tools.json.message.minifyFail') + ': ' + error.response?.data?.error || error.message)
      } finally {
        this.minifying = false
      }
    },

    async validateJson() {
      if (!this.validateInput.trim()) {
        ElMessage.warning(this.$t('tools.json.message.inputRequired'))
        return
      }
      this.validating = true
      try {
        const response = await axios.post('/api/json-tools/validate', {
          json_text: this.validateInput
        })
        this.validationResult = response.data
        if (response.data.valid) {
          ElMessage.success(this.$t('tools.json.message.jsonValid'))
        } else {
          ElMessage.error(this.$t('tools.json.message.jsonInvalid'))
        }
      } catch (error) {
        this.validationResult = {
          valid: false,
          error: error.response?.data?.error || error.message
        }
        ElMessage.error(this.$t('tools.json.message.validateFail') + ': ' + error.response?.data?.error || error.message)
      } finally {
        this.validating = false
      }
    },

    async escapeJson() {
      if (!this.escapeInput.trim()) {
        ElMessage.warning(this.$t('tools.json.message.escapeInputRequired'))
        return
      }
      this.escaping = true
      try {
        const response = await axios.post('/api/json-tools/escape', {
          text: this.escapeInput
        })
        if (response.data.success) {
          this.escapeOutput = response.data.escaped_text
          ElMessage.success(this.$t('tools.json.message.escapeSuccess'))
        } else {
          ElMessage.error(response.data.error)
        }
      } catch (error) {
        ElMessage.error(this.$t('tools.json.message.escapeFail') + ': ' + error.response?.data?.error || error.message)
      } finally {
        this.escaping = false
      }
    },

    async unescapeJson() {
      if (!this.unescapeInput.trim()) {
        ElMessage.warning(this.$t('tools.json.message.inputRequired'))
        return
      }
      this.unescaping = true
      try {
        const response = await axios.post('/api/json-tools/unescape', {
          json_string: this.unescapeInput
        })
        if (response.data.success) {
          this.unescapeOutput = response.data.unescaped_text
          ElMessage.success(this.$t('tools.json.message.unescapeSuccess'))
        } else {
          ElMessage.error(response.data.error)
        }
      } catch (error) {
        ElMessage.error(this.$t('tools.json.message.unescapeFail') + ': ' + error.response?.data?.error || error.message)
      } finally {
        this.unescaping = false
      }
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
  color: var(--dt-text-tertiary, #909399);
  line-height: 24px;
}

.toolbar-actions {
  display: flex;
  gap: 4px;
}

.validation-result {
  margin-top: var(--dt-spacing-sm);
}

.parsed-data-wrapper {
  margin-top: 8px;
}

.parsed-data {
  background-color: var(--dt-bg-section);
  padding: var(--dt-spacing-sm);
  border-radius: var(--dt-radius-sm);
  margin-top: 6px;
  white-space: pre-wrap;
  word-wrap: break-word;
  max-height: 300px;
  overflow-y: auto;
  font-size: 13px;
  line-height: 1.5;
}

@media (max-width: 768px) {
  .el-form-item :deep(.el-form-item__label) { width: auto !important; min-width: 70px; }
  .el-form-item :deep(.el-form-item__content) { flex: 1; }
  .action-buttons { flex-direction: column; }
  .action-buttons .el-button { width: 100%; margin-left: 0 !important; margin-top: 8px; }
  .el-row { flex-direction: column; }
  .el-col { max-width: 100% !important; flex: 0 0 100% !important; }
}
</style>
