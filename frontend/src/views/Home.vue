<template>
  <div class="home">
    <!-- Hero section -->
    <div class="hero">
      <div class="hero-content">
        <div class="hero-badge">v2.0</div>
        <h1 class="hero-title">DevToolBox</h1>
        <p class="hero-desc">{{ t('tools.home.desc1') }}</p>
      </div>
      <div class="hero-bg-icon">
        <span class="material-symbols-rounded">developer_board</span>
      </div>
    </div>

    <!-- Quick tools (single-item categories shown as prominent cards) -->
    <div v-if="quickTools.length" class="quick-section">
      <div class="section-header">
        <span class="material-symbols-rounded section-icon">bolt</span>
        <h2>{{ t('tools.home.quickAccess') || 'Quick Access' }}</h2>
      </div>
      <div class="quick-grid">
        <div
          v-for="tool in quickTools"
          :key="tool.id"
          class="quick-card"
          @click="$router.push(tool.route)"
        >
          <div class="quick-icon" :style="{ background: tool.color + '15', color: tool.color }">
            <span class="material-symbols-rounded">{{ tool.icon }}</span>
          </div>
          <div class="quick-info">
            <span class="quick-name">{{ t('categories.' + tool.id + '.name') }}</span>
            <span class="quick-desc">{{ t('categories.' + tool.id + '.description') }}</span>
          </div>
          <span class="material-symbols-rounded quick-arrow">arrow_forward</span>
        </div>
      </div>
    </div>

    <!-- All tool categories -->
    <div class="section-header">
      <span class="material-symbols-rounded section-icon">grid_view</span>
      <h2>{{ t('tools.home.allTools') || 'All Tools' }}</h2>
    </div>
    <div class="categories-grid">
      <div
        v-for="category in multiToolCategories"
        :key="category.id"
        class="category-card"
        @click="$router.push(category.route)"
      >
        <div class="card-icon" :style="{ color: category.color }">
          <span class="material-symbols-rounded">{{ category.icon }}</span>
        </div>
        <div class="card-body">
          <h3 class="card-title">{{ t('categories.' + category.id + '.name') }}</h3>
          <p class="card-desc">{{ t('categories.' + category.id + '.description') }}</p>
          <div class="card-tags">
            <span
              v-for="tool in category.tools.slice(0, 4)"
              :key="tool"
              class="tag"
            >{{ t('categories.' + category.id + '.tools.' + tool) }}</span>
            <span v-if="category.tools.length > 4" class="tag tag-more">+{{ category.tools.length - 4 }}</span>
          </div>
        </div>
        <span class="material-symbols-rounded card-arrow">chevron_right</span>
      </div>
    </div>

    <!-- Mobile: single-item tools inline -->
    <template v-if="deviceStore.isMobile">
      <div class="mobile-quick-list">
        <div
          v-for="tool in quickTools"
          :key="tool.id"
          class="mobile-tool-item"
          @click="$router.push(tool.route)"
        >
          <div class="mobile-tool-icon" :style="{ color: tool.color }">
            <span class="material-symbols-rounded">{{ tool.icon }}</span>
          </div>
          <div class="mobile-tool-info">
            <span class="mobile-tool-name">{{ t('categories.' + tool.id + '.name') }}</span>
            <span class="mobile-tool-desc">{{ t('categories.' + tool.id + '.description') }}</span>
          </div>
          <span class="material-symbols-rounded mobile-tool-arrow">chevron_right</span>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useDeviceStore } from '@/stores/device.js'
import { toolCategories } from '../data/toolCategories'

const { t } = useI18n()
const deviceStore = useDeviceStore()

const quickTools = computed(() =>
  toolCategories.filter(cat => cat.tools.length === 1)
)

const multiToolCategories = computed(() =>
  toolCategories.filter(cat => cat.tools.length > 1)
)
</script>

<style scoped>
.home {
  padding: var(--dt-spacing-lg);
  max-width: var(--dt-content-max-width);
  margin: 0 auto;
}

/* =========================================
   Hero
   ========================================= */
.hero {
  position: relative;
  padding: 40px 32px;
  border-radius: var(--dt-radius-xl);
  background: linear-gradient(135deg, var(--dt-primary) 0%, #6366f1 100%);
  color: #fff;
  margin-bottom: 32px;
  overflow: hidden;
}

.hero-content {
  position: relative;
  z-index: 1;
}

.hero-badge {
  display: inline-block;
  padding: 2px 10px;
  background: rgba(255,255,255,0.2);
  border-radius: 99px;
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.5px;
  margin-bottom: 12px;
  backdrop-filter: blur(4px);
}

.hero-title {
  font-size: 32px;
  font-weight: 700;
  margin: 0 0 8px;
  letter-spacing: -0.5px;
}

.hero-desc {
  font-size: 15px;
  opacity: 0.85;
  margin: 0;
  max-width: 480px;
  line-height: 1.5;
}

.hero-bg-icon {
  position: absolute;
  right: -10px;
  bottom: -20px;
  opacity: 0.08;
  pointer-events: none;
}

.hero-bg-icon .material-symbols-rounded {
  font-size: 180px;
}

/* =========================================
   Section headers
   ========================================= */
.section-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
}

.section-header h2 {
  font-size: 18px;
  font-weight: 600;
  margin: 0;
  color: var(--dt-text-primary);
}

.section-icon {
  font-size: 20px;
  color: var(--dt-text-secondary);
}

/* =========================================
   Quick Access (single-item categories)
   ========================================= */
.quick-section {
  margin-bottom: 32px;
}

.quick-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.quick-card {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 16px 20px;
  background: var(--dt-bg-card);
  border: 1px solid var(--dt-border-lighter);
  border-radius: var(--dt-radius-lg);
  cursor: pointer;
  transition: all 0.2s ease;
}

.quick-card:hover {
  border-color: var(--dt-primary);
  box-shadow: var(--dt-shadow-sm);
  transform: translateY(-1px);
}

.quick-icon {
  width: 44px;
  height: 44px;
  border-radius: var(--dt-radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.quick-icon .material-symbols-rounded {
  font-size: 22px;
}

.quick-info {
  flex: 1;
  min-width: 0;
}

.quick-name {
  display: block;
  font-size: 15px;
  font-weight: 600;
  color: var(--dt-text-primary);
}

.quick-desc {
  display: block;
  font-size: 12px;
  color: var(--dt-text-secondary);
  margin-top: 2px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.quick-arrow {
  font-size: 18px;
  color: var(--dt-text-placeholder);
  flex-shrink: 0;
}

/* =========================================
   Categories Grid (multi-item)
   ========================================= */
.categories-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.category-card {
  display: flex;
  align-items: flex-start;
  gap: 14px;
  padding: 20px;
  background: var(--dt-bg-card);
  border: 1px solid var(--dt-border-lighter);
  border-radius: var(--dt-radius-lg);
  cursor: pointer;
  transition: all 0.2s ease;
}

.category-card:hover {
  border-color: var(--dt-primary);
  box-shadow: var(--dt-shadow-md);
  transform: translateY(-2px);
}

.card-icon {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  border-radius: var(--dt-radius-md);
  background: var(--dt-bg-section);
}

.card-icon .material-symbols-rounded {
  font-size: 22px;
}

.card-body {
  flex: 1;
  min-width: 0;
}

.card-title {
  font-size: 15px;
  font-weight: 600;
  margin: 0 0 4px;
  color: var(--dt-text-primary);
}

.card-desc {
  font-size: 13px;
  color: var(--dt-text-secondary);
  margin: 0 0 10px;
  line-height: 1.4;
}

.card-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.tag {
  display: inline-block;
  padding: 2px 8px;
  background: var(--dt-bg-section);
  border-radius: 4px;
  font-size: 11px;
  color: var(--dt-text-secondary);
  white-space: nowrap;
}

.tag-more {
  color: var(--dt-primary);
  font-weight: 600;
}

.card-arrow {
  font-size: 20px;
  color: var(--dt-text-placeholder);
  flex-shrink: 0;
  margin-top: 2px;
}

/* =========================================
   Responsive
   ========================================= */
@media (max-width: 768px) {
  .home {
    padding: var(--dt-spacing-xs);
  }

  .hero {
    padding: 24px 20px;
    border-radius: var(--dt-radius-lg);
    margin-bottom: 20px;
  }

  .hero-title {
    font-size: 24px;
  }

  .hero-desc {
    font-size: 13px;
  }

  .hero-bg-icon .material-symbols-rounded {
    font-size: 120px;
  }

  .quick-grid {
    grid-template-columns: 1fr;
  }

  .categories-grid {
    grid-template-columns: 1fr;
  }

  .category-card {
    padding: 16px;
  }
}

@media (max-width: 480px) {
  .hero {
    padding: 20px 16px;
  }

  .hero-title {
    font-size: 20px;
  }
}
</style>
