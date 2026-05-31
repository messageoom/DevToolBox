<template>
  <div class="home">
    <el-card class="welcome-card">
      <template #header>
        <div class="card-header">
          <el-icon class="card-icon"><Star /></el-icon>
          <span>欢迎使用开发工具箱</span>
        </div>
      </template>
      <p>功能强大的开发工具集合，包含文件处理、数据格式转换、编码解码、加密哈希等多种实用工具。</p>
      <p>请选择下方工具分类开始使用。</p>
    </el-card>

    <div class="categories-grid">
      <el-card
        v-for="category in toolCategories"
        :key="category.id"
        class="category-card"
        @click="$router.push(category.route)"
      >
        <template #header>
          <div class="card-header">
            <el-icon class="card-icon"><component :is="category.icon" /></el-icon>
            <span>{{ category.name }}</span>
          </div>
        </template>
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
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { Star } from '@element-plus/icons-vue'
import { toolCategories } from '../data/toolCategories'
</script>

<style scoped>
.home {
  padding: var(--dt-spacing-lg);
  max-width: var(--dt-content-max-width);
  margin: 0 auto;
}

.welcome-card {
  text-align: center;
  margin-bottom: var(--dt-spacing-lg);
}

.welcome-card :deep(p) {
  margin: var(--dt-spacing-sm) 0;
  color: var(--dt-text-regular);
}

.categories-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--dt-spacing-lg);
}

.category-card {
  cursor: pointer;
  transition: transform var(--dt-transition-base), box-shadow var(--dt-transition-base), border-color var(--dt-transition-base);
  border: 1px solid var(--dt-border-lighter);
}

.category-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--dt-shadow-md);
  border-color: var(--dt-primary);
}

.category-card p {
  color: var(--dt-text-regular);
  font-size: var(--dt-font-size-base);
  margin-bottom: var(--dt-spacing-md);
}

.tools-list {
  display: flex;
  flex-wrap: wrap;
  gap: var(--dt-spacing-xs);
}

.tool-tag {
  margin: 0;
}

@media (max-width: 768px) {
  .categories-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: var(--dt-spacing-md);
  }

  .home {
    padding: var(--dt-spacing-md);
  }
}

@media (max-width: 480px) {
  .categories-grid {
    grid-template-columns: 1fr;
  }

  .home {
    padding: var(--dt-spacing-sm);
  }
}
</style>
