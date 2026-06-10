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
          @keydown="handleKeydown"
        />
      </div>

      <!-- 预览面板 -->
      <div class="preview-panel-wrapper">
        <MarkdownPreviewPanel
          :rendered-html="renderedHtml"
          :preview-theme="previewTheme"
          :current-typography-theme="currentTypographyTheme"
          :current-code-theme="currentCodeTheme"
          @theme-change="handleThemeChange"
          @preview-ready="handlePreviewReady"
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
    const {
      content,
      showPreview,
      previewTheme,
      editorTextarea,
      renderedHtml,
      stats,
      insertFormat,
      clearContent,
      exportMarkdown,
      togglePreview,
      setPreviewTheme,
      handleKeydown
    } = useMarkdownEditor()

    return {
      content,
      showPreview,
      previewTheme,
      editorTextarea,
      renderedHtml,
      stats,
      insertFormat,
      clearContent,
      exportMarkdown,
      togglePreview,
      setPreviewTheme,
      handleKeydown
    }
  },
  data() {
    return {
      layoutMode: 'split-view',
      currentTypographyTheme: 'classic',
      currentCodeTheme: 'github',
      previewContentEl: null,
      isSyncingScroll: false
    }
  },
  beforeUnmount() {
    this.removeScrollListeners()
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
      this.layoutMode = this.showPreview ? 'split-view' : 'editor-fullscreen'
    },
    handleClearContent() {
      this.clearContent()
    },
    handleExportMarkdown() {
      this.exportMarkdown()
    },
    handleContentUpdate(newContent) {
      this.content = newContent
    },
    handleTextareaReady(textarea) {
      this.editorTextarea = textarea
      this.setupSyncScroll()
    },
    handlePreviewReady(el) {
      this.previewContentEl = el
      this.setupSyncScroll()
    },
    setupSyncScroll() {
      const ta = this.editorTextarea
      const pv = this.previewContentEl
      if (!ta || !pv) return

      this._onEditorScroll = () => {
        if (this.isSyncingScroll) return
        this.isSyncingScroll = true
        const pct = ta.scrollTop / (ta.scrollHeight - ta.clientHeight || 1)
        pv.scrollTop = pct * (pv.scrollHeight - pv.clientHeight)
        this.isSyncingScroll = false
      }
      this._onPreviewScroll = () => {
        if (this.isSyncingScroll) return
        this.isSyncingScroll = true
        const pct = pv.scrollTop / (pv.scrollHeight - pv.clientHeight || 1)
        ta.scrollTop = pct * (ta.scrollHeight - ta.clientHeight)
        this.isSyncingScroll = false
      }
      ta.addEventListener('scroll', this._onEditorScroll, { passive: true })
      pv.addEventListener('scroll', this._onPreviewScroll, { passive: true })
    },
    removeScrollListeners() {
      if (this.editorTextarea && this._onEditorScroll) {
        this.editorTextarea.removeEventListener('scroll', this._onEditorScroll)
      }
      if (this.previewContentEl && this._onPreviewScroll) {
        this.previewContentEl.removeEventListener('scroll', this._onPreviewScroll)
      }
    },
    handleThemeChange(theme) {
      this.setPreviewTheme(theme)
    },
    handleSwitchLayout(mode) {
      this.layoutMode = mode
      this.showPreview = mode !== 'editor-fullscreen'
    },
    handleTypographyThemeChange(theme) {
      this.currentTypographyTheme = theme.id
    },
    handleCodeThemeChange(theme) {
      this.currentCodeTheme = theme.id
    }
  }
}
</script>

<style scoped>
.markdown-editor-container {
  height: 100%;
  display: flex;
  flex-direction: column;
  background-color: var(--dt-bg-page);
  overflow: hidden;
}

.editor-body {
  flex: 1;
  display: flex;
  overflow: hidden;
  position: relative;
}

/* 两侧面板各占一半 */
.editor-panel-wrapper {
  flex: 1 1 50%;
  height: 100%;
  position: relative;
  overflow: hidden;
  border-right: 1px solid var(--dt-border-light);
}

.preview-panel-wrapper {
  flex: 1 1 50%;
  height: 100%;
  position: relative;
  overflow: hidden;
  transition: flex 0.3s ease;
}

.editor-panel-wrapper {
  transition: flex 0.3s ease;
}

/* 全屏模式 - 编辑器独占 */
.editor-fullscreen .editor-panel-wrapper {
  flex: 1 1 100%;
  border-right: none;
}

.editor-fullscreen .preview-panel-wrapper {
  flex: 0 0 0px;
  overflow: hidden;
}

/* 全屏模式 - 预览独占 */
.preview-fullscreen .preview-panel-wrapper {
  flex: 1 1 100%;
}

.preview-fullscreen .editor-panel-wrapper {
  flex: 0 0 0px;
  overflow: hidden;
}

/* 分栏模式（默认，两面板各 50%） */
.split-view .editor-panel-wrapper,
.split-view .preview-panel-wrapper {
  flex: 1 1 50%;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .editor-body {
    flex-direction: column;
  }

  .editor-panel-wrapper,
  .preview-panel-wrapper {
    border-right: none;
    border-bottom: 1px solid var(--dt-border-light);
  }

  .split-view .editor-panel-wrapper,
  .split-view .preview-panel-wrapper {
    flex: 1 1 50%;
  }

  .editor-fullscreen .editor-panel-wrapper {
    flex: 1 1 100%;
  }

  .editor-fullscreen .preview-panel-wrapper {
    flex: 0 0 0px;
  }

  .preview-fullscreen .preview-panel-wrapper {
    flex: 1 1 100%;
  }

  .preview-fullscreen .editor-panel-wrapper {
    flex: 0 0 0px;
  }
}

.current-theme-info {
  font-size: 12px;
  color: var(--dt-text-secondary);
  background-color: var(--dt-bg-page);
  padding: 4px 8px;
  border-radius: 4px;
  border: 1px solid var(--dt-border-light);
}
</style>
