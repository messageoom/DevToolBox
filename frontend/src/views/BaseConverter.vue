<template>
  <ToolPage :title="$t('tools.base.title')" :icon="Histogram">
    <div class="tool-section">
      <!-- 输入区 -->
      <div class="config-row">
        <div class="config-item config-item--input">
          <div class="field-label">{{ $t('tools.base.labels.value') }}</div>
          <el-input
            v-model="inputValue"
            :placeholder="$t('tools.base.placeholders.input')"
            clearable
            @keyup.enter="convert"
          />
        </div>
        <div class="config-item">
          <div class="field-label">{{ $t('tools.base.labels.fromBase') }}</div>
          <el-select v-model="fromBase" style="width: 100%;">
            <el-option :label="$t('tools.base.labels.binary') + ' (2)'" :value="2" />
            <el-option :label="$t('tools.base.labels.octal') + ' (8)'" :value="8" />
            <el-option :label="$t('tools.base.labels.decimal') + ' (10)'" :value="10" />
            <el-option :label="$t('tools.base.labels.hex') + ' (16)'" :value="16" />
            <el-option :label="$t('tools.base.labels.custom')" :value="'custom'" />
          </el-select>
        </div>
        <div class="config-item" v-if="fromBase === 'custom'">
          <div class="field-label">{{ $t('tools.base.labels.customBase') }}</div>
          <el-input-number
            v-model="customBase"
            :min="2"
            :max="36"
            style="width: 100%;"
          />
        </div>
        <div class="config-item config-switch">
          <div class="field-label">{{ $t('tools.base.labels.groupBits') }}</div>
          <el-switch v-model="groupBits" />
        </div>
      </div>

      <div class="action-section">
        <el-button type="primary" @click="convert">
          {{ $t('common.convert') }}
        </el-button>
        <el-button plain @click="reset">
          {{ $t('common.reset') }}
        </el-button>
      </div>

      <!-- 输出区 -->
      <div class="output-section" v-if="hasResult">
        <h4 class="section-title">{{ $t('tools.base.labels.results') }}</h4>
        <div class="output-list">
          <div v-for="item in outputItems" :key="item.key" class="output-item">
            <div class="output-label">{{ item.label }}</div>
            <el-input
              :model-value="item.value"
              readonly
              class="output-field"
            >
              <template #append>
                <el-button :icon="CopyDocument" @click="copyValue(item.value)" />
              </template>
            </el-input>
          </div>
        </div>

        <!-- 二进制位分组展示 -->
        <div class="bit-section" v-if="results.binary">
          <h4 class="section-title">{{ $t('tools.base.labels.binaryView') }}</h4>
          <div class="bit-box" :class="{ 'bit-box--grouped': groupBits }">
            {{ groupedBinary }}
          </div>
        </div>
      </div>

      <div v-else class="empty-section">
        <el-empty :description="$t('tools.base.labels.emptyHint')" :image-size="80" />
      </div>
    </div>
  </ToolPage>
</template>

<script>
import { ElMessage } from 'element-plus'
import { Histogram, CopyDocument } from '@element-plus/icons-vue'
import ToolPage from '@/components/ToolPage.vue'
import { copyToClipboard } from '@/utils/format.js'

export default {
  name: 'BaseConverter',
  components: {
    Histogram,
    CopyDocument,
    ToolPage
  },
  data() {
    return {
      inputValue: '',
      fromBase: 10,
      customBase: 36,
      groupBits: true,
      results: null
    }
  },
  computed: {
    effectiveBase() {
      return this.fromBase === 'custom' ? this.customBase : this.fromBase
    },

    hasResult() {
      return this.results !== null
    },

    outputItems() {
      if (!this.results) return []
      return [
        { key: 'binary', label: this.$t('tools.base.labels.binary') + ' (2)', value: this.results.binary },
        { key: 'octal', label: this.$t('tools.base.labels.octal') + ' (8)', value: this.results.octal },
        { key: 'decimal', label: this.$t('tools.base.labels.decimal') + ' (10)', value: this.results.decimal },
        { key: 'hex', label: this.$t('tools.base.labels.hex') + ' (16)', value: this.results.hex }
      ]
    },

    groupedBinary() {
      const bin = this.results?.binary
      if (!bin) return ''
      if (!this.groupBits) return bin
      // 从右往左每 4 位分组
      const neg = bin.startsWith('-')
      let digits = neg ? bin.slice(1) : bin
      const padded = digits.padStart(Math.ceil(digits.length / 4) * 4, '0')
      const grouped = padded.match(/.{1,4}/g).join(' ')
      return (neg ? '-' : '') + grouped
    }
  },
  methods: {
    convert() {
      const raw = this.inputValue.trim()
      if (!raw) {
        ElMessage.warning(this.$t('tools.base.messages.inputRequired'))
        return
      }

      const base = this.effectiveBase
      if (base < 2 || base > 36) {
        ElMessage.warning(this.$t('tools.base.messages.invalidBase'))
        return
      }

      const negative = raw.startsWith('-')
      const unsigned = negative ? raw.slice(1) : raw

      // 校验字符对当前进制合法
      const validRe = this.charsetRegex(base)
      if (!validRe.test(unsigned)) {
        ElMessage.warning(this.$t('tools.base.messages.invalidInput'))
        return
      }

      let big
      try {
        // BigInt 不支持任意进制，需自行实现解析
        big = this.parseBigInt(unsigned, base)
      } catch (e) {
        ElMessage.warning(this.$t('tools.base.messages.invalidInput'))
        return
      }

      const sign = negative ? '-' : ''
      this.results = {
        binary: sign + this.toBase(big, 2),
        octal: sign + this.toBase(big, 8),
        decimal: sign + big.toString(10),
        hex: sign + this.toBase(big, 16).toUpperCase()
      }
      ElMessage.success(this.$t('tools.base.messages.convertSuccess'))
    },

    charsetRegex(base) {
      // 构造 0-9, a-z (大小写不敏感) 到指定进制的合法字符集
      const digits = '0123456789abcdefghijklmnopqrstuvwxyz'.slice(0, base)
      const escaped = digits.replace(/[-\\^]/g, '\\$&')
      return new RegExp(`^[${escaped}]+$`, 'i')
    },

    // 将任意进制字符串解析为 BigInt
    parseBigInt(str, base) {
      const digits = '0123456789abcdefghijklmnopqrstuvwxyz'
      let result = 0n
      const b = BigInt(base)
      for (const ch of str.toLowerCase()) {
        const v = digits.indexOf(ch)
        if (v < 0 || v >= base) throw new Error('invalid digit')
        result = result * b + BigInt(v)
      }
      return result
    },

    // 将 BigInt 转为任意进制字符串（2..36）
    toBase(big, base) {
      if (big === 0n) return '0'
      const digits = '0123456789abcdefghijklmnopqrstuvwxyz'
      const b = BigInt(base)
      let n = big
      let out = ''
      while (n > 0n) {
        out = digits[Number(n % b)] + out
        n = n / b
      }
      return out
    },

    reset() {
      this.inputValue = ''
      this.results = null
      this.fromBase = 10
      this.customBase = 36
    },

    async copyValue(text) {
      if (!text) {
        ElMessage.warning(this.$t('tools.base.messages.nothingToCopy'))
        return
      }
      try {
        await copyToClipboard(text)
        ElMessage.success(this.$t('common.copySuccess'))
      } catch {
        ElMessage.error(this.$t('common.copyFail'))
      }
    }
  }
}
</script>

<style scoped>
.tool-section {
  display: flex;
  flex-direction: column;
  gap: var(--dt-spacing-md, 16px);
}

.config-row {
  display: flex;
  gap: var(--dt-spacing-md, 16px);
  align-items: flex-end;
  flex-wrap: wrap;
}

.config-item {
  flex: 1;
  min-width: 140px;
}

.config-item--input {
  flex: 2;
  min-width: 200px;
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
  margin-bottom: var(--dt-spacing-xs, 6px);
}

.action-section {
  display: flex;
  gap: var(--dt-spacing-sm, 8px);
}

.output-section {
  margin-top: var(--dt-spacing-sm, 8px);
}

.section-title {
  font-size: var(--dt-font-size-base, 14px);
  font-weight: 600;
  color: var(--dt-text-primary, #303133);
  margin: 0 0 var(--dt-spacing-sm, 8px) 0;
}

.output-list {
  display: flex;
  flex-direction: column;
  gap: var(--dt-spacing-sm, 8px);
}

.output-item {
  display: flex;
  flex-direction: column;
  gap: var(--dt-spacing-xs, 6px);
}

.output-label {
  font-size: var(--dt-font-size-sm, 13px);
  color: var(--dt-text-secondary, #909399);
  font-weight: 500;
}

:deep(.output-field .el-input__inner) {
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: var(--dt-font-size-base, 14px);
  color: var(--dt-text-primary, #303133);
}

.bit-section {
  margin-top: var(--dt-spacing-md, 16px);
}

.bit-box {
  padding: var(--dt-spacing-md, 12px) var(--dt-spacing-lg, 16px);
  background: var(--dt-bg-section, #f5f7fa);
  border: 1px solid var(--dt-border-lighter, #ebeef5);
  border-radius: var(--dt-radius-md, 6px);
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: var(--dt-font-size-base, 14px);
  color: var(--dt-text-primary, #303133);
  word-break: break-all;
  line-height: 1.6;
}

.empty-section {
  padding: var(--dt-spacing-lg, 24px) 0;
}

@media (max-width: 768px) {
  .config-row {
    flex-direction: column;
    align-items: stretch;
  }

  .config-item,
  .config-item--input {
    min-width: 100%;
  }

  .action-section .el-button {
    flex: 1;
  }
}
</style>
