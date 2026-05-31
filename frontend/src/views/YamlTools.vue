<template>
  <ToolPage title="YAML工具" :icon="DocumentCopy">
    <el-tabs v-model="activeTab" @tab-click="handleTabClick">
      <!-- 格式化 -->
      <el-tab-pane label="格式化" name="format">
        <ToolSection
          input-label="输入YAML"
          output-label="格式化结果"
          action-text="格式化"
          :loading="formatting"
          @submit="formatYaml"
        >
          <template #input>
            <el-input
              v-model="formatInput"
              type="textarea"
              :rows="10"
              placeholder="请输入YAML字符串..."
              clearable
            />
          </template>
          <template #output>
            <el-input
              v-model="formatOutput"
              type="textarea"
              :rows="10"
              readonly
              placeholder="格式化后的YAML将显示在这里..."
            />
          </template>
        </ToolSection>
      </el-tab-pane>

      <!-- 验证 -->
      <el-tab-pane label="验证" name="validate">
        <div class="tool-section">
          <div class="input-section">
            <h4 class="section-title">输入YAML</h4>
            <el-input
              v-model="validateInput"
              type="textarea"
              :rows="10"
              placeholder="请输入YAML字符串..."
              clearable
            />
          </div>
          <div class="action-section">
            <el-button type="primary" @click="validateYaml" :loading="validating">
              验证
            </el-button>
          </div>
          <div class="output-section">
            <h4 class="section-title">验证结果</h4>
            <div class="validation-result">
              <el-alert
                v-if="validationResult"
                :title="validationResult.valid ? '验证成功' : '验证失败'"
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
      <el-tab-pane label="YAML转JSON" name="to-json">
        <ToolSection
          input-label="输入YAML"
          output-label="JSON结果"
          action-text="转换"
          :loading="converting"
          @submit="yamlToJson"
        >
          <template #input>
            <el-input
              v-model="yamlToJsonInput"
              type="textarea"
              :rows="10"
              placeholder="请输入YAML字符串..."
              clearable
            />
          </template>
          <template #output>
            <el-input
              v-model="yamlToJsonOutput"
              type="textarea"
              :rows="10"
              readonly
              placeholder="转换后的JSON将显示在这里..."
            />
          </template>
        </ToolSection>
      </el-tab-pane>

      <!-- JSON转YAML -->
      <el-tab-pane label="JSON转YAML" name="from-json">
        <ToolSection
          input-label="输入JSON"
          output-label="YAML结果"
          action-text="转换"
          :loading="converting"
          @submit="jsonToYaml"
        >
          <template #input>
            <el-input
              v-model="jsonToYamlInput"
              type="textarea"
              :rows="10"
              placeholder="请输入JSON字符串..."
              clearable
            />
          </template>
          <template #output>
            <el-input
              v-model="jsonToYamlOutput"
              type="textarea"
              :rows="10"
              readonly
              placeholder="转换后的YAML将显示在这里..."
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

export default {
  name: 'YamlTools',
  components: {
    DocumentCopy,
    ToolPage,
    ToolSection
  },
  data() {
    return {
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
        ElMessage.warning('请输入YAML字符串')
        return
      }

      this.formatting = true
      try {
        const response = await axios.post('/api/yaml-tools/format', {
          yaml_text: this.formatInput
        })

        if (response.data.success) {
          this.formatOutput = response.data.formatted_yaml
          ElMessage.success('格式化成功')
        } else {
          ElMessage.error(response.data.error)
        }
      } catch (error) {
        ElMessage.error('格式化失败: ' + error.response?.data?.error || error.message)
      } finally {
        this.formatting = false
      }
    },

    async validateYaml() {
      if (!this.validateInput.trim()) {
        ElMessage.warning('请输入YAML字符串')
        return
      }

      this.validating = true
      try {
        const response = await axios.post('/api/yaml-tools/validate', {
          yaml_text: this.validateInput
        })

        this.validationResult = response.data
        if (response.data.valid) {
          ElMessage.success('YAML格式正确')
        } else {
          ElMessage.error('YAML格式错误')
        }
      } catch (error) {
        this.validationResult = {
          valid: false,
          error: error.response?.data?.error || error.message
        }
        ElMessage.error('验证失败: ' + error.response?.data?.error || error.message)
      } finally {
        this.validating = false
      }
    },

    async yamlToJson() {
      if (!this.yamlToJsonInput.trim()) {
        ElMessage.warning('请输入YAML字符串')
        return
      }

      this.converting = true
      try {
        const response = await axios.post('/api/yaml-tools/to-json', {
          yaml_text: this.yamlToJsonInput
        })

        if (response.data.success) {
          this.yamlToJsonOutput = response.data.json_output
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

    async jsonToYaml() {
      if (!this.jsonToYamlInput.trim()) {
        ElMessage.warning('请输入JSON字符串')
        return
      }

      this.converting = true
      try {
        const response = await axios.post('/api/yaml-tools/from-json', {
          json_text: this.jsonToYamlInput
        })

        if (response.data.success) {
          this.jsonToYamlOutput = response.data.yaml_output
          ElMessage.success('转换成功')
        } else {
          ElMessage.error(response.data.error)
        }
      } catch (error) {
        ElMessage.error('转换失败: ' + error.response?.data?.error || error.message)
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
</style>
