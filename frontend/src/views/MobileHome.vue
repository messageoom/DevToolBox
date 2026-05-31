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
      <p>点击下方工具卡片选择工具开始使用。</p>
    </el-card>

    <!-- 移动端工具卡片 -->
    <div class="mobile-tool-grid">
      <el-row :gutter="10">
        <el-col 
          v-for="category in toolCategories" 
          :key="category.id" 
          :span="12" 
          class="tool-col"
        >
          <el-card class="mobile-tool-card" @click="goToCategory(category.route)">
            <div class="card-content">
              <el-icon class="tool-icon" :size="24">
                <component :is="category.icon" />
              </el-icon>
              <div class="tool-info">
                <h3 class="tool-name">{{ category.name }}</h3>
                <p class="tool-description">{{ category.description }}</p>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
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
  Upload,
  Document,
  Files,
  DocumentChecked,
  Unlock,
  Link,
  Timer,
  Calendar,
  Crop
} from '@element-plus/icons-vue'
import { toolCategories } from '../data/toolCategories'

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
    Calendar,
    Crop
  },
  data() {
    return {
      activeNames: [],
      toolCategories
    }
  },
  methods: {
    goToCategory(route) {
      this.$router.push(route)
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

.mobile-tool-grid {
  margin-top: 20px;
}

.tool-col {
  margin-bottom: 15px;
}

.mobile-tool-card {
  cursor: pointer;
  transition: all 0.3s ease;
  height: 100%;
}

.mobile-tool-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.card-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 15px 10px;
}

.tool-icon {
  color: #409eff;
  margin-bottom: 10px;
}

.tool-name {
  margin: 0 0 5px 0;
  font-size: 14px;
  font-weight: 600;
  color: #333;
}

.tool-description {
  margin: 0;
  font-size: 12px;
  color: #666;
  line-height: 1.4;
}
</style>