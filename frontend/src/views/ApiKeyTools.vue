<template>
  <ToolPage :title="$t('tools.apikey.title')" :icon="Key">
    <el-tabs v-model="activeTab">
      <!-- 生成Key -->
      <el-tab-pane :label="$t('tools.apikey.tab.generate')" name="generate">
        <div class="tool-section">
          <div class="config-row">
            <div class="config-item">
              <label class="config-label">{{ $t('tools.apikey.label.type') }}</label>
              <el-select v-model="genType" style="width: 100%;">
                <el-option :label="$t('tools.apikey.label.typeRandom')" value="random" />
                <el-option :label="$t('tools.apikey.label.typeBase64')" value="base64" />
                <el-option :label="$t('tools.apikey.label.typeUuid')" value="uuid" />
                <el-option :label="$t('tools.apikey.label.typeHex')" value="hex" />
              </el-select>
            </div>
            <div class="config-item">
              <label class="config-label">{{ $t('tools.apikey.label.length') }}</label>
              <el-input-number
                v-model="genLength"
                :min="16"
                :max="512"
                :disabled="genType === 'uuid'"
                style="width: 100%;"
              />
            </div>
            <div class="config-item">
              <label class="config-label">{{ $t('tools.apikey.label.prefix') }}</label>
              <el-input
                v-model="genPrefix"
                :placeholder="$t('tools.apikey.label.prefix')"
                clearable
                style="width: 100%;"
              />
            </div>
            <div class="config-item">
              <label class="config-label">{{ $t('tools.apikey.label.countLabel') }}</label>
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
              {{ $t('tools.apikey.label.generateKey') }}
            </el-button>
          </div>

          <div class="output-section" v-if="generatedKeys.length > 0">
            <div class="result-header">
              <h4 class="section-title">{{ $t('tools.apikey.label.generateResult') }} ({{ generatedKeys.length }})</h4>
              <el-button size="small" type="success" @click="copyAllKeys">{{ $t('tools.apikey.label.copyAll') }}</el-button>
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
              <el-table-column :label="$t('tools.apikey.label.type')" prop="type" width="90" />
              <el-table-column :label="$t('tools.apikey.label.length')" prop="length" width="70" />
              <el-table-column :label="$t('tools.apikey.label.action')" width="80" fixed="right">
                <template #default="{ row }">
                  <el-button size="small" link type="primary" @click="copyKey(row.prefixed_key)">
                    {{ $t('tools.apikey.label.copy') }}
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </div>
      </el-tab-pane>

      <!-- 验证Key -->
      <el-tab-pane :label="$t('tools.apikey.tab.validate')" name="validate">
        <div class="tool-section">
          <div class="input-section">
            <h4 class="section-title">{{ $t('tools.apikey.label.validateKey') }}</h4>
            <el-input
              v-model="valKey"
              type="textarea"
              :rows="3"
              :placeholder="$t('tools.apikey.label.validateKey')"
              clearable
            />
          </div>

          <el-collapse class="optional-collapse">
            <el-collapse-item :title="$t('tools.apikey.label.advancedOptions')" name="advanced">
              <div class="config-row">
                <div class="config-item">
                  <label class="config-label">{{ $t('tools.apikey.label.expectedType') }}</label>
                  <el-select v-model="valExpectedType" clearable :placeholder="$t('tools.apikey.label.autoDetect')" style="width: 100%;">
                    <el-option :label="$t('tools.apikey.label.typeRandom')" value="random" />
                    <el-option :label="$t('tools.apikey.label.typeBase64')" value="base64" />
                    <el-option :label="$t('tools.apikey.label.typeUuid')" value="uuid" />
                    <el-option :label="$t('tools.apikey.label.typeHex')" value="hex" />
                  </el-select>
                </div>
                <div class="config-item">
                  <label class="config-label">{{ $t('tools.apikey.label.minLength') }}</label>
                  <el-input-number v-model="valMinLength" :min="1" :max="512" style="width: 100%;" />
                </div>
                <div class="config-item">
                  <label class="config-label">{{ $t('tools.apikey.label.expectedPrefix') }}</label>
                  <el-input
                    v-model="valExpectedPrefix"
                    :placeholder="$t('tools.apikey.label.prefix')"
                    clearable
                    style="width: 100%;"
                  />
                </div>
              </div>
            </el-collapse-item>
          </el-collapse>

          <div class="action-buttons">
            <el-button type="primary" @click="validateKey" :loading="validating">
              {{ $t('tools.apikey.label.validateKey') }}
            </el-button>
          </div>

          <div class="output-section" v-if="validateResult !== null">
            <el-alert
              :title="validateResult.valid ? $t('tools.apikey.label.keyValid') : $t('tools.apikey.label.keyInvalid')"
              :type="validateResult.valid ? 'success' : 'error'"
              show-icon
              style="margin-bottom: 16px;"
            />
            <el-descriptions :column="2" border size="small">
              <el-descriptions-item :label="$t('tools.apikey.label.detectedType')">
                {{ validateResult.detected_type }}
              </el-descriptions-item>
              <el-descriptions-item :label="$t('tools.apikey.label.length')">
                {{ validateResult.length }}
              </el-descriptions-item>
              <el-descriptions-item :label="$t('tools.apikey.label.hasPrefix')">
                {{ validateResult.has_prefix ? $t('tools.apikey.label.yesNo').split('/')[0] : $t('tools.apikey.label.yesNo').split('/')[1] }}
              </el-descriptions-item>
            </el-descriptions>
            <div class="field-toolbar" style="margin-top: 6px;">
              <el-button link size="small" type="primary" @click="copyText(valKey)">
                <el-icon><CopyDocument /></el-icon> Copy
              </el-button>
            </div>
            <div v-if="validateResult.issues && validateResult.issues.length > 0" class="issues-list">
              <h4 class="section-title" style="color: var(--el-color-danger);">{{ $t('tools.apikey.label.issueList') }}</h4>
              <ul>
                <li v-for="(issue, idx) in validateResult.issues" :key="idx">{{ issue }}</li>
              </ul>
            </div>
          </div>
        </div>
      </el-tab-pane>

      <!-- Key哈希 -->
      <el-tab-pane :label="$t('tools.apikey.tab.hash')" name="hash">
        <div class="tool-section">
          <div class="input-section">
            <h4 class="section-title">{{ $t('tools.apikey.label.keyHash') }}</h4>
            <el-input
              v-model="hashKeyInput"
              type="textarea"
              :rows="3"
              :placeholder="$t('tools.apikey.label.inputKeyHash')"
              clearable
            />
          </div>

          <div class="config-row">
            <div class="config-item">
              <label class="config-label">{{ $t('tools.apikey.label.algorithm') }}</label>
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
              {{ $t('tools.apikey.label.calcHash') }}
            </el-button>
          </div>

          <div class="output-section" v-if="hashResult">
            <h4 class="section-title">{{ $t('tools.apikey.label.hashResult') }}</h4>
            <div class="hash-output-row">
              <el-input
                :model-value="hashResult.hash"
                readonly
                class="key-input"
              />
              <el-button size="small" @click="copyKey(hashResult.hash)">{{ $t('tools.apikey.label.copy') }}</el-button>
            </div>
            <div class="field-toolbar" style="margin-top: 6px;">
              <el-button link size="small" type="primary" @click="copyText(hashResult.hash)">
                <el-icon><CopyDocument /></el-icon> Copy
              </el-button>
            </div>

            <el-descriptions :column="2" border size="small" style="margin-top: 12px;">
              <el-descriptions-item :label="$t('tools.apikey.label.algorithm')">
                {{ hashResult.algorithm }}
              </el-descriptions-item>
              <el-descriptions-item :label="$t('tools.apikey.label.keyLength')">
                {{ hashResult.key_length }}
              </el-descriptions-item>
              <el-descriptions-item :label="$t('tools.apikey.label.hashLength')">
                {{ hashResult.hash_length }}
              </el-descriptions-item>
              <el-descriptions-item :label="$t('tools.apikey.label.maskedKey')">
                {{ hashResult.masked }}
              </el-descriptions-item>
            </el-descriptions>
            <div class="field-toolbar" style="margin-top: 6px;">
              <el-button link size="small" type="primary" @click="copyText(hashResult.masked)">
                <el-icon><CopyDocument /></el-icon> Copy Masked Key
              </el-button>
            </div>
          </div>
        </div>
      </el-tab-pane>
    </el-tabs>
  </ToolPage>
</template>

<script>
import { ElMessage } from 'element-plus'
import { Key, CopyDocument } from '@element-plus/icons-vue'
import axios from 'axios'
import ToolPage from '@/components/ToolPage.vue'

export default {
  name: 'ApiKeyTools',
  components: {
    Key,
    CopyDocument,
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
          ElMessage.success(this.$t('tools.apikey.message.generatedCount', { count: response.data.count }))
        } else {
          ElMessage.error(response.data.error || this.$t('tools.apikey.message.generateFail'))
        }
      } catch (error) {
        ElMessage.error(this.$t('tools.apikey.message.generateFail') + ': ' + (error.response?.data?.error || error.message))
      } finally {
        this.generating = false
      }
    },

    copyKey(text) {
      navigator.clipboard.writeText(text).then(() => {
        ElMessage.success(this.$t('tools.apikey.message.copiedToClipboard'))
      }).catch(() => {
        ElMessage.error(this.$t('tools.apikey.message.copyFail'))
      })
    },

    copyAllKeys() {
      const allKeys = this.generatedKeys.map(k => k.prefixed_key).join('\n')
      navigator.clipboard.writeText(allKeys).then(() => {
        ElMessage.success(this.$t('tools.apikey.message.copiedAllKeys', { count: this.generatedKeys.length }))
      }).catch(() => {
        ElMessage.error(this.$t('tools.apikey.message.copyFail'))
      })
    },

    async validateKey() {
      if (!this.valKey.trim()) {
        ElMessage.warning(this.$t('tools.apikey.message.inputKeyRequired'))
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
            ElMessage.success(this.$t('tools.apikey.message.keyFormatValid'))
          } else {
            ElMessage.warning(this.$t('tools.apikey.message.keyFormatIssues'))
          }
        } else {
          ElMessage.error(response.data.error || this.$t('tools.apikey.message.validateFail'))
        }
      } catch (error) {
        ElMessage.error(this.$t('tools.apikey.message.validateFail') + ': ' + (error.response?.data?.error || error.message))
      } finally {
        this.validating = false
      }
    },

    async hashKey() {
      if (!this.hashKeyInput.trim()) {
        ElMessage.warning(this.$t('tools.apikey.message.inputHashKeyRequired'))
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
          ElMessage.success(this.$t('tools.apikey.message.hashSuccess'))
        } else {
          ElMessage.error(response.data.error || this.$t('tools.apikey.message.hashFail'))
        }
      } catch (error) {
        ElMessage.error(this.$t('tools.apikey.message.hashFail') + ': ' + (error.response?.data?.error || error.message))
      } finally {
        this.hashing = false
      }
    },

    copyText(text) {
      if (!text) return
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(() => {
          ElMessage.success(this.$t('common.copySuccess'))
        }).catch(() => {
          this._fallbackCopy(text)
        })
      } else {
        this._fallbackCopy(text)
      }
    },

    _fallbackCopy(text) {
      const textarea = document.createElement('textarea')
      textarea.value = text
      textarea.style.position = 'fixed'
      textarea.style.opacity = '0'
      document.body.appendChild(textarea)
      textarea.select()
      try {
        document.execCommand('copy')
        ElMessage.success(this.$t('common.copySuccess'))
      } catch {
        ElMessage.error(this.$t('tools.apikey.message.copyFail'))
      }
      document.body.removeChild(textarea)
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
