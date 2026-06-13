<template>
  <ToolPage :title="$t('tools.uuid.title')" :icon="Key">
    <el-tabs v-model="activeTab">
      <!-- 生成UUID -->
      <el-tab-pane :label="$t('tools.uuid.tab.generate')" name="generate">
        <div class="tool-section">
          <div class="config-row">
            <div class="config-item">
              <div class="field-label">{{ $t('tools.uuid.labels.version') }}</div>
              <el-select v-model="version" style="width: 100%;">
                <el-option :label="$t('tools.uuid.labels.uuidV1')" :value="1" />
                <el-option :label="$t('tools.uuid.labels.uuidV3')" :value="3" />
                <el-option :label="$t('tools.uuid.labels.uuidV4')" :value="4" />
                <el-option :label="$t('tools.uuid.labels.uuidV5')" :value="5" />
                <el-option :label="$t('tools.uuid.labels.uuidV6')" :value="6" />
                <el-option :label="$t('tools.uuid.labels.uuidV7')" :value="7" />
              </el-select>
            </div>
            <div class="config-item">
              <div class="field-label">{{ $t('tools.uuid.labels.count') }}</div>
              <el-input-number
                v-model="count"
                :min="1"
                :max="100"
                style="width: 100%;"
              />
            </div>
            <div class="config-item config-switch">
              <div class="field-label">{{ $t('tools.uuid.labels.uppercase') }}</div>
              <el-switch v-model="uppercase" />
            </div>
          </div>

          <div class="config-row" v-if="version === 3 || version === 5">
            <div class="config-item">
              <div class="field-label">{{ $t('tools.uuid.labels.namespace') }}</div>
              <el-select v-model="namespace" style="width: 100%;">
                <el-option label="DNS" value="DNS" />
                <el-option label="URL" value="URL" />
                <el-option label="OID" value="OID" />
                <el-option label="X500" value="X500" />
              </el-select>
            </div>
            <div class="config-item" style="flex: 2;">
              <div class="field-label">{{ $t('tools.uuid.labels.name') }}</div>
              <el-input
                v-model="name"
                :placeholder="$t('tools.uuid.placeholders.nameInput')"
                clearable
              />
            </div>
          </div>

          <div class="action-section">
            <el-button type="primary" @click="generateUUIDs" :loading="generating">
              {{ $t('tools.uuid.labels.generate') }}
            </el-button>
          </div>

          <div class="output-section" v-if="generatedUUIDs.length > 0">
            <div class="result-header">
              <h4 class="section-title">{{ $t('tools.uuid.labels.generateResult') }} ({{ generatedUUIDs.length }})</h4>
              <el-button size="small" type="primary" plain @click="copyAll">
                {{ $t('tools.uuid.labels.copyAll') }}
              </el-button>
            </div>
            <div class="uuid-list">
              <div class="uuid-item" v-for="(item, index) in generatedUUIDs" :key="index">
                <span class="uuid-text">{{ item }}</span>
                <el-button size="small" text @click="copySingle(item)">
                  {{ $t('tools.uuid.labels.copy') }}
                </el-button>
              </div>
            </div>
          </div>
        </div>
      </el-tab-pane>

      <!-- 验证UUID -->
      <el-tab-pane :label="$t('tools.uuid.tab.validate')" name="validate">
        <div class="tool-section">
          <div class="input-section">
            <h4 class="section-title">{{ $t('tools.uuid.labels.uuidString') }}</h4>
            <el-input
              v-model="validateInput"
              :aria-label="$t('tools.uuid.labels.uuidString')"
              :placeholder="$t('tools.uuid.placeholders.uuidInput')"
              clearable
              @keyup.enter="validateUUID"
            />
          </div>

          <div class="action-section">
            <el-button type="primary" @click="validateUUID" :loading="validating">
              {{ $t('tools.uuid.labels.validate') }}
            </el-button>
          </div>

          <div class="output-section" v-if="validateResult !== null">
            <el-alert
              :title="validateResult.valid ? $t('tools.uuid.labels.validUuid') : $t('tools.uuid.labels.invalidUuid')"
              :type="validateResult.valid ? 'success' : 'error'"
              :description="validateResult.valid
                ? `${$t('tools.uuid.labels.versionLabel')}: v${validateResult.version} | ${$t('tools.uuid.labels.variant')}: ${validateResult.variant}`
                : $t('tools.uuid.messages.invalidUuidFormat')"
              show-icon
            />
            <el-descriptions
              v-if="validateResult.valid"
              :column="descColumn"
              border
              style="margin-top: 16px;"
            >
              <el-descriptions-item :label="$t('tools.uuid.labels.versionLabel')">
                v{{ validateResult.version }}
              </el-descriptions-item>
              <el-descriptions-item :label="$t('tools.uuid.labels.variant')">
                {{ validateResult.variant }}
              </el-descriptions-item>
            </el-descriptions>
            <div class="field-toolbar" style="margin-top: 6px;">
              <el-button link size="small" type="primary" @click="copyText(validateInput)">
                <el-icon><CopyDocument /></el-icon> Copy
              </el-button>
            </div>
          </div>
        </div>
      </el-tab-pane>

      <!-- 解析UUID -->
      <el-tab-pane :label="$t('tools.uuid.tab.parse')" name="parse">
        <div class="tool-section">
          <div class="input-section">
            <h4 class="section-title">{{ $t('tools.uuid.labels.uuidString') }}</h4>
            <el-input
              v-model="parseInput"
              :aria-label="$t('tools.uuid.labels.uuidString')"
              :placeholder="$t('tools.uuid.placeholders.uuidInput')"
              clearable
              @keyup.enter="parseUUID"
            />
          </div>

          <div class="action-section">
            <el-button type="primary" @click="parseUUID" :loading="parsing">
              {{ $t('tools.uuid.labels.parseUuid') }}
            </el-button>
          </div>

          <div class="output-section" v-if="parseResult">
            <h4 class="section-title">{{ $t('tools.uuid.labels.parseResult') }}</h4>
            <el-descriptions :column="descColumn" border>
              <el-descriptions-item :label="$t('tools.uuid.labels.uuid')">
                {{ parseResult.uuid }}
              </el-descriptions-item>
              <el-descriptions-item :label="$t('tools.uuid.labels.versionLabel')">
                v{{ parseResult.version }}
              </el-descriptions-item>
              <el-descriptions-item :label="$t('tools.uuid.labels.variant')">
                {{ parseResult.variant }}
              </el-descriptions-item>
              <el-descriptions-item label="time_low">
                {{ parseResult.fields.time_low }}
              </el-descriptions-item>
              <el-descriptions-item label="time_mid">
                {{ parseResult.fields.time_mid }}
              </el-descriptions-item>
              <el-descriptions-item label="time_hi_version">
                {{ parseResult.fields.time_hi_version }}
              </el-descriptions-item>
              <el-descriptions-item label="clock_seq_hi_variant">
                {{ parseResult.fields.clock_seq_hi_variant }}
              </el-descriptions-item>
              <el-descriptions-item label="clock_seq_low">
                {{ parseResult.fields.clock_seq_low }}
              </el-descriptions-item>
              <el-descriptions-item label="node">
                {{ parseResult.fields.node }}
              </el-descriptions-item>
            </el-descriptions>
            <div class="field-toolbar" style="margin-top: 6px;">
              <el-button link size="small" type="primary" @click="copyText(parseResult.uuid)">
                <el-icon><CopyDocument /></el-icon> Copy
              </el-button>
            </div>

            <!-- v1 extra fields -->
            <template v-if="parseResult.version === 1 && parseResult.time !== undefined">
              <h4 class="section-title" style="margin-top: 20px;">{{ $t('tools.uuid.labels.uuidV1Details') }}</h4>
              <el-descriptions :column="descColumn" border>
                <el-descriptions-item :label="$t('tools.uuid.labels.timestamp')">
                  {{ parseResult.time }}
                </el-descriptions-item>
                <el-descriptions-item :label="$t('tools.uuid.labels.timeUtc')" v-if="parseResult.time_as_datetime">
                  {{ parseResult.time_as_datetime }}
                </el-descriptions-item>
                <el-descriptions-item :label="$t('tools.uuid.labels.macAddress')">
                  {{ parseResult.mac_address }}
                </el-descriptions-item>
                <el-descriptions-item :label="$t('tools.uuid.labels.clockSequence')">
                  {{ parseResult.clock_seq }}
                </el-descriptions-item>
              </el-descriptions>
            </template>
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
import { copyToClipboard } from '@/utils/format.js'

export default {
  name: 'UuidTools',
  components: {
    Key,
    CopyDocument,
    ToolPage
  },
  data() {
    return {
      activeTab: 'generate',
      // Generate
      version: 4,
      count: 1,
      uppercase: false,
      namespace: 'DNS',
      name: '',
      generating: false,
      generatedUUIDs: [],
      // Validate
      validateInput: '',
      validating: false,
      validateResult: null,
      // Parse
      parseInput: '',
      parsing: false,
      parseResult: null,
      isMobile: typeof window !== 'undefined' && window.innerWidth <= 768
    }
  },
  computed: {
    descColumn() {
      return this.isMobile ? 1 : 2
    }
  },
  mounted() {
    this._onResize = () => { this.isMobile = window.innerWidth <= 768 }
    window.addEventListener('resize', this._onResize)
  },
  beforeUnmount() {
    if (this._onResize) window.removeEventListener('resize', this._onResize)
  },
  methods: {
    async generateUUIDs() {
      if ((this.version === 3 || this.version === 5) && !this.name.trim()) {
        ElMessage.warning(this.$t('tools.uuid.messages.v3v5NameRequired'))
        return
      }

      this.generating = true
      try {
        const payload = {
          version: this.version,
          count: this.count,
          uppercase: this.uppercase
        }
        if (this.version === 3 || this.version === 5) {
          payload.namespace = this.namespace
          payload.name = this.name
        }

        const response = await axios.post('/api/uuid-tools/generate', payload)

        if (response.data.success) {
          this.generatedUUIDs = response.data.uuids
          ElMessage.success(this.$t('tools.uuid.messages.generatedCount', { count: response.data.count }))
        } else {
          ElMessage.error(response.data.error || this.$t('tools.uuid.messages.generateFail'))
        }
      } catch (error) {
        ElMessage.error(this.$t('tools.uuid.messages.generateFail') + ': ' + (error.response?.data?.error || error.message))
      } finally {
        this.generating = false
      }
    },

    copySingle(text) {
      this.copyText(text, this.$t('tools.uuid.messages.copiedToClipboard'))
    },

    copyAll() {
      const text = this.generatedUUIDs.join('\n')
      this.copyText(text, this.$t('tools.uuid.messages.copiedAllUuids'))
    },

    async copyText(text, successMsg) {
      if (!text) return
      const msg = successMsg || this.$t('common.copySuccess')
      try {
        await copyToClipboard(text)
        ElMessage.success(msg)
      } catch {
        ElMessage.error(this.$t('common.copyFail'))
      }
    },

    async validateUUID() {
      if (!this.validateInput.trim()) {
        ElMessage.warning(this.$t('tools.uuid.messages.inputUuidRequired'))
        return
      }

      this.validating = true
      try {
        const response = await axios.post('/api/uuid-tools/validate', {
          uuid_str: this.validateInput.trim()
        })

        if (response.data.success) {
          this.validateResult = response.data
        } else {
          ElMessage.error(response.data.error || this.$t('tools.uuid.messages.validateFail'))
        }
      } catch (error) {
        ElMessage.error(this.$t('tools.uuid.messages.validateFail') + ': ' + (error.response?.data?.error || error.message))
      } finally {
        this.validating = false
      }
    },

    async parseUUID() {
      if (!this.parseInput.trim()) {
        ElMessage.warning(this.$t('tools.uuid.messages.inputUuidRequired'))
        return
      }

      this.parsing = true
      try {
        const response = await axios.post('/api/uuid-tools/parse', {
          uuid_str: this.parseInput.trim()
        })

        if (response.data.success) {
          this.parseResult = response.data
          ElMessage.success(this.$t('tools.uuid.messages.parseSuccess'))
        } else {
          ElMessage.error(response.data.error || this.$t('tools.uuid.messages.parseFail'))
        }
      } catch (error) {
        ElMessage.error(this.$t('tools.uuid.messages.parseFail') + ': ' + (error.response?.data?.error || error.message))
      } finally {
        this.parsing = false
      }
    }
  }
}
</script>

<style scoped>
.config-row {
  display: flex;
  gap: 16px;
  margin-bottom: 16px;
  align-items: flex-end;
  flex-wrap: wrap;
}

.config-item {
  flex: 1;
  min-width: 140px;
}

.config-switch {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  min-width: 80px;
}

.field-label {
  font-size: var(--dt-font-size-sm, 13px);
  color: var(--dt-text-secondary, #909399);
  margin-bottom: 6px;
}

.action-section {
  margin: 16px 0;
}

.output-section {
  margin-top: 20px;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.uuid-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.uuid-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: var(--dt-bg-section, #f5f7fa);
  border-radius: 6px;
  border: 1px solid var(--dt-border-lighter, #ebeef5);
  transition: background 0.2s;
}

.uuid-item:hover {
  background: var(--dt-bg-hover, #ecf5ff);
}

.uuid-text {
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: var(--dt-font-size-base, 14px);
  color: var(--dt-text-primary, #303133);
  word-break: break-all;
}

.section-title {
  font-size: var(--dt-font-size-base, 14px);
  font-weight: 600;
  color: var(--dt-text-primary, #303133);
  margin: 0 0 8px 0;
}

@media (max-width: 768px) {
  /* ── Padding handled by ToolPage parent ── */
  .tool-section {
    padding-bottom: var(--dt-spacing-md, 16px);
  }

  /* ── Config: stack vertically with card style ── */
  .config-row {
    flex-direction: column;
    gap: 12px;
    padding: 16px;
    background: var(--dt-bg-section);
    border-radius: var(--dt-radius-lg);
    border: 1px solid var(--dt-border-lighter);
  }

  .config-item {
    min-width: 100%;
  }

  .field-label {
    margin-bottom: 8px;
    font-weight: 500;
  }

  /* ── Action button ── */
  .action-section {
    margin: 16px 0;
  }

  .action-section .el-button {
    width: 100%;
  }

  /* ── Output section with card background ── */
  .output-section {
    padding: 16px;
    background: var(--dt-bg-section);
    border-radius: var(--dt-radius-lg);
    border: 1px solid var(--dt-border-lighter);
    margin-top: 16px;
  }

  /* ── UUID result items: card style ── */
  .uuid-list {
    gap: 10px;
  }

  .uuid-item {
    flex-direction: column;
    align-items: stretch;
    gap: 8px;
    padding: 12px 14px;
    border-radius: var(--dt-radius-md);
    background: var(--dt-bg-card);
    border: 1px solid var(--dt-border-lighter);
    box-shadow: var(--dt-shadow-sm);
  }

  .uuid-text {
    font-size: var(--dt-font-size-xs, 12px);
    line-height: 1.6;
    word-break: break-all;
  }

  .uuid-item .el-button {
    align-self: flex-end;
    min-height: 36px;
  }

  /* ── Input sections ── */
  .input-section {
    padding: 0;
    background: transparent;
    border: none;
  }

  /* ── Section title ── */
  .section-title {
    font-size: var(--dt-font-size-sm, 13px);
  }

  /* ── Result header ── */
  .result-header {
    margin-bottom: 14px;
  }

  /* ── Descriptions ── */
  :deep(.el-descriptions) {
    --el-descriptions-table-border: none;
  }

  :deep(.el-descriptions .el-descriptions__body .el-descriptions__table) {
    table-layout: fixed;
  }
}
</style>
