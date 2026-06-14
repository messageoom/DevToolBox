<template>
  <ToolPage :title="$t('tools.sql.title')" :icon="Grid">
    <div class="tool-section">
      <!-- Options -->
      <div class="config-row">
        <div class="config-item">
          <div class="field-label">{{ $t('tools.sql.labels.dialect') }}</div>
          <el-select v-model="dialect" style="width: 100%;">
            <el-option
              v-for="d in dialects"
              :key="d.value"
              :label="d.label"
              :value="d.value"
            />
          </el-select>
        </div>
        <div class="config-item">
          <div class="field-label">{{ $t('tools.sql.labels.keywordCase') }}</div>
          <el-select v-model="keywordCase" style="width: 100%;">
            <el-option :label="$t('tools.sql.options.upper')" value="upper" />
            <el-option :label="$t('tools.sql.options.lower')" value="lower" />
            <el-option :label="$t('tools.sql.options.preserve')" value="preserve" />
          </el-select>
        </div>
        <div class="config-item">
          <div class="field-label">{{ $t('tools.sql.labels.indent') }}</div>
          <el-select v-model="indent" style="width: 100%;">
            <el-option label="2" value="2" />
            <el-option label="4" value="4" />
            <el-option label="Tab" value="tab" />
          </el-select>
        </div>
        <div class="config-item config-switch">
          <div class="field-label">{{ $t('tools.sql.labels.minify') }}</div>
          <el-switch v-model="minify" />
        </div>
      </div>

      <!-- Input -->
      <div class="input-section">
        <h4 class="section-title">{{ $t('tools.sql.labels.input') }}</h4>
        <el-input
          v-model="inputSql"
          type="textarea"
          :rows="8"
          :placeholder="$t('tools.sql.placeholder.input')"
          spellcheck="false"
        />
        <div class="field-toolbar" v-if="inputSql">
          <span class="field-stats">
            {{ inputSql.length }} {{ $t('tools.sql.stats.chars') }}
          </span>
          <div class="toolbar-actions">
            <el-button link size="small" @click="loadSample">{{ $t('tools.sql.action.sample') }}</el-button>
            <el-button link size="small" @click="inputSql = ''; outputSql = ''">{{ $t('common.clear') }}</el-button>
          </div>
        </div>
      </div>

      <!-- Actions -->
      <div class="action-section">
        <el-button type="primary" @click="formatSql" :loading="formatting">
          {{ minify ? $t('common.minify') : $t('common.format') }}
        </el-button>
      </div>

      <!-- Output -->
      <div class="output-section" v-if="outputSql">
        <div class="result-header">
          <h4 class="section-title">{{ $t('tools.sql.labels.output') }}</h4>
          <el-button size="small" type="primary" plain @click="copyOutput">
            <el-icon><CopyDocument /></el-icon>
            {{ $t('tools.sql.action.copy') }}
          </el-button>
        </div>
        <el-input
          v-model="outputSql"
          type="textarea"
          :rows="10"
          readonly
          spellcheck="false"
        />
        <div class="field-toolbar">
          <span class="field-stats">
            {{ outputSql.length }} {{ $t('tools.sql.stats.chars') }}
          </span>
        </div>
      </div>
    </div>
  </ToolPage>
</template>

<script>
import { ElMessage } from 'element-plus'
import { Grid, CopyDocument } from '@element-plus/icons-vue'
import ToolPage from '@/components/ToolPage.vue'
import { copyToClipboard } from '@/utils/format.js'
import { format } from 'sql-formatter'

export default {
  name: 'SqlFormatter',
  components: { Grid, CopyDocument, ToolPage },
  data() {
    return {
      inputSql: '',
      outputSql: '',
      dialect: 'sql',
      keywordCase: 'upper',
      indent: '2',
      minify: false,
      formatting: false
    }
  },
  computed: {
    dialects() {
      return [
        { value: 'sql', label: this.$t('tools.sql.dialects.standard') },
        { value: 'mysql', label: this.$t('tools.sql.dialects.mysql') },
        { value: 'postgresql', label: this.$t('tools.sql.dialects.postgresql') },
        { value: 'sqlite', label: this.$t('tools.sql.dialects.sqlite') },
        { value: 'tsql', label: this.$t('tools.sql.dialects.tsql') },
        { value: 'mariadb', label: this.$t('tools.sql.dialects.mariadb') },
        { value: 'bigquery', label: this.$t('tools.sql.dialects.bigquery') }
      ]
    }
  },
  methods: {
    loadSample() {
      this.inputSql =
        "SELECT u.id, u.name, COUNT(o.id) AS order_count " +
        "FROM users u LEFT JOIN orders o ON u.id = o.user_id " +
        "WHERE u.status = 'active' AND u.created_at > '2024-01-01' " +
        "GROUP BY u.id, u.name HAVING COUNT(o.id) > 5 ORDER BY order_count DESC;"
    },

    formatSql() {
      const sql = this.inputSql.trim()
      if (!sql) {
        ElMessage.warning(this.$t('tools.sql.messages.inputRequired'))
        return
      }

      this.formatting = true
      try {
        if (this.minify) {
          // Strip extra whitespace for a minified single-line result
          const formatted = format(sql, {
            language: this.dialect,
            keywordCase: this.keywordCase
          })
          this.outputSql = formatted
            .replace(/\s+/g, ' ')
            .replace(/\s*,\s*/g, ', ')
            .replace(/\(\s+/g, '(')
            .replace(/\s+\)/g, ')')
            .trim()
        } else {
          const tabWidth = this.indent === 'tab' ? 1 : parseInt(this.indent, 10)
          const useTabs = this.indent === 'tab'
          this.outputSql = format(sql, {
            language: this.dialect,
            keywordCase: this.keywordCase,
            tabWidth,
            useTabs
          })
        }
        ElMessage.success(this.$t('tools.sql.messages.formatSuccess'))
      } catch (e) {
        ElMessage.warning(this.$t('tools.sql.messages.formatFail'))
      } finally {
        this.formatting = false
      }
    },

    async copyOutput() {
      if (!this.outputSql) return
      try {
        await copyToClipboard(this.outputSql)
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

.config-row {
  display: flex;
  gap: var(--dt-spacing-md);
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
  min-width: 90px;
}

.field-label {
  font-size: var(--dt-font-size-sm);
  color: var(--dt-text-secondary);
  margin-bottom: var(--dt-spacing-xs);
}

.section-title {
  font-size: var(--dt-font-size-base);
  font-weight: 600;
  color: var(--dt-text-primary);
  margin: 0 0 var(--dt-spacing-sm) 0;
}

.input-section,
.output-section {
  display: flex;
  flex-direction: column;
}

.field-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: var(--dt-spacing-xs);
}

.field-stats {
  font-size: var(--dt-font-size-xs);
  color: var(--dt-text-secondary);
}

.toolbar-actions {
  display: flex;
  gap: var(--dt-spacing-xs);
}

.action-section {
  display: flex;
  gap: var(--dt-spacing-sm);
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--dt-spacing-sm);
  gap: var(--dt-spacing-sm);
}

.output-section {
  padding: var(--dt-spacing-md);
  background: var(--dt-bg-section);
  border: 1px solid var(--dt-border-light);
  border-radius: var(--dt-radius-md);
}

:deep(.el-textarea__inner) {
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: var(--dt-font-size-base);
}

@media (max-width: 768px) {
  .config-row {
    flex-direction: column;
    gap: var(--dt-spacing-sm);
  }

  .config-item,
  .config-switch {
    min-width: 100%;
    width: 100%;
  }

  .config-switch {
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
  }

  .action-section .el-button {
    flex: 1;
  }
}
</style>
