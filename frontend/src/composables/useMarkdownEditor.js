import { ref, computed, nextTick, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Marked } from 'marked'
import { markedHighlight } from 'marked-highlight'
import hljs from 'highlight.js/lib/core'
import javascript from 'highlight.js/lib/languages/javascript'
import python from 'highlight.js/lib/languages/python'
import java from 'highlight.js/lib/languages/java'
import css from 'highlight.js/lib/languages/css'
import xml from 'highlight.js/lib/languages/xml'
import json from 'highlight.js/lib/languages/json'
import bash from 'highlight.js/lib/languages/bash'
import sql from 'highlight.js/lib/languages/sql'
import typescript from 'highlight.js/lib/languages/typescript'
import yaml from 'highlight.js/lib/languages/yaml'
import markdown from 'highlight.js/lib/languages/markdown'

// --- highlight.js 注册常用语言 ---
hljs.registerLanguage('javascript', javascript)
hljs.registerLanguage('js', javascript)
hljs.registerLanguage('python', python)
hljs.registerLanguage('py', python)
hljs.registerLanguage('java', java)
hljs.registerLanguage('css', css)
hljs.registerLanguage('html', xml)
hljs.registerLanguage('xml', xml)
hljs.registerLanguage('json', json)
hljs.registerLanguage('bash', bash)
hljs.registerLanguage('sh', bash)
hljs.registerLanguage('sql', sql)
hljs.registerLanguage('typescript', typescript)
hljs.registerLanguage('ts', typescript)
hljs.registerLanguage('yaml', yaml)
hljs.registerLanguage('yml', yaml)
hljs.registerLanguage('markdown', markdown)

// --- marked 实例（隔离，不污染全局） ---
const markedInstance = new Marked(
  markedHighlight({
    langPrefix: 'hljs language-',
    highlight(code, lang) {
      if (lang && hljs.getLanguage(lang)) {
        try { return hljs.highlight(code, { language: lang }).value }
        catch { /* fall through */ }
      }
      try { return hljs.highlightAuto(code).value }
      catch { return code }
    },
  }),
  { breaks: true, gfm: true },
)

const STORAGE_KEY = 'devtoolbox_md_content'
const DEFAULT_CONTENT = `# Markdown 沉浸式编辑器

欢迎使用 Markdown 沉浸式编辑器！

## 功能特性

- **实时预览**：左侧编辑，右侧实时预览
- **多种主题**：支持默认、暗色、简洁三种预览主题
- **统计信息**：显示字符数和行数
- **一键清空**：快速清空编辑内容
- **导出功能**：支持导出 Markdown 文件

## 使用方法

1. 在左侧编辑器中输入 Markdown 内容
2. 右侧会实时显示预览效果
3. 可以使用工具栏切换预览主题
4. 点击导出按钮保存文件

## Markdown 语法示例

### 标题

# 一级标题
## 二级标题
### 三级标题

### 列表

- 无序列表项 1
- 无序列表项 2
  - 子项
  - 子项

1. 有序列表项 1
2. 有序列表项 2

### 链接和图片

[链接文本](https://example.com)
![图片描述](https://example.com/image.jpg)

### 代码块

\`\`\`javascript
console.log('Hello, World!');
\`\`\`

### 表格

| 列1 | 列2 | 列3 |
|-----|-----|-----|
| 数据1 | 数据2 | 数据3 |
| 数据4 | 数据5 | 数据6 |

### 引用

> 这是一个引用块
> 可以包含多行内容

开始编辑你的 Markdown 文档吧！`

function loadSavedContent() {
  try {
    const saved = localStorage.getItem(STORAGE_KEY)
    return saved !== null ? saved : DEFAULT_CONTENT
  } catch {
    return DEFAULT_CONTENT
  }
}

export function useMarkdownEditor() {
  // 状态管理 — 从 localStorage 恢复内容
  const content = ref(loadSavedContent())
  const showPreview = ref(true)
  const previewTheme = ref('default')
  const editorTextarea = ref(null)

  // Auto-save: 防抖写入 localStorage
  let saveTimer = null
  watch(content, (val) => {
    clearTimeout(saveTimer)
    saveTimer = setTimeout(() => {
      try {
        localStorage.setItem(STORAGE_KEY, val)
      } catch { /* quota exceeded — silently ignore */ }
    }, 800)
  })

  // 计算属性
  const renderedHtml = computed(() => {
    if (content.value) {
      return markedInstance.parse(content.value)
    }
    return '<p class="empty-preview">暂无内容，请在左侧编辑器中输入 Markdown 内容</p>'
  })

  const stats = computed(() => ({
    characters: content.value.length,
    lines: content.value.split('\n').length
  }))

  // 方法
  const insertFormat = (type, data) => {
    if (!editorTextarea.value) return

    const textarea = editorTextarea.value
    let start = textarea.selectionStart
    const end = textarea.selectionEnd

    // Block-level types that must start at line beginning
    const blockTypes = new Set(['h1', 'h2', 'h3', 'unorderedlist', 'orderedlist', 'blockquote'])
    if (blockTypes.has(type)) {
      // Snap start to the beginning of the current line
      const lineStart = content.value.lastIndexOf('\n', start - 1) + 1
      start = lineStart
    }

    const selectedText = content.value.substring(start, end)
    let replacement = ''
    let newCursorPos = start

    switch (type) {
      case 'bold':
        replacement = `**${selectedText || '粗体文本'}**`
        newCursorPos = selectedText ? end + 2 : start + 2
        break
      case 'italic':
        replacement = `*${selectedText || '斜体文本'}*`
        newCursorPos = selectedText ? end + 1 : start + 1
        break
      case 'strikethrough':
        replacement = `~~${selectedText || '删除线文本'}~~`
        newCursorPos = selectedText ? end + 2 : start + 2
        break
      case 'h1':
        replacement = `# ${selectedText || '一级标题'}`
        newCursorPos = start + replacement.length
        break
      case 'h2':
        replacement = `## ${selectedText || '二级标题'}`
        newCursorPos = start + replacement.length
        break
      case 'h3':
        replacement = `### ${selectedText || '三级标题'}`
        newCursorPos = start + replacement.length
        break
      case 'link':
        replacement = `[${selectedText || '链接文本'}](https://example.com)`
        newCursorPos = selectedText ? end + 3 : start + 1
        break
      case 'image':
        replacement = `![${selectedText || '图片描述'}](https://example.com/image.jpg)`
        newCursorPos = selectedText ? end + 3 : start + 2
        break
      case 'codeblock':
        replacement = `\`\`\`javascript\n${selectedText || 'console.log(\'Hello, World!\');'}\n\`\`\``
        newCursorPos = start + 14
        break
      case 'unorderedlist':
        replacement = `- ${selectedText || '列表项'}`
        newCursorPos = start + replacement.length
        break
      case 'orderedlist':
        replacement = `1. ${selectedText || '列表项'}`
        newCursorPos = start + replacement.length
        break
      case 'blockquote':
        replacement = `> ${selectedText || '引用内容'}`
        newCursorPos = start + replacement.length
        break
      case 'table':
        replacement = `| 列1 | 列2 | 列3 |\n|-----|-----|-----|\n| 数据1 | 数据2 | 数据3 |\n| 数据4 | 数据5 | 数据6 |`
        newCursorPos = start + replacement.length
        break
      case 'hr':
        replacement = `\n---\n`
        newCursorPos = start + 5
        break
      case 'emoji':
        replacement = data || '😀'
        newCursorPos = start + replacement.length
        break
      default:
        return
    }

    // 替换文本
    content.value = content.value.substring(0, start) + replacement + content.value.substring(end)

    // 更新光标位置
    nextTick(() => {
      textarea.focus()
      textarea.setSelectionRange(newCursorPos, newCursorPos)
    })
  }

  const clearContent = async () => {
    try {
      await ElMessageBox.confirm('确定要清空所有内容吗？此操作不可撤销。', '确认清空', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      })
      content.value = ''
      ElMessage.success('内容已清空')
    } catch {
      // 用户取消操作
    }
  }

  const exportMarkdown = () => {
    if (!content.value.trim()) {
      ElMessage.warning('没有内容可导出')
      return
    }

    const blob = new Blob([content.value], { type: 'text/markdown' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `markdown-document-${new Date().toISOString().split('T')[0]}.md`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)

    ElMessage.success('文件导出成功')
  }

  const togglePreview = () => {
    showPreview.value = !showPreview.value
  }

  const setPreviewTheme = (theme) => {
    previewTheme.value = theme
  }

  /**
   * Keyboard shortcuts handler — call from textarea @keydown.
   * Returns true if the event was handled (caller should preventDefault).
   */
  const handleKeydown = (event) => {
    const { ctrlKey, metaKey, shiftKey, key } = event
    const mod = ctrlKey || metaKey // Cmd on Mac, Ctrl elsewhere

    if (!mod && key === 'Tab') {
      // Tab → insert 2 spaces (or outdent with Shift)
      if (!editorTextarea.value) return false
      const ta = editorTextarea.value
      const start = ta.selectionStart
      const end = ta.selectionEnd
      if (shiftKey) {
        // Outdent: remove up to 2 leading spaces on current line
        const lineStart = content.value.lastIndexOf('\n', start - 1) + 1
        const lineText = content.value.substring(lineStart, start)
        const removed = lineText.length - lineText.replace(/^ {1,2}/, '').length
        if (removed > 0) {
          content.value = content.value.substring(0, lineStart) + content.value.substring(lineStart + removed)
          nextTick(() => ta.setSelectionRange(Math.max(lineStart, start - removed), Math.max(lineStart, end - removed)))
        }
      } else {
        content.value = content.value.substring(0, start) + '  ' + content.value.substring(end)
        nextTick(() => ta.setSelectionRange(start + 2, start + 2))
      }
      return true
    }

    if (mod && key === 'b') { event.preventDefault(); insertFormat('bold'); return true }
    if (mod && key === 'i') { event.preventDefault(); insertFormat('italic'); return true }
    if (mod && key === 'k') { event.preventDefault(); insertFormat('link'); return true }
    if (mod && key === 's') { event.preventDefault(); exportMarkdown(); return true }

    return false
  }

  return {
    // 状态
    content,
    showPreview,
    previewTheme,
    editorTextarea,

    // 计算属性
    renderedHtml,
    stats,

    // 方法
    insertFormat,
    clearContent,
    exportMarkdown,
    togglePreview,
    setPreviewTheme,
    handleKeydown
  }
}
