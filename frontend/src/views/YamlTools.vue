<template>
  <ToolPage :title="$t('tools.yaml.title')" :icon="DocumentCopy">
    <el-tabs v-model="activeTab">
      <!-- 格式化 -->
      <el-tab-pane :label="$t('tools.yaml.tab.format')" name="format">
        <ToolSection
          :input-label="$t('tools.yaml.label.inputYaml')"
          :output-label="$t('tools.yaml.label.formatResult')"
          :action-text="$t('tools.yaml.tab.format')"
          :loading="formatting"
          @submit="formatYaml"
        >
          <template #input>
            <el-input
              v-model="formatInput"
              type="textarea"
              :rows="10"
              :placeholder="$t('tools.yaml.placeholder.inputYaml')"
              clearable
            />
            <div class="field-toolbar">
              <span class="field-stats" v-if="formatInput">
                {{ formatInput.length }} {{ $t('tools.yaml.stats.chars') }} · {{ lineCount(formatInput) }} {{ $t('tools.yaml.stats.lines') }}
              </span>
              <div class="toolbar-actions">
                <el-button link size="small" @click="loadSample('format')">{{ $t('tools.yaml.action.sample') }}</el-button>
                <el-button link size="small" v-if="formatInput || formatOutput" @click="clearFields('format')">{{ $t('tools.yaml.action.clear') }}</el-button>
              </div>
            </div>
          </template>
          <template #output>
            <el-input
              v-model="formatOutput"
              type="textarea"
              :rows="10"
              readonly
              :placeholder="$t('tools.yaml.placeholder.formatResult')"
            />
            <div class="field-toolbar" v-if="formatOutput">
              <span class="field-stats">
                {{ formatOutput.length }} {{ $t('tools.yaml.stats.chars') }} · {{ lineCount(formatOutput) }} {{ $t('tools.yaml.stats.lines') }}
              </span>
              <el-button link size="small" type="primary" @click="copyText(formatOutput)">
                <el-icon><CopyDocument /></el-icon> {{ $t('tools.yaml.action.copy') }}
              </el-button>
            </div>
          </template>
        </ToolSection>
      </el-tab-pane>

      <!-- 验证 -->
      <el-tab-pane :label="$t('tools.yaml.tab.validate')" name="validate">
        <ToolSection
          :input-label="$t('tools.yaml.label.inputYaml')"
          :output-label="$t('tools.yaml.label.validateResult')"
          :action-text="$t('tools.yaml.tab.validate')"
          :loading="validating"
          :has-output="!!validationResult"
          @submit="validateYaml"
        >
          <template #input>
            <el-input
              v-model="validateInput"
              type="textarea"
              :rows="10"
              :placeholder="$t('tools.yaml.placeholder.inputYaml')"
              clearable
            />
            <div class="field-toolbar">
              <span class="field-stats" v-if="validateInput">
                {{ validateInput.length }} {{ $t('tools.yaml.stats.chars') }} · {{ lineCount(validateInput) }} {{ $t('tools.yaml.stats.lines') }}
              </span>
              <div class="toolbar-actions">
                <el-button link size="small" @click="loadSample('validate')">{{ $t('tools.yaml.action.sample') }}</el-button>
                <el-button link size="small" v-if="validateInput || validationResult" @click="validateInput = ''; validationResult = null">{{ $t('tools.yaml.action.clear') }}</el-button>
              </div>
            </div>
          </template>
          <template #output>
            <div class="validation-result">
              <el-alert
                :title="validationResult.valid ? $t('tools.yaml.message.validateSuccess') : $t('tools.yaml.message.validateFail')"
                :type="validationResult.valid ? 'success' : 'error'"
                :description="validationResult.message || validationResult.error"
                show-icon
              />
              <div v-if="validationResult.parsed_data" class="parsed-data-wrapper">
                <div class="field-toolbar">
                  <span class="field-stats">{{ JSON.stringify(validationResult.parsed_data).length }} {{ $t('tools.yaml.stats.chars') }}</span>
                  <el-button link size="small" type="primary" @click="copyText(JSON.stringify(validationResult.parsed_data, null, 2))">
                    <el-icon><CopyDocument /></el-icon> {{ $t('tools.yaml.action.copy') }}
                  </el-button>
                </div>
                <pre class="parsed-data">{{ JSON.stringify(validationResult.parsed_data, null, 2) }}</pre>
              </div>
            </div>
          </template>
        </ToolSection>
      </el-tab-pane>

      <!-- YAML转JSON -->
      <el-tab-pane :label="$t('tools.yaml.tab.yamlToJson')" name="to-json">
        <ToolSection
          :input-label="$t('tools.yaml.label.inputYaml')"
          :output-label="$t('tools.yaml.label.jsonResult')"
          :action-text="$t('tools.yaml.tab.yamlToJson')"
          :loading="converting"
          @submit="yamlToJson"
        >
          <template #input>
            <el-input
              v-model="yamlToJsonInput"
              type="textarea"
              :rows="10"
              :placeholder="$t('tools.yaml.placeholder.inputYaml')"
              clearable
            />
            <div class="field-toolbar">
              <span class="field-stats" v-if="yamlToJsonInput">
                {{ yamlToJsonInput.length }} {{ $t('tools.yaml.stats.chars') }} · {{ lineCount(yamlToJsonInput) }} {{ $t('tools.yaml.stats.lines') }}
              </span>
              <div class="toolbar-actions">
                <el-button link size="small" @click="loadSample('to-json')">{{ $t('tools.yaml.action.sample') }}</el-button>
                <el-button link size="small" v-if="yamlToJsonInput || yamlToJsonOutput" @click="clearFields('to-json')">{{ $t('tools.yaml.action.clear') }}</el-button>
              </div>
            </div>
          </template>
          <template #output>
            <el-input
              v-model="yamlToJsonOutput"
              type="textarea"
              :rows="10"
              readonly
              :placeholder="$t('tools.yaml.placeholder.jsonResult')"
            />
            <div class="field-toolbar" v-if="yamlToJsonOutput">
              <span class="field-stats">
                {{ yamlToJsonOutput.length }} {{ $t('tools.yaml.stats.chars') }} · {{ lineCount(yamlToJsonOutput) }} {{ $t('tools.yaml.stats.lines') }}
              </span>
              <el-button link size="small" type="primary" @click="copyText(yamlToJsonOutput)">
                <el-icon><CopyDocument /></el-icon> {{ $t('tools.yaml.action.copy') }}
              </el-button>
            </div>
          </template>
        </ToolSection>
      </el-tab-pane>

      <!-- JSON转YAML -->
      <el-tab-pane :label="$t('tools.yaml.tab.jsonToYaml')" name="from-json">
        <ToolSection
          :input-label="$t('tools.yaml.label.inputJson')"
          :output-label="$t('tools.yaml.label.yamlResult')"
          :action-text="$t('tools.yaml.tab.jsonToYaml')"
          :loading="converting"
          @submit="jsonToYaml"
        >
          <template #input>
            <el-input
              v-model="jsonToYamlInput"
              type="textarea"
              :rows="10"
              :placeholder="$t('tools.yaml.placeholder.inputJson')"
              clearable
            />
            <div class="field-toolbar">
              <span class="field-stats" v-if="jsonToYamlInput">
                {{ jsonToYamlInput.length }} {{ $t('tools.yaml.stats.chars') }} · {{ lineCount(jsonToYamlInput) }} {{ $t('tools.yaml.stats.lines') }}
              </span>
              <div class="toolbar-actions">
                <el-button link size="small" @click="loadSample('from-json')">{{ $t('tools.yaml.action.sample') }}</el-button>
                <el-button link size="small" v-if="jsonToYamlInput || jsonToYamlOutput" @click="clearFields('from-json')">{{ $t('tools.yaml.action.clear') }}</el-button>
              </div>
            </div>
          </template>
          <template #output>
            <el-input
              v-model="jsonToYamlOutput"
              type="textarea"
              :rows="10"
              readonly
              :placeholder="$t('tools.yaml.placeholder.yamlResult')"
            />
            <div class="field-toolbar" v-if="jsonToYamlOutput">
              <span class="field-stats">
                {{ jsonToYamlOutput.length }} {{ $t('tools.yaml.stats.chars') }} · {{ lineCount(jsonToYamlOutput) }} {{ $t('tools.yaml.stats.lines') }}
              </span>
              <el-button link size="small" type="primary" @click="copyText(jsonToYamlOutput)">
                <el-icon><CopyDocument /></el-icon> {{ $t('tools.yaml.action.copy') }}
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
  format: `server:
  host: localhost
  port: 5000
  debug: true
database:
  engine: sqlite
  path: /data/app.db
auth:
  enabled: true
  tokenExpiry: 3600
logging:
  level: info
  file: app.log`,
  validate: `app:
  name: DevToolBox
  version: 1.0.0
  description: Developer toolbox
features:
  - json-tools
  - yaml-tools
  - markdown-editor
config:
  theme: auto
  language: zh-CN`,
  'to-json': `application:
  name: MyApp
  version: 2.0.0
settings:
  debug: false
  logLevel: warning
servers:
  - name: primary
    host: 192.168.1.1
    port: 8080
  - name: backup
    host: 192.168.1.2
    port: 8080`,
  'from-json': JSON.stringify({
    application: { name: "MyApp", version: "2.0.0" },
    settings: { debug: false, logLevel: "warning" },
    servers: [
      { name: "primary", host: "192.168.1.1", port: 8080 },
      { name: "backup", host: "192.168.1.2", port: 8080 }
    ]
  }, null, 2)
}

export default {
  name: 'YamlTools',
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
      validateInput: '',
      validationResult: null,
      validating: false,
      yamlToJsonInput: '',
      yamlToJsonOutput: '',
      jsonToYamlInput: '',
      jsonToYamlOutput: '',
      converting: false
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
        case 'validate': this.validateInput = sample; break
        case 'to-json': this.yamlToJsonInput = sample; break
        case 'from-json': this.jsonToYamlInput = sample; break
      }
    },

    clearFields(tab) {
      switch (tab) {
        case 'format': this.formatInput = ''; this.formatOutput = ''; break
        case 'to-json': this.yamlToJsonInput = ''; this.yamlToJsonOutput = ''; break
        case 'from-json': this.jsonToYamlInput = ''; this.jsonToYamlOutput = ''; break
      }
    },

    async copyText(text) {
      try {
        await navigator.clipboard.writeText(text)
        ElMessage.success(this.$t('tools.yaml.message.copied'))
      } catch {
        const ta = document.createElement('textarea')
        ta.value = text
        ta.style.position = 'fixed'
        ta.style.opacity = '0'
        document.body.appendChild(ta)
        ta.select()
        document.execCommand('copy')
        document.body.removeChild(ta)
        ElMessage.success(this.$t('tools.yaml.message.copied'))
      }
    },

    async formatYaml() {
      if (!this.formatInput.trim()) {
        ElMessage.warning(this.$t('tools.yaml.message.inputRequired'))
        return
      }
      this.formatting = true
      try {
        const response = await axios.post('/api/yaml-tools/format', {
          yaml_text: this.formatInput
        })
        if (response.data.success) {
          this.formatOutput = response.data.formatted_yaml
          ElMessage.success(this.$t('tools.yaml.message.formatSuccess'))
        } else {
          ElMessage.error(response.data.error)
        }
      } catch (error) {
        ElMessage.error(this.$t('tools.yaml.message.formatFail') + ': ' + error.response?.data?.error || error.message)
      } finally {
        this.formatting = false
      }
    },

    async validateYaml() {
      if (!this.validateInput.trim()) {
        ElMessage.warning(this.$t('tools.yaml.message.inputRequired'))
        return
      }
      this.validating = true
      try {
        const response = await axios.post('/api/yaml-tools/validate', {
          yaml_text: this.validateInput
        })
        this.validationResult = response.data
        if (response.data.valid) {
          ElMessage.success(this.$t('tools.yaml.message.yamlValid'))
        } else {
          ElMessage.error(this.$t('tools.yaml.message.yamlInvalid'))
        }
      } catch (error) {
        this.validationResult = {
          valid: false,
          error: error.response?.data?.error || error.message
        }
        ElMessage.error(this.$t('tools.yaml.message.validateFail') + ': ' + error.response?.data?.error || error.message)
      } finally {
        this.validating = false
      }
    },

    async yamlToJson() {
      if (!this.yamlToJsonInput.trim()) {
        ElMessage.warning(this.$t('tools.yaml.message.inputRequired'))
        return
      }
      this.converting = true
      try {
        const response = await axios.post('/api/yaml-tools/to-json', {
          yaml_text: this.yamlToJsonInput
        })
        if (response.data.success) {
          this.yamlToJsonOutput = response.data.json_output
          ElMessage.success(this.$t('tools.yaml.message.convertSuccess'))
        } else {
          ElMessage.error(response.data.error)
        }
      } catch (error) {
        ElMessage.error(this.$t('tools.yaml.message.convertFail') + ': ' + error.response?.data?.error || error.message)
      } finally {
        this.converting = false
      }
    },

    async jsonToYaml() {
      if (!this.jsonToYamlInput.trim()) {
        ElMessage.warning(this.$t('tools.yaml.message.inputJsonRequired'))
        return
      }
      this.converting = true
      try {
        const response = await axios.post('/api/yaml-tools/from-json', {
          json_text: this.jsonToYamlInput
        })
        if (response.data.success) {
          this.jsonToYamlOutput = response.data.yaml_output
          ElMessage.success(this.$t('tools.yaml.message.convertSuccess'))
        } else {
          ElMessage.error(response.data.error)
        }
      } catch (error) {
        ElMessage.error(this.$t('tools.yaml.message.convertFail') + ': ' + error.response?.data?.error || error.message)
      } finally {
        this.converting = false
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
  color: var(--dt-text-secondary);
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
</style>
