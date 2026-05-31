<template>
  <ToolPage title="API Key生成器" :icon="Key">
    <el-tabs v-model="activeTab">
      <!-- 生成Key -->
      <el-tab-pane label="生成Key" name="generate">
        <div class="tool-section">
          <div class="config-row">
            <div class="config-item">
              <label class="config-label">类型</label>
              <el-select v-model="genType" style="width: 100%;">
                <el-option label="随机字符串" value="random" />
                <el-option label="Base64编码" value="base64" />
                <el-option label="UUID格式" value="uuid" />
                <el-option label="十六进制" value="hex" />
              </el-select>
            </div>
            <div class="config-item">
              <label class="config-label">长度</label>
              <el-input-number
                v-model="genLength"
                :min="16"
                :max="512"
                :disabled="genType === 'uuid'"
                style="width: 100%;"
              />
            </div>
            <div class="config-item">
              <label class="config-label">前缀</label>
              <el-input
                v-model="genPrefix"
                placeholder="例如 sk_live"
                clearable
                style="width: 100%;"
              />
            </div>
            <div class="config-item">
              <label class="config-label">数量</label>
              <el-input-number
                v-model="genCount"
                :min="1"
                :max="50"
                style="width: 100%;"
              />
            </div>
          </div>

          <div class="action-buttons">
            <el-button type="primary" @click="generateKeys" :loading="generating">
              生成Key
            </el-button>
          </div>

          <div class="output-section" v-if="generatedKeys.length > 0">
            <div class="result-header">
              <h4 class="section-title">生成结果 ({{ generatedKeys.length }}个)</h4>
              <el-button size="small" type="success" @click="copyAllKeys">复制全部</el-button>
            </div>
            <el-table :data="generatedKeys" stripe style="width: 100%;">
              <el-table-column type="index" label="#" width="50" />
              <el-table-column label="Key" min-width="300">
                <template #default="{ row }">
                  <el-input
                    :model-value="row.prefixed_key"
                    readonly
                    class="key-input"
                    size="small"
                  />
                </template>
              </el-table-column>
              <el-table-column label="类型" prop="type" width="90" />
              <el-table-column label="长度" prop="length" width="70" />
              <el-table-column label="操作" width="80" fixed="right">
                <template #default="{ row }">
                  <el-button size="small" link type="primary" @click="copyKey(row.prefixed_key)">
                    复制
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </div>
      </el-tab-pane>

      <!-- 验证Key -->
      <el-tab-pane label="验证Key" name="validate">
        <div class="tool-section">
          <div class="input-section">
            <h4 class="section-title">Key</h4>
            <el-input
              v-model="valKey"
              type="textarea"
              :rows="3"
              placeholder="请输入要验证的API Key..."
              clearable
            />
          </div>

          <el-collapse class="optional-collapse">
            <el-collapse-item title="高级选项" name="advanced">
              <div class="config-row">
                <div class="config-item">
                  <label class="config-label">预期类型</label>
                  <el-select v-model="valExpectedType" clearable placeholder="自动检测" style="width: 100%;">
                    <el-option label="随机字符串" value="random" />
                    <el-option label="Base64编码" value="base64" />
                    <el-option label="UUID格式" value="uuid" />
                    <el-option label="十六进制" value="hex" />
                  </el-select>
                </div>
                <div class="config-item">
                  <label class="config-label">最小长度</label>
                  <el-input-number v-model="valMinLength" :min="1" :max="512" style="width: 100%;" />
                </div>
                <div class="config-item">
                  <label class="config-label">预期前缀</label>
                  <el-input
                    v-model="valExpectedPrefix"
                    placeholder="例如 sk_live"
                    clearable
                    style="width: 100%;"
                  />
                </div>
              </div>
            </el-collapse-item>
          </el-collapse>

          <div class="action-buttons">
            <el-button type="primary" @click="validateKey" :loading="validating">
              验证Key
            </el-button>
          </div>

          <div class="output-section" v-if="validateResult !== null">
            <el-alert
              :title="validateResult.valid ? 'Key格式有效' : 'Key格式无效'"
              :type="validateResult.valid ? 'success' : 'error'"
              show-icon
              style="margin-bottom: 16px;"
            />
            <el-descriptions :column="2" border size="small">
              <el-descriptions-item label="检测类型">
                {{ validateResult.detected_type }}
              </el-descriptions-item>
              <el-descriptions-item label="长度">
                {{ validateResult.length }}
              </el-descriptions-item>
              <el-descriptions-item label="包含前缀">
                {{ validateResult.has_prefix ? '是' : '否' }}
              </el-descriptions-item>
            </el-descriptions>
            <div v-if="validateResult.issues && validateResult.issues.length > 0" class="issues-list">
              <h4 class="section-title" style="color: var(--el-color-danger);">问题列表</h4>
              <ul>
                <li v-for="(issue, idx) in validateResult.issues" :key="idx">{{ issue }}</li>
              </ul>
            </div>
          </div>
        </div>
      </el-tab-pane>

      <!-- Key哈希 -->
      <el-tab-pane label="Key哈希" name="hash">
        <div class="tool-section">
          <div class="input-section">
            <h4 class="section-title">Key</h4>
            <el-input
              v-model="hashKeyInput"
              type="textarea"
              :rows="3"
              placeholder="请输入要哈希的API Key..."
              clearable
            />
          </div>

          <div class="config-row">
            <div class="config-item">
              <label class="config-label">算法</label>
              <el-select v-model="hashAlgorithm" style="width: 100%;">
                <el-option label="SHA-256" value="sha256" />
                <el-option label="SHA-384" value="sha384" />
                <el-option label="SHA-512" value="sha512" />
                <el-option label="MD5" value="md5" />
              </el-select>
            </div>
          </div>

          <div class="action-buttons">
            <el-button type="primary" @click="hashKey" :loading="hashing">
              计算哈希
            </el-button>
          </div>

          <div class="output-section" v-if="hashResult">
            <h4 class="section-title">哈希结果</h4>
            <div class="hash-output-row">
              <el-input
                :model-value="hashResult.hash"
                readonly
                class="key-input"
              />
              <el-button size="small" @click="copyKey(hashResult.hash)">复制</el-button>
            </div>

            <el-descriptions :column="2" border size="small" style="margin-top: 12px;">
              <el-descriptions-item label="算法">
                {{ hashResult.algorithm }}
              </el-descriptions-item>
              <el-descriptions-item label="Key长度">
                {{ hashResult.key_length }}
              </el-descriptions-item>
              <el-descriptions-item label="哈希长度">
                {{ hashResult.hash_length }}
              </el-descriptions-item>
              <el-descriptions-item label="脱敏Key">
                {{ hashResult.masked }}
              </el-descriptions-item>
            </el-descriptions>
          </div>
        </div>
      </el-tab-pane>
    </el-tabs>
  </ToolPage>
</template>

<script>
import { ElMessage } from 'element-plus'
import { Key } from '@element-plus/icons-vue'
import axios from 'axios'
import ToolPage from '@/components/ToolPage.vue'

export default {
  name: 'ApiKeyTools',
  components: {
    Key,
    ToolPage,
  },
  data() {
    return {
      activeTab: 'generate',
      // Generate
      genType: 'random',
      genLength: 32,
      genPrefix: '',
      genCount: 5,
      generating: false,
      generatedKeys: [],
      // Validate
      valKey: '',
      valExpectedType: '',
      valMinLength: 16,
      valExpectedPrefix: '',
      validating: false,
      validateResult: null,
      // Hash
      hashKeyInput: '',
      hashAlgorithm: 'sha256',
      hashing: false,
      hashResult: null,
    }
  },
  watch: {
    genType(val) {
      if (val === 'uuid') {
        this.genLength = 36
      }
    },
  },
  methods: {
    async generateKeys() {
      this.generating = true
      try {
        const payload = {
          type: this.genType,
          length: this.genLength,
          count: this.genCount,
        }
        if (this.genPrefix.trim()) {
          payload.prefix = this.genPrefix.trim()
        }

        const response = await axios.post('/api/apikey-tools/generate', payload)

        if (response.data.success) {
          this.generatedKeys = response.data.keys
          ElMessage.success(`成功生成 ${response.data.count} 个Key`)
        } else {
          ElMessage.error(response.data.error || '生成失败')
        }
      } catch (error) {
        ElMessage.error('生成失败: ' + (error.response?.data?.error || error.message))
      } finally {
        this.generating = false
      }
    },

    copyKey(text) {
      navigator.clipboard.writeText(text).then(() => {
        ElMessage.success('已复制到剪贴板')
      }).catch(() => {
        ElMessage.error('复制失败')
      })
    },

    copyAllKeys() {
      const allKeys = this.generatedKeys.map(k => k.prefixed_key).join('\n')
      navigator.clipboard.writeText(allKeys).then(() => {
        ElMessage.success(`已复制 ${this.generatedKeys.length} 个Key到剪贴板`)
      }).catch(() => {
        ElMessage.error('复制失败')
      })
    },

    async validateKey() {
      if (!this.valKey.trim()) {
        ElMessage.warning('请输入要验证的Key')
        return
      }

      this.validating = true
      this.validateResult = null
      try {
        const payload = {
          key: this.valKey,
          min_length: this.valMinLength,
        }
        if (this.valExpectedType) {
          payload.expected_type = this.valExpectedType
        }
        if (this.valExpectedPrefix.trim()) {
          payload.expected_prefix = this.valExpectedPrefix.trim()
        }

        const response = await axios.post('/api/apikey-tools/validate', payload)

        if (response.data.success) {
          this.validateResult = response.data
          if (response.data.valid) {
            ElMessage.success('Key格式有效')
          } else {
            ElMessage.warning('Key格式存在问题')
          }
        } else {
          ElMessage.error(response.data.error || '验证失败')
        }
      } catch (error) {
        ElMessage.error('验证失败: ' + (error.response?.data?.error || error.message))
      } finally {
        this.validating = false
      }
    },

    async hashKey() {
      if (!this.hashKeyInput.trim()) {
        ElMessage.warning('请输入要哈希的Key')
        return
      }

      this.hashing = true
      this.hashResult = null
      try {
        const response = await axios.post('/api/apikey-tools/hash-key', {
          key: this.hashKeyInput,
          algorithm: this.hashAlgorithm,
        })

        if (response.data.success) {
          this.hashResult = response.data
          ElMessage.success('哈希计算成功')
        } else {
          ElMessage.error(response.data.error || '哈希失败')
        }
      } catch (error) {
        ElMessage.error('哈希失败: ' + (error.response?.data?.error || error.message))
      } finally {
        this.hashing = false
      }
    },
  },
}
</script>

<style scoped>
.tool-section {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.config-row {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.config-item {
  flex: 1;
  min-width: 150px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.config-label {
  font-size: 13px;
  color: var(--dt-text-secondary, #909399);
  font-weight: 500;
}

.action-buttons {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.input-section {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.output-section {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.section-title {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
  color: var(--dt-text-primary, #303133);
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.key-input :deep(.el-input__inner) {
  font-family: 'Courier New', Courier, monospace;
  font-size: 13px;
}

.optional-collapse {
  border: none;
}

.optional-collapse :deep(.el-collapse-item__header) {
  color: var(--dt-text-secondary, #909399);
  font-size: 13px;
  border-bottom: none;
  height: 32px;
  line-height: 32px;
}

.optional-collapse :deep(.el-collapse-item__wrap) {
  border-bottom: none;
}

.issues-list {
  margin-top: 12px;
}

.issues-list ul {
  margin: 4px 0 0 0;
  padding-left: 20px;
  color: var(--el-color-danger);
  font-size: 13px;
}

.issues-list li {
  margin-bottom: 4px;
}

.hash-output-row {
  display: flex;
  gap: 8px;
  align-items: center;
}

.hash-output-row .el-input {
  flex: 1;
}

@media (max-width: 768px) {
  .config-row {
    flex-direction: column;
  }

  .config-item {
    min-width: unset;
    width: 100%;
  }

  .result-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }

  .hash-output-row {
    flex-direction: column;
  }

  .hash-output-row .el-button {
    align-self: flex-end;
  }
}
</style>
