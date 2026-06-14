<template>
  <ToolPage :title="$t('tools.jsonTs.title')" :icon="Document">
    <div class="tool-section">
      <div class="input-section">
        <div class="config-row">
          <div class="config-item config-item--root">
            <div class="field-label">{{ $t('tools.jsonTs.labels.rootName') }}</div>
            <el-input
              v-model="rootName"
              :placeholder="$t('tools.jsonTs.placeholders.rootName')"
              clearable
            />
          </div>
        </div>

        <h4 class="section-title">{{ $t('tools.jsonTs.labels.input') }}</h4>
        <el-input
          v-model="input"
          type="textarea"
          :rows="12"
          :placeholder="$t('tools.jsonTs.placeholders.input')"
          resize="vertical"
        />
      </div>

      <div class="action-section">
        <el-button type="primary" @click="convert" :loading="converting">
          {{ $t('tools.jsonTs.labels.convert') }}
        </el-button>
        <el-button @click="clearAll">
          {{ $t('common.clear') }}
        </el-button>
      </div>

      <div class="output-section" v-if="output">
        <div class="result-header">
          <h4 class="section-title">{{ $t('tools.jsonTs.labels.output') }}</h4>
          <el-button size="small" type="primary" plain @click="copyText(output)">
            <el-icon><CopyDocument /></el-icon> {{ $t('common.copy') }}
          </el-button>
        </div>
        <el-input
          :model-value="output"
          type="textarea"
          :rows="16"
          readonly
          resize="vertical"
          class="output-area"
        />
      </div>
    </div>
  </ToolPage>
</template>

<script>
import { ElMessage } from 'element-plus'
import { Document, CopyDocument } from '@element-plus/icons-vue'
import ToolPage from '@/components/ToolPage.vue'
import { copyToClipboard } from '@/utils/format.js'

export default {
  name: 'JsonToTs',
  components: { Document, CopyDocument, ToolPage },
  data() {
    return {
      rootName: 'RootObject',
      input: '',
      output: '',
      converting: false
    }
  },
  methods: {
    convert() {
      const trimmed = this.input.trim()
      if (!trimmed) {
        ElMessage.warning(this.$t('tools.jsonTs.messages.inputRequired'))
        return
      }

      this.converting = true
      try {
        const data = JSON.parse(trimmed)
        const interfaces = new Map()
        const safeRoot = this.pascalCase(this.rootName || 'RootObject')

        const rootType = this.inferType(data, safeRoot, interfaces)
        const rootInline = this.isPrimitiveType(rootType) ? rootType : safeRoot

        let code = ''
        // Declare root interface only if root is an object; for primitives show a type alias.
        if (this.isPrimitiveType(rootType)) {
          code += `type ${safeRoot} = ${rootType};\n`
        } else {
          code += `interface ${safeRoot} {\n${this.renderInterfaceBody(data, safeRoot, interfaces)}}\n`
        }

        // Emit collected interfaces (skip root name to avoid duplicates).
        for (const [name, body] of interfaces.entries()) {
          if (name === safeRoot) continue
          code += `\ninterface ${name} {\n${body}}\n`
        }

        this.output = code.trim() + '\n'
        ElMessage.success(this.$t('tools.jsonTs.messages.convertSuccess'))
      } catch (e) {
        ElMessage.warning(this.$t('tools.jsonTs.messages.invalidJson', { error: e.message }))
      } finally {
        this.converting = false
      }
    },

    isPrimitiveType(t) {
      return /^(string|number|boolean|null|undefined|any|never)$/.test(t)
    },

    pascalCase(str) {
      const cleaned = String(str).replace(/[^a-zA-Z0-9]+/g, ' ').trim()
      if (!cleaned) return 'RootObject'
      const parts = cleaned.split(/\s+/)
      const out = parts.map((p) => p.charAt(0).toUpperCase() + p.slice(1)).join('')
      // Ensure it does not start with a digit.
      if (/^[0-9]/.test(out)) return 'Root' + out
      return out
    },

    // Returns a type STRING (interface name for objects, otherwise primitive/array).
    inferType(value, suggestName, interfaces) {
      if (value === null) return 'null'
      if (Array.isArray(value)) return this.inferArrayType(value, suggestName, interfaces)
      const t = typeof value
      if (t === 'string') {
        if (/^\d{4}-\d{2}-\d{2}T.*$/.test(value)) return 'string'
        return 'string'
      }
      if (t === 'number') return Number.isInteger(value) ? 'number' : 'number'
      if (t === 'boolean') return 'boolean'
      if (t === 'object') {
        const name = suggestName || 'AnonymousObject'
        this.registerObject(value, name, interfaces)
        return name
      }
      return 'any'
    },

    registerObject(obj, name, interfaces) {
      if (!interfaces.has(name)) {
        interfaces.set(name, this.renderInterfaceBody(obj, name, interfaces))
      }
    },

    renderInterfaceBody(obj, parentName, interfaces) {
      // Returns the INNER body (indented lines only); callers wrap with braces.
      const keys = Object.keys(obj)
      if (keys.length === 0) return '  [key: string]: any;\n'
      const lines = keys.map((key) => {
        const value = obj[key]
        let type
        if (value === undefined) {
          // treat undefined as optional with any
          type = 'any'
          return `  ${this.safeKey(key)}?: ${type};`
        }
        const childName = parentName + this.pascalCase(key)
        if (value === null) {
          // null → optional field with inferred-or-any type union null
          return `  ${this.safeKey(key)}?: any | null;`
        }
        type = this.inferType(value, childName, interfaces)
        const optional = (type === 'null') ? '?' : ''
        return `  ${this.safeKey(key)}${optional}: ${type};`
      })
      return lines.join('\n') + '\n'
    },

    inferArrayType(arr, suggestName, interfaces) {
      if (arr.length === 0) return 'any[]'
      // Merge element types.
      const elementTypes = new Set()
      let hasNull = false
      for (const el of arr) {
        if (el === null) {
          hasNull = true
          continue
        }
        const childName = suggestName + 'Item'
        elementTypes.add(this.inferType(el, childName, interfaces))
      }
      let elementUnion = elementTypes.size === 0
        ? 'any'
        : Array.from(elementTypes).join(' | ')
      if (hasNull && elementUnion !== 'any') {
        elementUnion = elementUnion + ' | null'
      } else if (hasNull) {
        elementUnion = 'any'
      }
      // Wrap multi-type unions in parens so the array brackets bind correctly.
      const needsParens = elementUnion.includes(' | ') || elementUnion.includes(' & ')
      return needsParens ? `(${elementUnion})[]` : `${elementUnion}[]`
    },

    safeKey(key) {
      // Quote keys that aren't valid identifiers.
      if (/^[a-zA-Z_$][a-zA-Z0-9_$]*$/.test(key)) return key
      return JSON.stringify(key)
    },

    clearAll() {
      this.input = ''
      this.output = ''
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
  padding-bottom: var(--dt-spacing-md, 16px);
}

.config-row {
  display: flex;
  gap: var(--dt-spacing-md, 16px);
  margin-bottom: var(--dt-spacing-md, 16px);
  align-items: flex-end;
}

.config-item--root {
  max-width: 320px;
}

.field-label {
  font-size: var(--dt-font-size-sm, 13px);
  color: var(--dt-text-secondary, #909399);
  margin-bottom: var(--dt-spacing-xs, 6px);
}

.section-title {
  font-size: var(--dt-font-size-base, 14px);
  font-weight: 600;
  color: var(--dt-text-primary, #303133);
  margin: 0 0 var(--dt-spacing-sm, 8px) 0;
}

.input-section {
  margin-bottom: var(--dt-spacing-sm, 8px);
}

.action-section {
  display: flex;
  gap: var(--dt-spacing-sm, 8px);
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

.output-area :deep(textarea),
.output-area :deep(.el-textarea__inner) {
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: var(--dt-font-size-sm, 13px);
  line-height: 1.6;
}

@media (max-width: 768px) {
  .config-item--root {
    max-width: 100%;
  }

  .action-section .el-button {
    flex: 1;
  }

  .output-section {
    padding: var(--dt-spacing-md, 16px);
    background: var(--dt-bg-section, #f5f7fa);
    border-radius: var(--dt-radius-lg, 12px);
    border: 1px solid var(--dt-border-lighter, #ebeef5);
  }
}
</style>
