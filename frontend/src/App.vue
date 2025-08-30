<template>
  <div id="app">
    <el-container style="height: 100vh">
      <!-- 侧边栏 -->
      <el-aside width="200px" style="background-color: #f5f5f5; border-right: 1px solid #e6e6e6;">
        <el-menu
          :default-active="$route.path"
          class="el-menu-vertical-demo"
          @select="handleSelect"
          router
        >
          <el-menu-item index="/">
            <el-icon><HomeFilled /></el-icon>
            <span>首页</span>
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
  </div>
</template>

<script>
import {
  HomeFilled,
  FolderOpened,
  DocumentCopy,
  Key,
  Lock,
  Clock
} from '@element-plus/icons-vue'

export default {
  name: 'App',
  components: {
    HomeFilled,
    FolderOpened,
    DocumentCopy,
    Key,
    Lock,
    Clock
  },
  methods: {
    handleSelect(key, keyPath) {
      console.log(key, keyPath)
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
</style>
