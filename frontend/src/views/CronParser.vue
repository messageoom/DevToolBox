<template>
  <ToolPage :title="$t('tools.cron.title')" :icon="Timer">
    <div class="tool-section">
      <!-- Expression input -->
      <div class="input-section">
        <h4 class="section-title">{{ $t('tools.cron.labels.expression') }}</h4>
        <el-input
          v-model="expression"
          :placeholder="$t('tools.cron.placeholder.expression')"
          clearable
          spellcheck="false"
          @keyup.enter="parse"
        >
          <template #append>
            <el-button @click="parse" :loading="parsing">
              {{ $t('tools.cron.action.parse') }}
            </el-button>
          </template>
        </el-input>

        <!-- Field hints -->
        <div class="field-hint">
          <span class="field-cell"><b>{{ $t('tools.cron.fields.minute') }}</b></span>
          <span class="field-cell"><b>{{ $t('tools.cron.fields.hour') }}</b></span>
          <span class="field-cell"><b>{{ $t('tools.cron.fields.day') }}</b></span>
          <span class="field-cell"><b>{{ $t('tools.cron.fields.month') }}</b></span>
          <span class="field-cell"><b>{{ $t('tools.cron.fields.weekday') }}</b></span>
        </div>
      </div>

      <!-- Presets -->
      <div class="presets-row">
        <span class="field-label">{{ $t('tools.cron.labels.presets') }}</span>
        <div class="preset-buttons">
          <el-button
            v-for="p in presets"
            :key="p.value"
            size="small"
            plain
            @click="applyPreset(p.value)"
          >
            {{ p.label }}
          </el-button>
        </div>
      </div>

      <!-- Description -->
      <div class="output-section" v-if="description">
        <div class="result-header">
          <h4 class="section-title">{{ $t('tools.cron.labels.description') }}</h4>
          <el-button size="small" type="primary" plain @click="copyDescription">
            <el-icon><CopyDocument /></el-icon>
            {{ $t('tools.cron.action.copyDescription') }}
          </el-button>
        </div>
        <div class="description-box">{{ description }}</div>
      </div>

      <!-- Next runs -->
      <div class="output-section" v-if="nextRuns.length > 0">
        <div class="result-header">
          <h4 class="section-title">{{ $t('tools.cron.labels.nextRuns') }} ({{ nextRuns.length }})</h4>
        </div>
        <div class="run-list">
          <div class="run-item" v-for="(run, index) in nextRuns" :key="index">
            <span class="run-index">#{{ index + 1 }}</span>
            <span class="run-text">{{ run }}</span>
            <el-button size="small" text @click="copyText(run)">
              <el-icon><CopyDocument /></el-icon>
            </el-button>
          </div>
        </div>
      </div>
    </div>
  </ToolPage>
</template>

<script>
import { ElMessage } from 'element-plus'
import { Timer, CopyDocument } from '@element-plus/icons-vue'
import ToolPage from '@/components/ToolPage.vue'
import { copyToClipboard } from '@/utils/format.js'
import cronstrue from 'cronstrue'
import { CronExpressionParser } from 'cron-parser'

export default {
  name: 'CronParser',
  components: { Timer, CopyDocument, ToolPage },
  data() {
    return {
      expression: '*/5 * * * *',
      description: '',
      nextRuns: [],
      parsing: false
    }
  },
  computed: {
    presets() {
      return [
        { value: '* * * * *', label: this.$t('tools.cron.presets.everyMinute') },
        { value: '0 * * * *', label: this.$t('tools.cron.presets.hourly') },
        { value: '0 0 * * *', label: this.$t('tools.cron.presets.dailyMidnight') },
        { value: '0 0 * * 1-5', label: this.$t('tools.cron.presets.weekdays') },
        { value: '0 0 * * 0', label: this.$t('tools.cron.presets.weeklySunday') },
        { value: '0 0 1 * *', label: this.$t('tools.cron.presets.monthlyFirst') }
      ]
    }
  },
  mounted() {
    this.parse()
  },
  methods: {
    applyPreset(value) {
      this.expression = value
      this.parse()
    },

    parse() {
      const expr = this.expression.trim()
      if (!expr) {
        ElMessage.warning(this.$t('tools.cron.messages.expressionRequired'))
        return
      }

      this.parsing = true
      try {
        // Human-readable description via cronstrue
        this.description = cronstrue.toString(expr, { use24HourTimeFormat: true })

        // Next N runs via cron-parser
        const interval = CronExpressionParser.parse(expr, { currentDate: new Date() })
        const runs = []
        for (let i = 0; i < 5; i++) {
          runs.push(this.formatDate(interval.next().toDate()))
        }
        this.nextRuns = runs

        ElMessage.success(this.$t('tools.cron.messages.parseSuccess'))
      } catch (e) {
        this.description = ''
        this.nextRuns = []
        ElMessage.warning(this.$t('tools.cron.messages.invalidExpression'))
      } finally {
        this.parsing = false
      }
    },

    formatDate(date) {
      const pad = (n) => String(n).padStart(2, '0')
      const y = date.getFullYear()
      const mo = pad(date.getMonth() + 1)
      const d = pad(date.getDate())
      const h = pad(date.getHours())
      const mi = pad(date.getMinutes())
      const s = pad(date.getSeconds())
      return `${y}-${mo}-${d} ${h}:${mi}:${s}`
    },

    async copyDescription() {
      if (!this.description) return
      await this.copyText(this.description)
    },

    async copyText(text) {
      if (!text) return
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
  gap: var(--dt-spacing-md);
}

.section-title {
  font-size: var(--dt-font-size-base);
  font-weight: 600;
  color: var(--dt-text-primary);
  margin: 0 0 var(--dt-spacing-sm) 0;
}

.field-label {
  font-size: var(--dt-font-size-sm);
  color: var(--dt-text-secondary);
  margin-right: var(--dt-spacing-sm);
}

.field-hint {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: var(--dt-spacing-xs);
  margin-top: var(--dt-spacing-sm);
}

.field-cell {
  text-align: center;
  font-size: var(--dt-font-size-xs);
  color: var(--dt-text-secondary);
  padding: var(--dt-spacing-xs) 0;
  background: var(--dt-bg-section);
  border: 1px solid var(--dt-border-light);
  border-radius: var(--dt-radius-md);
}

.presets-row {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: var(--dt-spacing-sm);
}

.preset-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: var(--dt-spacing-xs);
}

.output-section {
  padding: var(--dt-spacing-md);
  background: var(--dt-bg-section);
  border: 1px solid var(--dt-border-light);
  border-radius: var(--dt-radius-md);
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--dt-spacing-sm);
  gap: var(--dt-spacing-sm);
}

.description-box {
  font-size: var(--dt-font-size-base);
  color: var(--dt-text-primary);
  background: var(--dt-bg-card);
  padding: var(--dt-spacing-sm) var(--dt-spacing-md);
  border-radius: var(--dt-radius-md);
  border: 1px solid var(--dt-border-light);
  line-height: 1.6;
}

.run-list {
  display: flex;
  flex-direction: column;
  gap: var(--dt-spacing-xs);
}

.run-item {
  display: flex;
  align-items: center;
  gap: var(--dt-spacing-sm);
  padding: var(--dt-spacing-xs) var(--dt-spacing-sm);
  background: var(--dt-bg-card);
  border: 1px solid var(--dt-border-light);
  border-radius: var(--dt-radius-md);
  transition: background var(--dt-transition-fast);
}

.run-item:hover {
  background: var(--dt-bg-hover, var(--dt-bg-card));
}

.run-index {
  font-size: var(--dt-font-size-sm);
  font-weight: 600;
  color: var(--dt-primary);
  min-width: 32px;
}

.run-text {
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: var(--dt-font-size-base);
  color: var(--dt-text-primary);
  flex: 1;
}

@media (max-width: 768px) {
  .field-hint {
    gap: 4px;
  }

  .field-cell {
    font-size: 10px;
    padding: 4px 2px;
  }

  .presets-row {
    flex-direction: column;
    align-items: flex-start;
  }

  .preset-buttons .el-button {
    flex: 1;
  }
}
</style>
