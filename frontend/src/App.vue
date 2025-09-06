<template>
  <div id="app">
    <!-- 桌面端布局 -->
    <el-container v-if="!isMobile" style="height: 100vh">
      <!-- 侧边栏 -->
      <el-aside :width="isCollapse ? '64px' : '200px'" style="background-color: var(--el-bg-color); border-right: 1px solid var(--el-border-color); transition: width 0.3s;">
        <div style="display: flex; justify-content: flex-end; padding: 10px;">
          <el-button @click="toggleCollapse" type="primary" link>
            <el-icon>
              <Expand v-if="isCollapse" />
              <Fold v-else />
            </el-icon>
          </el-button>
        </div>
        <el-menu
          :default-active="$route.path"
          class="el-menu-vertical-demo"
          @select="handleSelect"
          router
          :collapse="isCollapse"
          :collapse-transition="false"
          background-color="var(--el-bg-color)"
          text-color="var(--el-text-color-primary)"
          active-text-color="var(--el-color-primary)"
        >
          <el-menu-item index="/">
            <el-icon><HomeFilled /></el-icon>
            <template #title>首页</template>
          </el-menu-item>

          <el-sub-menu index="file-tools">
            <template #title>
              <el-icon><FolderOpened /></el-icon>
              <span>文件工具</span>
            </template>
            <el-menu-item index="/file-upload">文件上传</el-menu-item>
          </el-sub-menu>

          <el-sub-menu index="data-tools">
            <template #title>
              <el-icon><DocumentCopy /></el-icon>
              <span>数据工具</span>
            </template>
            <el-menu-item index="/json-tools">JSON工具</el-menu-item>
            <el-menu-item index="/yaml-tools">YAML工具</el-menu-item>
            <el-menu-item index="/markdown-tools">Markdown工具</el-menu-item>
            <el-menu-item index="/data-conversion">数据互转</el-menu-item>
            <el-menu-item index="/markdown-editor" @click="handleMarkdownEditorClick">Markdown编辑器</el-menu-item>
          </el-sub-menu>

          <el-sub-menu index="encoding-tools">
            <template #title>
              <el-icon><Key /></el-icon>
              <span>编码工具</span>
            </template>
            <el-menu-item index="/base64-tools">Base64工具</el-menu-item>
            <el-menu-item index="/url-tools">URL工具</el-menu-item>
          </el-sub-menu>

          <el-sub-menu index="crypto-tools">
            <template #title>
              <el-icon><Lock /></el-icon>
              <span>加密工具</span>
            </template>
            <el-menu-item index="/hash-tools">哈希工具</el-menu-item>
            <el-menu-item index="/crypto-tools">加密工具</el-menu-item>
          </el-sub-menu>

          <el-sub-menu index="time-tools">
            <template #title>
              <el-icon><Clock /></el-icon>
              <span>时间工具</span>
            </template>
            <el-menu-item index="/timestamp-tools">时间戳工具</el-menu-item>
            <el-menu-item index="/time-calculator">时间计算器</el-menu-item>
          </el-sub-menu>

          <el-sub-menu index="other-tools">
            <template #title>
              <el-icon><Crop /></el-icon>
              <span>其他工具</span>
            </template>
            <el-menu-item index="/qr-tools">二维码工具</el-menu-item>
          </el-sub-menu>
        </el-menu>
      </el-aside>

      <!-- 主内容区域 -->
      <el-container>
        <el-header style="background-color: var(--el-bg-color); border-bottom: 1px solid var(--el-border-color); padding: 0 20px; display: flex; justify-content: space-between; align-items: center;">
          <h1 style="margin: 0; line-height: 60px;">DevToolBox - 开发工具箱</h1>
          <!-- 主题切换开关 -->
          <div style="display: flex; align-items: center;">
            <el-switch
              v-model="isDark"
              inline-prompt
              active-text="暗黑模式"
              inactive-text="默认主题"
              @change="toggleTheme"
              style="--el-switch-on-color: #409eff; --el-switch-off-color: #c0ccda;"
            />
          </div>
        </el-header>

        <el-main style="padding: 20px; background-color: var(--el-bg-color-page);">
          <router-view />
        </el-main>
      </el-container>
    </el-container>

    <!-- 移动端布局 -->
    <el-container v-else style="height: 100vh">
      <!-- 顶部导航栏 -->
      <el-header style="background-color: var(--el-color-primary); color: white; padding: 0 10px; display: flex; align-items: center; justify-content: space-between;">
        <div style="display: flex; align-items: center;">
          <el-button @click="toggleMobileMenu" type="primary" link style="color: white; font-size: 24px;">
            <el-icon><Menu /></el-icon>
          </el-button>
          <h1 style="margin: 0; margin-left: 10px; font-size: 18px;">DevToolBox</h1>
        </div>
        <!-- 移动端主题切换开关 -->
        <el-switch
          v-model="isDark"
          inline-prompt
          active-text="暗黑"
          inactive-text="默认"
          @change="toggleTheme"
          style="--el-switch-on-color: #409eff; --el-switch-off-color: #c0ccda;"
        />
      </el-header>

      <!-- 主内容区域 -->
      <el-main style="padding: 10px; background-color: var(--el-bg-color-page);">
        <router-view />
      </el-main>

      <!-- 移动端菜单抽屉 -->
      <MobileMenu :drawer="mobileMenuVisible" @update:drawer="mobileMenuVisible = $event" />
    </el-container>
  </div>
</template>

<script>
import {
  HomeFilled,
  FolderOpened,
  DocumentCopy,
  Key,
  Lock,
  Clock,
  Expand,
  Fold,
  Menu,
  Crop
} from '@element-plus/icons-vue'
import MobileMenu from './components/MobileMenu.vue'

export default {
  name: 'App',
  components: {
    HomeFilled,
    FolderOpened,
    DocumentCopy,
    Key,
    Lock,
    Clock,
    Expand,
    Fold,
    Menu,
    Crop,
    MobileMenu
  },
  data() {
    return {
      isCollapse: false,
      isMobile: false,
      mobileMenuVisible: false,
      isDark: false // 主题状态
    }
  },
  methods: {
    handleSelect(key, keyPath) {
      console.log(key, keyPath)
    },
    toggleCollapse() {
      this.isCollapse = !this.isCollapse
    },
    toggleMobileMenu() {
      this.mobileMenuVisible = true
    },
    handleMarkdownEditorClick() {
      // 点击Markdown编辑器菜单时自动收起侧边栏
      this.isCollapse = true
      // 导航到Markdown编辑器页面
      this.$router.push('/markdown-editor')
    },
    checkDevice() {
      // 检测设备类型
      this.isMobile = window.innerWidth <= 768
    },
    toggleTheme() {
      // 切换主题
      if (this.isDark) {
        document.documentElement.classList.add('dark')
      } else {
        document.documentElement.classList.remove('dark')
      }
      
      // 保存主题设置到localStorage
      localStorage.setItem('devtoolbox-theme', this.isDark ? 'dark' : 'light')
    },
    initTheme() {
      // 初始化主题
      const savedTheme = localStorage.getItem('devtoolbox-theme')
      if (savedTheme) {
        this.isDark = savedTheme === 'dark'
      } else {
        // 如果没有保存的主题设置，根据系统偏好设置
        this.isDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches
      }
      
      // 应用主题
      if (this.isDark) {
        document.documentElement.classList.add('dark')
      } else {
        document.documentElement.classList.remove('dark')
      }
    }
  },
  mounted() {
    // 初始化设备检测
    this.checkDevice()
    
    // 初始化主题
    this.initTheme()
    
    // 监听窗口大小变化
    window.addEventListener('resize', this.checkDevice)
    
    // 监听系统主题变化
    if (window.matchMedia) {
      window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
        // 只有在用户没有手动设置主题时才跟随系统变化
        if (!localStorage.getItem('devtoolbox-theme')) {
          this.isDark = e.matches
          if (this.isDark) {
            document.documentElement.classList.add('dark')
          } else {
            document.documentElement.classList.remove('dark')
          }
        }
      })
    }
  },
  beforeUnmount() {
    // 清理事件监听器
    window.removeEventListener('resize', this.checkDevice)
    if (window.matchMedia) {
      window.matchMedia('(prefers-color-scheme: dark)').removeEventListener('change')
    }
  }
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

.el-menu {
  border-right: none;
}

.el-menu-item {
  height: 48px;
  line-height: 48px;
}

.el-sub-menu .el-menu-item {
  height: 40px;
  line-height: 40px;
  padding-left: 50px !important;
}

/* 适配暗黑主题的菜单项 */
html.dark .el-menu {
  --el-menu-bg-color: var(--el-bg-color);
  --el-menu-text-color: var(--el-text-color-primary);
  --el-menu-hover-bg-color: var(--el-bg-color-page);
}

html.dark .el-menu-vertical-demo:not(.el-menu--collapse) {
  width: 200px;
}
</style>
