<template>
  <div class="home">
    <!-- Desktop: card grid -->
    <template v-if="!deviceStore.isMobile">
      <el-card class="welcome-card">
        <template #header>
          <div class="card-header">
            <el-icon class="card-icon"><Star /></el-icon>
            <span>{{ t('tools.home.welcome') }}</span>
          </div>
        </template>
        <p>{{ t('tools.home.desc1') }}</p>
        <p>{{ t('tools.home.desc2') }}</p>
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
              <span>{{ t('categories.' + category.id + '.name') }}</span>
            </div>
          </template>
          <p>{{ t('categories.' + category.id + '.description') }}</p>
          <div class="tools-list">
            <el-tag
              v-for="tool in category.tools"
              :key="tool"
              type="info"
              size="small"
              class="tool-tag"
            >
              {{ t('categories.' + category.id + '.tools.' + tool) }}
            </el-tag>
          </div>
        </el-card>
      </div>
    </template>

    <!-- Mobile: compact list -->
    <template v-else>
      <div class="mobile-categories">
        <div
          v-for="category in toolCategories"
          :key="category.id"
          class="mobile-category-item"
          @click="$router.push(category.route)"
        >
          <el-icon class="item-icon"><component :is="category.icon" /></el-icon>
          <div class="item-info">
            <span class="item-name">{{ t('categories.' + category.id + '.name') }}</span>
            <span class="item-desc">{{ t('categories.' + category.id + '.description') }}</span>
          </div>
          <el-icon class="item-arrow"><ArrowRight /></el-icon>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { Star, ArrowRight } from '@element-plus/icons-vue'
import { useI18n } from 'vue-i18n'
import { useDeviceStore } from '@/stores/device.js'
import { toolCategories } from '../data/toolCategories'

const { t } = useI18n()
const deviceStore = useDeviceStore()
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

/* --- Mobile list layout --- */
.mobile-categories {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.mobile-category-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  background: var(--dt-bg-card);
  cursor: pointer;
  transition: background var(--dt-transition-fast);
  border-radius: var(--dt-radius-sm);
}

.mobile-category-item:active {
  background: var(--dt-bg-hover);
}

.item-icon {
  font-size: 22px;
  color: var(--dt-primary);
  flex-shrink: 0;
}

.item-info {
  flex: 1;
  min-width: 0;
}

.item-name {
  display: block;
  font-size: 15px;
  font-weight: 500;
  color: var(--dt-text-primary);
}

.item-desc {
  display: block;
  font-size: 12px;
  color: var(--dt-text-secondary);
  margin-top: 2px;
}

.item-arrow {
  color: var(--dt-text-placeholder);
  flex-shrink: 0;
}
</style>
