<template>
  <div class="tool-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <el-icon class="card-icon"><component :is="icon" /></el-icon>
          <span>{{ title }}</span>
        </div>
      </template>
      <slot />
    </el-card>
  </div>
</template>

<script setup>
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
</script>
