<template>
  <div class="json-tools">
    <el-card>
      <template #header>
        <div class="card-header">
          <el-icon class="card-icon"><DocumentCopy /></el-icon>
          <span>JSON工具</span>
        </div>
      </template>

      <el-tabs v-model="activeTab" @tab-click="handleTabClick">
        <!-- 格式化 -->
        <el-tab-pane label="格式化" name="format">
          <div class="tool-section">
            <div class="input-section">
              <h4>输入JSON</h4>
              <el-input
                v-model="formatInput"
                type="textarea"
                :rows="10"
                placeholder="请输入JSON字符串..."
                clearable
              />
            </div>
            <div class="action-section">
              <el-button type="primary" @click="formatJson" :loading="formatting">
                格式化
              </el-button>
            </div>
            <div class="output-section">
              <h4>格式化结果</h4>
              <el-input
                v-model="formatOutput"
                type="textarea"
                :rows="10"
                readonly
                placeholder="格式化后的JSON将显示在这里..."
              />
            </div>
          </div>
        </el-tab-pane>

        <!-- 压缩 -->
        <el-tab-pane label="压缩" name="minify">
          <div class="tool-section">
            <div class="input-section">
              <h4>输入JSON</h4>
              <el-input
                v-model="minifyInput"
                type="textarea"
                :rows="10"
                placeholder="请输入JSON字符串..."
                clearable
              />
            </div>
            <div class="action-section">
              <el-button type="primary" @click="minifyJson" :loading="minifying">
                压缩
              </el-button>
            </div>
            <div class="output-section">
              <h4>压缩结果</h4>
              <el-input
                v-model="minifyOutput"
                type="textarea"
                :rows="10"
                readonly
                placeholder="压缩后的JSON将显示在这里..."
              />
            </div>
          </div>
        </el-tab-pane>

        <!-- 验证 -->
        <el-tab-pane label="验证" name="validate">
          <div class="tool-section">
            <div class="input-section">
              <h4>输入JSON</h4>
              <el-input
                v-model="validateInput"
                type="textarea"
                :rows="10"
                placeholder="请输入JSON字符串..."
                clearable
              />
            </div>
            <div class="action-section">
              <el-button type="primary" @click="validateJson" :loading="validating">
                验证
              </el-button>
            </div>
            <div class="output-section">
              <h4>验证结果</h4>
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

        <!-- 转义 -->
        <el-tab-pane label="转义" name="escape">
          <div class="tool-section">
            <div class="input-section">
              <h4>输入文本</h4>
              <el-input
                v-model="escapeInput"
                type="textarea"
                :rows="10"
                placeholder="请输入要转义的文本..."
                clearable
              />
            </div>
            <div class="action-section">
              <el-button type="primary" @click="escapeJson" :loading="escaping">
                转义
              </el-button>
            </div>
            <div class="output-section">
              <h4>转义结果</h4>
              <el-input
                v-model="escapeOutput"
                type="textarea"
                :rows="10"
                readonly
                placeholder="转义后的字符串将显示在这里..."
              />
            </div>
          </div>
        </el-tab-pane>

        <!-- 反转义 -->
        <el-tab-pane label="反转义" name="unescape">
          <div class="tool-section">
            <div class="input-section">
              <h4>输入JSON字符串</h4>
              <el-input
                v-model="unescapeInput"
                type="textarea"
                :rows="10"
                placeholder="请输入JSON字符串..."
                clearable
              />
            </div>
            <div class="action-section">
              <el-button type="primary" @click="unescapeJson" :loading="unescaping">
                反转义
              </el-button>
            </div>
            <div class="output-section">
              <h4>反转义结果</h4>
              <el-input
                v-model="unescapeOutput"
                type="textarea"
                :rows="10"
                readonly
                placeholder="反转义后的文本将显示在这里..."
              />
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script>
import { ElMessage } from 'element-plus'
import { DocumentCopy } from '@element-plus/icons-vue'
import axios from 'axios'

export default {
  name: 'JsonTools',
  components: {
    DocumentCopy
  },
  data() {
    return {
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
        ElMessage.warning('请输入JSON字符串')
        return
      }

      this.formatting = true
      try {
        const response = await axios.post('/api/json-tools/format', {
          json_text: this.formatInput
        })

        if (response.data.success) {
          this.formatOutput = response.data.formatted_json
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

    async minifyJson() {
      if (!this.minifyInput.trim()) {
        ElMessage.warning('请输入JSON字符串')
        return
      }

      this.minifying = true
      try {
        const response = await axios.post('/api/json-tools/minify', {
          json_text: this.minifyInput
        })

        if (response.data.success) {
          this.minifyOutput = response.data.minified_json
          ElMessage.success('压缩成功')
        } else {
          ElMessage.error(response.data.error)
        }
      } catch (error) {
        ElMessage.error('压缩失败: ' + error.response?.data?.error || error.message)
      } finally {
        this.minifying = false
      }
    },

    async validateJson() {
      if (!this.validateInput.trim()) {
        ElMessage.warning('请输入JSON字符串')
        return
      }

      this.validating = true
      try {
        const response = await axios.post('/api/json-tools/validate', {
          json_text: this.validateInput
        })

        this.validationResult = response.data
        if (response.data.valid) {
          ElMessage.success('JSON格式正确')
        } else {
          ElMessage.error('JSON格式错误')
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

    async escapeJson() {
      if (!this.escapeInput.trim()) {
        ElMessage.warning('请输入要转义的文本')
        return
      }

      this.escaping = true
      try {
        const response = await axios.post('/api/json-tools/escape', {
          text: this.escapeInput
        })

        if (response.data.success) {
          this.escapeOutput = response.data.escaped_text
          ElMessage.success('转义成功')
        } else {
          ElMessage.error(response.data.error)
        }
      } catch (error) {
        ElMessage.error('转义失败: ' + error.response?.data?.error || error.message)
      } finally {
        this.escaping = false
      }
    },

    async unescapeJson() {
      if (!this.unescapeInput.trim()) {
        ElMessage.warning('请输入JSON字符串')
        return
      }

      this.unescaping = true
      try {
        const response = await axios.post('/api/json-tools/unescape', {
          json_string: this.unescapeInput
        })

        if (response.data.success) {
          this.unescapeOutput = response.data.unescaped_text
          ElMessage.success('反转义成功')
        } else {
          ElMessage.error(response.data.error)
        }
      } catch (error) {
        ElMessage.error('反转义失败: ' + error.response?.data?.error || error.message)
      } finally {
        this.unescaping = false
      }
    }
  }
}
</script>

<style scoped>
.json-tools {
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

.validation-result {
  margin-top: 10px;
}

.parsed-data {
  background-color: #f5f5f5;
  padding: 10px;
  border-radius: 4px;
  margin-top: 10px;
  white-space: pre-wrap;
  word-wrap: break-word;
  max-height: 300px;
  overflow-y: auto;
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
</style>
