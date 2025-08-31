<template>
  <div class="markdown-editor-container">
    <!-- 工具栏 -->
    <MarkdownEditorToolbar
      :show-preview="showPreview"
      @back="handleBack"
      @insert-format="handleInsertFormat"
      @toggle-preview="handleTogglePreview"
      @clear-content="handleClearContent"
      @export-markdown="handleExportMarkdown"
      @switch-layout="handleSwitchLayout"
      @typography-theme-change="handleTypographyThemeChange"
      @code-theme-change="handleCodeThemeChange"
    />

    <!-- 编辑器主体 -->
    <div class="editor-body" :class="layoutMode">
      <!-- 编辑器面板 -->
      <div class="editor-panel-wrapper">
        <MarkdownEditorPanel
          :content="content"
          :show-preview="showPreview"
          :stats="stats"
          @update:content="handleContentUpdate"
          @textarea-ready="handleTextareaReady"
        />
      </div>

      <!-- 预览面板 -->
      <div class="preview-panel-wrapper">
        <MarkdownPreviewPanel
          :show-preview="showPreview"
          :rendered-html="renderedHtml"
          :preview-theme="previewTheme"
          :current-typography-theme="currentTypographyTheme"
          :current-code-theme="currentCodeTheme"
          @theme-change="handleThemeChange"
        />
      </div>
    </div>
  </div>
</template>

<script>
import { useMarkdownEditor } from '../../composables/useMarkdownEditor.js'
import MarkdownEditorToolbar from './MarkdownEditorToolbar.vue'
import MarkdownEditorPanel from './MarkdownEditorPanel.vue'
import MarkdownPreviewPanel from './MarkdownPreviewPanel.vue'

export default {
  name: 'MarkdownEditorContainer',
  components: {
    MarkdownEditorToolbar,
    MarkdownEditorPanel,
    MarkdownPreviewPanel
  },
  setup() {
    // 使用 composable
    const {
      content,
      showPreview,
      previewTheme,
      editorTextarea,
      renderedHtml,
      stats,
      updatePreview,
      insertFormat,
      clearContent,
      exportMarkdown,
      togglePreview,
      setPreviewTheme
    } = useMarkdownEditor()

    return {
      content,
      showPreview,
      previewTheme,
      editorTextarea,
      renderedHtml,
      stats,
      updatePreview,
      insertFormat,
      clearContent,
      exportMarkdown,
      togglePreview,
      setPreviewTheme
    }
  },
  data() {
    return {
      layoutMode: 'split-view', // 'split-view', 'editor-fullscreen', 'preview-fullscreen'
      currentTypographyTheme: 'classic',
      currentCodeTheme: 'github'
    }
  },
  computed: {
    getLayoutClass() {
      return this.layoutMode
    }
  },
  methods: {
    handleBack() {
      this.$router.push('/markdown-tools')
    },
    handleInsertFormat(type, data) {
      if (type === 'emoji') {
        this.insertFormat('emoji', data)
      } else {
        this.insertFormat(type)
      }
    },
    handleTogglePreview() {
      this.togglePreview()
      // 根据预览状态调整布局模式
      if (!this.showPreview) {
        this.layoutMode = 'editor-fullscreen'
      } else {
        this.layoutMode = 'split-view'
      }
    },
    handleClearContent() {
      this.clearContent()
    },
    handleExportMarkdown() {
      this.exportMarkdown()
    },
    handleContentUpdate(newContent) {
      this.content = newContent
      this.updatePreview()
    },
    handleTextareaReady(textarea) {
      this.editorTextarea = textarea
    },
    handleThemeChange(theme) {
      this.setPreviewTheme(theme)
    },
    handleSwitchLayout(mode) {
      this.layoutMode = mode
      // 根据布局模式调整预览显示状态
      if (mode === 'editor-fullscreen') {
        this.showPreview = false
      } else if (mode === 'preview-fullscreen') {
        this.showPreview = true
      } else if (mode === 'split-view') {
        this.showPreview = true
      }
    },
    handleTypographyThemeChange(theme) {
      // 更新当前排版主题状态
      this.currentTypographyTheme = theme.id
      // 处理排版主题切换
      this.applyTypographyTheme(theme)
    },
    handleCodeThemeChange(theme) {
      // 更新当前代码主题状态
      this.currentCodeTheme = theme.id
      // 处理代码主题切换
      this.applyCodeTheme(theme)
    },
    applyTypographyTheme(theme) {
      // 应用排版主题到预览区域
      const previewContent = document.querySelector('.preview-content')
      if (previewContent && theme.styles) {
        Object.assign(previewContent.style, theme.styles)

        // 应用标题样式
        const headings = previewContent.querySelectorAll('h1, h2, h3, h4, h5, h6')
        headings.forEach(heading => {
          if (theme.headingStyles) {
            Object.assign(heading.style, theme.headingStyles)
          }
        })
      }
    },
    applyCodeTheme(theme) {
      // 应用代码主题到预览区域
      const previewContent = document.querySelector('.preview-content')
      if (previewContent && theme.styles) {
        const codeBlocks = previewContent.querySelectorAll('pre')
        codeBlocks.forEach(block => {
          Object.assign(block.style, theme.styles)
        })

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
}
</script>

<style scoped>
.markdown-editor-container {
  position: fixed;
  top: 0; /* 从顶部开始 */
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  flex-direction: column;
  background-color: #f8f9fa;
  overflow: hidden; /* 防止内容溢出 */
  z-index: 1; /* 降低容器z-index，让工具栏可以更高 */
}

.editor-body {
  flex: 1;
  display: flex;
  overflow: hidden;
  position: relative;
}

/* 编辑器面板 - 铺满左侧 */
.editor-panel-wrapper {
  flex: 1;
  height: 100%;
  position: relative;
  background-color: #fff;
  border-right: 1px solid #e6e6e6;
  transition: all 0.3s ease;
}

/* 预览面板 - 铺满右侧 */
.preview-panel-wrapper {
  flex: 1;
  height: 100%;
  position: relative;
  background-color: #fff;
  transition: all 0.3s ease;
}

/* 全屏模式 - 编辑器独占 */
.editor-fullscreen .editor-panel-wrapper {
  flex: 1;
  border-right: none;
}

.editor-fullscreen .preview-panel-wrapper {
  flex: 0;
  width: 0;
  overflow: hidden;
}

/* 全屏模式 - 预览独占 */
.preview-fullscreen .preview-panel-wrapper {
  flex: 1;
}

.preview-fullscreen .editor-panel-wrapper {
  flex: 0;
  width: 0;
  overflow: hidden;
}

/* 分栏模式 */
.split-view .editor-panel-wrapper,
.split-view .preview-panel-wrapper {
  flex: 1;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .markdown-editor-container {
    top: 120px; /* 移动端工具栏高度 */
  }

  .editor-body {
    flex-direction: column;
  }

  .editor-panel-wrapper,
  .preview-panel-wrapper {
    border-right: none;
    border-bottom: 1px solid #e6e6e6;
  }

  /* 移动端默认垂直布局 */
  .editor-panel-wrapper {
    height: 50%;
    border-bottom: 1px solid #e6e6e6;
  }

  .preview-panel-wrapper {
    height: 50%;
  }

  /* 移动端全屏模式 */
  .editor-fullscreen .editor-panel-wrapper {
    height: 100%;
  }

  .editor-fullscreen .preview-panel-wrapper {
    height: 0;
  }

  .preview-fullscreen .preview-panel-wrapper {
    height: 100%;
  }

  .preview-fullscreen .editor-panel-wrapper {
    height: 0;
  }
}

@media (max-width: 480px) {
  .markdown-editor-container {
    top: 140px; /* 小屏幕设备工具栏高度 */
  }
}

/* 主题样式支持 */
.current-theme-info {
  font-size: 12px;
  color: #666;
  background-color: #f8f9fa;
  padding: 4px 8px;
  border-radius: 4px;
  border: 1px solid #e6e6e6;
}
</style>
