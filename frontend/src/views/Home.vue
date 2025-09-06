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
            <p>请选择下方工具分类开始使用。</p>
          </el-card>
        </el-col>
      </el-row>

      <!-- 工具分类卡片 -->
      <el-row :gutter="20" class="tool-categories-row">
        <el-col :span="8" v-for="category in toolCategories" :key="category.id" class="tool-category-col">
          <el-card class="tool-category-card" @click="goToCategory(category.route)">
            <template #header>
              <div class="card-header">
                <el-icon class="card-icon"><component :is="category.icon" /></el-icon>
                <span>{{ category.name }}</span>
              </div>
            </template>
            <div class="category-content">
              <p>{{ category.description }}</p>
              <div class="tools-list">
                <el-tag 
                  v-for="tool in category.tools" 
                  :key="tool" 
                  type="info" 
                  size="small" 
                  class="tool-tag"
                >
                  {{ tool }}
                </el-tag>
              </div>
            </div>
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
      isMobile: false,
      windowWidth: 0,
      toolCategories: [
        {
          id: 'file',
          name: '文件工具',
          description: '文件上传、管理与处理',
          icon: 'FolderOpened',
          route: '/file-upload',
          tools: ['文件上传', '文件管理', '批量处理']
        },
        {
          id: 'crypto',
          name: '加密工具',
          description: '哈希算法、对称与非对称加密',
          icon: 'Key',
          route: '/crypto-main-menu',
          tools: ['RSA', 'ECC', 'AES', 'ChaCha20', 'SM2', 'SM4', 'MD5', 'SHA256', 'SM3', 'BLAKE3']
        },
        {
          id: 'data',
          name: '数据工具',
          description: '数据格式转换与处理',
          icon: 'DocumentCopy',
          route: '/json-tools',
          tools: ['JSON', 'YAML', 'Markdown', 'Base64']
        },
        {
          id: 'encoding',
          name: '编码工具',
          description: '各种编码解码工具',
          icon: 'Lock',
          route: '/base64-tools',
          tools: ['Base64', 'URL编码', '时间戳']
        },
        {
          id: 'time',
          name: '时间工具',
          description: '时间戳与日期时间处理',
          icon: 'Clock',
          route: '/timestamp-tools',
          tools: ['时间戳转换', '日期计算']
        },
        {
          id: 'other',
          name: '其他工具',
          description: '二维码生成等其他实用工具',
          icon: 'Crop',
          route: '/qr-tools',
          tools: ['二维码生成', '二维码美化']
        }
      ]
    }
  },
  methods: {
    checkDevice() {
      // 检测设备类型
      this.windowWidth = window.innerWidth;
      this.isMobile = window.innerWidth <= 768;
      console.log('Device check - isMobile:', this.isMobile, 'window.innerWidth:', window.innerWidth);
    },
    goToCategory(route) {
      console.log('Navigating to:', route);
      this.$router.push(route);
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

.tool-categories-row {
  margin-top: 20px;
}

.tool-category-col {
  margin-bottom: 20px;
}

.tool-category-card {
  height: 100%;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 1px solid #ebeef5;
}

.tool-category-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  border-color: #409eff;
}

.category-content p {
  color: #666;
  font-size: 14px;
  margin-bottom: 15px;
}

.card-header {
  display: flex;
  align-items: center;
}

.card-icon {
  margin-right: 8px;
  font-size: 18px;
  color: #409eff;
}

.card-header span {
  font-weight: bold;
  font-size: 16px;
}

.tools-list {
  margin-top: 10px;
}

.tool-tag {
  margin-right: 5px;
  margin-bottom: 5px;
}
</style>