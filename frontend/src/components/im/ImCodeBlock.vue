<template>
  <div class="im-code-block">
    <div class="code-header">
      <span class="code-lang">{{ displayLang }}</span>
      <button class="code-copy-btn" @click="copyCode">
        {{ copied ? t('common.copied') || '✓' : t('common.copy') }}
      </button>
    </div>
    <pre><code :class="codeClass" v-html="highlighted"></code></pre>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import hljs from 'highlight.js/lib/core'
import javascript from 'highlight.js/lib/languages/javascript'
import python from 'highlight.js/lib/languages/python'
import css from 'highlight.js/lib/languages/css'
import xml from 'highlight.js/lib/languages/xml'
import json from 'highlight.js/lib/languages/json'
import bash from 'highlight.js/lib/languages/bash'
import sql from 'highlight.js/lib/languages/sql'
import java from 'highlight.js/lib/languages/java'
import cpp from 'highlight.js/lib/languages/cpp'
import csharp from 'highlight.js/lib/languages/csharp'
import go from 'highlight.js/lib/languages/go'
import rust from 'highlight.js/lib/languages/rust'
import yaml from 'highlight.js/lib/languages/yaml'
import markdown from 'highlight.js/lib/languages/markdown'
import plaintext from 'highlight.js/lib/languages/plaintext'
import 'highlight.js/styles/github-dark.min.css'

hljs.registerLanguage('javascript', javascript)
hljs.registerLanguage('js', javascript)
hljs.registerLanguage('typescript', javascript)
hljs.registerLanguage('ts', javascript)
hljs.registerLanguage('python', python)
hljs.registerLanguage('py', python)
hljs.registerLanguage('css', css)
hljs.registerLanguage('html', xml)
hljs.registerLanguage('xml', xml)
hljs.registerLanguage('json', json)
hljs.registerLanguage('bash', bash)
hljs.registerLanguage('shell', bash)
hljs.registerLanguage('sh', bash)
hljs.registerLanguage('sql', sql)
hljs.registerLanguage('java', java)
hljs.registerLanguage('cpp', cpp)
hljs.registerLanguage('c', cpp)
hljs.registerLanguage('csharp', csharp)
hljs.registerLanguage('cs', csharp)
hljs.registerLanguage('go', go)
hljs.registerLanguage('rust', rust)
hljs.registerLanguage('yaml', yaml)
hljs.registerLanguage('yml', yaml)
hljs.registerLanguage('markdown', markdown)
hljs.registerLanguage('md', markdown)
hljs.registerLanguage('plaintext', plaintext)
hljs.registerLanguage('text', plaintext)

const props = defineProps({
  code: {
    type: String,
    required: true,
  },
  language: {
    type: String,
    default: '',
  },
})

const { t } = useI18n()
const copied = ref(false)

const highlighted = computed(() => {
  if (!props.code) return ''
  if (props.language && hljs.getLanguage(props.language)) {
    return hljs.highlight(props.code, { language: props.language }).value
  }
  return hljs.highlightAuto(props.code).value
})

const displayLang = computed(() => {
  if (props.language) return props.language
  if (!props.code) return ''
  const result = hljs.highlightAuto(props.code)
  return result.language || 'text'
})

const codeClass = computed(() => {
  const lang = props.language || displayLang.value || ''
  return lang ? `hljs language-${lang}` : 'hljs'
})

function copyCode() {
  navigator.clipboard.writeText(props.code).then(() => {
    copied.value = true
    ElMessage.success(t('common.copySuccess'))
    setTimeout(() => {
      copied.value = false
    }, 1500)
  })
}
</script>

<style scoped>
.im-code-block {
  border-radius: var(--dt-radius-md);
  overflow: hidden;
  background: #1e1e2e;
  font-family: 'Consolas', 'Monaco', 'Fira Code', monospace;
}

.code-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 6px 12px;
  background: rgba(255, 255, 255, 0.06);
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.code-lang {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.5);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-family: inherit;
}

.code-copy-btn {
  background: none;
  border: none;
  color: rgba(255, 255, 255, 0.5);
  cursor: pointer;
  font-size: 12px;
  padding: 2px 8px;
  border-radius: var(--dt-radius-sm);
  transition: all 0.15s ease;
  font-family: inherit;
}

.code-copy-btn:hover {
  color: rgba(255, 255, 255, 0.85);
  background: rgba(255, 255, 255, 0.1);
}

.im-code-block pre {
  margin: 0;
  padding: 12px;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
}

.im-code-block pre::-webkit-scrollbar {
  height: 4px;
}

.im-code-block pre::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.15);
  border-radius: 2px;
}

.im-code-block pre code {
  font-family: inherit;
  font-size: var(--dt-font-size-xs);
  line-height: 1.5;
  white-space: pre;
}
</style>
