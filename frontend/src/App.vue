<template>
  <div id="app">
    <!-- 桌面端布局 -->
    <el-container v-if="!isMobile" style="height: 100vh">
      <!-- 侧边栏 -->
      <el-aside :width="isCollapse ? '64px' : '200px'" style="background-color: #f5f5f5; border-right: 1px solid #e6e6e6; transition: width 0.3s;">
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
          </el-sub-menu>

          <el-sub-menu index="time-tools">
            <template #title>
              <el-icon><Clock /></el-icon>
              <span>时间工具</span>
            </template>
            <el-menu-item index="/timestamp-tools">时间戳工具</el-menu-item>
            <el-menu-item index="/time-calculator">时间计算器</el-menu-item>
          </el-sub-menu>
        </el-menu>
      </el-aside>

      <!-- 主内容区域 -->
      <el-container>
        <el-header style="background-color: #fff; border-bottom: 1px solid #e6e6e6; padding: 0 20px;">
          <h1 style="margin: 0; line-height: 60px;">DevToolBox - 开发工具箱</h1>
        </el-header>

        <el-main style="padding: 20px;">
          <router-view />
        </el-main>
      </el-container>
    </el-container>

    <!-- 移动端布局 -->
    <el-container v-else style="height: 100vh">
      <!-- 顶部导航栏 -->
      <el-header style="background-color: #409eff; color: white; padding: 0 10px; display: flex; align-items: center; justify-content: space-between;">
        <div style="display: flex; align-items: center;">
          <el-button @click="toggleMobileMenu" type="primary" link style="color: white; font-size: 24px;">
            <el-icon><Menu /></el-icon>
          </el-button>
          <h1 style="margin: 0; margin-left: 10px; font-size: 18px;">DevToolBox</h1>
        </div>
      </el-header>

      <!-- 主内容区域 -->
      <el-main style="padding: 10px;">
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
  Menu
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
    MobileMenu
  },
  data() {
    return {
      isCollapse: false,
      isMobile: false,
      mobileMenuVisible: false
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
    checkDevice() {
      // 检测设备类型
      this.isMobile = window.innerWidth <= 768
    }
  },
  mounted() {
    // 初始化设备检测
    this.checkDevice()
    
    // 监听窗口大小变化
    window.addEventListener('resize', this.checkDevice)
  },
  beforeUnmount() {
    // 清理事件监听器
    window.removeEventListener('resize', this.checkDevice)
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
</style>
