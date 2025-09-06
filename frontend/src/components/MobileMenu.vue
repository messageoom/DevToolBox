<template>
  <el-drawer
    v-model="visible"
    title="开发工具箱"
    direction="ltr"
    size="80%"
    :with-header="true"
  >
    <el-menu
      :default-active="$route.path"
      class="mobile-menu"
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
        <el-menu-item index="/data-conversion">数据互转</el-menu-item>
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
  </el-drawer>
</template>

<script>
import {
  HomeFilled,
  FolderOpened,
  DocumentCopy,
  Key,
  Lock,
  Clock,
  Crop
} from '@element-plus/icons-vue'

export default {
  name: 'MobileMenu',
  components: {
    HomeFilled,
    FolderOpened,
    DocumentCopy,
    Key,
    Lock,
    Clock,
    Crop
  },
  props: {
    drawer: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      visible: false
    }
  },
  watch: {
    drawer(newVal) {
      this.visible = newVal
    },
    visible(newVal) {
      if (!newVal) {
        // 抽屉关闭时的回调
        console.log('Drawer closed')
        this.$emit('update:drawer', false)
      }
    }
  },
  methods: {
    handleSelect(key, keyPath) {
      console.log(key, keyPath)
      // 关闭抽屉
      this.visible = false
      this.$emit('update:drawer', false)
    },
    closeDrawer() {
      this.visible = false
      this.$emit('update:drawer', false)
    }
  }
}
</script>

<style scoped>
.mobile-menu {
  border-right: none;
}

.mobile-menu .el-menu-item {
  height: 48px;
  line-height: 48px;
}

.mobile-menu .el-sub-menu .el-menu-item {
  height: 40px;
  line-height: 40px;
  padding-left: 50px !important;
}
</style>
