<template>
  <div class="markdown-editor-toolbar">
    <!-- 左侧导航 -->
    <div class="toolbar-left">
      <el-button @click.stop="$emit('back')" @mousedown.prevent type="primary" plain size="small" tabindex="-1">
        <el-icon><ArrowLeft /></el-icon>
        {{ $t('common.back') }}
      </el-button>
      <span class="editor-title">{{ $t('tools.markdownEditor.title') }}</span>
    </div>

    <!-- 中间工具栏 -->
    <div class="toolbar-center">
      <!-- 文本格式化 -->
      <el-button-group size="small">
        <el-tooltip :content="$t('tools.markdownEditor.toolbar.bold')" placement="bottom">
          <el-button @click.stop="$emit('insert-format', 'bold')" @mousedown.prevent type="default" tabindex="-1">
            <strong>B</strong>
          </el-button>
        </el-tooltip>
        <el-tooltip :content="$t('tools.markdownEditor.toolbar.italic')" placement="bottom">
          <el-button @click.stop="$emit('insert-format', 'italic')" @mousedown.prevent type="default" tabindex="-1">
            <em>I</em>
          </el-button>
        </el-tooltip>
        <el-tooltip :content="$t('tools.markdownEditor.toolbar.strikethrough')" placement="bottom">
          <el-button @click.stop="$emit('insert-format', 'strikethrough')" @mousedown.prevent type="default" tabindex="-1">
            <del>S</del>
          </el-button>
        </el-tooltip>
      </el-button-group>

      <el-divider direction="vertical" />

      <!-- 标题层级 -->
      <el-button-group size="small">
        <el-tooltip :content="$t('tools.markdownEditor.toolbar.heading1')" placement="bottom">
          <el-button @click.stop="$emit('insert-format', 'h1')" @mousedown.prevent type="default" tabindex="-1">H1</el-button>
        </el-tooltip>
        <el-tooltip :content="$t('tools.markdownEditor.toolbar.heading2')" placement="bottom">
          <el-button @click.stop="$emit('insert-format', 'h2')" @mousedown.prevent type="default" tabindex="-1">H2</el-button>
        </el-tooltip>
        <el-tooltip :content="$t('tools.markdownEditor.toolbar.heading3')" placement="bottom">
          <el-button @click.stop="$emit('insert-format', 'h3')" @mousedown.prevent type="default" tabindex="-1">H3</el-button>
        </el-tooltip>
      </el-button-group>

      <el-divider direction="vertical" />

      <!-- 链接和媒体 -->
      <el-button-group size="small">
        <el-tooltip :content="$t('tools.markdownEditor.toolbar.link')" placement="bottom">
          <el-button @click.stop="$emit('insert-format', 'link')" @mousedown.prevent type="default" tabindex="-1">
            🔗
          </el-button>
        </el-tooltip>
        <el-tooltip :content="$t('tools.markdownEditor.toolbar.image')" placement="bottom">
          <el-button @click.stop="$emit('insert-format', 'image')" @mousedown.prevent type="default" tabindex="-1">
            🖼️
          </el-button>
        </el-tooltip>
        <el-tooltip :content="$t('tools.markdownEditor.toolbar.codeBlock')" placement="bottom">
          <el-button @click.stop="$emit('insert-format', 'codeblock')" @mousedown.prevent type="default" tabindex="-1">
            {}
          </el-button>
        </el-tooltip>
      </el-button-group>

      <el-divider direction="vertical" />

      <!-- 列表和引用 -->
      <el-button-group size="small">
        <el-tooltip :content="$t('tools.markdownEditor.toolbar.unorderedList')" placement="bottom">
          <el-button @click.stop="$emit('insert-format', 'unorderedlist')" @mousedown.prevent type="default" tabindex="-1">
            •
          </el-button>
        </el-tooltip>
        <el-tooltip :content="$t('tools.markdownEditor.toolbar.orderedList')" placement="bottom">
          <el-button @click.stop="$emit('insert-format', 'orderedlist')" @mousedown.prevent type="default" tabindex="-1">
            1.
          </el-button>
        </el-tooltip>
        <el-tooltip :content="$t('tools.markdownEditor.toolbar.blockquote')" placement="bottom">
          <el-button @click.stop="$emit('insert-format', 'blockquote')" @mousedown.prevent type="default" tabindex="-1">
            "
          </el-button>
        </el-tooltip>
      </el-button-group>

      <el-divider direction="vertical" />

      <!-- 其他元素 -->
      <el-button-group size="small">
        <el-tooltip :content="$t('tools.markdownEditor.toolbar.emoji')" placement="bottom">
          <el-button @click.stop="handleEmojiButtonClick" @mousedown.stop.prevent type="default" tabindex="-1">
            😀
          </el-button>
        </el-tooltip>
        <el-tooltip :content="$t('tools.markdownEditor.toolbar.table')" placement="bottom">
          <el-button @click.stop="$emit('insert-format', 'table')" @mousedown.prevent type="default" tabindex="-1">
            ⊞
          </el-button>
        </el-tooltip>
        <el-tooltip :content="$t('tools.markdownEditor.toolbar.horizontalRule')" placement="bottom">
          <el-button @click.stop="$emit('insert-format', 'hr')" @mousedown.prevent type="default" tabindex="-1">
            ―
          </el-button>
        </el-tooltip>
      </el-button-group>

      <!-- 表情符号选择面板 -->
      <Teleport to="body">
        <div
          v-show="showEmojiPicker"
          class="emoji-picker-overlay"
          @click.stop="showEmojiPicker = false"
          @mousedown.stop.prevent
        >
          <div
            ref="emojiPicker"
            class="emoji-picker"
            :style="{ top: emojiPickerPosition.top + 'px', left: emojiPickerPosition.left + 'px' }"
            @click.stop
            @mousedown.stop.prevent
          >
            <div class="emoji-header">
              <span>{{ $t('tools.markdownEditor.toolbar.selectEmoji') }}</span>
              <el-button @click.stop="showEmojiPicker = false" type="text" size="small">✕</el-button>
            </div>
            <div class="emoji-grid">
              <button
                v-for="emoji in emojiList"
                :key="emoji"
                @click.stop="insertEmoji(emoji)"
                @mousedown.stop.prevent
                class="emoji-button"
                type="button"
              >
                {{ emoji }}
              </button>
            </div>
          </div>
        </div>
      </Teleport>
    </div>

    <!-- 右侧操作 -->
    <div class="toolbar-right">
      <!-- 主题按钮组 -->
      <el-button-group size="small">
        <el-tooltip :content="$t('tools.markdownEditor.toolbar.typographyTheme')" placement="bottom">
          <el-button @click.stop="toggleTypographyThemes" @mousedown.prevent type="default" tabindex="-1">
            <span class="theme-btn-icon">📖</span>
          </el-button>
        </el-tooltip>
        <el-tooltip :content="$t('tools.markdownEditor.toolbar.codeTheme')" placement="bottom">
          <el-button @click.stop="toggleCodeThemes" @mousedown.prevent type="default" tabindex="-1">
            <span class="theme-btn-icon">💻</span>
          </el-button>
        </el-tooltip>
      </el-button-group>

      <el-divider direction="vertical" />

      <!-- 布局切换按钮 -->
      <el-button-group size="small">
        <el-tooltip :content="$t('tools.markdownEditor.toolbar.splitView')" placement="bottom">
          <el-button @click.stop="$emit('switch-layout', 'split')" @mousedown.prevent type="default" tabindex="-1">
            <el-icon><Grid /></el-icon>
          </el-button>
        </el-tooltip>
        <el-tooltip :content="$t('tools.markdownEditor.toolbar.fullscreenEdit')" placement="bottom">
          <el-button @click.stop="$emit('switch-layout', 'editor-fullscreen')" @mousedown.prevent type="default" tabindex="-1">
            <el-icon><Edit /></el-icon>
          </el-button>
        </el-tooltip>
        <el-tooltip :content="$t('tools.markdownEditor.toolbar.fullscreenPreview')" placement="bottom">
          <el-button @click.stop="$emit('switch-layout', 'preview-fullscreen')" @mousedown.prevent type="default" tabindex="-1">
            <el-icon><View /></el-icon>
          </el-button>
        </el-tooltip>
      </el-button-group>

      <el-divider direction="vertical" />

      <el-button @click.stop="$emit('toggle-preview')" @mousedown.prevent :type="showPreview ? 'primary' : 'default'" size="small" tabindex="-1">
        <el-icon><View /></el-icon>
        {{ showPreview ? $t('tools.markdownEditor.toolbar.hidePreview') : $t('tools.markdownEditor.toolbar.showPreview') }}
      </el-button>
      <el-button @click.stop="$emit('clear-content')" @mousedown.prevent type="danger" plain size="small" tabindex="-1">
        <el-icon><Delete /></el-icon>
        {{ $t('common.clear') }}
      </el-button>
      <el-button @click.stop="$emit('export-markdown')" @mousedown.prevent type="success" size="small" tabindex="-1">
        <el-icon><Download /></el-icon>
        {{ $t('tools.markdownEditor.toolbar.export') }}
      </el-button>
    </div>

    <!-- 排版主题面板 -->
    <Teleport to="body">
      <div
        v-show="showTypographyThemes"
        class="theme-panel-overlay"
        @click.stop="showTypographyThemes = false"
        @mousedown.stop.prevent
      >
        <div
          ref="typographyPanel"
          class="theme-panel typography-panel"
          :style="{ top: typographyPanelPosition.top + 'px', left: typographyPanelPosition.left + 'px' }"
          @click.stop
          @mousedown.stop.prevent
        >
          <div class="theme-panel-header">
            <span class="theme-panel-title">📖 {{ $t('tools.markdownEditor.toolbar.typographyTheme') }}</span>
            <el-button @click.stop="showTypographyThemes = false" type="text" size="small">✕</el-button>
          </div>
          <div class="theme-grid">
            <div
              v-for="theme in typographyThemes"
              :key="theme.id"
              @click.stop="selectTypographyTheme(theme)"
              @mousedown.stop.prevent
              class="theme-item"
              :class="{ active: currentTypographyTheme === theme.id }"
            >
              <div class="theme-preview">
                <div class="preview-content" :class="`typography-${theme.id}`">
                  <h3>{{ $t(`tools.markdownEditor.typographyThemes.${theme.id}`) }}</h3>
                  <p>{{ $t(`tools.markdownEditor.typographyThemes.${theme.id}Desc`) }}</p>
                  <p><em>{{ $t('tools.markdownEditor.toolbar.sampleText') }}：{{ $t(`tools.markdownEditor.typographyThemes.${theme.id}Sample`) }}</em></p>
                </div>
              </div>
              <div class="theme-info">
                <div class="theme-name">{{ $t(`tools.markdownEditor.typographyThemes.${theme.id}`) }}</div>
                <div class="theme-desc">{{ $t(`tools.markdownEditor.typographyThemes.${theme.id}Desc`) }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- 代码主题面板 -->
    <Teleport to="body">
      <div
        v-show="showCodeThemes"
        class="theme-panel-overlay"
        @click.stop="showCodeThemes = false"
        @mousedown.stop.prevent
      >
        <div
          ref="codePanel"
          class="theme-panel code-panel"
          :style="{ top: codePanelPosition.top + 'px', left: codePanelPosition.left + 'px' }"
          @click.stop
          @mousedown.stop.prevent
        >
          <div class="theme-panel-header">
            <span class="theme-panel-title">💻 {{ $t('tools.markdownEditor.toolbar.codeTheme') }}</span>
            <el-button @click.stop="showCodeThemes = false" type="text" size="small">✕</el-button>
          </div>
          <div class="theme-grid">
            <div
              v-for="theme in codeThemes"
              :key="theme.id"
              @click.stop="selectCodeTheme(theme)"
              @mousedown.stop.prevent
              class="theme-item"
              :class="{ active: currentCodeTheme === theme.id }"
            >
              <div class="theme-preview">
                <div class="preview-content" :class="`code-${theme.id}`">
                  <pre><code>{{ theme.sample }}</code></pre>
                </div>
              </div>
              <div class="theme-info">
                <div class="theme-name">{{ $t(`tools.markdownEditor.codeThemes.${theme.id}`) }}</div>
                <div class="theme-desc">{{ $t(`tools.markdownEditor.codeThemes.${theme.id}Desc`) }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script>
import { ArrowLeft, View, Delete, Download, Edit, Grid } from '@element-plus/icons-vue'
import { typographyThemes, codeThemes } from './themes.js'

export default {
  name: 'MarkdownEditorToolbar',
  components: {
    ArrowLeft,
    View,
    Delete,
    Download
  },
  props: {
    showPreview: {
      type: Boolean,
      default: true
    }
  },
  emits: ['back', 'insert-format', 'toggle-preview', 'clear-content', 'export-markdown', 'switch-layout', 'theme-change', 'typography-theme-change', 'code-theme-change'],
  data() {
    return {
      showEmojiPicker: false,
      emojiPickerPosition: { top: 0, left: 0 },
      currentTheme: 'default',
      // 主题面板状态
      showTypographyThemes: false,
      showCodeThemes: false,
      typographyPanelPosition: { top: 0, left: 0 },
      codePanelPosition: { top: 0, left: 0 },
      currentTypographyTheme: 'classic',
      currentCodeTheme: 'github',
      // 从外部配置文件导入主题数据
      typographyThemes: typographyThemes,
      codeThemes: codeThemes,
      emojiList: [
        '😀', '😃', '😄', '😁', '😆', '😅', '😂', '🤣', '😊', '😇',
        '🙂', '🙃', '😉', '😌', '😍', '🥰', '😘', '😗', '😙', '😚',
        '😋', '😛', '😝', '😜', '🤪', '🤨', '🧐', '🤓', '😎', '🤩',
        '🥳', '😏', '😒', '😞', '😔', '😟', '😕', '🙁', '☹️', '😣',
        '😖', '😫', '😩', '🥺', '😢', '😭', '😤', '😠', '😡', '🤬',
        '🤯', '😳', '🥵', '🥶', '😱', '😨', '😰', '😥', '😓', '🤗',
        '🤭', '🤫', '🤥', '😶', '😐', '😑', '😬', '🙄', '😯',
        '😦', '😧', '😮', '😲', '🥱', '😴', '🤤', '😪', '😵', '🤐',
        '🥴', '🤢', '🤮', '🤧', '😷', '🤒', '🤕', '🤑', '🤠', '😈',
        '👿', '👹', '👺', '🤡', '💩', '👻', '💀', '☠️', '👽', '👾',
        '🤖', '🎃', '😺', '😸', '😹', '😻', '😼', '😽', '🙀', '😿',
        '😾', '👍', '👎', '👌', '✌️', '🤞', '🤟', '🤘', '🤙', '👈',
        '👉', '👆', '🖕', '👇', '☝️', '👋', '🤚', '🖐️', '✋', '🖖',
        '👏', '🙌', '🤲', '🤝', '🙏', '✍️', '💅', '🤳', '💪', '🦾',
        '🦿', '🦵', '🦶', '👂', '🦻', '👃', '🧠', '🫀', '🫁', '🦷',
        '🦴', '👀', '👁️', '👅', '👄', '💋', '🩸', '❤️', '🧡', '💛',
        '💚', '💙', '💜', '🖤', '🤍', '🤎', '💔', '❤️‍🔥', '❤️‍🩹', '💕',
        '💞', '💓', '💗', '💖', '💘', '💝', '💟', '☮️', '✝️', '☪️',
        '🕉️', '☸️', '✡️', '🔯', '🕎', '☯️', '☦️', '🛐', '⛎', '♈',
        '♉', '♊', '♋', '♌', '♍', '♎', '♏', '♐', '♑', '♒',
        '♓', '🆔', '⚛️', '🉑', '☢️', '☣️', '📴', '📳', '🈶', '🈚',
        '🈸', '🈺', '🈷️', '✴️', '❇️', '™️', '🎌', '🔰', '🔱', '⚜️'
      ]
    }
  },
  mounted() {
    // 点击外部关闭表情符号面板
    document.addEventListener('click', this.handleClickOutside)
    // 监听窗口大小变化，重新计算面板位置
    window.addEventListener('resize', this.recalculatePanelPositions)
    // 监听滚动事件，重新计算面板位置
    window.addEventListener('scroll', this.recalculatePanelPositions)
  },
  beforeUnmount() {
    document.removeEventListener('click', this.handleClickOutside)
    window.removeEventListener('resize', this.recalculatePanelPositions)
    window.removeEventListener('scroll', this.recalculatePanelPositions)
  },
  methods: {
    handleEmojiButtonClick(event) {
      // 确保阻止所有可能的事件传播
      event.preventDefault()
      event.stopPropagation()
      event.stopImmediatePropagation()

      // 切换表情符号面板显示状态
      this.showEmojiPicker = !this.showEmojiPicker
    },
    toggleEmojiPicker() {
      this.showEmojiPicker = !this.showEmojiPicker
    },
    insertEmoji(emoji) {
      this.$emit('insert-format', 'emoji', emoji)
      this.showEmojiPicker = false
    },
    closeEmojiPicker() {
      this.showEmojiPicker = false
    },
    calculateEmojiPickerPosition() {
      // 计算表情符号按钮的位置
      const emojiButton = this.$el.querySelector('.toolbar-center .el-button-group:last-child .el-button')
      if (emojiButton) {
        const rect = emojiButton.getBoundingClientRect()
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop
        const scrollLeft = window.pageXOffset || document.documentElement.scrollLeft

        // 将面板定位在按钮下方居中
        this.emojiPickerPosition = {
          top: rect.bottom + scrollTop + 5, // 按钮下方5px
          left: rect.left + scrollLeft + (rect.width / 2) - 176 // 居中，面板宽度352px的一半
        }
      }
    },
    handleClickOutside(event) {
      if (this.showEmojiPicker) {
        const emojiPicker = document.querySelector('.emoji-picker')
        const emojiButton = this.$el.querySelector('.toolbar-center .el-button-group:last-child .el-button')

        if (emojiPicker &&
            !emojiPicker.contains(event.target) &&
            emojiButton &&
            !emojiButton.contains(event.target)) {
          this.showEmojiPicker = false
        }
      }
    },
    handleThemeChange(theme) {
      this.currentTheme = theme
      this.$emit('theme-change', theme)
    },
    toggleTypographyThemes() {
      this.showTypographyThemes = !this.showTypographyThemes
      this.showCodeThemes = false
      this.showEmojiPicker = false
    },
    toggleCodeThemes() {
      this.showCodeThemes = !this.showCodeThemes
      this.showTypographyThemes = false
      this.showEmojiPicker = false
    },
    selectTypographyTheme(theme) {
      this.currentTypographyTheme = theme.id
      this.showTypographyThemes = false
      this.$emit('typography-theme-change', theme)
    },
    selectCodeTheme(theme) {
      this.currentCodeTheme = theme.id
      this.showCodeThemes = false
      this.$emit('code-theme-change', theme)
    },
    calculateTypographyPanelPosition() {
      // 计算排版主题按钮的位置
      const typographyButton = this.$el.querySelector('.toolbar-right .el-button-group:first-child .el-button:first-child')
      if (typographyButton) {
        const rect = typographyButton.getBoundingClientRect()
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop
        const scrollLeft = window.pageXOffset || document.documentElement.scrollLeft

        // 获取面板的实际尺寸
        const panelWidth = 400
        const panelHeight = 400

        // 计算最佳位置
        let top = rect.top + scrollTop - panelHeight - 10 // 按钮上方10px
        let left = rect.left + scrollLeft + (rect.width / 2) - (panelWidth / 2) // 居中

        // 确保面板不会超出视窗边界
        const viewportWidth = window.innerWidth
        const viewportHeight = window.innerHeight

        // 右侧边界检查
        if (left + panelWidth > viewportWidth + scrollLeft) {
          left = viewportWidth + scrollLeft - panelWidth - 10
        }

        // 左侧边界检查
        if (left < scrollLeft + 10) {
          left = scrollLeft + 10
        }

        // 上方空间不足时，显示在按钮下方
        if (top < scrollTop + 10) {
          top = rect.bottom + scrollTop + 10
        }

        // 下方空间不足时，显示在按钮上方
        if (top + panelHeight > viewportHeight + scrollTop) {
          top = rect.top + scrollTop - panelHeight - 10
        }

        this.typographyPanelPosition = {
          top: Math.max(10, top),
          left: Math.max(10, left)
        }
      }
    },
    calculateCodePanelPosition() {
      // 计算代码主题按钮的位置
      const codeButton = this.$el.querySelector('.toolbar-right .el-button-group:first-child .el-button:last-child')
      if (codeButton) {
        const rect = codeButton.getBoundingClientRect()
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop
        const scrollLeft = window.pageXOffset || document.documentElement.scrollLeft

        // 获取面板的实际尺寸
        const panelWidth = 400
        const panelHeight = 400

        // 计算最佳位置
        let top = rect.top + scrollTop - panelHeight - 10 // 按钮上方10px
        let left = rect.left + scrollLeft + (rect.width / 2) - (panelWidth / 2) // 居中

        // 确保面板不会超出视窗边界
        const viewportWidth = window.innerWidth
        const viewportHeight = window.innerHeight

        // 右侧边界检查
        if (left + panelWidth > viewportWidth + scrollLeft) {
          left = viewportWidth + scrollLeft - panelWidth - 10
        }

        // 左侧边界检查
        if (left < scrollLeft + 10) {
          left = scrollLeft + 10
        }

        // 上方空间不足时，显示在按钮下方
        if (top < scrollTop + 10) {
          top = rect.bottom + scrollTop + 10
        }

        // 下方空间不足时，显示在按钮上方
        if (top + panelHeight > viewportHeight + scrollTop) {
          top = rect.top + scrollTop - panelHeight - 10
        }

        this.codePanelPosition = {
          top: Math.max(10, top),
          left: Math.max(10, left)
        }
      }
    },
    // 重新计算面板位置的方法
    recalculatePanelPositions() {
      if (this.showTypographyThemes) {
        this.calculateTypographyPanelPosition()
      }
      if (this.showCodeThemes) {
        this.calculateCodePanelPosition()
      }
      if (this.showEmojiPicker) {
        this.calculateEmojiPickerPosition()
      }
    }
  },
  watch: {
    showEmojiPicker(newVal) {
      if (newVal) {
        // 延迟计算位置，确保DOM已更新
        this.$nextTick(() => {
          this.calculateEmojiPickerPosition()
        })
      }
    },
    showTypographyThemes(newVal) {
      if (newVal) {
        // 延迟计算位置，确保DOM已更新
        this.$nextTick(() => {
          this.calculateTypographyPanelPosition()
        })
      }
    },
    showCodeThemes(newVal) {
      if (newVal) {
        // 延迟计算位置，确保DOM已更新
        this.$nextTick(() => {
          this.calculateCodePanelPosition()
        })
      }
    }
  }
}
</script>

<style scoped>
.markdown-editor-toolbar {
  position: relative; /* 改为相对定位 */
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 20px;
  background-color: #fff;
  border-bottom: 1px solid #e6e6e6;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  flex-shrink: 0; /* 防止工具栏被压缩 */
  z-index: 1000; /* 确保工具栏本身有足够高的层级 */
}

.toolbar-left {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-shrink: 0;
}

.editor-title {
  font-size: 18px;
  font-weight: bold;
  color: #333;
}

.toolbar-center {
  display: flex;
  align-items: center;
  gap: 8px;
  overflow-x: auto;
  scrollbar-width: none;
  -ms-overflow-style: none;
  flex: 1;
  justify-content: center;
  margin: 0 20px;
}

.toolbar-center::-webkit-scrollbar {
  display: none;
}

.toolbar-right {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .toolbar-center {
    margin: 0 10px;
  }

  .editor-title {
    font-size: 16px;
  }
}

@media (max-width: 768px) {
  .markdown-editor-toolbar {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    padding: 8px 12px;
    flex-direction: column;
    gap: 8px;
    height: auto;
    min-height: 120px;
  }

  .toolbar-center {
    order: 3;
    width: 100%;
    margin: 0;
    justify-content: flex-start;
    overflow-x: auto;
    padding: 4px 0;
  }

  .toolbar-left {
    order: 1;
    width: 100%;
    justify-content: space-between;
  }

  .toolbar-right {
    order: 2;
    width: 100%;
    justify-content: center;
    flex-wrap: wrap;
  }

  .editor-title {
    display: none;
  }
}

@media (max-width: 480px) {
  .markdown-editor-toolbar {
    min-height: 140px;
  }

  .toolbar-center {
    gap: 4px;
  }

  .toolbar-right {
    gap: 4px;
  }

  /* 在小屏幕上隐藏一些不常用的按钮组 */
  .toolbar-center > :nth-child(5),
  .toolbar-center > :nth-child(7) {
    display: none;
  }
}

/* 确保工具栏在所有情况下都可见 */
.markdown-editor-toolbar {
  -webkit-transform: translateZ(0);
  transform: translateZ(0);
}

/* 防止工具栏内容溢出 */
.toolbar-center {
  min-width: 0;
}

/* 工具栏阴影增强 */
.markdown-editor-toolbar::after {
  content: '';
  position: absolute;
  bottom: -1px;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(0,0,0,0.1), transparent);
}

/* 滚动时的视觉反馈 */
.markdown-editor-toolbar.scroll-shadow {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

/* 毛玻璃效果增强 */
.markdown-editor-toolbar {
  background-color: rgba(255, 255, 255, 0.95);
}

/* 支持 Safari 的毛玻璃效果 */
@supports (backdrop-filter: blur(10px)) {
  .markdown-editor-toolbar {
    background-color: rgba(255, 255, 255, 0.8);
  }
}

/* 工具栏按钮悬停效果 */
.markdown-editor-toolbar :deep(.el-button:hover) {
  transform: translateY(-1px);
  transition: all 0.2s ease;
}

.markdown-editor-toolbar :deep(.el-button:active) {
  transform: translateY(0);
}

/* 工具提示样式优化 */
.markdown-editor-toolbar :deep(.el-tooltip__popper) {
  font-size: 12px;
  padding: 8px 12px;
}

/* 确保工具栏在高分辨率屏幕上清晰 */
@media (-webkit-min-device-pixel-ratio: 2), (min-resolution: 192dpi) {
  .markdown-editor-toolbar {
    border-bottom-width: 0.5px;
  }
}

/* 表情符号选择面板样式 */
.emoji-picker {
  position: absolute;
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  z-index: 10000;
  background-color: #fff;
  border: 1px solid #e6e6e6;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  width: 352px; /* 精确计算：10*28 + 9*4 + 2*8 = 280 + 36 + 16 = 332px，留8px余量 */
  max-width: 352px;
  height: 320px; /* 增加高度：显示约9行表情，头部32px + 网格288px */
  max-height: 320px;
  overflow: hidden;
  animation: emojiFadeIn 0.2s ease-out;
}

.emoji-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background-color: #f8f9fa;
  border-bottom: 1px solid #e6e6e6;
  font-size: 12px;
  font-weight: bold;
  color: #333;
}

.emoji-grid {
  display: grid;
  grid-template-columns: repeat(10, 1fr);
  gap: 4px;
  padding: 8px;
  height: 272px; /* 面板总高320px - 头部32px - 内边距16px = 272px */
  max-height: 272px;
  overflow-y: auto;
  scrollbar-width: thin;
  scrollbar-color: #ccc transparent;
}

.emoji-grid::-webkit-scrollbar {
  width: 4px;
}

.emoji-grid::-webkit-scrollbar-track {
  background: transparent;
}

.emoji-grid::-webkit-scrollbar-thumb {
  background: #ccc;
  border-radius: 2px;
}

.emoji-grid::-webkit-scrollbar-thumb:hover {
  background: #999;
}

.emoji-button {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border: none;
  background: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 18px;
  transition: all 0.15s ease;
  user-select: none;
}

.emoji-button:hover {
  background-color: #f0f0f0;
  transform: scale(1.1);
}

.emoji-button:active {
  background-color: #e6e6e6;
  transform: scale(0.95);
}

/* 表情符号面板动画 */
@keyframes emojiFadeIn {
  from {
    opacity: 0;
    transform: translateX(-50%) translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateX(-50%) translateY(0);
  }
}

/* 响应式表情符号面板 */
@media (max-width: 768px) {
  .emoji-picker {
    max-width: 280px;
    max-height: 180px;
  }

  .emoji-grid {
    grid-template-columns: repeat(8, 1fr);
    gap: 2px;
    padding: 6px;
    max-height: 140px;
  }

  .emoji-button {
    width: 24px;
    height: 24px;
    font-size: 16px;
  }
}

@media (max-width: 480px) {
  .emoji-picker {
    max-width: 240px;
    max-height: 160px;
  }

  .emoji-grid {
    grid-template-columns: repeat(6, 1fr);
    gap: 2px;
    padding: 4px;
    max-height: 120px;
  }

  .emoji-button {
    width: 20px;
    height: 20px;
    font-size: 14px;
  }
}

/* 点击外部关闭表情符号面板 */
.emoji-picker::before {
  content: '';
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: -1;
}

/* 深色模式支持 */
@media (prefers-color-scheme: dark) {
  .markdown-editor-toolbar {
    background-color: rgba(24, 24, 24, 0.95);
    border-bottom-color: rgba(255, 255, 255, 0.1);
  }

  .editor-title {
    color: #e0e0e0;
  }

  .emoji-picker {
    background-color: rgba(24, 24, 24, 0.95);
    border-color: rgba(255, 255, 255, 0.1);
  }

  .emoji-header {
    background-color: rgba(32, 32, 32, 0.95);
    border-bottom-color: rgba(255, 255, 255, 0.1);
    color: #e0e0e0;
  }

  .emoji-button:hover {
    background-color: rgba(255, 255, 255, 0.1);
  }

  .emoji-button:active {
    background-color: rgba(255, 255, 255, 0.2);
  }
}

/* 主题选择器样式 */
.theme-selector {
  display: flex;
  align-items: center;
}

.theme-selector :deep(.el-select) {
  min-width: 120px;
}

.theme-option {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 0;
}

.theme-icon {
  font-size: 16px;
  width: 20px;
  text-align: center;
}

.theme-option span:last-child {
  font-size: 14px;
  color: #333;
}

/* 响应式主题选择器 */
@media (max-width: 768px) {
  .theme-selector {
    width: 100%;
    margin-bottom: 8px;
  }

  .theme-selector :deep(.el-select) {
    width: 100%;
    min-width: auto;
  }
}

@media (max-width: 480px) {
  .theme-selector :deep(.el-select) {
    font-size: 12px;
  }

  .theme-option {
    gap: 6px;
  }

  .theme-icon {
    font-size: 14px;
    width: 18px;
  }

  .theme-option span:last-child {
    font-size: 13px;
  }
}

/* 主题面板样式 */
.theme-panel-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 10000;
  pointer-events: none;
}

.theme-panel-overlay .theme-panel {
  position: absolute;
  pointer-events: auto;
  z-index: 10001;
}

.theme-panel {
  background-color: #fff;
  border: 1px solid #e6e6e6;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  width: 400px;
  max-width: 90vw;
  max-height: 70vh;
  overflow: hidden;
  animation: themePanelFadeIn 0.2s ease-out;
}

.theme-panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background-color: #f8f9fa;
  border-bottom: 1px solid #e6e6e6;
  font-size: 14px;
  font-weight: bold;
  color: #333;
}

.theme-panel-title {
  display: flex;
  align-items: center;
  gap: 8px;
}

.theme-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 12px;
  padding: 16px;
  max-height: calc(70vh - 60px);
  overflow-y: auto;
  scrollbar-width: thin;
  scrollbar-color: #ccc transparent;
}

.theme-grid::-webkit-scrollbar {
  width: 4px;
}

.theme-grid::-webkit-scrollbar-track {
  background: transparent;
}

.theme-grid::-webkit-scrollbar-thumb {
  background: #ccc;
  border-radius: 2px;
}

.theme-grid::-webkit-scrollbar-thumb:hover {
  background: #999;
}

.theme-item {
  display: flex;
  flex-direction: column;
  border: 2px solid #e6e6e6;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
  overflow: hidden;
}

.theme-item:hover {
  border-color: #409eff;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.15);
}

.theme-item.active {
  border-color: #67c23a;
  background-color: rgba(103, 194, 58, 0.05);
}

.theme-preview {
  padding: 12px;
  background-color: #fafafa;
  border-bottom: 1px solid #e6e6e6;
  min-height: 100px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.theme-preview .preview-content {
  width: 100%;
  font-size: 12px;
  line-height: 1.4;
  text-align: left;
}

.theme-preview .preview-content h3 {
  margin: 0 0 8px 0;
  font-size: 14px;
  font-weight: bold;
  color: #333;
}

.theme-preview .preview-content p {
  margin: 4px 0;
  color: #666;
}

.theme-preview .preview-content em {
  color: #999;
  font-style: italic;
}

.theme-preview .preview-content pre {
  margin: 8px 0;
  padding: 8px;
  background-color: #f6f8fa;
  border-radius: 4px;
  font-size: 11px;
  line-height: 1.3;
  overflow: hidden;
  white-space: pre-wrap;
  word-break: break-all;
}

.theme-preview .preview-content code {
  background-color: #f6f8fa;
  padding: 2px 4px;
  border-radius: 3px;
  font-size: 11px;
  color: #d73a49;
}

.theme-info {
  padding: 12px;
  background-color: #fff;
}

.theme-name {
  font-size: 14px;
  font-weight: bold;
  color: #333;
  margin-bottom: 4px;
}

.theme-desc {
  font-size: 12px;
  color: #666;
  line-height: 1.4;
}

/* 主题面板动画 */
@keyframes themePanelFadeIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 响应式主题面板 */
@media (max-width: 768px) {
  .theme-panel {
    width: 350px;
    max-width: 95vw;
  }

  .theme-grid {
    grid-template-columns: 1fr;
    gap: 8px;
    padding: 12px;
  }

  .theme-item {
    flex-direction: row;
  }

  .theme-preview {
    flex: 1;
    min-height: auto;
    border-bottom: none;
    border-right: 1px solid #e6e6e6;
  }

  .theme-info {
    flex: 1;
  }
}

@media (max-width: 480px) {
  .theme-panel {
    width: 320px;
    max-width: 98vw;
  }

  .theme-grid {
    padding: 8px;
  }

  .theme-preview {
    padding: 8px;
  }

  .theme-info {
    padding: 8px;
  }

  .theme-name {
    font-size: 13px;
  }

  .theme-desc {
    font-size: 11px;
  }
}

/* 深色模式支持 */
@media (prefers-color-scheme: dark) {
  .theme-panel {
    background-color: rgba(24, 24, 24, 0.95);
    border-color: rgba(255, 255, 255, 0.1);
  }

  .theme-panel-header {
    background-color: rgba(32, 32, 32, 0.95);
    border-bottom-color: rgba(255, 255, 255, 0.1);
    color: #e0e0e0;
  }

  .theme-item {
    border-color: rgba(255, 255, 255, 0.1);
  }

  .theme-item:hover {
    border-color: #409eff;
  }

  .theme-item.active {
    border-color: #67c23a;
    background-color: rgba(103, 194, 58, 0.1);
  }

  .theme-preview {
    background-color: rgba(32, 32, 32, 0.95);
    border-bottom-color: rgba(255, 255, 255, 0.1);
  }

  .theme-preview .preview-content h3 {
    color: #e0e0e0;
  }

  .theme-preview .preview-content p {
    color: #cccccc;
  }

  .theme-preview .preview-content em {
    color: #999;
  }

  .theme-preview .preview-content pre {
    background-color: rgba(32, 32, 32, 0.95);
    border: 1px solid rgba(255, 255, 255, 0.1);
  }

  .theme-preview .preview-content code {
    background-color: rgba(32, 32, 32, 0.95);
    color: #ff7b72;
  }

  .theme-info {
    background-color: rgba(24, 24, 24, 0.95);
  }

  .theme-name {
    color: #e0e0e0;
  }

  .theme-desc {
    color: #cccccc;
  }
}

/* 主题按钮图标样式 */
.theme-btn-icon {
  font-size: 16px;
  line-height: 1;
}

/* 全局样式 - 表情符号面板 */
.emoji-picker-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 10000;
  pointer-events: none;
}

.emoji-picker-overlay .emoji-picker {
  position: absolute;
  pointer-events: auto;
  z-index: 10001;
}
</style>
