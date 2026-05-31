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
import { toolCategories, MOBILE_BREAKPOINT } from '../data/toolCategories'

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
      toolCategories
    }
  },
  methods: {
    checkDevice() {
      // 检测设备类型
      this.windowWidth = window.innerWidth;
      this.isMobile = window.innerWidth <= MOBILE_BREAKPOINT;
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