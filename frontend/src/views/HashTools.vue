<template>
  <ToolPage :title="$t('tools.hash.title')" :icon="Lock">
    <el-tabs v-model="activeTab">
      <!-- 生成哈希 -->
      <el-tab-pane :label="$t('tools.hash.tab.generate')" name="generate">
        <div class="tool-section">
          <div class="input-section">
            <h4 class="section-title">{{ $t('tools.hash.label.inputText') }}</h4>
            <el-input
              v-model="inputText"
              type="textarea"
              :rows="6"
              :placeholder="$t('tools.hash.placeholder.inputText')"
              clearable
            />
          </div>

          <HashAlgorithmCardSelector
            v-model="algorithm"
            :algorithms="availableAlgorithms"
            class="algorithm-selector"
          />

          <div class="config-section">
            <div class="action-buttons">
              <el-button type="primary" @click="generateHash" :loading="generating">
                {{ $t('tools.hash.action.generateHash') }}
              </el-button>
            </div>
          </div>

          <div class="output-section" v-if="hashResult">
            <h4 class="section-title">{{ $t('tools.hash.label.hashResult') }}</h4>
            <el-input
              v-model="hashResult"
              readonly
              type="textarea"
              :rows="4"
            />
            <div class="field-toolbar" v-if="hashResult" style="margin-top: 6px;">
              <el-button link size="small" type="primary" @click="copyText(hashResult)">
                <el-icon><CopyDocument /></el-icon> Copy
              </el-button>
            </div>
          </div>
        </div>
      </el-tab-pane>

      <!-- 验证哈希 -->
      <el-tab-pane :label="$t('tools.hash.tab.verify')" name="verify">
        <div class="tool-section">
          <div class="input-section">
            <h4 class="section-title">{{ $t('tools.hash.label.inputText') }}</h4>
            <el-input
              v-model="verifyText"
              type="textarea"
              :rows="4"
              :placeholder="$t('tools.hash.placeholder.inputOriginalText')"
              clearable
            />
          </div>

          <div class="input-section">
            <h4 class="section-title">{{ $t('tools.hash.label.expectedHash') }}</h4>
            <el-input
              v-model="verifyHash"
              :placeholder="$t('tools.hash.placeholder.inputExpectedHash')"
              clearable
            />
          </div>

          <HashAlgorithmCardSelector
            v-model="algorithm"
            :algorithms="availableAlgorithms"
            class="algorithm-selector"
          />

          <div class="config-section">
            <div class="action-buttons">
              <el-button type="primary" @click="verifyHashAction" :loading="verifying">
                {{ $t('tools.hash.action.verifyHash') }}
              </el-button>
            </div>
          </div>

          <div class="output-section" v-if="verifyResult !== null">
            <el-alert
              :title="verifyResult ? $t('tools.hash.message.hashVerified') : $t('tools.hash.message.hashFail')"
              :type="verifyResult ? 'success' : 'error'"
              :description="verifyResult ? $t('tools.hash.message.hashMatchDesc') : $t('tools.hash.message.hashMismatchDesc')"
              show-icon
            />
          </div>
        </div>
      </el-tab-pane>

      <!-- HMAC -->
      <el-tab-pane :label="$t('tools.hash.tab.hmac')" name="hmac">
        <div class="tool-section">
          <div class="input-section">
            <h4 class="section-title">{{ $t('tools.hash.label.inputText') }}</h4>
            <el-input
              v-model="hmacText"
              type="textarea"
              :rows="4"
              :placeholder="$t('tools.hash.placeholder.inputMessageText')"
              clearable
            />
          </div>

          <div class="input-section">
            <h4 class="section-title">{{ $t('tools.hash.label.secretKey') }}</h4>
            <el-input
              v-model="hmacKey"
              :placeholder="$t('tools.hash.placeholder.inputHmacKey')"
              clearable
              show-password
            />
          </div>

          <HashAlgorithmCardSelector
            v-model="algorithm"
            :algorithms="availableAlgorithms"
            class="algorithm-selector"
          />

          <div class="config-section">
            <div class="action-buttons">
              <el-button type="primary" @click="generateHMAC" :loading="generatingHMAC">
                {{ $t('tools.hash.action.generateHmac') }}
              </el-button>
            </div>
          </div>

          <div class="output-section" v-if="hmacResult">
            <h4 class="section-title">{{ $t('tools.hash.label.hmacResult') }}</h4>
            <el-input
              v-model="hmacResult"
              readonly
              type="textarea"
              :rows="4"
            />
            <div class="field-toolbar" v-if="hmacResult" style="margin-top: 6px;">
              <el-button link size="small" type="primary" @click="copyText(hmacResult)">
                <el-icon><CopyDocument /></el-icon> Copy
              </el-button>
            </div>
          </div>
        </div>
      </el-tab-pane>

      <!-- 密码哈希 -->
      <el-tab-pane :label="$t('tools.hash.tab.passwordHash')" name="password">
        <div class="tool-section">
          <div class="input-section">
            <h4 class="section-title">{{ $t('tools.hash.label.password') }}</h4>
            <el-input
              v-model="passwordText"
              :placeholder="$t('tools.hash.placeholder.inputPassword')"
              clearable
              show-password
            />
          </div>

          <el-tabs v-model="passwordHashTab" type="border-card">
            <el-tab-pane label="bcrypt" name="bcrypt">
              <div class="config-section">
                <el-form label-width="80px">
                  <el-form-item :label="$t('tools.hash.bcryptForm.rounds')">
                    <el-slider v-model="bcryptRounds" :min="4" :max="14" :step="1" show-stops style="width: 200px;" />
                    <span style="margin-left: 10px; color: var(--dt-text-secondary);">{{ bcryptRounds }}</span>
                  </el-form-item>
                </el-form>
              </div>
              <div class="action-buttons">
                <el-button type="primary" @click="generateBcrypt" :loading="generatingPassword">
                  {{ $t('tools.hash.action.generateBcrypt') }}
                </el-button>
              </div>
              <div class="output-section" v-if="bcryptResult">
                <h4 class="section-title">{{ $t('tools.hash.label.bcryptHash') }}</h4>
                <el-input v-model="bcryptResult" readonly />
                <div class="field-toolbar" v-if="bcryptResult" style="margin-top: 6px;">
                  <el-button link size="small" type="primary" @click="copyText(bcryptResult)">
                    <el-icon><CopyDocument /></el-icon> Copy
                  </el-button>
                </div>
              </div>

              <el-divider>{{ $t('tools.hash.bcryptForm.verifyBcrypt') }}</el-divider>
              <div class="input-section">
                <el-input v-model="bcryptVerifyPassword" :placeholder="$t('tools.hash.placeholder.inputPasswordVerify')" show-password />
              </div>
              <div class="input-section">
                <el-input v-model="bcryptVerifyHash" :placeholder="$t('tools.hash.placeholder.inputBcryptHash')" />
              </div>
              <div class="action-buttons">
                <el-button type="primary" @click="verifyBcrypt" :loading="verifyingBcrypt">
                  {{ $t('tools.hash.action.verify') }}
                </el-button>
              </div>
              <div class="output-section" v-if="bcryptVerifyResult !== null">
                <el-alert
                  :title="bcryptVerifyResult ? $t('tools.hash.message.passwordMatch') : $t('tools.hash.message.passwordMismatch')"
                  :type="bcryptVerifyResult ? 'success' : 'error'"
                  show-icon
                />
              </div>
            </el-tab-pane>

            <el-tab-pane label="PBKDF2" name="pbkdf2">
              <div class="config-section">
                <el-form label-width="80px">
                  <el-form-item :label="$t('tools.hash.pbkdf2Form.salt')">
                    <el-input v-model="pbkdf2Salt" :placeholder="$t('tools.hash.pbkdf2Form.saltPlaceholder')" clearable style="width: 300px;" />
                  </el-form-item>
                  <el-form-item :label="$t('tools.hash.pbkdf2Form.iterations')">
                    <el-input-number v-model="pbkdf2Iterations" :min="1000" :max="500000" :step="10000" />
                  </el-form-item>
                  <el-form-item :label="$t('tools.hash.pbkdf2Form.keyLength')">
                    <el-input-number v-model="pbkdf2Dklen" :min="16" :max="128" :step="8" />
                  </el-form-item>
                  <el-form-item :label="$t('tools.hash.pbkdf2Form.algorithm')">
                    <el-select v-model="pbkdf2Algorithm">
                      <el-option label="SHA-256" value="sha256" />
                      <el-option label="SHA-384" value="sha384" />
                      <el-option label="SHA-512" value="sha512" />
                    </el-select>
                  </el-form-item>
                </el-form>
              </div>
              <div class="action-buttons">
                <el-button type="primary" @click="generatePBKDF2" :loading="generatingPassword">
                  {{ $t('tools.hash.action.generatePbkdf2') }}
                </el-button>
              </div>
              <div class="output-section" v-if="pbkdf2Result">
                <h4 class="section-title">{{ $t('tools.hash.label.pbkdf2Result') }}</h4>
                <el-input v-model="pbkdf2Result" readonly />
                <div class="field-toolbar" v-if="pbkdf2Result" style="margin-top: 6px;">
                  <el-button link size="small" type="primary" @click="copyText(pbkdf2Result)">
                    <el-icon><CopyDocument /></el-icon> Copy
                  </el-button>
                </div>
                <div style="margin-top: 8px; color: var(--dt-text-secondary); font-size: 12px;">
                  {{ $t('tools.hash.message.pbkdf2Meta', { salt: pbkdf2ResultSalt, iterations: pbkdf2Iterations, length: pbkdf2Dklen }) }}
                </div>
              </div>
            </el-tab-pane>
          </el-tabs>
        </div>
      </el-tab-pane>
    </el-tabs>
  </ToolPage>
</template>

<script>
import { ElMessage } from 'element-plus'
import { Lock, CopyDocument } from '@element-plus/icons-vue'
import axios from 'axios'
import { useDeviceStore } from '@/stores/device.js'
import HashAlgorithmCardSelector from '@/components/HashAlgorithmCardSelector.vue'
import ToolPage from '@/components/ToolPage.vue'

export default {
  name: 'HashTools',
  components: {
    Lock,
    CopyDocument,
    HashAlgorithmCardSelector,
    ToolPage
  },
  data() {
    const deviceStore = useDeviceStore()
    return {
      deviceStore,
      activeTab: 'generate',
      algorithm: 'sha256',
      availableAlgorithms: [],
      // 生成哈希
      inputText: '',
      hashResult: '',
      generating: false,
      // 验证哈希
      verifyText: '',
      verifyHash: '',
      verifying: false,
      verifyResult: null,
      // HMAC
      hmacText: '',
      hmacKey: '',
      hmacResult: '',
      generatingHMAC: false,
      // 密码哈希
      passwordText: '',
      generatingPassword: false,
      passwordHashTab: 'bcrypt',
      // bcrypt
      bcryptRounds: 12,
      bcryptResult: '',
      bcryptVerifyPassword: '',
      bcryptVerifyHash: '',
      verifyingBcrypt: false,
      bcryptVerifyResult: null,
      // PBKDF2
      pbkdf2Salt: '',
      pbkdf2Iterations: 100000,
      pbkdf2Dklen: 32,
      pbkdf2Algorithm: 'sha256',
      pbkdf2Result: '',
      pbkdf2ResultSalt: ''
    }
  },
  async mounted() {
    try {
      const response = await axios.get('/api/hash-tools/algorithms')
      if (response.data.success) {
        this.availableAlgorithms = response.data.algorithms
      }
    } catch (error) {
      // Silently handle algorithm fetch failure
    }
  },
  methods: {
    async generateHash() {
      if (!this.inputText.trim()) {
        ElMessage.warning(this.$t('tools.hash.message.inputTextRequired'))
        return
      }

      this.generating = true
      try {
        const response = await axios.post('/api/hash-tools/generate', {
          text: this.inputText,
          algorithm: this.algorithm
        })

        if (response.data.success) {
          this.hashResult = response.data.hash
          ElMessage.success(this.$t('tools.hash.message.hashSuccess'))
        } else {
          ElMessage.error(response.data.error)
        }
      } catch (error) {
        ElMessage.error(this.$t('tools.hash.message.hashFail') + ': ' + (error.response?.data?.error || error.message))
      } finally {
        this.generating = false
      }
    },

    async verifyHashAction() {
      if (!this.verifyText.trim()) {
        ElMessage.warning(this.$t('tools.hash.message.inputOriginalRequired'))
        return
      }
      if (!this.verifyHash.trim()) {
        ElMessage.warning(this.$t('tools.hash.message.inputExpectedRequired'))
        return
      }

      this.verifying = true
      try {
        const response = await axios.post('/api/hash-tools/verify', {
          text: this.verifyText,
          hash: this.verifyHash,
          algorithm: this.algorithm
        })

        if (response.data.success) {
          this.verifyResult = response.data.valid
          if (response.data.valid) {
            ElMessage.success(this.$t('tools.hash.message.verifySuccess'))
          } else {
            ElMessage.error(this.$t('tools.hash.message.verifyMismatch'))
          }
        } else {
          ElMessage.error(response.data.error)
        }
      } catch (error) {
        ElMessage.error(this.$t('tools.hash.message.verifyFail') + ': ' + (error.response?.data?.error || error.message))
      } finally {
        this.verifying = false
      }
    },

    async generateHMAC() {
      if (!this.hmacText.trim()) {
        ElMessage.warning(this.$t('tools.hash.message.inputMessageRequired'))
        return
      }
      if (!this.hmacKey.trim()) {
        ElMessage.warning(this.$t('tools.hash.message.inputHmacKeyRequired'))
        return
      }

      this.generatingHMAC = true
      try {
        const response = await axios.post('/api/hash-tools/hmac', {
          text: this.hmacText,
          key: this.hmacKey,
          algorithm: this.algorithm
        })

        if (response.data.success) {
          this.hmacResult = response.data.hmac
          ElMessage.success(this.$t('tools.hash.message.hmacSuccess'))
        } else {
          ElMessage.error(response.data.error)
        }
      } catch (error) {
        ElMessage.error(this.$t('tools.hash.message.hmacFail') + ': ' + (error.response?.data?.error || error.message))
      } finally {
        this.generatingHMAC = false
      }
    },

    async generateBcrypt() {
      if (!this.passwordText) {
        ElMessage.warning(this.$t('tools.hash.message.inputPasswordRequired'))
        return
      }

      this.generatingPassword = true
      try {
        const response = await axios.post('/api/hash-tools/bcrypt', {
          password: this.passwordText,
          rounds: this.bcryptRounds
        })

        if (response.data.success) {
          this.bcryptResult = response.data.hash
          ElMessage.success(this.$t('tools.hash.message.bcryptSuccess'))
        } else {
          ElMessage.error(response.data.error)
        }
      } catch (error) {
        ElMessage.error(this.$t('tools.hash.message.bcryptFail') + ': ' + (error.response?.data?.error || error.message))
      } finally {
        this.generatingPassword = false
      }
    },

    async verifyBcrypt() {
      if (!this.bcryptVerifyPassword) {
        ElMessage.warning(this.$t('tools.hash.message.inputPasswordRequired'))
        return
      }
      if (!this.bcryptVerifyHash) {
        ElMessage.warning(this.$t('tools.hash.message.inputBcryptHash'))
        return
      }

      this.verifyingBcrypt = true
      try {
        const response = await axios.post('/api/hash-tools/bcrypt/verify', {
          password: this.bcryptVerifyPassword,
          hash: this.bcryptVerifyHash
        })

        if (response.data.success) {
          this.bcryptVerifyResult = response.data.valid
          if (response.data.valid) {
            ElMessage.success(this.$t('tools.hash.message.passwordMatch'))
          } else {
            ElMessage.error(this.$t('tools.hash.message.passwordMismatch'))
          }
        } else {
          ElMessage.error(response.data.error)
        }
      } catch (error) {
        ElMessage.error(this.$t('tools.hash.message.verifyFail') + ': ' + (error.response?.data?.error || error.message))
      } finally {
        this.verifyingBcrypt = false
      }
    },

    async generatePBKDF2() {
      if (!this.passwordText) {
        ElMessage.warning(this.$t('tools.hash.message.inputPasswordRequired'))
        return
      }

      this.generatingPassword = true
      const salt = this.pbkdf2Salt || Math.random().toString(36).substring(2, 18)
      try {
        const response = await axios.post('/api/hash-tools/pbkdf2', {
          password: this.passwordText,
          salt: salt,
          algorithm: this.pbkdf2Algorithm,
          iterations: this.pbkdf2Iterations,
          dklen: this.pbkdf2Dklen
        })

        if (response.data.success) {
          this.pbkdf2Result = response.data.derived_key
          this.pbkdf2ResultSalt = response.data.salt
          ElMessage.success(this.$t('tools.hash.message.pbkdf2Success'))
        } else {
          ElMessage.error(response.data.error)
        }
      } catch (error) {
        ElMessage.error(this.$t('tools.hash.message.pbkdf2Fail') + ': ' + (error.response?.data?.error || error.message))
      } finally {
        this.generatingPassword = false
      }
    },

    copyText(text) {
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(() => {
          ElMessage.success(this.$t('common.copied'))
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
        ElMessage.success(this.$t('common.copied'))
      } catch (e) {
        ElMessage.error(this.$t('common.copyFail') || 'Copy failed')
      }
      document.body.removeChild(textarea)
    },

    copyResult() {
      this.copyText(this.hashResult)
    },

    copyHmacResult() {
      this.copyText(this.hmacResult)
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
}

.action-buttons {
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
}

.algorithm-selector {
  margin-bottom: 20px;
}

@media (max-width: 768px) {
  .el-descriptions :deep(.el-descriptions__body) { width: 100%; }
  .el-descriptions :deep(.el-descriptions__label) { min-width: 80px; }
  .action-buttons { flex-direction: column; }
  .action-buttons .el-button { width: 100%; margin-left: 0 !important; margin-top: 8px; }
  .el-row { flex-direction: column; }
  .el-col { max-width: 100% !important; flex: 0 0 100% !important; }
}
</style>
