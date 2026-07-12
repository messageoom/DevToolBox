<template>
  <div class="home">
    <!-- 搜索框(桌面 + 移动统一) -->
    <div class="home-search" :class="{ 'is-focused': searchFocused }">
      <span class="material-symbols-rounded home-search-icon">search</span>
      <input
        v-model="searchQuery"
        type="text"
        :placeholder="t('tools.home.searchPlaceholder') || '搜索工具...'"
        class="home-search-input"
        @focus="searchFocused = true"
        @blur="searchFocused = false"
      />
      <span
        v-if="searchQuery"
        class="material-symbols-rounded home-search-clear"
        role="button"
        :aria-label="t('tools.home.clear') || '清除'"
        @click="searchQuery = ''"
      >close</span>
    </div>

    <!-- 最近使用(无搜索时显示) -->
    <div v-if="!searchQuery && recentTools.length" class="recent-section">
      <div class="recent-header">
        <span class="material-symbols-rounded recent-header-icon">history</span>
        <span class="recent-header-title">{{ t('tools.home.recentlyUsed') || '最近使用' }}</span>
      </div>
      <div class="recent-scroll">
        <div
          v-for="tool in recentTools"
          :key="'recent-' + tool.route"
          class="recent-chip"
          role="button"
          tabindex="0"
          :aria-label="tool.label"
          @click="$router.push(tool.route)"
          @keydown="onCardKeydown($event, tool.route)"
        >
          <div class="recent-chip-icon" :style="{ background: tool.color + '15', color: tool.color }">
            <span class="material-symbols-rounded">{{ tool.icon }}</span>
          </div>
          <span class="recent-chip-label">{{ tool.label }}</span>
        </div>
      </div>
    </div>

    <!-- 搜索结果(有搜索词时) -->
    <template v-if="searchQuery">
      <div v-if="filteredTools.length === 0" class="search-empty">
        <span class="material-symbols-rounded search-empty-icon">search_off</span>
        <span class="search-empty-text">{{ t('tools.home.noResults') || '没有找到匹配的工具' }}</span>
      </div>
      <div v-else class="tools-grid">
        <div
          v-for="tool in filteredTools"
          :key="tool.route"
          class="tool-card"
          role="button"
          tabindex="0"
          :aria-label="tool.label"
          @click="$router.push(tool.route)"
          @keydown="onCardKeydown($event, tool.route)"
        >
          <div class="tool-card-icon" :style="{ background: tool.color + '15', color: tool.color }">
            <span class="material-symbols-rounded">{{ tool.icon }}</span>
          </div>
          <span class="tool-card-label">{{ tool.label }}</span>
        </div>
      </div>
    </template>

    <!-- 全部工具:按分类分组(无搜索时) -->
    <template v-else>
      <section
        v-for="group in groupedTools"
        :key="group.id"
        class="tool-group"
      >
        <div class="tool-group-header">
          <span class="material-symbols-rounded tool-group-icon" :style="{ color: group.color }">{{ group.icon }}</span>
          <span class="tool-group-title">{{ group.name }}</span>
          <span class="tool-group-count">{{ group.tools.length }}</span>
        </div>
        <div class="tools-grid">
          <div
            v-for="tool in group.tools"
            :key="tool.route"
            class="tool-card"
            role="button"
            tabindex="0"
            :aria-label="tool.label"
            @click="$router.push(tool.route)"
            @keydown="onCardKeydown($event, tool.route)"
          >
            <div class="tool-card-icon" :style="{ background: tool.color + '15', color: tool.color }">
              <span class="material-symbols-rounded">{{ tool.icon }}</span>
            </div>
            <span class="tool-card-label">{{ tool.label }}</span>
          </div>
        </div>
      </section>
    </template>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { toolCategories } from '../data/toolCategories'
import { getRecentTools } from '@/composables/useRecentTools'

const { t } = useI18n()
const router = useRouter()

// 卡片键盘导航:Enter / Space 触发,如同原生 button
function onCardKeydown(event, route) {
  if (event.key === 'Enter' || event.key === ' ' || event.key === 'Spacebar') {
    event.preventDefault()
    router.push(route)
  }
}

const searchQuery = ref('')
const searchFocused = ref(false)

// 每个 route 对应的图标(工具卡片用)
const routeIconMap = {
  '/file-upload': 'upload_file',
  '/text-transfer': 'chat',
  '/json-tools': 'data_object',
  '/yaml-tools': 'code_blocks',
  '/markdown-tools': 'article',
  '/data-conversion': 'transform',
  '/markdown-editor': 'edit_note',
  '/base64-tools': 'swap_horiz',
  '/url-tools': 'link',
  '/hash-tools': 'tag',
  '/crypto-tools': 'enhanced_encryption',
  '/timestamp-tools': 'schedule',
  '/time-calculator': 'timer',
  '/uuid-tools': 'fingerprint',
  '/password-tools': 'password',
  '/apikey-tools': 'key',
  '/jwt-debugger': 'encrypted',
  '/diff-tool': 'difference',
  '/qr-tools': 'qr_code_2',
  '/case-converter': 'text_fields',
  '/sql-formatter': 'storage',
  '/base-converter': 'pin',
  '/dummy-data': 'dataset',
  '/regex-tester': 'find_in_page',
  '/cron-parser': 'event_repeat',
  '/json-to-ts': 'data_array',
  '/image-tools': 'image',
  '/color-tools': 'palette',
}

// 每个分类下的工具(route + i18n labelKey),用于展开成扁平工具列表
const categoryToolsMap = {
  file: [
    { route: '/file-upload', labelKey: 'sidebar.fileUpload' },
    { route: '/image-tools', labelKey: 'sidebar.imageTools' },
  ],
  transfer: [{ route: '/text-transfer', labelKey: 'sidebar.textTransfer' }],
  data: [
    { route: '/json-tools', labelKey: 'sidebar.jsonTools' },
    { route: '/yaml-tools', labelKey: 'sidebar.yamlTools' },
    { route: '/markdown-tools', labelKey: 'sidebar.markdownTools' },
    { route: '/data-conversion', labelKey: 'sidebar.dataConversion' },
    { route: '/markdown-editor', labelKey: 'sidebar.markdownEditor' },
    { route: '/json-to-ts', labelKey: 'sidebar.jsonToTs' },
  ],
  text: [
    { route: '/case-converter', labelKey: 'sidebar.caseConverter' },
    { route: '/sql-formatter', labelKey: 'sidebar.sqlFormatter' },
  ],
  encoding: [
    { route: '/base64-tools', labelKey: 'sidebar.base64Tools' },
    { route: '/url-tools', labelKey: 'sidebar.urlTools' },
    { route: '/base-converter', labelKey: 'sidebar.baseConverter' },
  ],
  crypto: [
    { route: '/hash-tools', labelKey: 'sidebar.hashTools' },
    { route: '/crypto-tools', labelKey: 'sidebar.cryptoTools' },
  ],
  time: [
    { route: '/timestamp-tools', labelKey: 'sidebar.timestampTools' },
    { route: '/time-calculator', labelKey: 'sidebar.timeCalculator' },
    { route: '/cron-parser', labelKey: 'sidebar.cronParser' },
  ],
  generator: [
    { route: '/uuid-tools', labelKey: 'sidebar.uuidTools' },
    { route: '/password-tools', labelKey: 'sidebar.passwordTools' },
    { route: '/apikey-tools', labelKey: 'sidebar.apikeyTools' },
    { route: '/jwt-debugger', labelKey: 'sidebar.jwtDebugger' },
    { route: '/diff-tool', labelKey: 'sidebar.diffTool' },
    { route: '/dummy-data', labelKey: 'sidebar.dummyData' },
    { route: '/regex-tester', labelKey: 'sidebar.regexTester' },
  ],
  other: [
    { route: '/qr-tools', labelKey: 'sidebar.qrTools' },
    { route: '/color-tools', labelKey: 'sidebar.colorTools' },
  ],
}

// 扁平工具列表(带 categoryId,用于分组与搜索)
const allTools = computed(() => {
  const result = []
  toolCategories.forEach(cat => {
    const tools = categoryToolsMap[cat.id] || []
    tools.forEach(r => {
      result.push({
        route: r.route,
        label: t(r.labelKey),
        icon: routeIconMap[r.route] || cat.icon,
        color: cat.color,
        categoryId: cat.id,
      })
    })
  })
  return result
})

// 按分类分组(无搜索时展示)
const groupedTools = computed(() =>
  toolCategories
    .map(cat => ({
      id: cat.id,
      icon: cat.icon,
      color: cat.color,
      name: t('categories.' + cat.id + '.name'),
      tools: allTools.value.filter(tool => tool.categoryId === cat.id),
    }))
    .filter(g => g.tools.length > 0)
)

// 搜索过滤结果
const filteredTools = computed(() => {
  if (!searchQuery.value) return []
  const q = searchQuery.value.toLowerCase()
  return allTools.value.filter(tool =>
    tool.label.toLowerCase().includes(q) || tool.route.toLowerCase().includes(q)
  )
})

// 最近使用(补图标)
const recentTools = computed(() =>
  getRecentTools().map(tool => ({ ...tool, icon: routeIconMap[tool.route] || tool.icon }))
)
</script>

<style scoped>
.home {
  padding: var(--dt-spacing-lg, 24px);
  max-width: var(--dt-content-max-width, 1100px);
  margin: 0 auto;
}

/* ============ 搜索框 ============ */
.home-search {
  position: relative;
  display: flex;
  align-items: center;
  max-width: 560px;
  margin: 0 auto 28px;
  background: var(--dt-bg-card);
  border: 2px solid var(--dt-border-lighter);
  border-radius: 999px;
  padding: 4px 8px 4px 20px;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}
.home-search.is-focused {
  border-color: var(--dt-primary);
  box-shadow: 0 0 0 4px color-mix(in srgb, var(--dt-primary) 15%, transparent);
}
.home-search-icon {
  font-size: 22px;
  color: var(--dt-text-secondary);
  margin-right: 10px;
  flex-shrink: 0;
}
.home-search-input {
  flex: 1;
  border: none;
  outline: none;
  background: transparent;
  font-size: 15px;
  color: var(--dt-text-primary);
  padding: 10px 0;
  min-width: 0;
}
.home-search-input::placeholder {
  color: var(--dt-text-placeholder);
}
.home-search-clear {
  font-size: 20px;
  color: var(--dt-text-secondary);
  cursor: pointer;
  padding: 8px;
  border-radius: 50%;
  transition: background 0.15s, color 0.15s;
}
.home-search-clear:hover {
  background: var(--dt-bg-hover);
  color: var(--dt-text-primary);
}

/* ============ 最近使用 ============ */
.recent-section {
  margin-bottom: 28px;
}
.recent-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  color: var(--dt-text-secondary);
  font-size: 13px;
  font-weight: 600;
}
.recent-header-icon {
  font-size: 18px;
}
.recent-scroll {
  display: flex;
  gap: 10px;
  overflow-x: auto;
  padding-bottom: 4px;
  scrollbar-width: thin;
}
.recent-chip {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 14px 8px 8px;
  background: var(--dt-bg-card);
  border: 1px solid var(--dt-border-lighter);
  border-radius: 999px;
  cursor: pointer;
  flex-shrink: 0;
  transition: border-color 0.15s, transform 0.15s, background 0.15s;
}
.recent-chip:hover {
  border-color: var(--dt-primary);
  transform: translateY(-1px);
  background: var(--dt-bg-hover);
}
.recent-chip-icon {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}
.recent-chip-icon .material-symbols-rounded {
  font-size: 18px;
}
.recent-chip-label {
  font-size: 13px;
  color: var(--dt-text-primary);
  white-space: nowrap;
}

/* ============ 分类分组 ============ */
.tool-group {
  margin-bottom: 28px;
}
.tool-group-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 14px;
  padding-bottom: 10px;
  border-bottom: 1px solid var(--dt-border-lighter);
}
.tool-group-icon {
  font-size: 20px;
}
.tool-group-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--dt-text-primary);
}
.tool-group-count {
  font-size: 12px;
  color: var(--dt-text-secondary);
  background: var(--dt-bg-section);
  padding: 1px 8px;
  border-radius: 99px;
}

/* ============ 工具卡片网格 ============ */
.tools-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(132px, 1fr));
  gap: 12px;
}
.tool-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 18px 10px;
  background: var(--dt-bg-card);
  border: 1px solid var(--dt-border-lighter);
  border-radius: var(--dt-radius-md, 10px);
  cursor: pointer;
  transition: transform 0.18s ease, border-color 0.18s ease, box-shadow 0.18s ease;
  text-align: center;
}
.tool-card:hover {
  transform: translateY(-3px);
  border-color: var(--dt-primary);
  box-shadow: 0 6px 18px rgba(0, 0, 0, 0.08);
}
.tool-card:focus-visible {
  outline: 2px solid var(--dt-primary);
  outline-offset: 2px;
}
.tool-card-icon {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.tool-card-icon .material-symbols-rounded {
  font-size: 24px;
}
.tool-card-label {
  font-size: 13px;
  font-weight: 500;
  color: var(--dt-text-primary);
  line-height: 1.3;
  word-break: break-word;
}

/* ============ 搜索无结果 ============ */
.search-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  padding: 60px 20px;
  color: var(--dt-text-secondary);
}
.search-empty-icon {
  font-size: 40px;
  color: var(--dt-text-placeholder);
}
.search-empty-text {
  font-size: 14px;
}

/* ============ 响应式 ============ */
@media (max-width: 768px) {
  .home {
    padding: 16px;
  }
  .home-search {
    max-width: 100%;
    margin-bottom: 20px;
  }
  .tools-grid {
    grid-template-columns: repeat(auto-fill, minmax(96px, 1fr));
    gap: 10px;
  }
  .tool-card {
    padding: 14px 6px;
    gap: 8px;
  }
  .tool-card-icon {
    width: 38px;
    height: 38px;
    border-radius: 10px;
  }
  .tool-card-icon .material-symbols-rounded {
    font-size: 21px;
  }
  .tool-card-label {
    font-size: 12px;
  }
  .tool-group {
    margin-bottom: 22px;
  }
}
</style>
