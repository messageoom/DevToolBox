<template>
  <ToolPage :title="$t('tools.dummy.title')" :icon="DataLine">
    <div class="tool-section">
      <!-- 字段类型选择 -->
      <div class="input-section">
        <h4 class="section-title">{{ $t('tools.dummy.labels.fieldTypes') }}</h4>
        <el-checkbox-group v-model="selectedFields" class="field-checkbox-group">
          <el-checkbox
            v-for="opt in fieldOptions"
            :key="opt"
            :label="opt"
            :value="opt"
          >
            {{ $t('tools.dummy.fields.' + opt) }}
          </el-checkbox>
        </el-checkbox-group>
      </div>

      <!-- 配置行 -->
      <div class="config-row">
        <div class="config-item">
          <div class="field-label">{{ $t('tools.dummy.labels.count') }}</div>
          <el-input-number
            v-model="count"
            :min="1"
            :max="100"
            style="width: 100%;"
          />
        </div>
        <div class="config-item">
          <div class="field-label">{{ $t('tools.dummy.labels.format') }}</div>
          <el-select v-model="format" style="width: 100%;">
            <el-option :label="$t('tools.dummy.labels.jsonArray')" value="json" />
            <el-option :label="$t('tools.dummy.labels.onePerLine')" value="lines" />
          </el-select>
        </div>
      </div>

      <div class="action-section">
        <el-button type="primary" @click="generate" :disabled="!canGenerate">
          {{ $t('common.generate') }}
        </el-button>
        <el-button plain @click="reset">
          {{ $t('common.reset') }}
        </el-button>
      </div>

      <!-- 输出区 -->
      <div class="output-section" v-if="output">
        <div class="result-header">
          <h4 class="section-title">
            {{ $t('tools.dummy.labels.result') }}
            <span class="result-count">({{ generatedRecords.length }})</span>
          </h4>
          <el-button size="small" type="primary" plain @click="copyAll">
            {{ $t('tools.dummy.labels.copyAll') }}
          </el-button>
        </div>
        <el-input
          :model-value="output"
          type="textarea"
          :rows="14"
          readonly
          resize="vertical"
          class="output-area"
        />
      </div>

      <div v-else class="empty-section">
        <el-empty :description="$t('tools.dummy.labels.emptyHint')" :image-size="80" />
      </div>
    </div>
  </ToolPage>
</template>

<script>
import { ElMessage } from 'element-plus'
import { DataLine } from '@element-plus/icons-vue'
import ToolPage from '@/components/ToolPage.vue'
import { copyToClipboard } from '@/utils/format.js'

export default {
  name: 'DummyDataGenerator',
  components: {
    DataLine,
    ToolPage
  },
  data() {
    return {
      selectedFields: ['name', 'email'],
      count: 5,
      format: 'json',
      output: '',
      generatedRecords: []
    }
  },
  computed: {
    fieldOptions() {
      return [
        'name',
        'email',
        'phone',
        'uuid',
        'username',
        'address',
        'city',
        'date',
        'lorem'
      ]
    },
    canGenerate() {
      return this.selectedFields.length > 0
    }
  },
  methods: {
    generate() {
      if (this.selectedFields.length === 0) {
        ElMessage.warning(this.$t('tools.dummy.messages.selectField'))
        return
      }

      const records = []
      for (let i = 0; i < this.count; i++) {
        records.push(this.generateRecord(this.selectedFields))
      }

      this.generatedRecords = records

      if (this.format === 'json') {
        this.output = JSON.stringify(records, null, 2)
      } else {
        // one-per-line：每条记录序列化为单行（字段顺序固定）
        this.output = records.map((r) => JSON.stringify(r)).join('\n')
      }

      ElMessage.success(
        this.$t('tools.dummy.messages.generateSuccess', { count: records.length })
      )
    },

    generateRecord(fields) {
      const record = {}
      // 先统一抽取可复用的姓名，保证 name/email 一致性
      const fullName = this.pickName()
      for (const f of fields) {
        switch (f) {
          case 'name':
            record.name = fullName
            break
          case 'email':
            record.email = this.makeEmail(fullName)
            break
          case 'phone':
            record.phone = this.makePhone()
            break
          case 'uuid':
            record.uuid = this.makeUuid()
            break
          case 'username':
            record.username = this.makeUsername(fullName)
            break
          case 'address':
            record.address = this.makeAddress()
            break
          case 'city':
            record.city = this.pickCity()
            break
          case 'date':
            record.date = this.makeDate()
            break
          case 'lorem':
            record.lorem = this.makeLorem()
            break
        }
      }
      return record
    },

    // ---------- 纯 JS 生成器 ----------
    pick(arr) {
      return arr[Math.floor(Math.random() * arr.length)]
    },

    pickName() {
      const first = [
        'James', 'Mary', 'John', 'Patricia', 'Robert', 'Jennifer', 'Michael',
        'Linda', 'William', 'Elizabeth', 'David', 'Barbara', 'Richard', 'Susan',
        'Joseph', 'Jessica', 'Thomas', 'Sarah', 'Charles', 'Karen', 'Daniel',
        'Nancy', 'Emma', 'Oliver', 'Sophia', 'Lucas', 'Mia', 'Henry', 'Ava'
      ]
      const last = [
        'Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller',
        'Davis', 'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez',
        'Wilson', 'Anderson', 'Thomas', 'Taylor', 'Moore', 'Jackson', 'Martin',
        'Lee', 'Perez', 'Thompson', 'White', 'Harris', 'Clark', 'Lewis'
      ]
      return `${this.pick(first)} ${this.pick(last)}`
    },

    makeEmail(name) {
      const handle = name.toLowerCase().replace(/[^a-z]/g, '.')
      const num = Math.floor(Math.random() * 1000)
      const domains = ['example.com', 'test.com', 'mail.com', 'demo.org']
      return `${handle}${num}@${this.pick(domains)}`
    },

    makePhone() {
      const n = () => Math.floor(Math.random() * 10)
      return `+1-${n()}${n()}${n()}-${n()}${n()}${n()}-${n()}${n()}${n()}${n()}`
    },

    makeUuid() {
      if (typeof crypto !== 'undefined' && crypto.randomUUID) {
        return crypto.randomUUID()
      }
      // 回退实现（RFC4122 v4）
      return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
        const r = (Math.random() * 16) | 0
        const v = c === 'x' ? r : (r & 0x3) | 0x8
        return v.toString(16)
      })
    },

    makeUsername(name) {
      const parts = name.toLowerCase().split(' ')
      const suffix = Math.floor(Math.random() * 999)
      return `${parts[0]}${parts[parts.length - 1].slice(0, 1)}${suffix}`
    },

    makeAddress() {
      const streets = [
        'Main St', 'High St', 'Park Ave', 'Oak Rd', 'Pine St', 'Maple Ave',
        'Cedar Ln', 'Elm St', 'Washington St', 'Lake Dr', 'Hill Rd', 'River Rd'
      ]
      return `${Math.floor(Math.random() * 9999) + 1} ${this.pick(streets)}`
    },

    pickCity() {
      const cities = [
        'New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix',
        'Philadelphia', 'San Antonio', 'San Diego', 'Dallas', 'San Jose',
        'Austin', 'Jacksonville', 'Seattle', 'Denver', 'Boston', 'Portland'
      ]
      return this.pick(cities)
    },

    makeDate() {
      const start = new Date(2000, 0, 1).getTime()
      const end = new Date(2025, 11, 31).getTime()
      const d = new Date(start + Math.random() * (end - start))
      const pad = (x) => String(x).padStart(2, '0')
      return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`
    },

    makeLorem() {
      const words = [
        'lorem', 'ipsum', 'dolor', 'sit', 'amet', 'consectetur', 'adipiscing',
        'elit', 'sed', 'do', 'eiusmod', 'tempor', 'incididunt', 'ut', 'labore',
        'et', 'dolore', 'magna', 'aliqua', 'enim', 'ad', 'minim', 'veniam',
        'quis', 'nostrud', 'exercitation', 'ullamco', 'laboris', 'nisi', 'aliquip'
      ]
      const len = 6 + Math.floor(Math.random() * 8)
      const parts = []
      for (let i = 0; i < len; i++) parts.push(this.pick(words))
      let sentence = parts.join(' ')
      return sentence.charAt(0).toUpperCase() + sentence.slice(1) + '.'
    },

    reset() {
      this.selectedFields = ['name', 'email']
      this.count = 5
      this.format = 'json'
      this.output = ''
      this.generatedRecords = []
    },

    async copyAll() {
      if (!this.output) {
        ElMessage.warning(this.$t('tools.dummy.messages.nothingToCopy'))
        return
      }
      try {
        await copyToClipboard(this.output)
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

.field-checkbox-group {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: var(--dt-spacing-sm, 8px);
  padding: var(--dt-spacing-md, 12px) var(--dt-spacing-md, 16px);
  background: var(--dt-bg-section, #f5f7fa);
  border: 1px solid var(--dt-border-lighter, #ebeef5);
  border-radius: var(--dt-radius-md, 6px);
}

.config-row {
  display: flex;
  gap: var(--dt-spacing-md, 16px);
  align-items: flex-end;
  flex-wrap: wrap;
}

.config-item {
  flex: 1;
  min-width: 160px;
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

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--dt-spacing-sm, 8px);
}

.result-count {
  color: var(--dt-text-secondary, #909399);
  font-weight: 500;
}

:deep(.output-area .el-textarea__inner) {
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: var(--dt-font-size-base, 14px);
  line-height: 1.6;
  color: var(--dt-text-primary, #303133);
  background: var(--dt-bg-section, #f5f7fa);
}

.empty-section {
  padding: var(--dt-spacing-lg, 24px) 0;
}

@media (max-width: 768px) {
  .config-row {
    flex-direction: column;
    align-items: stretch;
  }

  .config-item {
    min-width: 100%;
  }

  .action-section .el-button {
    flex: 1;
  }
}
</style>
