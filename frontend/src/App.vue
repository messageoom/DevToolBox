<template>
  <div id="app" :class="layoutClasses">
    <!-- Header -->
    <header class="app-header">
      <div class="header-left">
        <el-button
          v-if="deviceStore.isTablet"
          class="sidebar-toggle"
          link
          @click="sidebarOpen = !sidebarOpen"
        >
          <el-icon :size="20">
            <Expand v-if="!sidebarOpen" />
            <Fold v-else />
          </el-icon>
        </el-button>
        <h1 class="app-title">DevToolBox</h1>
      </div>
      <div class="header-right">
        <el-switch
          :model-value="themeStore.isDark"
          inline-prompt
          active-text="暗黑"
          inactive-text="亮色"
          @change="themeStore.toggleTheme()"
          class="theme-switch"
        />
      </div>
    </header>

    <!-- Sidebar (desktop + tablet only) -->
    <aside
      v-if="!deviceStore.isMobile"
      class="app-sidebar"
      :class="{
        'sidebar-collapsed': isSidebarCollapsed,
        'sidebar-overlay': deviceStore.isTablet && sidebarOpen,
        'sidebar-hidden': deviceStore.isTablet && !sidebarOpen,
      }"
    >
      <!-- Collapse toggle (desktop only) -->
      <div v-if="deviceStore.isDesktop" class="sidebar-collapse-btn">
        <el-button @click="isSidebarCollapsed = !isSidebarCollapsed" link>
          <el-icon>
            <Expand v-if="isSidebarCollapsed" />
            <Fold v-else />
          </el-icon>
        </el-button>
      </div>

      <el-menu
        :default-active="currentPath"
        :collapse="deviceStore.isDesktop && isSidebarCollapsed"
        :collapse-transition="false"
        router
        class="sidebar-menu"
        @select="onMenuSelect"
      >
        <!-- Home -->
        <el-menu-item index="/">
          <el-icon><HomeFilled /></el-icon>
          <template #title>首页</template>
        </el-menu-item>

        <!-- Dynamic categories from toolCategories data -->
        <template v-for="category in sidebarCategories" :key="category.id">
          <el-sub-menu :index="'cat-' + category.id">
            <template #title>
              <el-icon><component :is="getIcon(category.icon)" /></el-icon>
              <span>{{ category.name }}</span>
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

    <!-- Tablet backdrop for sidebar overlay -->
    <div
      v-if="deviceStore.isTablet && sidebarOpen"
      class="sidebar-backdrop"
      @click="sidebarOpen = false"
    />

    <!-- Main content -->
    <main
      class="app-content"
      :class="{
        'content-full': deviceStore.isMobile,
        'content-markdown-editor': isMarkdownEditor,
      }"
    >
      <div class="content-wrapper" :class="{ 'content-wrapper--padded': !isMarkdownEditor }">
        <router-view />
      </div>
    </main>

    <!-- Mobile bottom navigation -->
    <nav v-if="deviceStore.isMobile" class="app-bottom-nav">
      <router-link
        v-for="tab in mobileNavTabs"
        :key="tab.route"
        :to="tab.route"
        class="bottom-nav-item"
        :class="{ active: isTabActive(tab) }"
      >
        <el-icon :size="22"><component :is="tab.icon" /></el-icon>
        <span class="bottom-nav-label">{{ tab.label }}</span>
      </router-link>
    </nav>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useDeviceStore } from '@/stores/device.js'
import { useThemeStore } from '@/stores/theme.js'
import { toolCategories } from '@/data/toolCategories.js'
import {
  HomeFilled,
  FolderOpened,
  DocumentCopy,
  Key,
  Lock,
  Clock,
  Expand,
  Fold,
  Crop,
  Sunny,
  Moon,
} from '@element-plus/icons-vue'

// --- Stores ---
const deviceStore = useDeviceStore()
const themeStore = useThemeStore()
const route = useRoute()
const router = useRouter()

// --- Reactive state ---
const isSidebarCollapsed = ref(false)
const sidebarOpen = ref(false)

// --- Computed ---
const currentPath = computed(() => route.path)

const isMarkdownEditor = computed(() => route.path === '/markdown-editor')

const layoutClasses = computed(() => ({
  'layout-desktop': deviceStore.isDesktop,
  'layout-tablet': deviceStore.isTablet,
  'layout-mobile': deviceStore.isMobile,
}))

/**
 * Build sidebar menu structure from toolCategories.
 * Each category maps to a sub-menu with its tools listed as menu items.
 * The 'data' category is expanded to include JSON, YAML, Markdown, DataConversion, MarkdownEditor.
 */
const sidebarCategories = computed(() => {
  const categoryToolMap = {
    file: [
      { label: '文件上传', route: '/file-upload' },
    ],
    data: [
      { label: 'JSON工具', route: '/json-tools' },
      { label: 'YAML工具', route: '/yaml-tools' },
      { label: 'Markdown工具', route: '/markdown-tools' },
      { label: '数据互转', route: '/data-conversion' },
      { label: 'Markdown编辑器', route: '/markdown-editor' },
    ],
    encoding: [
      { label: 'Base64工具', route: '/base64-tools' },
      { label: 'URL工具', route: '/url-tools' },
    ],
    crypto: [
      { label: '哈希工具', route: '/hash-tools' },
      { label: '加密工具', route: '/crypto-tools' },
    ],
    time: [
      { label: '时间戳工具', route: '/timestamp-tools' },
      { label: '时间计算器', route: '/time-calculator' },
    ],
    other: [
      { label: '二维码工具', route: '/qr-tools' },
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
const mobileNavTabs = [
  { label: '首页', route: '/', icon: HomeFilled, matchPrefix: '' },
  { label: '数据', route: '/json-tools', icon: DocumentCopy, matchPrefix: '/json-tools,/yaml-tools,/markdown-tools,/data-conversion,/markdown-editor' },
  { label: '编码', route: '/base64-tools', icon: Lock, matchPrefix: '/base64-tools,/url-tools' },
  { label: '加密', route: '/hash-tools', icon: Key, matchPrefix: '/hash-tools,/crypto-tools,/crypto-main-menu' },
  { label: '时间', route: '/timestamp-tools', icon: Clock, matchPrefix: '/timestamp-tools,/time-calculator' },
]

// --- Methods ---
function getIcon(iconName) {
  const iconMap = {
    FolderOpened,
    DocumentCopy,
    Key,
    Lock,
    Clock,
    Crop,
  }
  return iconMap[iconName] || DocumentCopy
}

function isTabActive(tab) {
  if (tab.route === '/') {
    return route.path === '/'
  }
  return tab.matchPrefix.split(',').some((prefix) => route.path.startsWith(prefix))
}

function onMenuSelect(index) {
  // Auto-collapse markdown editor to give full viewport
  if (index === '/markdown-editor') {
    isSidebarCollapsed.value = true
  }
  // Close tablet sidebar overlay on navigation
  if (deviceStore.isTablet) {
    sidebarOpen.value = false
  }
}

function handleResize() {
  deviceStore.checkDevice()
  // Auto-collapse sidebar on resize to tablet
  if (deviceStore.isTablet) {
    sidebarOpen.value = false
  }
}

// --- Lifecycle ---
onMounted(() => {
  themeStore.initTheme()
  deviceStore.checkDevice()
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
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

/* Tablet: header row + content (sidebar overlays) */
.layout-tablet {
  grid-template-columns: 1fr;
  grid-template-rows: var(--dt-header-height) 1fr;
  grid-template-areas:
    "header"
    "content";
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
}

.theme-switch {
  --el-switch-on-color: var(--dt-primary);
  --el-switch-off-color: var(--dt-border-base);
}

/* =========================================
   Sidebar
   ========================================= */
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

/* Tablet: sidebar overlays content */
.sidebar-overlay {
  position: fixed;
  top: var(--dt-header-height);
  left: 0;
  bottom: 0;
  width: var(--dt-sidebar-width);
  box-shadow: var(--dt-shadow-lg);
  z-index: 200;
}

.sidebar-overlay .sidebar-menu {
  width: var(--dt-sidebar-width);
}

.sidebar-hidden {
  display: none;
}

.sidebar-backdrop {
  position: fixed;
  top: var(--dt-header-height);
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.4);
  z-index: 190;
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
}

.bottom-nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  flex: 1;
  padding: 4px 0;
  text-decoration: none;
  color: var(--dt-text-secondary);
  transition: color var(--dt-transition-fast);
  gap: 2px;
}

.bottom-nav-item.active {
  color: var(--dt-primary);
}

.bottom-nav-label {
  font-size: var(--dt-font-size-xs);
  line-height: 1;
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
