<template>
  <ToolPage :title="$t('tools.yaml.title')" :icon="DocumentCopy">
    <el-tabs v-model="activeTab" @tab-click="handleTabClick">
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
          </template>
          <template #output>
            <el-input
              v-model="formatOutput"
              type="textarea"
              :rows="10"
              readonly
              :placeholder="$t('tools.yaml.placeholder.formatResult')"
            />
          </template>
        </ToolSection>
      </el-tab-pane>

      <!-- 验证 -->
      <el-tab-pane :label="$t('tools.yaml.tab.validate')" name="validate">
        <div class="tool-section">
          <div class="input-section">
            <h4 class="section-title">{{ $t('tools.yaml.label.inputYaml') }}</h4>
            <el-input
              v-model="validateInput"
              type="textarea"
              :rows="10"
              :placeholder="$t('tools.yaml.placeholder.inputYaml')"
              clearable
            />
          </div>
          <div class="action-section">
            <el-button type="primary" @click="validateYaml" :loading="validating">
              {{ $t('tools.yaml.tab.validate') }}
            </el-button>
          </div>
          <div class="output-section">
            <h4 class="section-title">{{ $t('tools.yaml.label.validateResult') }}</h4>
            <div class="validation-result">
              <el-alert
                v-if="validationResult"
                :title="validationResult.valid ? $t('tools.yaml.message.validateSuccess') : $t('tools.yaml.message.validateFail')"
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
          </template>
          <template #output>
            <el-input
              v-model="yamlToJsonOutput"
              type="textarea"
              :rows="10"
              readonly
              :placeholder="$t('tools.yaml.placeholder.jsonResult')"
            />
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
          </template>
          <template #output>
            <el-input
              v-model="jsonToYamlOutput"
              type="textarea"
              :rows="10"
              readonly
              :placeholder="$t('tools.yaml.placeholder.yamlResult')"
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
  name: 'YamlTools',
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
      // 验证
      validateInput: '',
      validationResult: null,
      validating: false,
      // YAML转JSON
      yamlToJsonInput: '',
      yamlToJsonOutput: '',
      // JSON转YAML
      jsonToYamlInput: '',
      jsonToYamlOutput: '',
      converting: false
    }
  },
  methods: {
    handleTabClick(tab) {
      this.activeTab = tab.props.name
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
  .action-buttons { flex-direction: column; }
  .action-buttons .el-button { width: 100%; margin-left: 0 !important; margin-top: 8px; }
  .el-row { flex-direction: column; }
  .el-col { max-width: 100% !important; flex: 0 0 100% !important; }
}
</style>
