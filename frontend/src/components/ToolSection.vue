<template>
  <div class="tool-section">
    <div class="input-section">
      <h4 class="section-title">{{ inputLabel }}</h4>
      <slot name="input" />
    </div>
    <div class="action-section">
      <slot name="actions">
        <el-button type="primary" :loading="loading" @click="$emit('submit')">
          {{ actionText }}
        </el-button>
      </slot>
    </div>
    <div v-if="hasOutput" class="output-section">
      <h4 class="section-title">{{ outputLabel }}</h4>
      <slot name="output" />
    </div>
  </div>
</template>

<script setup>
defineProps({
  inputLabel: {
    type: String,
    required: true
  },
  outputLabel: {
    type: String,
    required: true
  },
  actionText: {
    type: String,
    default: '执行'
  },
  loading: {
    type: Boolean,
    default: false
  },
  hasOutput: {
    type: Boolean,
    default: true
  }
})

defineEmits(['submit'])
</script>
