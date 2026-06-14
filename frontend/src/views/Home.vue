<template>
  <div class="home">
    <!-- Hero section (desktop) -->
    <div class="hero">
      <div class="hero-content">
        <div class="hero-badge">v2.0</div>
        <h1 class="hero-title">DevToolBox</h1>
        <p class="hero-desc">{{ t('tools.home.desc1') }}</p>
      </div>
      <div class="hero-bg-icon">
        <span class="material-symbols-rounded">developer_board</span>
      </div>
    </div>

    <!-- Quick tools (desktop: single-item categories) -->
    <div v-if="quickTools.length" class="quick-section">
      <div class="section-header">
        <span class="material-symbols-rounded section-icon">bolt</span>
        <h2>{{ t('tools.home.quickAccess') || 'Quick Access' }}</h2>
      </div>
      <div class="quick-grid">
        <div
          v-for="tool in quickTools"
          :key="tool.id"
          class="quick-card"
          role="button"
          tabindex="0"
          :aria-label="t('categories.' + tool.id + '.name')"
          @click="$router.push(tool.route)"
          @keydown="onCardKeydown($event, tool.route)"
        >
          <div class="quick-icon" :style="{ background: tool.color + '15', color: tool.color }">
            <span class="material-symbols-rounded">{{ tool.icon }}</span>
          </div>
          <div class="quick-info">
            <span class="quick-name">{{ t('categories.' + tool.id + '.name') }}</span>
            <span class="quick-desc">{{ t('categories.' + tool.id + '.description') }}</span>
          </div>
          <span class="material-symbols-rounded quick-arrow">arrow_forward</span>
        </div>
      </div>
    </div>

    <!-- All tool categories (desktop) -->
    <div class="section-header">
      <span class="material-symbols-rounded section-icon">grid_view</span>
      <h2>{{ t('tools.home.allTools') || 'All Tools' }}</h2>
    </div>
    <div class="categories-grid">
      <div
        v-for="category in multiToolCategories"
        :key="category.id"
        class="category-card"
        role="button"
        tabindex="0"
        :aria-label="t('categories.' + category.id + '.name')"
        @click="$router.push(category.route)"
        @keydown="onCardKeydown($event, category.route)"
      >
        <div class="card-icon" :style="{ color: category.color }">
          <span class="material-symbols-rounded">{{ category.icon }}</span>
        </div>
        <div class="card-body">
          <h3 class="card-title">{{ t('categories.' + category.id + '.name') }}</h3>
          <p class="card-desc">{{ t('categories.' + category.id + '.description') }}</p>
          <div class="card-tags">
            <span
              v-for="tool in category.tools.slice(0, 4)"
              :key="tool"
              class="tag"
            >{{ t('categories.' + category.id + '.tools.' + tool) }}</span>
            <span v-if="category.tools.length > 4" class="tag tag-more">+{{ category.tools.length - 4 }}</span>
          </div>
        </div>
        <span class="material-symbols-rounded card-arrow">chevron_right</span>
      </div>
    </div>

    <!-- Mobile: Function Matrix -->
    <template v-if="deviceStore.isMobile">
      <!-- Search -->
      <div class="mobile-search">
        <span class="material-symbols-rounded mobile-search-icon">search</span>
        <input
          v-model="searchQuery"
          type="text"
          :placeholder="t('tools.home.searchPlaceholder') || '搜索工具...'"
          class="mobile-search-input"
        />
        <span v-if="searchQuery" class="material-symbols-rounded mobile-search-clear" @click="searchQuery = ''">close</span>
      </div>

      <!-- Recently used tools -->
      <div v-if="!searchQuery && recentTools.length" class="recent-section">
        <div class="recent-header">
          <span class="material-symbols-rounded" style="font-size:16px; color: var(--dt-text-secondary);">history</span>
          <span class="recent-title">{{ t('tools.home.recentlyUsed') || '最近使用' }}</span>
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

      <!-- Tool matrix grid -->
      <div class="mobile-matrix">
        <div
          v-for="(tool, index) in visibleTools"
          :key="tool.route"
          class="matrix-item"
          :style="{ '--item-color': tool.color }"
          role="button"
          tabindex="0"
          :aria-label="tool.label"
          @click="$router.push(tool.route)"
          @keydown="onCardKeydown($event, tool.route)"
        >
          <div class="matrix-icon" :style="{ background: tool.color + '15', color: tool.color }">
            <span class="material-symbols-rounded">{{ tool.icon }}</span>
          </div>
          <span class="matrix-label">{{ tool.label }}</span>
        </div>
      </div>

      <!-- No results -->
      <div v-if="searchQuery && filteredTools.length === 0" class="matrix-empty">
        <span class="material-symbols-rounded" style="font-size: 32px; color: var(--dt-text-placeholder);">search_off</span>
        <span style="font-size: 13px; color: var(--dt-text-secondary);">{{ t('tools.home.noResults') || '没有找到匹配的工具' }}</span>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { useDeviceStore } from '@/stores/device.js'
import { toolCategories } from '../data/toolCategories'
import { getRecentTools } from '@/composables/useRecentTools'

const { t } = useI18n()
const deviceStore = useDeviceStore()
const router = useRouter()

// Keyboard navigation for cards: Enter / Space activate, like a native button
function onCardKeydown(event, route) {
  if (event.key === 'Enter' || event.key === ' ' || event.key === 'Spacebar') {
    event.preventDefault()
    router.push(route)
  }
}

const searchQuery = ref('')

const quickTools = computed(() =>
  toolCategories.filter(cat => cat.tools.length === 1)
)

const multiToolCategories = computed(() =>
  toolCategories.filter(cat => cat.tools.length > 1)
)

// Per-tool unique icons (shared by allTools and recentTools)
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

// Flat list of all tool entries for the mobile matrix
const allTools = computed(() => {
  const routeMap = {
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

  const result = []
  toolCategories.forEach(cat => {
    const routes = routeMap[cat.id] || []
    routes.forEach(r => {
      result.push({
        route: r.route,
        label: t(r.labelKey),
        icon: routeIconMap[r.route] || cat.icon,
        color: cat.color,
      })
    })
  })
  return result
})

const recentTools = computed(() => {
  return getRecentTools().map(t => ({ ...t, icon: routeIconMap[t.route] || t.icon }))
})

const filteredTools = computed(() => {
  if (!searchQuery.value) return allTools.value
  const q = searchQuery.value.toLowerCase()
  return allTools.value.filter(t =>
    t.label.toLowerCase().includes(q) ||
    t.route.toLowerCase().includes(q)
  )
})

const visibleTools = computed(() => {
  if (searchQuery.value) return filteredTools.value
  return allTools.value
})
</script>

<style scoped>
.home {
  padding: var(--dt-spacing-lg);
  max-width: var(--dt-content-max-width);
  margin: 0 auto;
}

/* =========================================
   Hero
   ========================================= */
.hero {
  position: relative;
  padding: 40px 32px;
  border-radius: var(--dt-radius-xl);
  background: linear-gradient(135deg, var(--dt-primary) 0%, #6366f1 100%);
  color: #fff;
  margin-bottom: 32px;
  overflow: hidden;
}

.hero-content {
  position: relative;
  z-index: 1;
}

.hero-badge {
  display: inline-block;
  padding: 2px 10px;
  background: rgba(255,255,255,0.2);
  border-radius: 99px;
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.5px;
  margin-bottom: 12px;
  backdrop-filter: blur(4px);
}

.hero-title {
  font-size: 32px;
  font-weight: 700;
  margin: 0 0 8px;
  letter-spacing: -0.5px;
}

.hero-desc {
  font-size: 15px;
  opacity: 0.85;
  margin: 0;
  max-width: 480px;
  line-height: 1.5;
}

.hero-bg-icon {
  position: absolute;
  right: -10px;
  bottom: -20px;
  opacity: 0.08;
  pointer-events: none;
}

.hero-bg-icon .material-symbols-rounded {
  font-size: 180px;
}

/* =========================================
   Section headers
   ========================================= */
.section-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
}

.section-header h2 {
  font-size: 18px;
  font-weight: 600;
  margin: 0;
  color: var(--dt-text-primary);
}

.section-icon {
  font-size: 20px;
  color: var(--dt-text-secondary);
}

/* =========================================
   Quick Access (single-item categories)
   ========================================= */
.quick-section {
  margin-bottom: 32px;
}

.quick-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.quick-card {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 16px 20px;
  background: var(--dt-bg-card);
  border: 1px solid var(--dt-border-lighter);
  border-radius: var(--dt-radius-lg);
  cursor: pointer;
  transition: all 0.2s ease;
}

.quick-card:hover {
  border-color: var(--dt-primary);
  box-shadow: var(--dt-shadow-sm);
  transform: translateY(-1px);
}

.quick-card:focus-visible {
  outline: 2px solid var(--dt-primary);
  outline-offset: 2px;
}

.quick-icon {
  width: 44px;
  height: 44px;
  border-radius: var(--dt-radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.quick-icon .material-symbols-rounded {
  font-size: 22px;
}

.quick-info {
  flex: 1;
  min-width: 0;
}

.quick-name {
  display: block;
  font-size: 15px;
  font-weight: 600;
  color: var(--dt-text-primary);
}

.quick-desc {
  display: block;
  font-size: 12px;
  color: var(--dt-text-secondary);
  margin-top: 2px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.quick-arrow {
  font-size: 18px;
  color: var(--dt-text-placeholder);
  flex-shrink: 0;
}

/* =========================================
   Categories Grid (multi-item)
   ========================================= */
.categories-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.category-card {
  display: flex;
  align-items: flex-start;
  gap: 14px;
  padding: 20px;
  background: var(--dt-bg-card);
  border: 1px solid var(--dt-border-lighter);
  border-radius: var(--dt-radius-lg);
  cursor: pointer;
  transition: all 0.2s ease;
}

.category-card:hover {
  border-color: var(--dt-primary);
  box-shadow: var(--dt-shadow-md);
  transform: translateY(-2px);
}

.category-card:focus-visible {
  outline: 2px solid var(--dt-primary);
  outline-offset: 2px;
}

.card-icon {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  border-radius: var(--dt-radius-md);
  background: var(--dt-bg-section);
}

.card-icon .material-symbols-rounded {
  font-size: 22px;
}

.card-body {
  flex: 1;
  min-width: 0;
}

.card-title {
  font-size: 15px;
  font-weight: 600;
  margin: 0 0 4px;
  color: var(--dt-text-primary);
}

.card-desc {
  font-size: 13px;
  color: var(--dt-text-secondary);
  margin: 0 0 10px;
  line-height: 1.4;
}

.card-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.tag {
  display: inline-block;
  padding: 2px 8px;
  background: var(--dt-bg-section);
  border-radius: 4px;
  font-size: 11px;
  color: var(--dt-text-secondary);
  white-space: nowrap;
}

.tag-more {
  color: var(--dt-primary);
  font-weight: 600;
}

.card-arrow {
  font-size: 20px;
  color: var(--dt-text-placeholder);
  flex-shrink: 0;
  margin-top: 2px;
}

/* =========================================
   Mobile: Search
   ========================================= */
.mobile-search {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 0 2px 14px;
  position: relative;
}

.mobile-search-icon {
  font-size: 20px;
  color: var(--dt-text-placeholder);
  flex-shrink: 0;
}

.mobile-search-input {
  flex: 1;
  height: 38px;
  border: 1px solid var(--dt-border-light);
  border-radius: var(--dt-radius-md);
  padding: 0 32px 0 12px;
  font-size: 14px;
  color: var(--dt-text-primary);
  background: var(--dt-bg-card);
  outline: none;
  transition: border-color 0.2s;
}

.mobile-search-input::placeholder {
  color: var(--dt-text-placeholder);
}

.mobile-search-input:focus {
  border-color: var(--dt-primary);
}

.mobile-search-clear {
  position: absolute;
  right: 10px;
  font-size: 18px;
  color: var(--dt-text-secondary);
  cursor: pointer;
}

/* =========================================
   Mobile: Recently Used
   ========================================= */
.recent-section {
  margin-bottom: 16px;
}

.recent-header {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-bottom: 8px;
  padding: 0 2px;
}

.recent-title {
  font-size: 12px;
  font-weight: 500;
  color: var(--dt-text-secondary);
}

.recent-scroll {
  display: flex;
  gap: 8px;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: none;
  padding-bottom: 2px;
}

.recent-scroll::-webkit-scrollbar {
  display: none;
}

.recent-chip {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  background: var(--dt-bg-card);
  border: 1px solid var(--dt-border-lighter);
  border-radius: 99px;
  cursor: pointer;
  flex-shrink: 0;
  -webkit-tap-highlight-color: transparent;
  user-select: none;
  transition: background 0.15s;
}

.recent-chip:active {
  background: var(--dt-bg-hover);
}

.recent-chip-icon {
  width: 22px;
  height: 22px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.recent-chip-icon .material-symbols-rounded {
  font-size: 14px;
}

.recent-chip-label {
  font-size: 12px;
  font-weight: 500;
  color: var(--dt-text-primary);
  white-space: nowrap;
}

/* =========================================
   Mobile: Empty state
   ========================================= */
.matrix-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 32px 16px;
}

/* =========================================
   Mobile: Function Matrix
   ========================================= */
.mobile-matrix {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
}

.matrix-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  padding: 14px 6px 12px;
  background: var(--dt-bg-card);
  border: 1px solid var(--dt-border-lighter);
  border-radius: var(--dt-radius-lg);
  cursor: pointer;
  transition: all 0.15s ease;
  -webkit-tap-highlight-color: transparent;
  user-select: none;
}

.matrix-item:active {
  background: var(--dt-bg-hover);
  transform: scale(0.97);
}

.matrix-item:focus-visible,
.recent-chip:focus-visible {
  outline: 2px solid var(--dt-primary);
  outline-offset: 2px;
}

.matrix-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.matrix-icon .material-symbols-rounded {
  font-size: 20px;
}

.matrix-label {
  font-size: 11px;
  font-weight: 500;
  color: var(--dt-text-primary);
  text-align: center;
  line-height: 1.2;
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* =========================================
   Responsive
   ========================================= */
@media (max-width: 768px) {
  .home {
    padding: var(--dt-spacing-sm);
  }

  .hero,
  .quick-section,
  .section-header,
  .quick-grid,
  .categories-grid {
    display: none;
  }
}
</style>
