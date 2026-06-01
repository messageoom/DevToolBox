<template>
  <ToolPage :title="$t('tools.json.title')" :icon="DocumentCopy">
    <el-tabs v-model="activeTab" @tab-click="handleTabClick">
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
          </template>
          <template #output>
            <el-input
              v-model="formatOutput"
              type="textarea"
              :rows="10"
              readonly
              :placeholder="$t('tools.json.placeholder.formatResult')"
            />
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
          </template>
          <template #output>
            <el-input
              v-model="minifyOutput"
              type="textarea"
              :rows="10"
              readonly
              :placeholder="$t('tools.json.placeholder.minifyResult')"
            />
          </template>
        </ToolSection>
      </el-tab-pane>

      <!-- 验证 -->
      <el-tab-pane :label="$t('tools.json.tab.validate')" name="validate">
        <div class="tool-section">
          <div class="input-section">
            <h4 class="section-title">{{ $t('tools.json.label.inputJson') }}</h4>
            <el-input
              v-model="validateInput"
              type="textarea"
              :rows="10"
              :placeholder="$t('tools.json.placeholder.inputJson')"
              clearable
            />
          </div>
          <div class="action-section">
            <el-button type="primary" @click="validateJson" :loading="validating">
              {{ $t('tools.json.action.validate') }}
            </el-button>
          </div>
          <div class="output-section">
            <h4 class="section-title">{{ $t('tools.json.label.validateResult') }}</h4>
            <div class="validation-result">
              <el-alert
                v-if="validationResult"
                :title="validationResult.valid ? $t('tools.json.message.validateSuccess') : $t('tools.json.message.validateFail')"
                :type="validationResult.valid ? 'success' : 'error'"
                :description="validationResult.message || validationResult.error"
                show-icon
              />
              <pre v-if="validationResult && validationResult.parsed_data" class="parsed-data">
                {{ JSON.stringify(validationResult.parsed_data, null, 2) }}
              </pre>
            </div>
          </div>
        </div>
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
          </template>
          <template #output>
            <el-input
              v-model="escapeOutput"
              type="textarea"
              :rows="10"
              readonly
              :placeholder="$t('tools.json.placeholder.escapeResult')"
            />
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
          </template>
          <template #output>
            <el-input
              v-model="unescapeOutput"
              type="textarea"
              :rows="10"
              readonly
              :placeholder="$t('tools.json.placeholder.unescapeResult')"
            />
          </template>
        </ToolSection>
      </el-tab-pane>
    </el-tabs>
  </ToolPage>
</template>

<script>
import { ElMessage } from 'element-plus'
import { DocumentCopy } from '@element-plus/icons-vue'
import axios from 'axios'
import ToolPage from '@/components/ToolPage.vue'
import ToolSection from '@/components/ToolSection.vue'
import { useDeviceStore } from '@/stores/device.js'

export default {
  name: 'JsonTools',
  components: {
    DocumentCopy,
    ToolPage,
    ToolSection
  },
  data() {
    const deviceStore = useDeviceStore()
    return {
      deviceStore,
      activeTab: 'format',
      // 格式化
      formatInput: '',
      formatOutput: '',
      formatting: false,
      // 压缩
      minifyInput: '',
      minifyOutput: '',
      minifying: false,
      // 验证
      validateInput: '',
      validationResult: null,
      validating: false,
      // 转义
      escapeInput: '',
      escapeOutput: '',
      escaping: false,
      // 反转义
      unescapeInput: '',
      unescapeOutput: '',
      unescaping: false
    }
  },
  methods: {
    handleTabClick(tab) {
      this.activeTab = tab.props.name
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
.validation-result {
  margin-top: var(--dt-spacing-sm);
}

.parsed-data {
  background-color: var(--dt-bg-section);
  padding: var(--dt-spacing-sm);
  border-radius: var(--dt-radius-sm);
  margin-top: var(--dt-spacing-sm);
  white-space: pre-wrap;
  word-wrap: break-word;
  max-height: 300px;
  overflow-y: auto;
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
