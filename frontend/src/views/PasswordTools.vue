<template>
  <ToolPage :title="$t('tools.password.title')" :icon="Lock">
    <el-tabs v-model="activeTab">

      <!-- 密码生成 -->
      <el-tab-pane :label="$t('tools.password.tab.generate')" name="generate">
        <div class="tool-section">
          <el-form label-width="120px" label-position="right">
            <el-form-item :label="$t('tools.password.labels.passwordLength')">
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

            <el-form-item :label="$t('tools.password.labels.charTypes')">
              <el-checkbox-group v-model="generateForm.charset">
                <el-checkbox label="uppercase">{{ $t('tools.password.labels.uppercase') }}</el-checkbox>
                <el-checkbox label="lowercase">{{ $t('tools.password.labels.lowercase') }}</el-checkbox>
                <el-checkbox label="numbers">{{ $t('tools.password.labels.numbers') }}</el-checkbox>
                <el-checkbox label="symbols">{{ $t('tools.password.labels.symbols') }}</el-checkbox>
              </el-checkbox-group>
            </el-form-item>

            <el-form-item :label="$t('tools.password.labels.excludeAmbiguous')">
              <el-switch
                v-model="generateForm.excludeAmbiguous"
                :active-text="$t('tools.password.labels.exclude')"
                :inactive-text="$t('tools.password.labels.include')"
              />
              <span class="hint-text">{{ $t('tools.password.labels.excludeAmbiguousDesc') }}</span>
            </el-form-item>

            <el-form-item :label="$t('tools.password.labels.generateCount')">
              <el-input-number
                v-model="generateForm.count"
                :min="1"
                :max="50"
                :step="1"
              />
            </el-form-item>

            <el-form-item>
              <el-button type="primary" @click="generatePasswords" :loading="generating">
                {{ $t('tools.password.labels.generatePassword') }}
              </el-button>
            </el-form-item>
          </el-form>

          <div class="result-section" v-if="generatedPasswords.length > 0">
            <div class="result-header">
              <h4 class="section-title">{{ $t('tools.password.labels.generateResult') }}</h4>
              <el-button size="small" type="success" @click="copyAllPasswords">
                {{ $t('tools.password.labels.copyAll') }}
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
                    {{ $t('tools.password.labels.copy') }}
                  </el-button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </el-tab-pane>

      <!-- 强度检测 -->
      <el-tab-pane :label="$t('tools.password.tab.strengthCheck')" name="strength">
        <div class="tool-section">
          <el-form label-width="120px" label-position="right">
            <el-form-item :label="$t('tools.password.labels.inputPassword')">
              <el-input
                v-model="strengthPassword"
                :placeholder="$t('tools.password.labels.inputPassword')"
                show-password
                clearable
                @input="onPasswordInput"
              />
            </el-form-item>
            <el-form-item v-if="strengthPassword.length > 0">
              <span class="hint-text">{{ $t('tools.password.labels.currentLength', { length: strengthPassword.length }) }}</span>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="checkStrength" :loading="checkingStrength">
                {{ $t('tools.password.labels.checkStrength') }}
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
              <el-descriptions-item :label="$t('tools.password.labels.passwordLengthLabel')">
                {{ strengthResult.length }}
              </el-descriptions-item>
              <el-descriptions-item :label="$t('tools.password.labels.strengthLevel')">
                <el-tag :type="getLevelTagType(strengthResult.score)">
                  {{ strengthResult.level }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item :label="$t('tools.password.labels.hasUppercase')">
                <el-tag :type="strengthResult.has_uppercase ? 'success' : 'info'" size="small">
                  {{ strengthResult.has_uppercase ? $t('tools.password.labels.yes') : $t('tools.password.labels.no') }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item :label="$t('tools.password.labels.hasLowercase')">
                <el-tag :type="strengthResult.has_lowercase ? 'success' : 'info'" size="small">
                  {{ strengthResult.has_lowercase ? $t('tools.password.labels.yes') : $t('tools.password.labels.no') }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item :label="$t('tools.password.labels.hasNumbers')">
                <el-tag :type="strengthResult.has_numbers ? 'success' : 'info'" size="small">
                  {{ strengthResult.has_numbers ? $t('tools.password.labels.yes') : $t('tools.password.labels.no') }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item :label="$t('tools.password.labels.hasSymbols')">
                <el-tag :type="strengthResult.has_symbols ? 'success' : 'info'" size="small">
                  {{ strengthResult.has_symbols ? $t('tools.password.labels.yes') : $t('tools.password.labels.no') }}
                </el-tag>
              </el-descriptions-item>
            </el-descriptions>

            <div class="field-toolbar" style="margin-top: 6px;">
              <el-button link size="small" type="primary" @click="copyText(strengthPassword)">
                <el-icon><CopyDocument /></el-icon> Copy
              </el-button>
            </div>

            <div class="suggestions-section" v-if="strengthResult.suggestions.length > 0">
              <h4 class="section-title">{{ $t('tools.password.labels.suggestions') }}</h4>
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
      <el-tab-pane :label="$t('tools.password.tab.mnemonic')" name="passphrase">
        <div class="tool-section">
          <el-form label-width="120px" label-position="right">
            <el-form-item :label="$t('tools.password.labels.wordCount')">
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

            <el-form-item :label="$t('tools.password.labels.separator')">
              <el-select v-model="passphraseForm.separator">
                <el-option :label="$t('tools.password.labels.separatorDash')" value="-" />
                <el-option :label="$t('tools.password.labels.separatorUnderscore')" value="_" />
                <el-option :label="$t('tools.password.labels.separatorSpace')" value=" " />
                <el-option :label="$t('tools.password.labels.separatorDot')" value="." />
              </el-select>
            </el-form-item>

            <el-form-item :label="$t('tools.password.labels.capitalize')">
              <el-switch v-model="passphraseForm.capitalize" />
            </el-form-item>

            <el-form-item :label="$t('tools.password.labels.includeNumbers')">
              <el-switch v-model="passphraseForm.includeNumber" />
            </el-form-item>

            <el-form-item>
              <el-button type="primary" @click="generatePassphrase" :loading="generatingPassphrase">
                {{ $t('tools.password.labels.generateMnemonic') }}
              </el-button>
            </el-form-item>
          </el-form>

          <div class="passphrase-result" v-if="passphraseResult">
            <div class="result-header">
              <h4 class="section-title">{{ $t('tools.password.labels.mnemonicResult') }}</h4>
              <el-button size="small" type="primary" @click="copyPassphrase">
                {{ $t('tools.password.labels.copy') }}
              </el-button>
            </div>
            <div class="passphrase-display">
              {{ passphraseResult.passphrase }}
            </div>
            <div class="field-toolbar" style="margin-top: 6px;">
              <el-button link size="small" type="primary" @click="copyText(passphraseResult.passphrase)">
                <el-icon><CopyDocument /></el-icon> Copy
              </el-button>
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
import { Lock, CopyDocument } from '@element-plus/icons-vue'
import axios from 'axios'
import ToolPage from '@/components/ToolPage.vue'

export default {
  name: 'PasswordTools',
  components: {
    Lock,
    CopyDocument,
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
        ElMessage.warning(this.$t('tools.password.messages.selectCharType'))
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
          const visible = {}
          response.data.passwords.forEach((_, i) => { visible[i] = true })
          this.visiblePasswords = visible
          ElMessage.success(this.$t('tools.password.messages.generatedCount', { count: response.data.passwords.length }))
        } else {
          ElMessage.error(response.data.error || this.$t('tools.password.messages.generateFail'))
        }
      } catch (error) {
        ElMessage.error(this.$t('tools.password.messages.generateFail') + ': ' + (error.response?.data?.error || error.message))
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
      this.copyText(pwd, this.$t('tools.password.messages.copiedToClipboard'))
    },

    copyAllPasswords() {
      const text = this.generatedPasswords.join('\n')
      this.copyText(text, this.$t('tools.password.messages.copiedAllPasswords'))
    },

    onPasswordInput() {
      // Real-time length display is handled via the template binding
    },

    async checkStrength() {
      if (!this.strengthPassword) {
        ElMessage.warning(this.$t('tools.password.messages.inputPasswordRequired'))
        return
      }

      this.checkingStrength = true
      try {
        const response = await axios.post('/api/password-tools/strength', {
          password: this.strengthPassword
        })

        if (response.data.success) {
          this.strengthResult = response.data
          ElMessage.success(this.$t('tools.password.messages.checkComplete'))
        } else {
          ElMessage.error(response.data.error || this.$t('tools.password.messages.checkFail'))
        }
      } catch (error) {
        ElMessage.error(this.$t('tools.password.messages.checkFail') + ': ' + (error.response?.data?.error || error.message))
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
          ElMessage.success(this.$t('tools.password.messages.mnemonicSuccess'))
        } else {
          ElMessage.error(response.data.error || this.$t('tools.password.messages.generateFail'))
        }
      } catch (error) {
        ElMessage.error(this.$t('tools.password.messages.generateFail') + ': ' + (error.response?.data?.error || error.message))
      } finally {
        this.generatingPassphrase = false
      }
    },

    copyPassphrase() {
      if (!this.passphraseResult) return
      this.copyText(this.passphraseResult.passphrase, this.$t('tools.password.messages.copiedToClipboard'))
    },

    copyText(text, successMsg) {
      if (!text) return
      const msg = successMsg || this.$t('common.copySuccess')
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(() => {
          ElMessage.success(msg)
        }).catch(() => {
          this._fallbackCopy(text, msg)
        })
      } else {
        this._fallbackCopy(text, msg)
      }
    },

    _fallbackCopy(text, successMsg) {
      const textarea = document.createElement('textarea')
      textarea.value = text
      textarea.style.position = 'fixed'
      textarea.style.opacity = '0'
      document.body.appendChild(textarea)
      textarea.select()
      try {
        document.execCommand('copy')
        ElMessage.success(successMsg || this.$t('common.copySuccess'))
      } catch {
        ElMessage.error(this.$t('tools.password.messages.copyFail'))
      }
      document.body.removeChild(textarea)
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
  /* ── Padding handled by ToolPage parent ── */
  .tool-section {
    padding-bottom: var(--dt-spacing-md, 16px);
  }

  /* ── Form: top-aligned labels ── */
  .tool-section :deep(.el-form-item) {
    margin-bottom: 14px;
  }

  .tool-section :deep(.el-form-item__label) {
    float: none !important;
    display: block;
    text-align: left;
    padding-bottom: 4px;
    width: auto !important;
    font-size: var(--dt-font-size-sm, 13px);
    color: var(--dt-text-secondary);
    font-weight: 500;
  }

  .tool-section :deep(.el-form-item__content) {
    margin-left: 0 !important;
  }

  /* ── Slider: full width stacked ── */
  .slider-row {
    flex-direction: column;
    align-items: stretch;
    gap: 8px;
  }

  .slider-number {
    width: 100%;
  }

  /* ── Result sections with card background ── */
  .result-section,
  .strength-result,
  .passphrase-result {
    padding: 16px;
    background: var(--dt-bg-section);
    border-radius: var(--dt-radius-lg);
    border: 1px solid var(--dt-border-lighter);
  }

  /* ── Password items: card style ── */
  .password-list {
    gap: 10px;
  }

  .password-item {
    flex-direction: column;
    align-items: stretch;
    gap: 8px;
    padding: 12px 14px;
    border-radius: var(--dt-radius-md);
    background: var(--dt-bg-card);
    border: 1px solid var(--dt-border-lighter);
    box-shadow: var(--dt-shadow-sm);
  }

  .password-text {
    margin-right: 0;
    width: 100%;
    font-size: var(--dt-font-size-sm, 13px);
    line-height: 1.6;
    padding: 4px 0;
  }

  .password-actions {
    display: flex;
    justify-content: flex-end;
    gap: 8px;
  }

  /* ── Passphrase display ── */
  .passphrase-display {
    font-size: 15px;
    padding: 14px;
    letter-spacing: 1px;
    border-radius: var(--dt-radius-lg);
  }

  /* ── Hint text ── */
  .hint-text {
    margin-left: 0;
    display: block;
    margin-top: 4px;
    font-size: var(--dt-font-size-xs, 12px);
  }

  /* ── Strength level ── */
  .strength-level {
    font-size: var(--dt-font-size-lg, 16px);
  }

  /* ── el-descriptions ── */
  :deep(.el-descriptions) {
    --el-descriptions-table-border: none;
  }

  :deep(.el-descriptions .el-descriptions__body .el-descriptions__table) {
    table-layout: fixed;
  }

  /* ── Tag sizing ── */
  .suggestion-tag,
  .word-tag {
    font-size: var(--dt-font-size-xs, 12px);
  }
}
</style>
