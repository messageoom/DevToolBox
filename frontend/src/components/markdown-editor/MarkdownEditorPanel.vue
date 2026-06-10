<template>
  <div class="markdown-editor-panel" :class="{ 'full-width': !showPreview }">
    <!-- 编辑器头部 -->
    <div class="editor-header">
      <div class="header-left">
        <el-icon class="editor-icon"><Edit /></el-icon>
        <span>{{ $t('tools.markdownEditor.editor') }}</span>
      </div>
      <div class="header-right">
        <div class="editor-stats">
          <span>{{ $t('tools.markdownEditor.characters') }}: {{ stats.characters }}</span>
          <span>{{ $t('tools.markdownEditor.lines') }}: {{ stats.lines }}</span>
        </div>
      </div>
    </div>

    <!-- 编辑器主体 -->
    <div class="editor-body">
        <textarea
          ref="editorTextarea"
          :value="content"
          class="editor-textarea"
          :placeholder="$t('tools.markdownEditor.placeholder')"
          @input="$emit('update:content', $event.target.value)"
          @select="$emit('selection-change', $event)"
          @keydown="onKeydown"
        ></textarea>
    </div>
  </div>
</template>

<script>
import { Edit } from '@element-plus/icons-vue'

export default {
  name: 'MarkdownEditorPanel',
  components: {
    Edit
  },
  props: {
    content: {
      type: String,
      default: ''
    },
    showPreview: {
      type: Boolean,
      default: true
    },
    stats: {
      type: Object,
      default: () => ({
        characters: 0,
        lines: 0
      })
    }
  },
  emits: ['update:content', 'selection-change', 'keydown'],
  mounted() {
    // 将 textarea 引用传递给父组件
    this.$emit('textarea-ready', this.$refs.editorTextarea)
  },
  methods: {
    onKeydown(event) {
      // Let the parent's handleKeydown decide if this is a shortcut
      this.$emit('keydown', event)
    }
  }
}
</script>

<style scoped>
.markdown-editor-panel {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  flex-direction: column;
  background-color: var(--dt-bg-card);
  height: 100%;
  width: 100%;
}

.markdown-editor-panel.full-width {
  flex: 1;
  border-right: none;
}

.editor-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background-color: var(--dt-bg-section);
  border-bottom: 1px solid var(--dt-border-light);
  font-weight: bold;
  color: var(--dt-text-primary);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.editor-icon {
  color: var(--dt-primary);
}

.header-right {
  display: flex;
  align-items: center;
}

.editor-stats {
  font-size: 12px;
  color: var(--dt-text-secondary);
  display: flex;
  gap: 16px;
  font-weight: normal;
}

.editor-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.editor-textarea {
  flex: 1;
  padding: 16px;
  border: none;
  outline: none;
  resize: none;
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 14px;
  line-height: 1.6;
  color: var(--dt-text-primary);
  background-color: var(--dt-bg-page);
  transition: background-color 0.2s ease;
}

.editor-textarea:focus {
  background-color: var(--dt-bg-card);
  box-shadow: inset 0 0 0 1px var(--dt-primary);
}

.editor-textarea::placeholder {
  color: var(--dt-text-placeholder);
  font-style: italic;
}

/* 滚动条样式 */
.editor-textarea::-webkit-scrollbar {
  width: 8px;
}

.editor-textarea::-webkit-scrollbar-track {
  background: transparent;
  border-radius: 4px;
}

.editor-textarea::-webkit-scrollbar-thumb {
  background: var(--dt-border-light);
  border-radius: 4px;
}

.editor-textarea::-webkit-scrollbar-thumb:hover {
  background: var(--dt-text-secondary);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .markdown-editor-panel {
    border-right: none;
    border-bottom: 1px solid var(--dt-border-light);
    max-height: 50vh;
  }

  .editor-header {
    padding: 8px 12px;
  }

  .editor-stats {
    font-size: 11px;
    gap: 12px;
  }

  .editor-textarea {
    font-size: 16px; /* 防止iOS缩放 */
    padding: 12px;
  }
}

@media (max-width: 480px) {
  .editor-header {
    padding: 6px 8px;
  }

  .editor-stats {
    flex-direction: column;
    gap: 4px;
    align-items: flex-end;
  }

  .editor-textarea {
    padding: 8px;
  }
}
</style>
