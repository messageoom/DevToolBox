<template>
  <div class="tool-page" :class="{ 'tool-page--mobile': deviceStore.isMobile }">
    <template v-if="deviceStore.isMobile">
      <h2 class="mobile-title">{{ title }}</h2>
      <slot />
    </template>
    <template v-else>
      <el-card>
        <template #header>
          <div class="card-header">
            <el-icon class="card-icon"><component :is="icon" /></el-icon>
            <span>{{ title }}</span>
          </div>
        </template>
        <slot />
      </el-card>
    </template>
  </div>
</template>

<script setup>
import { useDeviceStore } from '@/stores/device.js'

defineProps({
  title: {
    type: String,
    required: true
  },
  icon: {
    type: [String, Object],
    default: 'Document'
  }
})

const deviceStore = useDeviceStore()
</script>

<style scoped>
/* v2.2.1 */
.mobile-title {
  font-size: var(--dt-font-size-lg);
  font-weight: 600;
  color: var(--dt-text-primary);
  margin: 0 0 var(--dt-spacing-sm) 0;
}

/* Override global .tool-page--mobile { padding: 0 } —
   tool pages need horizontal breathing room on mobile */
.tool-page--mobile {
  padding: 0 var(--dt-spacing-md, 16px);
}
</style>
