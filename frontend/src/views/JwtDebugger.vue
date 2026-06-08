<template>
  <ToolPage :title="$t('tools.jwt.title')" :icon="Unlock">
    <div class="jwt-debugger">
      <!-- Input Section -->
      <div class="input-section">
        <div class="section-header">
          <h4 class="section-title">{{ $t('tools.jwt.jwtToken') }}</h4>
          <el-button size="small" @click="clearToken">{{ $t('tools.jwt.clear') }}</el-button>
        </div>
        <el-input
          v-model="token"
          type="textarea"
          :rows="6"
          :placeholder="$t('tools.jwt.placeholder')"
          clearable
        />
      </div>

      <!-- Error Display -->
      <div v-if="parsed.error" class="error-section">
        <el-alert :title="parsed.error" type="error" show-icon :closable="false" />
      </div>

      <!-- Parsed Sections -->
      <div v-if="parsed.isValid" class="parsed-sections">
        <!-- Header -->
        <el-card class="jwt-card header-card">
          <template #header>
            <div class="card-header-row">
              <span>{{ $t('tools.jwt.header') }}</span>
              <el-button size="small" @click="copyToClipboard(headerJson)">{{ $t('common.copy') }}</el-button>
            </div>
          </template>
          <el-input
            v-model="headerJson"
            type="textarea"
            :rows="4"
            readonly
            class="code-textarea"
          />
          <div class="field-toolbar" style="margin-top: 6px;">
            <el-button link size="small" type="primary" @click="copyText(headerJson)">
              <el-icon><CopyDocument /></el-icon> Copy
            </el-button>
          </div>
        </el-card>

        <!-- Payload -->
        <el-card class="jwt-card payload-card">
          <template #header>
            <div class="card-header-row">
              <span>{{ $t('tools.jwt.payload') }}</span>
              <el-button size="small" @click="copyToClipboard(payloadJson)">{{ $t('common.copy') }}</el-button>
            </div>
          </template>
          <el-input
            v-model="payloadJson"
            type="textarea"
            :rows="6"
            readonly
            class="code-textarea"
          />
          <div class="field-toolbar" style="margin-top: 6px;">
            <el-button link size="small" type="primary" @click="copyText(payloadJson)">
              <el-icon><CopyDocument /></el-icon> Copy
            </el-button>
          </div>
          <div v-if="hasSpecialClaims" class="claims-section">
            <el-descriptions :column="1" border size="small">
              <el-descriptions-item v-if="parsed.payload.exp !== undefined" :label="$t('tools.jwt.expirationTime')">
                {{ formatTimestamp(parsed.payload.exp) }}
                <el-tag
                  :type="isExpired(parsed.payload.exp) ? 'danger' : 'success'"
                  size="small"
                  style="margin-left: 8px;"
                >
                  {{ isExpired(parsed.payload.exp) ? $t('tools.jwt.expired') : $t('tools.jwt.valid') }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item v-if="parsed.payload.iat !== undefined" :label="$t('tools.jwt.issuedAt')">
                {{ formatTimestamp(parsed.payload.iat) }}
              </el-descriptions-item>
              <el-descriptions-item v-if="parsed.payload.nbf !== undefined" :label="$t('tools.jwt.notBefore')">
                {{ formatTimestamp(parsed.payload.nbf) }}
              </el-descriptions-item>
              <el-descriptions-item v-if="parsed.payload.iss !== undefined" :label="$t('tools.jwt.issuer')">
                {{ parsed.payload.iss }}
              </el-descriptions-item>
              <el-descriptions-item v-if="parsed.payload.sub !== undefined" :label="$t('tools.jwt.subject')">
                {{ parsed.payload.sub }}
              </el-descriptions-item>
              <el-descriptions-item v-if="parsed.payload.aud !== undefined" :label="$t('tools.jwt.audience')">
                {{ parsed.payload.aud }}
              </el-descriptions-item>
              <el-descriptions-item v-if="parsed.payload.jti !== undefined" :label="$t('tools.jwt.jwtId')">
                {{ parsed.payload.jti }}
              </el-descriptions-item>
            </el-descriptions>
          </div>
        </el-card>

        <!-- Signature -->
        <el-card class="jwt-card signature-card">
          <template #header>
            <div class="card-header-row">
              <span>{{ $t('tools.jwt.signature') }}</span>
              <el-button size="small" @click="copyToClipboard(parsed.signature)">{{ $t('common.copy') }}</el-button>
            </div>
          </template>
          <div class="signature-content">
            <code class="signature-code">{{ truncatedSignature }}</code>
          </div>
          <div class="field-toolbar" style="margin-top: 6px;">
            <el-button link size="small" type="primary" @click="copyText(parsed.signature)">
              <el-icon><CopyDocument /></el-icon> Copy
            </el-button>
          </div>
          <el-alert
            :title="$t('tools.jwt.tip')"
            type="info"
            :closable="false"
            show-icon
            style="margin-top: 12px;"
          >
            <template #default>
              {{ $t('tools.jwt.signatureTip') }}
            </template>
          </el-alert>
        </el-card>
      </div>
    </div>
  </ToolPage>
</template>

<script>
import { ElMessage } from 'element-plus'
import { Unlock, CopyDocument } from '@element-plus/icons-vue'
import ToolPage from '@/components/ToolPage.vue'

export default {
  name: 'JwtDebugger',
  components: {
    Unlock,
    CopyDocument,
    ToolPage
  },
  data() {
    return {
      token: '',
      parsed: {
        header: null,
        payload: null,
        signature: '',
        isValid: false,
        error: ''
      },
      headerJson: '',
      payloadJson: ''
    }
  },
  computed: {
    hasSpecialClaims() {
      if (!this.parsed.payload) return false
      const keys = ['exp', 'iat', 'nbf', 'iss', 'sub', 'aud', 'jti']
      return keys.some((key) => this.parsed.payload[key] !== undefined)
    },
    truncatedSignature() {
      if (!this.parsed.signature) return ''
      if (this.parsed.signature.length > 100) {
        return this.parsed.signature.slice(0, 100) + '...'
      }
      return this.parsed.signature
    }
  },
  watch: {
    token() {
      this.parseJwt()
    }
  },
  methods: {
    parseJwt() {
      const raw = this.token.trim()
      if (!raw) {
        this.parsed = {
          header: null,
          payload: null,
          signature: '',
          isValid: false,
          error: ''
        }
        this.headerJson = ''
        this.payloadJson = ''
        return
      }

      const parts = raw.split('.')
      if (parts.length !== 3) {
        this.parsed = {
          header: null,
          payload: null,
          signature: '',
          isValid: false,
          error: this.$t('tools.jwt.invalidFormat')
        }
        this.headerJson = ''
        this.payloadJson = ''
        return
      }

      try {
        const headerStr = this.base64UrlDecode(parts[0])
        const payloadStr = this.base64UrlDecode(parts[1])
        const header = JSON.parse(headerStr)
        const payload = JSON.parse(payloadStr)

        this.parsed = {
          header,
          payload,
          signature: parts[2],
          isValid: true,
          error: ''
        }
        this.headerJson = JSON.stringify(header, null, 2)
        this.payloadJson = JSON.stringify(payload, null, 2)
      } catch (err) {
        this.parsed = {
          header: null,
          payload: null,
          signature: '',
          isValid: false,
          error: this.$t('tools.jwt.parseFail') + '：' + (err.message || this.$t('tools.jwt.invalidJwt'))
        }
        this.headerJson = ''
        this.payloadJson = ''
      }
    },

    base64UrlDecode(str) {
      // Replace base64url chars with base64 chars
      let base64 = str.replace(/-/g, '+').replace(/_/g, '/')
      // Pad with '=' to make length a multiple of 4
      while (base64.length % 4) {
        base64 += '='
      }
      // Decode base64 to string
      const decoded = atob(base64)
      // Convert to UTF-8
      try {
        return decodeURIComponent(
          decoded
            .split('')
            .map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
            .join('')
        )
      } catch (e) {
        return decoded
      }
    },

    formatTimestamp(ts) {
      const num = typeof ts === 'string' ? parseInt(ts, 10) : ts
      if (isNaN(num)) return this.$t('tools.jwt.invalidTimestamp')
      const date = new Date(num * 1000)
      return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      })
    },

    copyToClipboard(text) {
      if (!text) return
      navigator.clipboard.writeText(text).then(() => {
        ElMessage.success(this.$t('common.copySuccess'))
      }).catch(() => {
        ElMessage.error(this.$t('common.copyFail'))
      })
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
        ElMessage.error(this.$t('common.copyFail'))
      } finally {
        document.body.removeChild(textarea)
      }
    },

    isExpired(exp) {
      const num = typeof exp === 'string' ? parseInt(exp, 10) : exp
      if (isNaN(num)) return false
      return num < Date.now() / 1000
    },

    clearToken() {
      this.token = ''
    }
  }
}
</script>

<style scoped>
.jwt-debugger {
  display: flex;
  flex-direction: column;
  gap: var(--dt-spacing-lg);
}

.input-section {
  background-color: var(--dt-bg-section);
  border: 1px solid var(--dt-border-light);
  border-radius: var(--dt-border-radius-base);
  padding: var(--dt-spacing-lg);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--dt-spacing-sm);
}

.section-title {
  margin: 0;
  font-size: var(--dt-font-size-base);
  font-weight: 600;
  color: var(--dt-text-primary);
}

.error-section {
  margin-top: var(--dt-spacing-sm);
}

.parsed-sections {
  display: grid;
  grid-template-columns: 1fr;
  gap: var(--dt-spacing-lg);
}

.jwt-card {
  border-radius: var(--dt-border-radius-base);
}

.jwt-card :deep(.el-card__header) {
  padding: var(--dt-spacing-sm) var(--dt-spacing-lg);
  font-weight: 600;
}

.card-header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-card {
  border-left: 4px solid var(--dt-primary);
}

.header-card :deep(.el-card__header) {
  background-color: rgba(var(--dt-primary-rgb, 64, 158, 255), 0.08);
  color: var(--dt-primary);
}

.payload-card {
  border-left: 4px solid var(--dt-success);
}

.payload-card :deep(.el-card__header) {
  background-color: rgba(var(--dt-success-rgb, 103, 194, 58), 0.08);
  color: var(--dt-success);
}

.signature-card {
  border-left: 4px solid var(--dt-danger);
}

.signature-card :deep(.el-card__header) {
  background-color: rgba(var(--dt-danger-rgb, 245, 108, 108), 0.08);
  color: var(--dt-danger);
}

.code-textarea :deep(textarea) {
  font-family: 'Courier New', monospace;
  background-color: var(--dt-bg-section);
}

.claims-section {
  margin-top: var(--dt-spacing-md);
}

.signature-content {
  background-color: var(--dt-bg-section);
  border: 1px solid var(--dt-border-light);
  border-radius: var(--dt-border-radius-base);
  padding: var(--dt-spacing-md);
  word-break: break-all;
}

.signature-code {
  font-family: 'Courier New', monospace;
  font-size: var(--dt-font-size-sm);
  color: var(--dt-text-regular);
}

/* Responsive */
@media (max-width: 768px) {
  .parsed-sections {
    grid-template-columns: 1fr;
  }

  .input-section {
    padding: var(--dt-spacing-md);
  }
}
</style>
