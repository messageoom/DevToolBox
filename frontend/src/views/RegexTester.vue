<template>
  <ToolPage :title="$t('tools.regex.title')" :icon="Key">
    <div class="tool-section">
      <!-- Pattern + presets -->
      <div class="config-row">
        <div class="config-item config-item--pattern">
          <div class="field-label">{{ $t('tools.regex.labels.pattern') }}</div>
          <el-input
            v-model="pattern"
            :placeholder="$t('tools.regex.placeholders.pattern')"
            clearable
          >
            <template #prepend>
              <span class="slash">/</span>
            </template>
            <template #append>
              <span class="slash">/{{ flags }}</span>
            </template>
          </el-input>
        </div>
        <div class="config-item">
          <div class="field-label">{{ $t('tools.regex.labels.presets') }}</div>
          <el-select
            v-model="selectedPreset"
            :placeholder="$t('tools.regex.placeholders.presets')"
            style="width: 100%;"
            clearable
            @change="applyPreset"
          >
            <el-option
              v-for="p in presetList"
              :key="p.key"
              :label="$t('tools.regex.presets.' + p.key)"
              :value="p.key"
            />
          </el-select>
        </div>
      </div>

      <!-- Flags -->
      <div class="flags-row">
        <div class="field-label">{{ $t('tools.regex.labels.flags') }}</div>
        <div class="flags">
          <el-checkbox v-model="flagG" border size="small">g</el-checkbox>
          <el-checkbox v-model="flagI" border size="small">i</el-checkbox>
          <el-checkbox v-model="flagM" border size="small">m</el-checkbox>
          <el-checkbox v-model="flagS" border size="small">s</el-checkbox>
          <el-checkbox v-model="flagU" border size="small">u</el-checkbox>
          <el-checkbox v-model="flagY" border size="small">y</el-checkbox>
        </div>
      </div>

      <!-- Error -->
      <el-alert
        v-if="error"
        :title="error"
        type="error"
        show-icon
        :closable="false"
        style="margin-top: 12px;"
      />

      <!-- Test string -->
      <div class="input-section">
        <h4 class="section-title">{{ $t('tools.regex.labels.testString') }}</h4>
        <el-input
          v-model="testString"
          type="textarea"
          :rows="6"
          :placeholder="$t('tools.regex.placeholders.testString')"
          resize="vertical"
        />
      </div>

      <!-- Output -->
      <div class="output-section" v-if="!error && testString">
        <div class="result-header">
          <h4 class="section-title">
            {{ $t('tools.regex.labels.matchCount', { count: matches.length }) }}
          </h4>
          <el-tag v-if="matches.length === 0" type="info" size="small">
            {{ $t('tools.regex.labels.noMatches') }}
          </el-tag>
        </div>

        <!-- Highlighted render -->
        <div class="highlight-box" v-html="highlightedHtml"></div>

        <!-- Match list -->
        <div class="match-list" v-if="matches.length > 0">
          <div class="match-item" v-for="(m, index) in matches" :key="index">
            <div class="match-head">
              <span class="match-index">#{{ index + 1 }}</span>
              <span class="match-pos">
                {{ $t('tools.regex.labels.position', { start: m.index, end: m.index + m.value.length }) }}
              </span>
              <el-button link size="small" type="primary" @click="copyText(m.value)">
                <el-icon><CopyDocument /></el-icon> {{ $t('common.copy') }}
              </el-button>
            </div>
            <div class="match-value">{{ m.value || $t('tools.regex.labels.emptyMatch') }}</div>
            <!-- Capture groups -->
            <div class="groups" v-if="m.groups && m.groups.length > 0">
              <div class="group-item" v-for="g in m.groups" :key="g.n">
                <span class="group-label">{{ g.name || ('$' + g.n) }}:</span>
                <span class="group-value">{{ g.value === null ? $t('tools.regex.labels.undefined') : (g.value === '' ? $t('tools.regex.labels.empty') : g.value) }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </ToolPage>
</template>

<script>
import { ElMessage } from 'element-plus'
import { Key, CopyDocument } from '@element-plus/icons-vue'
import ToolPage from '@/components/ToolPage.vue'
import { copyToClipboard } from '@/utils/format.js'

export default {
  name: 'RegexTester',
  components: { Key, CopyDocument, ToolPage },
  data() {
    return {
      pattern: '',
      testString: '',
      selectedPreset: '',
      flagG: true,
      flagI: false,
      flagM: false,
      flagS: false,
      flagU: false,
      flagY: false,
      error: '',
      presetList: [
        { key: 'email', value: '[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}' },
        { key: 'url', value: 'https?://[^\\s]+' },
        { key: 'ipv4', value: '\\b(?:\\d{1,3}\\.){3}\\d{1,3}\\b' },
        { key: 'phone', value: '\\+?\\d[\\d\\s\\-()]{7,}\\d' },
        { key: 'date', value: '\\d{4}-\\d{2}-\\d{2}' }
      ]
    }
  },
  computed: {
    flags() {
      let f = ''
      if (this.flagG) f += 'g'
      if (this.flagI) f += 'i'
      if (this.flagM) f += 'm'
      if (this.flagS) f += 's'
      if (this.flagU) f += 'u'
      if (this.flagY) f += 'y'
      return f
    },
    compiledRegex() {
      if (!this.pattern) return null
      try {
        const re = new RegExp(this.pattern, this.flags)
        this.error = ''
        return re
      } catch (e) {
        this.error = this.$t('tools.regex.messages.invalidPattern', { error: e.message })
        return null
      }
    },
    matches() {
      const re = this.compiledRegex
      if (!re || !this.testString) return []
      const result = []
      // Re-build with global to iterate all matches; if not global, take single match.
      let working
      try {
        working = new RegExp(this.pattern, this.flags.includes('g') ? this.flags : this.flags + 'g')
      } catch (e) {
        return []
      }
      let m
      let guard = 0
      while ((m = working.exec(this.testString)) !== null) {
        const groups = []
        for (let i = 1; i < m.length; i++) {
          let name = null
          if (m.groups) {
            const keys = Object.keys(m.groups)
            // find the named key whose value/index corresponds
            const namedKey = keys.find(k => m.groups[k] === m[i] && !groups.some(g => g.name === k))
            if (namedKey) name = namedKey
          }
          groups.push({ n: i, name, value: m[i] === undefined ? null : m[i] })
        }
        result.push({
          index: m.index,
          value: m[0],
          groups
        })
        // Guard against zero-length match infinite loops
        if (m.index === working.lastIndex) working.lastIndex++
        if (++guard > 100000) break
      }
      return result
    },
    highlightedHtml() {
      const text = this.testString
      if (!text) return ''
      const matches = this.matches
      if (matches.length === 0) return this.escapeHtml(text)
      // Build ranges, escape each chunk, wrap matches in <mark>
      let html = ''
      let cursor = 0
      matches.forEach((m) => {
        const start = m.index
        const end = m.index + m.value.length
        if (start > cursor) {
          html += this.escapeHtml(text.slice(cursor, start))
        }
        html += '<mark>' + this.escapeHtml(text.slice(start, end)) + '</mark>'
        cursor = end
      })
      if (cursor < text.length) {
        html += this.escapeHtml(text.slice(cursor))
      }
      return html
    }
  },
  methods: {
    escapeHtml(str) {
      return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;')
    },
    applyPreset(key) {
      if (!key) return
      const preset = this.presetList.find(p => p.key === key)
      if (preset) {
        this.pattern = preset.value
        this.flagG = true
        this.flagI = true
      }
    },
    async copyText(text) {
      if (text === undefined || text === null || text === '') return
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
.config-row {
  display: flex;
  gap: var(--dt-spacing-md, 16px);
  margin-bottom: var(--dt-spacing-md, 16px);
  align-items: flex-end;
  flex-wrap: wrap;
}

.config-item {
  flex: 1;
  min-width: 180px;
}

.config-item--pattern {
  flex: 2;
}

.field-label {
  font-size: var(--dt-font-size-sm, 13px);
  color: var(--dt-text-secondary, #909399);
  margin-bottom: var(--dt-spacing-xs, 6px);
}

.slash {
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  color: var(--dt-text-secondary, #909399);
  font-weight: 600;
}

.flags-row {
  margin-bottom: var(--dt-spacing-md, 16px);
}

.flags {
  display: flex;
  flex-wrap: wrap;
  gap: var(--dt-spacing-sm, 8px);
}

.flags :deep(.el-checkbox.is-bordered) {
  margin-right: 0;
}

.section-title {
  font-size: var(--dt-font-size-base, 14px);
  font-weight: 600;
  color: var(--dt-text-primary, #303133);
  margin: 0 0 var(--dt-spacing-sm, 8px) 0;
}

.input-section {
  margin-top: var(--dt-spacing-sm, 8px);
}

.action-section {
  margin: var(--dt-spacing-md, 16px) 0;
}

.output-section {
  margin-top: var(--dt-spacing-lg, 20px);
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--dt-spacing-sm, 8px);
}

.highlight-box {
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: var(--dt-font-size-base, 14px);
  line-height: 1.8;
  white-space: pre-wrap;
  word-break: break-all;
  padding: var(--dt-spacing-md, 16px);
  background: var(--dt-bg-section, #f5f7fa);
  border: 1px solid var(--dt-border-light, #dcdfe6);
  border-radius: var(--dt-radius-md, 6px);
  color: var(--dt-text-primary, #303133);
  margin-bottom: var(--dt-spacing-md, 16px);
}

.highlight-box :deep(mark) {
  background: rgba(255, 213, 79, 0.6);
  color: var(--dt-text-primary, #303133);
  border-radius: 3px;
  padding: 1px 2px;
  font-weight: 600;
}

.match-list {
  display: flex;
  flex-direction: column;
  gap: var(--dt-spacing-sm, 8px);
}

.match-item {
  padding: var(--dt-spacing-sm, 8px) var(--dt-spacing-md, 12px);
  background: var(--dt-bg-section, #f5f7fa);
  border-radius: var(--dt-radius-md, 6px);
  border: 1px solid var(--dt-border-light, #dcdfe6);
  transition: background var(--dt-transition-fast, 0.2s);
}

.match-item:hover {
  background: var(--dt-bg-hover, #ecf5ff);
}

.match-head {
  display: flex;
  align-items: center;
  gap: var(--dt-spacing-sm, 8px);
  margin-bottom: var(--dt-spacing-xs, 4px);
}

.match-index {
  font-weight: 700;
  color: var(--dt-primary, #409eff);
  min-width: 32px;
}

.match-pos {
  font-size: var(--dt-font-size-xs, 12px);
  color: var(--dt-text-secondary, #909399);
  flex: 1;
}

.match-value {
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: var(--dt-font-size-base, 14px);
  color: var(--dt-text-primary, #303133);
  word-break: break-all;
  padding: var(--dt-spacing-xs, 4px) var(--dt-spacing-sm, 8px);
  background: var(--dt-bg-card, #fff);
  border-radius: var(--dt-radius-md, 6px);
  border: 1px solid var(--dt-border-lighter, #ebeef5);
}

.groups {
  margin-top: var(--dt-spacing-xs, 4px);
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.group-item {
  font-size: var(--dt-font-size-xs, 12px);
  display: flex;
  gap: var(--dt-spacing-xs, 4px);
}

.group-label {
  color: var(--dt-warning, #e6a23c);
  font-weight: 600;
  white-space: nowrap;
}

.group-value {
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  color: var(--dt-text-primary, #303133);
  word-break: break-all;
}

@media (max-width: 768px) {
  .config-row {
    flex-direction: column;
    gap: var(--dt-spacing-sm, 8px);
  }

  .config-item {
    min-width: 100%;
  }

  .output-section {
    padding: var(--dt-spacing-md, 16px);
    background: var(--dt-bg-section, #f5f7fa);
    border-radius: var(--dt-radius-lg, 12px);
    border: 1px solid var(--dt-border-lighter, #ebeef5);
  }
}
</style>
