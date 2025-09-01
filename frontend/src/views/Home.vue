<template>
  <div class="home">
    <!-- 桌面端布局 -->
    <div v-if="!isMobile">
      <el-row :gutter="20">
        <el-col :span="24">
          <el-card class="welcome-card">
            <template #header>
              <div class="card-header">
                <el-icon class="card-icon"><Star /></el-icon>
                <span>欢迎使用开发工具箱</span>
              </div>
            </template>
            <p>这是一个功能强大的开发工具集合，包含文件处理、数据格式转换、编码解码、加密哈希等多种实用工具。</p>
            <p>请选择左侧菜单中的工具开始使用。</p>
          </el-card>
        </el-col>
      </el-row>

      <el-row :gutter="20" style="margin-top: 20px;">
        <el-col :span="8">
          <el-card class="tool-card">
            <template #header>
              <div class="card-header">
                <el-icon class="card-icon"><FolderOpened /></el-icon>
                <span>文件工具</span>
              </div>
            </template>
            <ul>
              <li>文件上传与管理</li>
              <li>批量文件处理</li>
              <li>文件分类显示</li>
            </ul>
          </el-card>
        </el-col>

        <el-col :span="8">
          <el-card class="tool-card">
            <template #header>
              <div class="card-header">
                <el-icon class="card-icon"><DocumentCopy /></el-icon>
                <span>数据工具</span>
              </div>
            </template>
            <ul>
              <li>JSON格式化/压缩/验证</li>
              <li>YAML格式化/验证</li>
              <li>数据格式转换</li>
            </ul>
          </el-card>
        </el-col>

        <el-col :span="8">
          <el-card class="tool-card">
            <template #header>
              <div class="card-header">
                <el-icon class="card-icon"><Key /></el-icon>
                <span>编码工具</span>
              </div>
            </template>
            <ul>
              <li>Base64编码/解码</li>
              <li>URL编码/解码</li>
              <li>字符串转义</li>
            </ul>
          </el-card>
        </el-col>
      </el-row>

      <el-row :gutter="20" style="margin-top: 20px;">
        <el-col :span="8">
          <el-card class="tool-card">
            <template #header>
              <div class="card-header">
                <el-icon class="card-icon"><Lock /></el-icon>
                <span>加密工具</span>
              </div>
            </template>
            <ul>
              <li>哈希生成与验证</li>
              <li>HMAC生成</li>
              <li>密码哈希</li>
            </ul>
          </el-card>
        </el-col>

        <el-col :span="8">
          <el-card class="tool-card">
            <template #header>
              <div class="card-header">
                <el-icon class="card-icon"><Clock /></el-icon>
                <span>时间工具</span>
              </div>
            </template>
            <ul>
              <li>时间戳转换</li>
              <li>日期时间计算</li>
              <li>时间格式化</li>
            </ul>
          </el-card>
        </el-col>

        <el-col :span="8">
          <el-card class="tool-card">
            <template #header>
              <div class="card-header">
                <el-icon class="card-icon"><Crop /></el-icon>
                <span>二维码工具</span>
              </div>
            </template>
            <ul>
              <li>二维码生成</li>
              <li>二维码美化</li>
              <li>自定义样式</li>
            </ul>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 移动端布局 -->
    <div v-else>
      <MobileHome />
    </div>
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
  Crop
} from '@element-plus/icons-vue'
import MobileHome from './MobileHome.vue'

export default {
  name: 'Home',
  components: {
    Star,
    FolderOpened,
    DocumentCopy,
    Key,
    Lock,
    Clock,
    Crop,
    MobileHome
  },
  data() {
    return {
      isMobile: false
    }
  },
  methods: {
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

<style scoped>
.home {
  padding: 20px;
}

.welcome-card {
  text-align: center;
}

.welcome-card p {
  margin: 10px 0;
  color: #666;
}

.tool-card {
  height: 100%;
}

.tool-card ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.tool-card li {
  padding: 5px 0;
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
</style>
