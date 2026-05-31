<template>
  <ToolPage title="哈希工具" :icon="Lock">
    <el-tabs v-model="activeTab">
      <!-- 生成哈希 -->
      <el-tab-pane label="生成哈希" name="generate">
        <div class="tool-section">
          <div class="input-section">
            <h4 class="section-title">输入文本</h4>
            <el-input
              v-model="inputText"
              type="textarea"
              :rows="6"
              placeholder="请输入要生成哈希的文本..."
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
                生成哈希
              </el-button>
            </div>
          </div>

          <div class="output-section" v-if="hashResult">
            <h4 class="section-title">哈希结果</h4>
            <el-input
              v-model="hashResult"
              readonly
              type="textarea"
              :rows="4"
            />
            <div class="action-section" style="margin-top: 8px;">
              <el-button size="small" @click="copyResult">复制</el-button>
            </div>
          </div>
        </div>
      </el-tab-pane>

      <!-- 验证哈希 -->
      <el-tab-pane label="验证哈希" name="verify">
        <div class="tool-section">
          <div class="input-section">
            <h4 class="section-title">输入文本</h4>
            <el-input
              v-model="verifyText"
              type="textarea"
              :rows="4"
              placeholder="请输入原始文本..."
              clearable
            />
          </div>

          <div class="input-section">
            <h4 class="section-title">预期哈希值</h4>
            <el-input
              v-model="verifyHash"
              placeholder="请输入预期的哈希值..."
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
                验证哈希
              </el-button>
            </div>
          </div>

          <div class="output-section" v-if="verifyResult !== null">
            <el-alert
              :title="verifyResult ? '哈希验证通过' : '哈希验证失败'"
              :type="verifyResult ? 'success' : 'error'"
              :description="verifyResult ? '输入的哈希值与计算结果匹配' : '输入的哈希值与计算结果不匹配'"
              show-icon
            />
          </div>
        </div>
      </el-tab-pane>

      <!-- HMAC -->
      <el-tab-pane label="HMAC" name="hmac">
        <div class="tool-section">
          <div class="input-section">
            <h4 class="section-title">输入文本</h4>
            <el-input
              v-model="hmacText"
              type="textarea"
              :rows="4"
              placeholder="请输入消息文本..."
              clearable
            />
          </div>

          <div class="input-section">
            <h4 class="section-title">密钥</h4>
            <el-input
              v-model="hmacKey"
              placeholder="请输入HMAC密钥..."
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
                生成HMAC
              </el-button>
            </div>
          </div>

          <div class="output-section" v-if="hmacResult">
            <h4 class="section-title">HMAC结果</h4>
            <el-input
              v-model="hmacResult"
              readonly
              type="textarea"
              :rows="4"
            />
            <div class="action-section" style="margin-top: 8px;">
              <el-button size="small" @click="copyHmacResult">复制</el-button>
            </div>
          </div>
        </div>
      </el-tab-pane>

      <!-- 密码哈希 -->
      <el-tab-pane label="密码哈希" name="password">
        <div class="tool-section">
          <div class="input-section">
            <h4 class="section-title">密码</h4>
            <el-input
              v-model="passwordText"
              placeholder="请输入密码..."
              clearable
              show-password
            />
          </div>

          <el-tabs v-model="passwordHashTab" type="border-card">
            <el-tab-pane label="bcrypt" name="bcrypt">
              <div class="config-section">
                <el-form label-width="80px">
                  <el-form-item label="轮数">
                    <el-slider v-model="bcryptRounds" :min="4" :max="14" :step="1" show-stops style="width: 200px;" />
                    <span style="margin-left: 10px; color: var(--dt-text-secondary);">{{ bcryptRounds }}</span>
                  </el-form-item>
                </el-form>
              </div>
              <div class="action-buttons">
                <el-button type="primary" @click="generateBcrypt" :loading="generatingPassword">
                  生成bcrypt哈希
                </el-button>
              </div>
              <div class="output-section" v-if="bcryptResult">
                <h4 class="section-title">bcrypt哈希</h4>
                <el-input v-model="bcryptResult" readonly />
              </div>

              <el-divider>验证bcrypt</el-divider>
              <div class="input-section">
                <el-input v-model="bcryptVerifyPassword" placeholder="输入密码验证..." show-password />
              </div>
              <div class="input-section">
                <el-input v-model="bcryptVerifyHash" placeholder="输入bcrypt哈希值..." />
              </div>
              <div class="action-buttons">
                <el-button type="primary" @click="verifyBcrypt" :loading="verifyingBcrypt">
                  验证
                </el-button>
              </div>
              <div class="output-section" v-if="bcryptVerifyResult !== null">
                <el-alert
                  :title="bcryptVerifyResult ? '密码匹配' : '密码不匹配'"
                  :type="bcryptVerifyResult ? 'success' : 'error'"
                  show-icon
                />
              </div>
            </el-tab-pane>

            <el-tab-pane label="PBKDF2" name="pbkdf2">
              <div class="config-section">
                <el-form label-width="80px">
                  <el-form-item label="盐值">
                    <el-input v-model="pbkdf2Salt" placeholder="留空则自动生成" clearable style="width: 300px;" />
                  </el-form-item>
                  <el-form-item label="迭代次数">
                    <el-input-number v-model="pbkdf2Iterations" :min="1000" :max="500000" :step="10000" />
                  </el-form-item>
                  <el-form-item label="密钥长度">
                    <el-input-number v-model="pbkdf2Dklen" :min="16" :max="128" :step="8" />
                  </el-form-item>
                  <el-form-item label="算法">
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
                  生成PBKDF2
                </el-button>
              </div>
              <div class="output-section" v-if="pbkdf2Result">
                <h4 class="section-title">PBKDF2结果</h4>
                <el-input v-model="pbkdf2Result" readonly />
                <div style="margin-top: 8px; color: var(--dt-text-secondary); font-size: 12px;">
                  盐值: {{ pbkdf2ResultSalt }} | 迭代: {{ pbkdf2Iterations }} | 长度: {{ pbkdf2Dklen }}字节
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
import { Lock } from '@element-plus/icons-vue'
import axios from 'axios'
import HashAlgorithmCardSelector from '@/components/HashAlgorithmCardSelector.vue'
import ToolPage from '@/components/ToolPage.vue'

export default {
  name: 'HashTools',
  components: {
    Lock,
    HashAlgorithmCardSelector,
    ToolPage
  },
  data() {
    return {
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
        ElMessage.warning('请输入要生成哈希的文本')
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
          ElMessage.success('哈希生成成功')
        } else {
          ElMessage.error(response.data.error)
        }
      } catch (error) {
        ElMessage.error('哈希生成失败: ' + (error.response?.data?.error || error.message))
      } finally {
        this.generating = false
      }
    },

    async verifyHashAction() {
      if (!this.verifyText.trim()) {
        ElMessage.warning('请输入原始文本')
        return
      }
      if (!this.verifyHash.trim()) {
        ElMessage.warning('请输入预期哈希值')
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
            ElMessage.success('哈希验证通过')
          } else {
            ElMessage.error('哈希验证失败：不匹配')
          }
        } else {
          ElMessage.error(response.data.error)
        }
      } catch (error) {
        ElMessage.error('验证失败: ' + (error.response?.data?.error || error.message))
      } finally {
        this.verifying = false
      }
    },

    async generateHMAC() {
      if (!this.hmacText.trim()) {
        ElMessage.warning('请输入消息文本')
        return
      }
      if (!this.hmacKey.trim()) {
        ElMessage.warning('请输入HMAC密钥')
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
          ElMessage.success('HMAC生成成功')
        } else {
          ElMessage.error(response.data.error)
        }
      } catch (error) {
        ElMessage.error('HMAC生成失败: ' + (error.response?.data?.error || error.message))
      } finally {
        this.generatingHMAC = false
      }
    },

    async generateBcrypt() {
      if (!this.passwordText) {
        ElMessage.warning('请输入密码')
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
          ElMessage.success('bcrypt哈希生成成功')
        } else {
          ElMessage.error(response.data.error)
        }
      } catch (error) {
        ElMessage.error('bcrypt生成失败: ' + (error.response?.data?.error || error.message))
      } finally {
        this.generatingPassword = false
      }
    },

    async verifyBcrypt() {
      if (!this.bcryptVerifyPassword) {
        ElMessage.warning('请输入密码')
        return
      }
      if (!this.bcryptVerifyHash) {
        ElMessage.warning('请输入bcrypt哈希值')
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
            ElMessage.success('密码匹配')
          } else {
            ElMessage.error('密码不匹配')
          }
        } else {
          ElMessage.error(response.data.error)
        }
      } catch (error) {
        ElMessage.error('验证失败: ' + (error.response?.data?.error || error.message))
      } finally {
        this.verifyingBcrypt = false
      }
    },

    async generatePBKDF2() {
      if (!this.passwordText) {
        ElMessage.warning('请输入密码')
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
          ElMessage.success('PBKDF2生成成功')
        } else {
          ElMessage.error(response.data.error)
        }
      } catch (error) {
        ElMessage.error('PBKDF2生成失败: ' + (error.response?.data?.error || error.message))
      } finally {
        this.generatingPassword = false
      }
    },

    copyResult() {
      navigator.clipboard.writeText(this.hashResult).then(() => {
        ElMessage.success('已复制到剪贴板')
      })
    },

    copyHmacResult() {
      navigator.clipboard.writeText(this.hmacResult).then(() => {
        ElMessage.success('已复制到剪贴板')
      })
    }
  }
}
</script>

<style scoped>
.action-buttons {
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
}

.algorithm-selector {
  margin-bottom: 20px;
}
</style>
