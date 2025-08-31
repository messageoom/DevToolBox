<template>
  <div v-if="showPreview" class="markdown-preview-panel">
    <!-- 预览头部 -->
    <div class="preview-header">
      <div class="header-left">
        <el-icon class="preview-icon"><View /></el-icon>
        <span>预览</span>
      </div>
      <div class="header-right">
        <span class="current-theme-info">
          当前主题: {{ currentTypographyThemeName }} + {{ currentCodeThemeName }}
        </span>
      </div>
    </div>

    <!-- 预览主体 -->
    <div class="preview-body">
      <div
        ref="previewContent"
        class="preview-content"
        :class="`theme-${previewTheme}`"
        v-html="renderedHtml"
      ></div>
    </div>
  </div>
</template>

<script>
import { View } from '@element-plus/icons-vue'
import { typographyThemes, codeThemes, getTypographyTheme, getCodeTheme } from './themes.js'

export default {
  name: 'MarkdownPreviewPanel',
  components: {
    View
  },
  props: {
    showPreview: {
      type: Boolean,
      default: true
    },
    renderedHtml: {
      type: String,
      default: ''
    },
    previewTheme: {
      type: String,
      default: 'default'
    },
    currentTypographyTheme: {
      type: String,
      default: 'classic'
    },
    currentCodeTheme: {
      type: String,
      default: 'github'
    }
  },
  emits: ['theme-change'],
  data() {
    return {
      typographyThemes: typographyThemes,
      codeThemes: codeThemes
    }
  },
  computed: {
    currentTypographyThemeName() {
      const theme = getTypographyTheme(this.currentTypographyTheme)
      return theme ? theme.name : '经典优雅'
    },
    currentCodeThemeName() {
      const theme = getCodeTheme(this.currentCodeTheme)
      return theme ? theme.name : 'GitHub 主题'
    }
  },
  watch: {
    currentTypographyTheme: {
      handler(newTheme) {
        this.applyTypographyTheme(newTheme)
      },
      immediate: true
    },
    currentCodeTheme: {
      handler(newTheme) {
        this.applyCodeTheme(newTheme)
      },
      immediate: true
    }
  },
  methods: {
    applyTypographyTheme(themeId) {
      const theme = getTypographyTheme(themeId)
      if (!theme || !this.$refs.previewContent) return

      const previewContent = this.$refs.previewContent
      Object.assign(previewContent.style, theme.styles)

      // 应用标题样式
      const headings = previewContent.querySelectorAll('h1, h2, h3, h4, h5, h6')
      headings.forEach(heading => {
        if (theme.headingStyles) {
          Object.assign(heading.style, theme.headingStyles)
        }
      })
    },
    applyCodeTheme(themeId) {
      const theme = getCodeTheme(themeId)
      if (!theme || !this.$refs.previewContent) return

      const previewContent = this.$refs.previewContent

      // 应用代码块样式
      const codeBlocks = previewContent.querySelectorAll('pre')
      codeBlocks.forEach(block => {
        Object.assign(block.style, theme.styles)
      })

      // 应用内联代码样式
      const inlineCodes = previewContent.querySelectorAll('code')
      inlineCodes.forEach(code => {
        if (!code.closest('pre')) {
          Object.assign(code.style, {
            backgroundColor: theme.styles.backgroundColor,
            color: theme.keywordColor,
            padding: '2px 4px',
            borderRadius: '3px',
            fontSize: '0.9em'
          })
        }
      })
    }
  }
}
</script>

<style scoped>
.markdown-preview-panel {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  flex-direction: column;
  background-color: #fff;
  height: 100%;
  width: 100%;
  overflow: hidden;
}

.preview-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background-color: #f8f9fa;
  border-bottom: 1px solid #e6e6e6;
  font-weight: bold;
  color: #333;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.preview-icon {
  color: #67c23a;
}

.header-right {
  display: flex;
  align-items: center;
}

.preview-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.preview-content {
  flex: 1;
  padding: 16px;
  overflow-y: auto;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  line-height: 1.6;
}

/* Markdown 样式 */
.preview-content :deep(h1),
.preview-content :deep(h2),
.preview-content :deep(h3),
.preview-content :deep(h4),
.preview-content :deep(h5),
.preview-content :deep(h6) {
  margin-top: 1.5em;
  margin-bottom: 0.5em;
  color: #333;
}

.preview-content :deep(h1) {
  font-size: 2em;
  border-bottom: 1px solid #eee;
  padding-bottom: 0.3em;
}

.preview-content :deep(h2) {
  font-size: 1.5em;
  border-bottom: 1px solid #eee;
  padding-bottom: 0.3em;
}

.preview-content :deep(p) {
  margin: 1em 0;
}

.preview-content :deep(code) {
  background-color: #f6f8fa;
  padding: 0.2em 0.4em;
  border-radius: 3px;
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 0.9em;
}

.preview-content :deep(pre) {
  background-color: #f6f8fa;
  padding: 16px;
  border-radius: 6px;
  overflow-x: auto;
  margin: 1em 0;
}

.preview-content :deep(pre code) {
  background-color: transparent;
  padding: 0;
}

.preview-content :deep(blockquote) {
  border-left: 4px solid #ddd;
  padding-left: 16px;
  margin: 1em 0;
  color: #666;
}

.preview-content :deep(table) {
  border-collapse: collapse;
  width: 100%;
  margin: 1em 0;
}

.preview-content :deep(th),
.preview-content :deep(td) {
  border: 1px solid #ddd;
  padding: 8px 12px;
  text-align: left;
}

.preview-content :deep(th) {
  background-color: #f8f9fa;
  font-weight: bold;
}

.preview-content :deep(ul),
.preview-content :deep(ol) {
  margin: 1em 0;
  padding-left: 2em;
}

.preview-content :deep(li) {
  margin: 0.5em 0;
}

.preview-content :deep(a) {
  color: #409eff;
  text-decoration: none;
}

.preview-content :deep(a:hover) {
  text-decoration: underline;
}

.preview-content :deep(img) {
  max-width: 100%;
  height: auto;
  border-radius: 4px;
}

.empty-preview {
  text-align: center;
  color: #999;
  font-style: italic;
  margin-top: 2em;
}

/* 主题样式 */
.theme-default {
  /* 默认主题样式已在上面定义 */
}

.theme-dark {
  background-color: #1e1e1e;
  color: #d4d4d4;
}

.theme-dark :deep(h1),
.theme-dark :deep(h2),
.theme-dark :deep(h3),
.theme-dark :deep(h4),
.theme-dark :deep(h5),
.theme-dark :deep(h6) {
  color: #ffffff;
}

.theme-dark :deep(code) {
  background-color: #2d2d2d;
  color: #d4d4d4;
}

.theme-dark :deep(pre) {
  background-color: #2d2d2d;
}

.theme-dark :deep(blockquote) {
  border-left-color: #555;
  color: #cccccc;
}

.theme-dark :deep(th),
.theme-dark :deep(td) {
  border-color: #555;
  color: #d4d4d4;
}

.theme-dark :deep(th) {
  background-color: #2d2d2d;
}

.theme-simple {
  font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
  color: #333;
}

.theme-simple :deep(h1),
.theme-simple :deep(h2),
.theme-simple :deep(h3) {
  font-weight: 300;
  color: #222;
}

.theme-simple :deep(code) {
  background-color: #f0f0f0;
  color: #c7254e;
}

.theme-simple :deep(pre) {
  background-color: #f8f8f8;
  border: 1px solid #e7e7e7;
}

.theme-simple :deep(blockquote) {
  border-left-color: #ccc;
  font-style: italic;
  color: #666;
}

/* 滚动条样式 */
.preview-content::-webkit-scrollbar {
  width: 8px;
}

.preview-content::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.preview-content::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;
}

.preview-content::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .markdown-preview-panel {
    max-height: 50vh;
  }

  .preview-header {
    padding: 8px 12px;
  }

  .preview-content {
    font-size: 16px; /* 防止iOS缩放 */
    padding: 12px;
  }
}

@media (max-width: 480px) {
  .preview-header {
    padding: 6px 8px;
  }

  .preview-content {
    padding: 8px;
  }
}
</style>
