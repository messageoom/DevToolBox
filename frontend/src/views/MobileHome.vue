<template>
  <div class="mobile-home">
    <el-card class="mobile-welcome-card">
      <template #header>
        <div class="card-header">
          <el-icon class="card-icon"><Star /></el-icon>
          <span>欢迎使用开发工具箱</span>
        </div>
      </template>
      <p>这是一个功能强大的开发工具集合，包含文件处理、数据格式转换、编码解码、加密哈希等多种实用工具。</p>
      <p>点击左上角菜单按钮选择工具开始使用。</p>
    </el-card>

    <el-collapse v-model="activeNames" style="margin-top: 20px;">
      <el-collapse-item title="文件工具" name="1">
        <template #title>
          <el-icon class="card-icon"><FolderOpened /></el-icon>
          <span>文件工具</span>
        </template>
        <div class="tool-item" @click="$router.push('/file-upload')">
          <el-icon><Upload /></el-icon>
          <span>文件上传</span>
        </div>
      </el-collapse-item>

      <el-collapse-item title="数据工具" name="2">
        <template #title>
          <el-icon class="card-icon"><DocumentCopy /></el-icon>
          <span>数据工具</span>
        </template>
        <div class="tool-item" @click="$router.push('/json-tools')">
          <el-icon><Document /></el-icon>
          <span>JSON工具</span>
        </div>
        <div class="tool-item" @click="$router.push('/yaml-tools')">
          <el-icon><Files /></el-icon>
          <span>YAML工具</span>
        </div>
        <div class="tool-item" @click="$router.push('/markdown-tools')">
          <el-icon><DocumentChecked /></el-icon>
          <span>Markdown工具</span>
        </div>
      </el-collapse-item>

      <el-collapse-item title="编码工具" name="3">
        <template #title>
          <el-icon class="card-icon"><Key /></el-icon>
          <span>编码工具</span>
        </template>
        <div class="tool-item" @click="$router.push('/base64-tools')">
          <el-icon><Unlock /></el-icon>
          <span>Base64工具</span>
        </div>
        <div class="tool-item" @click="$router.push('/url-tools')">
          <el-icon><Link /></el-icon>
          <span>URL工具</span>
        </div>
      </el-collapse-item>

      <el-collapse-item title="加密工具" name="4">
        <template #title>
          <el-icon class="card-icon"><Lock /></el-icon>
          <span>加密工具</span>
        </template>
        <div class="tool-item" @click="$router.push('/hash-tools')">
          <el-icon><Key /></el-icon>
          <span>哈希工具</span>
        </div>
      </el-collapse-item>

      <el-collapse-item title="时间工具" name="5">
        <template #title>
          <el-icon class="card-icon"><Clock /></el-icon>
          <span>时间工具</span>
        </template>
        <div class="tool-item" @click="$router.push('/timestamp-tools')">
          <el-icon><Timer /></el-icon>
          <span>时间戳工具</span>
        </div>
        <div class="tool-item" @click="$router.push('/time-calculator')">
          <el-icon><Calendar /></el-icon>
          <span>时间计算器</span>
        </div>
      </el-collapse-item>
    </el-collapse>
  </div>
</template>

<script>
import {
  Star,
  FolderOpened,
  DocumentCopy,
  Key,
  Lock,
  Clock,
  Upload,
  Document,
  Files,
  DocumentChecked,
  Unlock,
  Link,
  Timer,
  Calendar
} from '@element-plus/icons-vue'

export default {
  name: 'MobileHome',
  components: {
    Star,
    FolderOpened,
    DocumentCopy,
    Key,
    Lock,
    Clock,
    Upload,
    Document,
    Files,
    DocumentChecked,
    Unlock,
    Link,
    Timer,
    Calendar
  },
  data() {
    return {
      activeNames: []
    }
  }
}
</script>

<style scoped>
.mobile-home {
  padding: 10px;
}

.mobile-welcome-card {
  text-align: center;
}

.mobile-welcome-card p {
  margin: 8px 0;
  color: #666;
  font-size: 14px;
}

.card-header {
  display: flex;
  align-items: center;
}

.card-icon {
  margin-right: 8px;
  font-size: 18px;
}

.card-header span {
  font-weight: bold;
}

.tool-item {
  display: flex;
  align-items: center;
  padding: 12px 15px;
  border-bottom: 1px solid #f0f0f0;
  cursor: pointer;
}

.tool-item:last-child {
  border-bottom: none;
}

.tool-item:hover {
  background-color: #f5f5f5;
}

.tool-item el-icon {
  margin-right: 10px;
  font-size: 18px;
  color: #409eff;
}
</style>
