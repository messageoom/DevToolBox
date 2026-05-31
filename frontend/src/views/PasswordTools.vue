<template>
  <ToolPage title="密码生成器" :icon="Lock">
    <el-tabs v-model="activeTab">

      <!-- 密码生成 -->
      <el-tab-pane label="密码生成" name="generate">
        <div class="tool-section">
          <el-form label-width="120px" label-position="right">
            <el-form-item label="密码长度">
              <div class="slider-row">
                <el-slider
                  v-model="generateForm.length"
                  :min="8"
                  :max="128"
                  :step="1"
                  class="slider"
                />
                <el-input-number
                  v-model="generateForm.length"
                  :min="8"
                  :max="128"
                  :step="1"
                  size="small"
                  class="slider-number"
                />
              </div>
            </el-form-item>

            <el-form-item label="字符类型">
              <el-checkbox-group v-model="generateForm.charset">
                <el-checkbox label="uppercase">大写字母 (A-Z)</el-checkbox>
                <el-checkbox label="lowercase">小写字母 (a-z)</el-checkbox>
                <el-checkbox label="numbers">数字 (0-9)</el-checkbox>
                <el-checkbox label="symbols">特殊符号 (!@#$...)</el-checkbox>
              </el-checkbox-group>
            </el-form-item>

            <el-form-item label="排除歧义字符">
              <el-switch
                v-model="generateForm.excludeAmbiguous"
                active-text="排除"
                inactive-text="包含"
              />
              <span class="hint-text">排除易混淆字符: l/I/1, O/0</span>
            </el-form-item>

            <el-form-item label="生成数量">
              <el-input-number
                v-model="generateForm.count"
                :min="1"
                :max="50"
                :step="1"
              />
            </el-form-item>

            <el-form-item>
              <el-button type="primary" @click="generatePasswords" :loading="generating">
                生成密码
              </el-button>
            </el-form-item>
          </el-form>

          <div class="result-section" v-if="generatedPasswords.length > 0">
            <div class="result-header">
              <h4 class="section-title">生成结果</h4>
              <el-button size="small" type="success" @click="copyAllPasswords">
                复制全部
              </el-button>
            </div>
            <div class="password-list">
              <div
                v-for="(pwd, index) in generatedPasswords"
                :key="index"
                class="password-item"
              >
                <span class="password-text" v-if="!visiblePasswords[index]">
                  {{ concealPassword(pwd) }}
                </span>
                <span class="password-text password-visible" v-else>
                  {{ pwd }}
                </span>
                <div class="password-actions">
                  <el-button
                    size="small"
                    :icon="visiblePasswords[index] ? 'Hide' : 'View'"
                    circle
                    @click="toggleVisibility(index)"
                  />
                  <el-button
                    size="small"
                    type="primary"
                    @click="copyPassword(pwd)"
                  >
                    复制
                  </el-button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </el-tab-pane>

      <!-- 强度检测 -->
      <el-tab-pane label="强度检测" name="strength">
        <div class="tool-section">
          <el-form label-width="120px" label-position="right">
            <el-form-item label="输入密码">
              <el-input
                v-model="strengthPassword"
                placeholder="请输入要检测的密码..."
                show-password
                clearable
                @input="onPasswordInput"
              />
            </el-form-item>
            <el-form-item v-if="strengthPassword.length > 0">
              <span class="hint-text">当前长度: {{ strengthPassword.length }} 个字符</span>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="checkStrength" :loading="checkingStrength">
                检测强度
              </el-button>
            </el-form-item>
          </el-form>

          <div class="strength-result" v-if="strengthResult">
            <div class="strength-progress">
              <el-progress
                :percentage="strengthResult.score"
                :color="getScoreColor(strengthResult.score)"
                :stroke-width="20"
                :text-inside="true"
              />
              <div class="strength-level" :style="{ color: getScoreColor(strengthResult.score) }">
                {{ strengthResult.level }} ({{ strengthResult.score }}分)
              </div>
            </div>

            <el-descriptions :column="2" border style="margin-top: 20px;">
              <el-descriptions-item label="密码长度">
                {{ strengthResult.length }}
              </el-descriptions-item>
              <el-descriptions-item label="强度等级">
                <el-tag :type="getLevelTagType(strengthResult.score)">
                  {{ strengthResult.level }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="包含大写字母">
                <el-tag :type="strengthResult.has_uppercase ? 'success' : 'info'" size="small">
                  {{ strengthResult.has_uppercase ? '是' : '否' }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="包含小写字母">
                <el-tag :type="strengthResult.has_lowercase ? 'success' : 'info'" size="small">
                  {{ strengthResult.has_lowercase ? '是' : '否' }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="包含数字">
                <el-tag :type="strengthResult.has_numbers ? 'success' : 'info'" size="small">
                  {{ strengthResult.has_numbers ? '是' : '否' }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="包含特殊符号">
                <el-tag :type="strengthResult.has_symbols ? 'success' : 'info'" size="small">
                  {{ strengthResult.has_symbols ? '是' : '否' }}
                </el-tag>
              </el-descriptions-item>
            </el-descriptions>

            <div class="suggestions-section" v-if="strengthResult.suggestions.length > 0">
              <h4 class="section-title">改进建议</h4>
              <div class="suggestion-tags">
                <el-tag
                  v-for="(suggestion, index) in strengthResult.suggestions"
                  :key="index"
                  type="warning"
                  class="suggestion-tag"
                >
                  {{ suggestion }}
                </el-tag>
              </div>
            </div>
          </div>
        </div>
      </el-tab-pane>

      <!-- 助记密码 -->
      <el-tab-pane label="助记密码" name="passphrase">
        <div class="tool-section">
          <el-form label-width="120px" label-position="right">
            <el-form-item label="单词数量">
              <div class="slider-row">
                <el-slider
                  v-model="passphraseForm.wordCount"
                  :min="3"
                  :max="12"
                  :step="1"
                  class="slider"
                  show-stops
                />
                <el-input-number
                  v-model="passphraseForm.wordCount"
                  :min="3"
                  :max="12"
                  :step="1"
                  size="small"
                  class="slider-number"
                />
              </div>
            </el-form-item>

            <el-form-item label="分隔符">
              <el-select v-model="passphraseForm.separator">
                <el-option label="短横线 (-)" value="-" />
                <el-option label="下划线 (_)" value="_" />
                <el-option label="空格" value=" " />
                <el-option label="点号 (.)" value="." />
              </el-select>
            </el-form-item>

            <el-form-item label="首字母大写">
              <el-switch v-model="passphraseForm.capitalize" />
            </el-form-item>

            <el-form-item label="包含数字">
              <el-switch v-model="passphraseForm.includeNumber" />
            </el-form-item>

            <el-form-item>
              <el-button type="primary" @click="generatePassphrase" :loading="generatingPassphrase">
                生成助记密码
              </el-button>
            </el-form-item>
          </el-form>

          <div class="passphrase-result" v-if="passphraseResult">
            <div class="result-header">
              <h4 class="section-title">生成结果</h4>
              <el-button size="small" type="primary" @click="copyPassphrase">
                复制
              </el-button>
            </div>
            <div class="passphrase-display">
              {{ passphraseResult.passphrase }}
            </div>
            <div class="word-tags">
              <el-tag
                v-for="(word, index) in passphraseResult.words"
                :key="index"
                class="word-tag"
                type=""
                effect="plain"
              >
                {{ word }}
              </el-tag>
            </div>
          </div>
        </div>
      </el-tab-pane>

    </el-tabs>
  </ToolPage>
</template>

<script>
import { ElMessage } from 'element-plus'
import { Lock } from '@element-plus/icons-vue'
import axios from 'axios'
import ToolPage from '@/components/ToolPage.vue'

export default {
  name: 'PasswordTools',
  components: {
    Lock,
    ToolPage
  },
  data() {
    return {
      activeTab: 'generate',
      Lock,
      // Password generation
      generateForm: {
        length: 16,
        charset: ['uppercase', 'lowercase', 'numbers', 'symbols'],
        excludeAmbiguous: false,
        count: 5
      },
      generating: false,
      generatedPasswords: [],
      visiblePasswords: {},
      // Strength check
      strengthPassword: '',
      checkingStrength: false,
      strengthResult: null,
      // Passphrase
      passphraseForm: {
        wordCount: 4,
        separator: '-',
        capitalize: false,
        includeNumber: false
      },
      generatingPassphrase: false,
      passphraseResult: null
    }
  },
  methods: {
    async generatePasswords() {
      if (this.generateForm.charset.length === 0) {
        ElMessage.warning('请至少选择一种字符类型')
        return
      }

      this.generating = true
      try {
        const response = await axios.post('/api/password-tools/generate', {
          length: this.generateForm.length,
          uppercase: this.generateForm.charset.includes('uppercase'),
          lowercase: this.generateForm.charset.includes('lowercase'),
          numbers: this.generateForm.charset.includes('numbers'),
          symbols: this.generateForm.charset.includes('symbols'),
          exclude_ambiguous: this.generateForm.excludeAmbiguous,
          count: this.generateForm.count
        })

        if (response.data.success) {
          this.generatedPasswords = response.data.passwords
          this.visiblePasswords = {}
          ElMessage.success(`成功生成 ${response.data.passwords.length} 个密码`)
        } else {
          ElMessage.error(response.data.error || '生成失败')
        }
      } catch (error) {
        ElMessage.error('生成失败: ' + (error.response?.data?.error || error.message))
      } finally {
        this.generating = false
      }
    },

    concealPassword(pwd) {
      return '•'.repeat(pwd.length)
    },

    toggleVisibility(index) {
      this.visiblePasswords[index] = !this.visiblePasswords[index]
      // Force reactivity update
      this.visiblePasswords = { ...this.visiblePasswords }
    },

    copyPassword(pwd) {
      navigator.clipboard.writeText(pwd).then(() => {
        ElMessage.success('已复制到剪贴板')
      }).catch(() => {
        ElMessage.error('复制失败')
      })
    },

    copyAllPasswords() {
      const text = this.generatedPasswords.join('\n')
      navigator.clipboard.writeText(text).then(() => {
        ElMessage.success('已复制全部密码到剪贴板')
      }).catch(() => {
        ElMessage.error('复制失败')
      })
    },

    onPasswordInput() {
      // Real-time length display is handled via the template binding
    },

    async checkStrength() {
      if (!this.strengthPassword) {
        ElMessage.warning('请输入密码')
        return
      }

      this.checkingStrength = true
      try {
        const response = await axios.post('/api/password-tools/strength', {
          password: this.strengthPassword
        })

        if (response.data.success) {
          this.strengthResult = response.data
          ElMessage.success('检测完成')
        } else {
          ElMessage.error(response.data.error || '检测失败')
        }
      } catch (error) {
        ElMessage.error('检测失败: ' + (error.response?.data?.error || error.message))
      } finally {
        this.checkingStrength = false
      }
    },

    getScoreColor(score) {
      if (score <= 20) return '#F56C6C'
      if (score <= 40) return '#E6A23C'
      if (score <= 60) return '#409EFF'
      if (score <= 80) return '#67C23A'
      return '#33CC99'
    },

    getLevelTagType(score) {
      if (score <= 20) return 'danger'
      if (score <= 40) return 'warning'
      if (score <= 60) return ''
      if (score <= 80) return 'success'
      return 'success'
    },

    async generatePassphrase() {
      this.generatingPassphrase = true
      try {
        const response = await axios.post('/api/password-tools/passphrase', {
          word_count: this.passphraseForm.wordCount,
          separator: this.passphraseForm.separator,
          capitalize: this.passphraseForm.capitalize,
          include_number: this.passphraseForm.includeNumber
        })

        if (response.data.success) {
          this.passphraseResult = response.data
          ElMessage.success('助记密码生成成功')
        } else {
          ElMessage.error(response.data.error || '生成失败')
        }
      } catch (error) {
        ElMessage.error('生成失败: ' + (error.response?.data?.error || error.message))
      } finally {
        this.generatingPassphrase = false
      }
    },

    copyPassphrase() {
      if (!this.passphraseResult) return
      navigator.clipboard.writeText(this.passphraseResult.passphrase).then(() => {
        ElMessage.success('已复制到剪贴板')
      }).catch(() => {
        ElMessage.error('复制失败')
      })
    }
  }
}
</script>

<style scoped>
.tool-section {
  padding: 10px 0;
}

.section-title {
  margin: 16px 0 12px;
  color: var(--dt-text-primary, #333);
  font-weight: 600;
  font-size: 15px;
}

.slider-row {
  display: flex;
  align-items: center;
  width: 100%;
  gap: 16px;
}

.slider {
  flex: 1;
}

.slider-number {
  width: 110px;
  flex-shrink: 0;
}

.hint-text {
  margin-left: 12px;
  color: var(--dt-text-secondary, #909399);
  font-size: 13px;
}

.result-section {
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid var(--dt-border-color, #ebeef5);
}

.result-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.result-header .section-title {
  margin: 0;
}

.password-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.password-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 14px;
  background: var(--dt-bg-color, #f5f7fa);
  border-radius: 6px;
  border: 1px solid var(--dt-border-color, #e4e7ed);
  transition: border-color 0.2s;
}

.password-item:hover {
  border-color: var(--el-color-primary, #409eff);
}

.password-text {
  font-family: 'Consolas', 'Courier New', monospace;
  font-size: 14px;
  color: var(--dt-text-primary, #333);
  letter-spacing: 1px;
  word-break: break-all;
  flex: 1;
  margin-right: 12px;
  user-select: all;
}

.password-visible {
  font-weight: 500;
}

.password-actions {
  display: flex;
  gap: 6px;
  flex-shrink: 0;
}

.strength-result {
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid var(--dt-border-color, #ebeef5);
}

.strength-progress {
  margin-bottom: 10px;
}

.strength-level {
  text-align: center;
  font-size: 18px;
  font-weight: 700;
  margin-top: 10px;
}

.suggestions-section {
  margin-top: 20px;
}

.suggestion-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.suggestion-tag {
  font-size: 13px;
}

.passphrase-result {
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid var(--dt-border-color, #ebeef5);
}

.passphrase-display {
  background: var(--dt-bg-color, #f5f7fa);
  border: 2px solid var(--el-color-primary, #409eff);
  border-radius: 8px;
  padding: 20px;
  font-size: 22px;
  font-family: 'Consolas', 'Courier New', monospace;
  text-align: center;
  word-break: break-all;
  color: var(--dt-text-primary, #333);
  font-weight: 600;
  letter-spacing: 2px;
  margin-bottom: 16px;
}

.word-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.word-tag {
  font-size: 14px;
  font-family: 'Consolas', 'Courier New', monospace;
}

@media (max-width: 768px) {
  .slider-row {
    flex-direction: column;
    align-items: stretch;
  }

  .slider-number {
    width: 100%;
  }

  .password-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }

  .password-text {
    margin-right: 0;
    width: 100%;
  }

  .password-actions {
    align-self: flex-end;
  }

  .passphrase-display {
    font-size: 16px;
    padding: 14px;
    letter-spacing: 1px;
  }

  :deep(.el-form-item__label) {
    width: 100px !important;
  }

  :deep(.el-descriptions) {
    --el-descriptions-table-border: none;
  }

  :deep(.el-descriptions .el-descriptions__body .el-descriptions__table) {
    table-layout: fixed;
  }
}
</style>
