<template>
  <div id="app" :class="layoutClasses">
    <!-- Header (hidden in immersive editor mode) -->
    <header v-if="!isMarkdownEditor" class="app-header">
      <div class="header-left">
        <h1 class="app-title">DevToolBox</h1>
      </div>
      <div class="header-right">
        <el-dropdown @command="switchLang" class="lang-dropdown" trigger="click">
          <span class="lang-toggle">{{ locale === 'zh' ? '中文' : 'EN' }}</span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="zh">中文</el-dropdown-item>
              <el-dropdown-item command="en">English</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
        <el-switch
          :model-value="themeStore.isDark"
          inline-prompt
          :active-text="t('app.dark')"
          :inactive-text="t('app.light')"
          @change="themeStore.toggleTheme()"
          class="theme-switch"
        />
      </div>
    </header>

    <!-- Sidebar (desktop only, hidden in immersive editor mode) -->
    <aside
      v-if="!deviceStore.isMobile && !isMarkdownEditor"
      class="app-sidebar"
      :class="{ 'sidebar-collapsed': isSidebarCollapsed }"
    >
      <!-- Collapse toggle -->
      <div class="sidebar-collapse-btn">
        <el-button @click="isSidebarCollapsed = !isSidebarCollapsed" link>
          <el-icon>
            <Expand v-if="isSidebarCollapsed" />
            <Fold v-else />
          </el-icon>
        </el-button>
      </div>

      <el-menu
        :default-active="currentPath"
        :default-openeds="openedCategoryIds"
        :collapse="isSidebarCollapsed"
        :collapse-transition="false"
        router
        class="sidebar-menu"
        @select="onMenuSelect"
      >
        <!-- Home -->
        <el-menu-item index="/">
          <span class="material-symbols-rounded sidebar-icon">home</span>
          <template #title>{{ t('app.home') }}</template>
        </el-menu-item>

        <!-- Dynamic categories from toolCategories data -->
        <template v-for="category in sidebarCategories" :key="category.id">
          <!-- Single-item category: render as direct menu item (no sub-menu) -->
          <el-menu-item
            v-if="category.items.length === 1"
            :index="category.items[0].route"
          >
            <span class="material-symbols-rounded sidebar-icon">{{ category.icon }}</span>
            <template #title>{{ category.items[0].label }}</template>
          </el-menu-item>
          <!-- Multi-item category: render as sub-menu -->
          <el-sub-menu v-else :index="'cat-' + category.id">
            <template #title>
              <span class="material-symbols-rounded sidebar-icon">{{ category.icon }}</span>
              <span>{{ t('categories.' + category.id + '.name') }}</span>
            </template>
            <el-menu-item
              v-for="tool in category.items"
              :key="tool.route"
              :index="tool.route"
            >
              {{ tool.label }}
            </el-menu-item>
          </el-sub-menu>
        </template>
      </el-menu>
    </aside>

    <!-- Main content -->
    <main
      class="app-content"
      :class="{
        'content-full': deviceStore.isMobile,
        'content-markdown-editor': isMarkdownEditor,
      }"
    >
      <div class="content-wrapper" :class="{ 'content-wrapper--padded': !isMarkdownEditor }">
        <router-view v-slot="{ Component, route }">
          <transition name="page-slide" mode="out-in">
            <component :is="Component" :key="route.path" />
          </transition>
        </router-view>
      </div>
    </main>

    <!-- Mobile bottom navigation (hidden in immersive editor mode) -->
    <nav v-if="deviceStore.isMobile && !isMarkdownEditor" ref="bottomNavRef" class="app-bottom-nav">
      <router-link
        v-for="tab in mobileNavTabs"
        :key="tab.route"
        :to="tab.route"
        class="bottom-nav-item"
        :class="{ active: isTabActive(tab) }"
      >
        <span class="material-symbols-rounded bottom-nav-icon">{{ tab.icon }}</span>
        <span class="bottom-nav-label">{{ tab.label }}</span>
      </router-link>
    </nav>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useDeviceStore } from '@/stores/device.js'
import { useThemeStore } from '@/stores/theme.js'
import { toolCategories } from '@/data/toolCategories.js'
import { addRecentTool } from '@/composables/useRecentTools.js'
import {
  Expand,
  Fold,
} from '@element-plus/icons-vue'

// --- Stores ---
const { t, locale } = useI18n()
const deviceStore = useDeviceStore()
const themeStore = useThemeStore()
const route = useRoute()
const router = useRouter()

// --- Reactive state ---
const isSidebarCollapsed = ref(false)
const bottomNavRef = ref(null)

// --- Computed ---
const currentPath = computed(() => route.path)

const isMarkdownEditor = computed(() => route.path === '/markdown-editor')

// All multi-item categories expanded by default — tools visible without extra click
const openedCategoryIds = computed(() =>
  sidebarCategories.value
    .filter(cat => cat.items.length > 1)
    .map(cat => 'cat-' + cat.id)
)

const layoutClasses = computed(() => {
  if (isMarkdownEditor.value) {
    return { 'layout-immersive': true }
  }
  return {
    'layout-desktop': !deviceStore.isMobile,
    'layout-mobile': deviceStore.isMobile,
  }
})

/**
 * Build sidebar menu structure from toolCategories.
 * Each category maps to a sub-menu with its tools listed as menu items.
 * The 'data' category is expanded to include JSON, YAML, Markdown, DataConversion, MarkdownEditor.
 */
const sidebarCategories = computed(() => {
  const categoryToolMap = {
    file: [
      { label: t('sidebar.fileUpload'), route: '/file-upload' },
    ],
    data: [
      { label: t('sidebar.jsonTools'), route: '/json-tools' },
      { label: t('sidebar.yamlTools'), route: '/yaml-tools' },
      { label: t('sidebar.markdownTools'), route: '/markdown-tools' },
      { label: t('sidebar.dataConversion'), route: '/data-conversion' },
      { label: t('sidebar.markdownEditor'), route: '/markdown-editor' },
    ],
    encoding: [
      { label: t('sidebar.base64Tools'), route: '/base64-tools' },
      { label: t('sidebar.urlTools'), route: '/url-tools' },
    ],
    crypto: [
      { label: t('sidebar.hashTools'), route: '/hash-tools' },
      { label: t('sidebar.cryptoTools'), route: '/crypto-tools' },
    ],
    time: [
      { label: t('sidebar.timestampTools'), route: '/timestamp-tools' },
      { label: t('sidebar.timeCalculator'), route: '/time-calculator' },
    ],
    other: [
      { label: t('sidebar.qrTools'), route: '/qr-tools' },
    ],
    generator: [
      { label: t('sidebar.uuidTools'), route: '/uuid-tools' },
      { label: t('sidebar.passwordTools'), route: '/password-tools' },
      { label: t('sidebar.apikeyTools'), route: '/apikey-tools' },
      { label: t('sidebar.jwtDebugger'), route: '/jwt-debugger' },
      { label: t('sidebar.diffTool'), route: '/diff-tool' },
    ],
    transfer: [
      { label: t('sidebar.textTransfer'), route: '/text-transfer' },
    ],
  }

  return toolCategories.map((cat) => ({
    ...cat,
    items: categoryToolMap[cat.id] || [],
  })).filter((cat) => cat.items.length > 0)
})

/**
 * Mobile bottom navigation tabs - show top-level categories.
 * Picked 5 key categories to fit the bottom bar.
 */
const mobileNavTabs = computed(() => [
  { label: t('mobileNav.home'), route: '/', icon: 'home', matchPrefix: '' },
  { label: t('mobileNav.file'), route: '/file-upload', icon: 'upload_file', matchPrefix: '/file-upload' },
  { label: t('mobileNav.transfer'), route: '/text-transfer', icon: 'chat', matchPrefix: '/text-transfer' },
  { label: t('mobileNav.generator'), route: '/password-tools', icon: 'password', matchPrefix: '/password-tools,/apikey-tools,/jwt-debugger,/diff-tool' },
  { label: t('mobileNav.uuid'), route: '/uuid-tools', icon: 'fingerprint', matchPrefix: '/uuid-tools' },
])

// --- Methods ---
function switchLang(lang) {
  locale.value = lang
  localStorage.setItem('dt-lang', lang)
}

function isTabActive(tab) {
  if (tab.route === '/') {
    return route.path === '/'
  }
  return tab.matchPrefix.split(',').some((prefix) => route.path.startsWith(prefix))
}

function onMenuSelect() {
  /* no-op: sidebar items use router mode */
}

// Route-to-tool-meta mapping (icon/color static; label resolved lazily so it
// tracks the active language instead of freezing at first mount)
const _routeIconMap = {
  '/file-upload': 'upload_file', '/text-transfer': 'chat',
  '/json-tools': 'data_object', '/yaml-tools': 'code_blocks',
  '/markdown-tools': 'article', '/data-conversion': 'transform',
  '/markdown-editor': 'edit_note', '/base64-tools': 'swap_horiz',
  '/url-tools': 'link', '/hash-tools': 'tag',
  '/crypto-tools': 'enhanced_encryption', '/timestamp-tools': 'schedule',
  '/time-calculator': 'timer', '/uuid-tools': 'fingerprint',
  '/password-tools': 'password', '/apikey-tools': 'key',
  '/jwt-debugger': 'encrypted', '/diff-tool': 'difference',
  '/qr-tools': 'qr_code_2',
}
const _catIconMap = {
  file: 'upload_file', transfer: 'chat', data: 'database', encoding: 'code',
  crypto: 'shield', time: 'schedule', generator: 'auto_awesome', other: 'qr_code_2',
}
const _routeLabelKey = {
  '/file-upload': 'sidebar.fileUpload', '/text-transfer': 'sidebar.textTransfer',
  '/json-tools': 'sidebar.jsonTools', '/yaml-tools': 'sidebar.yamlTools',
  '/markdown-tools': 'sidebar.markdownTools', '/data-conversion': 'sidebar.dataConversion',
  '/markdown-editor': 'sidebar.markdownEditor', '/base64-tools': 'sidebar.base64Tools',
  '/url-tools': 'sidebar.urlTools', '/hash-tools': 'sidebar.hashTools',
  '/crypto-tools': 'sidebar.cryptoTools', '/timestamp-tools': 'sidebar.timestampTools',
  '/time-calculator': 'sidebar.timeCalculator', '/uuid-tools': 'sidebar.uuidTools',
  '/password-tools': 'sidebar.passwordTools', '/apikey-tools': 'sidebar.apikeyTools',
  '/jwt-debugger': 'sidebar.jwtDebugger', '/diff-tool': 'sidebar.diffTool',
  '/qr-tools': 'sidebar.qrTools',
}
// Build icon/color lookup once (language-independent)
const routeIconColor = {}
toolCategories.forEach(cat => {
  const routes = {
    file: ['/file-upload'],
    transfer: ['/text-transfer'],
    data: ['/json-tools', '/yaml-tools', '/markdown-tools', '/data-conversion', '/markdown-editor'],
    encoding: ['/base64-tools', '/url-tools'],
    crypto: ['/hash-tools', '/crypto-tools'],
    time: ['/timestamp-tools', '/time-calculator'],
    generator: ['/uuid-tools', '/password-tools', '/apikey-tools', '/jwt-debugger', '/diff-tool'],
    other: ['/qr-tools'],
  }
  ;(routes[cat.id] || []).forEach(r => {
    routeIconColor[r] = { icon: _routeIconMap[r] || _catIconMap[cat.id] || cat.icon, color: cat.color }
  })
})

// Resolve label + icon/color for a route at call time (reactive to locale)
function getRouteMeta(path) {
  const ic = routeIconColor[path]
  if (!ic) return null
  const labelKey = _routeLabelKey[path]
  return { label: labelKey ? t(labelKey) : path, icon: ic.icon, color: ic.color }
}

// --- Lifecycle ---
onMounted(() => {
  themeStore.initTheme()
  deviceStore.initListener()
})

onBeforeUnmount(() => {
  deviceStore.cleanupListener()
})

// Auto-scroll active bottom nav tab into view on route change
watch(currentPath, (path) => {
  if (deviceStore.isMobile && bottomNavRef.value) {
    requestAnimationFrame(() => {
      const active = bottomNavRef.value.querySelector('.bottom-nav-item.active')
      active?.scrollIntoView({ behavior: 'smooth', inline: 'center', block: 'nearest' })
    })
  }

  // Record recent tool visit
  if (path !== '/') {
    const entry = getRouteMeta(path)
    if (entry) {
      addRecentTool({ route: path, label: entry.label, icon: entry.icon, color: entry.color })
    }
  }
})
</script>

<style>
/* === Global resets === */
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* Element Plus menu overrides */
.el-menu {
  border-right: none !important;
}

.el-menu-item {
  height: 48px !important;
  line-height: 48px !important;
}

.el-sub-menu .el-menu-item {
  height: 40px !important;
  line-height: 40px !important;
  padding-left: 50px !important;
}
</style>

<style scoped>
/* =========================================
   Layout Grid
   ========================================= */
#app {
  display: grid;
  height: 100vh;
  height: 100dvh;
  width: 100vw;
  overflow: hidden;
  background-color: var(--dt-bg-page);
  color: var(--dt-text-primary);
}

/* Desktop: header row + sidebar | content */
.layout-desktop {
  grid-template-columns: auto 1fr;
  grid-template-rows: var(--dt-header-height) 1fr;
  grid-template-areas:
    "header header"
    "sidebar content";
}

/* Mobile: header + content + bottom nav */
.layout-mobile {
  grid-template-columns: 1fr;
  grid-template-rows: var(--dt-header-height) 1fr 56px;
  grid-template-areas:
    "header"
    "content"
    "bottomnav";
}

/* Immersive: content fills entire viewport (no header/sidebar/bottomnav) */
.layout-immersive {
  grid-template-columns: 1fr;
  grid-template-rows: 1fr;
  grid-template-areas: "content";
}

.layout-immersive .app-content {
  overflow: hidden;
}

/* =========================================
   Header
   ========================================= */
.app-header {
  grid-area: header;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 var(--dt-spacing-lg);
  height: var(--dt-header-height);
  background-color: var(--dt-bg-card);
  border-bottom: 1px solid var(--dt-border-light);
  z-index: 100;
}

.header-left {
  display: flex;
  align-items: center;
  gap: var(--dt-spacing-sm);
}

.sidebar-toggle {
  color: var(--dt-text-primary);
}

.app-title {
  margin: 0;
  font-size: var(--dt-font-size-xl);
  font-weight: 600;
  color: var(--dt-text-primary);
  white-space: nowrap;
}

.header-right {
  display: flex;
  align-items: center;
  gap: var(--dt-spacing-sm);
}

.lang-dropdown {
  cursor: pointer;
}

.lang-toggle {
  font-size: var(--dt-font-size-sm);
  color: var(--dt-text-regular);
  padding: 4px 8px;
  border-radius: 4px;
  transition: color var(--dt-transition-fast);
}

.lang-toggle:hover {
  color: var(--dt-primary);
}

.theme-switch {
  --el-switch-on-color: var(--dt-primary);
  --el-switch-off-color: var(--dt-border-base);
}

/* =========================================
   Sidebar
   ========================================= */
.sidebar-icon {
  font-size: 20px;
  width: 24px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}
.app-sidebar {
  grid-area: sidebar;
  background-color: var(--dt-bg-card);
  border-right: 1px solid var(--dt-border-light);
  overflow-y: auto;
  overflow-x: hidden;
  transition: width var(--dt-transition-base);
  z-index: 90;
}

.sidebar-collapsed {
  width: var(--dt-sidebar-collapsed);
}

.sidebar-collapsed .sidebar-menu {
  width: var(--dt-sidebar-collapsed);
}

/* Non-collapsed sidebar inherits width from grid */
.app-sidebar:not(.sidebar-collapsed) {
  width: var(--dt-sidebar-width);
}

.app-sidebar:not(.sidebar-collapsed) .sidebar-menu {
  width: var(--dt-sidebar-width);
}

.sidebar-collapse-btn {
  display: flex;
  justify-content: flex-end;
  padding: var(--dt-spacing-sm);
}

.sidebar-menu {
  border-right: none;
  background-color: var(--dt-bg-card);
  --el-menu-bg-color: var(--dt-bg-card);
  --el-menu-text-color: var(--dt-text-regular);
  --el-menu-active-color: var(--dt-primary);
  --el-menu-hover-bg-color: var(--dt-bg-hover);
}

/* =========================================
   Content
   ========================================= */
.app-content {
  grid-area: content;
  overflow-y: auto;
  overflow-x: hidden;
  background-color: var(--dt-bg-page);
}

.content-wrapper {
  max-width: var(--dt-content-max-width);
  margin: 0 auto;
}

.content-wrapper--padded {
  padding: var(--dt-spacing-lg);
}

/* Markdown editor needs full viewport, no padding */
.content-markdown-editor {
  padding: 0 !important;
}

.content-markdown-editor .content-wrapper {
  padding: 0;
  max-width: none;
  height: 100%;
}

/* =========================================
   Page Transition
   ========================================= */
.page-slide-enter-active,
.page-slide-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.page-slide-enter-from {
  opacity: 0;
  transform: translateY(8px);
}

.page-slide-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}

/* =========================================
   Mobile Bottom Navigation
   ========================================= */
.app-bottom-nav {
  grid-area: bottomnav;
  display: flex;
  align-items: center;
  justify-content: space-around;
  background-color: var(--dt-bg-card);
  border-top: 1px solid var(--dt-border-light);
  z-index: 100;
  position: relative;
}

.app-bottom-nav::-webkit-scrollbar {
  display: none;
}

.bottom-nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  flex: 1;
  padding: 6px 4px;
  text-decoration: none;
  color: var(--dt-text-secondary);
  transition: color var(--dt-transition-fast);
  gap: 2px;
  -webkit-tap-highlight-color: transparent;
}

.bottom-nav-icon {
  font-size: 20px;
}

.bottom-nav-item .el-icon {
  font-size: 18px;
}

.bottom-nav-item.active {
  color: var(--dt-primary);
}

.bottom-nav-item:active {
  background: var(--dt-bg-hover);
  border-radius: 4px;
}

.bottom-nav-label {
  font-size: 10px;
  line-height: 1.2;
  white-space: nowrap;
}

/* =========================================
   Mobile responsive overrides
   ========================================= */
@media (max-width: 768px) {
  .content-wrapper--padded {
    padding: var(--dt-spacing-xs) !important;
  }
}

/* =========================================
   Dark mode Element Plus menu overrides
   ========================================= */
html.dark .sidebar-menu {
  --el-menu-bg-color: var(--dt-bg-card);
  --el-menu-text-color: var(--dt-text-regular);
  --el-menu-hover-bg-color: var(--dt-bg-hover);
}
</style>
