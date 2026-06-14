<template>
  <ToolPage :title="$t('tools.case.title')" :icon="EditPen">
    <div class="tool-section">
      <!-- 输入区 -->
      <div class="input-section">
        <h4 class="section-title">{{ $t('tools.case.labels.input') }}</h4>
        <el-input
          v-model="input"
          type="textarea"
          :rows="4"
          :placeholder="$t('tools.case.placeholders.input')"
          clearable
          resize="vertical"
        />
      </div>

      <!-- 当前 case 检测提示 -->
      <div v-if="input.trim()" class="detect-hint">
        <el-icon class="detect-icon"><InfoFilled /></el-icon>
        <span>{{ $t('tools.case.labels.detected') }}: <strong>{{ detectedCaseLabel }}</strong></span>
      </div>

      <!-- 转换结果区 -->
      <div class="output-section" v-if="input.trim()">
        <div class="result-header">
          <h4 class="section-title">{{ $t('tools.case.labels.results') }}</h4>
          <el-button size="small" type="primary" plain @click="copyAll">
            {{ $t('tools.case.labels.copyAll') }}
          </el-button>
        </div>

        <div class="result-grid">
          <div
            v-for="item in resultItems"
            :key="item.key"
            class="result-item"
            :title="$t('tools.case.labels.clickToCopy')"
          >
            <div class="result-label">{{ item.label }}</div>
            <div class="result-value" @click="copyValue(item.value)">
              <span class="result-text">{{ item.value || $t('tools.case.labels.empty') }}</span>
              <el-icon class="copy-icon"><CopyDocument /></el-icon>
            </div>
          </div>
        </div>
      </div>

      <!-- 空输入占位 -->
      <div v-else class="empty-section">
        <el-empty :description="$t('tools.case.labels.emptyHint')" :image-size="80" />
      </div>
    </div>
  </ToolPage>
</template>

<script>
import { ElMessage } from 'element-plus'
import { EditPen, CopyDocument, InfoFilled } from '@element-plus/icons-vue'
import ToolPage from '@/components/ToolPage.vue'
import { copyToClipboard } from '@/utils/format.js'

export default {
  name: 'CaseConverter',
  components: {
    EditPen,
    CopyDocument,
    InfoFilled,
    ToolPage
  },
  data() {
    return {
      input: ''
    }
  },
  computed: {
    // 预处理：按分隔符拆成单词数组
    words() {
      const raw = this.input.trim()
      if (!raw) return []

      // 优先按非字母数字字符分割
      let parts = raw.split(/[^a-zA-Z0-9]+/).filter(Boolean)
      // 如果整体没有分隔符（如 camelCase），按大小写边界再拆
      if (parts.length <= 1) {
        parts = raw
          .replace(/([a-z0-9])([A-Z])/g, '$1 $2')
          .replace(/([A-Z]+)([A-Z][a-z])/g, '$1 $2')
          .split(/[^a-zA-Z0-9]+/)
          .filter(Boolean)
      }
      return parts.map((p) => p.toLowerCase())
    },

    converted() {
      const w = this.words
      if (!w.length) {
        return {
          camel: '',
          pascal: '',
          snake: '',
          kebab: '',
          constant: '',
          lower: '',
          title: '',
          sentence: ''
        }
      }
      const cap = (s) => s.charAt(0).toUpperCase() + s.slice(1)
      return {
        camel: w.map((p, i) => (i === 0 ? p : cap(p))).join(''),
        pascal: w.map(cap).join(''),
        snake: w.join('_'),
        kebab: w.join('-'),
        constant: w.map((p) => p.toUpperCase()).join('_'),
        lower: w.join(' ').toLowerCase(),
        title: w.map(cap).join(' '),
        sentence: cap(w.join(' '))
      }
    },

    resultItems() {
      return [
        { key: 'camel', label: this.$t('tools.case.labels.camel'), value: this.converted.camel },
        { key: 'pascal', label: this.$t('tools.case.labels.pascal'), value: this.converted.pascal },
        { key: 'snake', label: this.$t('tools.case.labels.snake'), value: this.converted.snake },
        { key: 'kebab', label: this.$t('tools.case.labels.kebab'), value: this.converted.kebab },
        { key: 'constant', label: this.$t('tools.case.labels.constant'), value: this.converted.constant },
        { key: 'lower', label: this.$t('tools.case.labels.lower'), value: this.converted.lower },
        { key: 'title', label: this.$t('tools.case.labels.title'), value: this.converted.title },
        { key: 'sentence', label: this.$t('tools.case.labels.sentence'), value: this.converted.sentence }
      ]
    },

    detectedCase() {
      return this.detectCase(this.input.trim())
    },

    detectedCaseLabel() {
      const key = this.detectedCase
      if (!key) return this.$t('tools.case.labels.unknownCase')
      const map = {
        camel: this.$t('tools.case.labels.camel'),
        pascal: this.$t('tools.case.labels.pascal'),
        snake: this.$t('tools.case.labels.snake'),
        kebab: this.$t('tools.case.labels.kebab'),
        constant: this.$t('tools.case.labels.constant'),
        title: this.$t('tools.case.labels.title'),
        sentence: this.$t('tools.case.labels.sentence'),
        lower: this.$t('tools.case.labels.lower')
      }
      return map[key] || this.$t('tools.case.labels.unknownCase')
    }
  },
  methods: {
    detectCase(str) {
      if (!str) return ''
      if (/^[A-Z0-9_]+$/.test(str) && str.includes('_')) return 'constant'
      if (str.includes('_')) return 'snake'
      if (str.includes('-')) return 'kebab'
      if (/^[A-Z][a-zA-Z0-9]*$/.test(str)) return 'pascal'
      if (/[a-z][A-Z]/.test(str)) return 'camel'
      if (/^[a-z0-9 ]+$/.test(str)) {
        const words = str.split(/\s+/)
        if (words.length > 1 && words.every((w) => /^[A-Z]/.test(w))) return 'title'
        if (words.length > 1 && /^[A-Z]/.test(words[0]) && words.slice(1).every((w) => /^[a-z]/.test(w))) return 'sentence'
        return 'lower'
      }
      return ''
    },

    async copyValue(text) {
      if (!text) {
        ElMessage.warning(this.$t('tools.case.messages.nothingToCopy'))
        return
      }
      try {
        await copyToClipboard(text)
        ElMessage.success(this.$t('common.copySuccess'))
      } catch {
        ElMessage.error(this.$t('common.copyFail'))
      }
    },

    async copyAll() {
      const lines = this.resultItems
        .filter((it) => it.value)
        .map((it) => `${it.label}: ${it.value}`)
        .join('\n')
      if (!lines) {
        ElMessage.warning(this.$t('tools.case.messages.nothingToCopy'))
        return
      }
      try {
        await copyToClipboard(lines)
        ElMessage.success(this.$t('tools.case.messages.copiedAll'))
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

.input-section {
  display: flex;
  flex-direction: column;
}

.section-title {
  font-size: var(--dt-font-size-base, 14px);
  font-weight: 600;
  color: var(--dt-text-primary, #303133);
  margin: 0 0 var(--dt-spacing-sm, 8px) 0;
}

.detect-hint {
  display: flex;
  align-items: center;
  gap: var(--dt-spacing-xs, 6px);
  font-size: var(--dt-font-size-sm, 13px);
  color: var(--dt-text-secondary, #909399);
  padding: var(--dt-spacing-sm, 8px) var(--dt-spacing-md, 16px);
  background: var(--dt-bg-section, #f5f7fa);
  border: 1px solid var(--dt-border-lighter, #ebeef5);
  border-radius: var(--dt-radius-md, 6px);
}

.detect-icon {
  color: var(--dt-primary, #409eff);
  flex-shrink: 0;
}

.detect-hint strong {
  color: var(--dt-text-primary, #303133);
  font-weight: 600;
}

.output-section {
  margin-top: var(--dt-spacing-sm, 8px);
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--dt-spacing-sm, 8px);
}

.result-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--dt-spacing-md, 16px);
}

.result-item {
  display: flex;
  flex-direction: column;
  gap: var(--dt-spacing-xs, 6px);
}

.result-label {
  font-size: var(--dt-font-size-sm, 13px);
  color: var(--dt-text-secondary, #909399);
  font-weight: 500;
}

.result-value {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: var(--dt-spacing-sm, 8px);
  padding: var(--dt-spacing-sm, 8px) var(--dt-spacing-md, 12px);
  background: var(--dt-bg-section, #f5f7fa);
  border: 1px solid var(--dt-border-light, #dcdfe6);
  border-radius: var(--dt-radius-md, 6px);
  cursor: pointer;
  transition: all var(--dt-transition-fast, 0.2s);
}

.result-value:hover {
  border-color: var(--dt-primary, #409eff);
  background: var(--dt-bg-hover, #ecf5ff);
}

.result-text {
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: var(--dt-font-size-base, 14px);
  color: var(--dt-text-primary, #303133);
  word-break: break-all;
  flex: 1;
}

.copy-icon {
  color: var(--dt-text-secondary, #909399);
  flex-shrink: 0;
  transition: color var(--dt-transition-fast, 0.2s);
}

.result-value:hover .copy-icon {
  color: var(--dt-primary, #409eff);
}

.empty-section {
  padding: var(--dt-spacing-lg, 24px) 0;
}

@media (max-width: 768px) {
  .result-grid {
    grid-template-columns: 1fr;
  }
}
</style>
