<template>
  <div class="tool-section">
    <div class="input-section">
      <h4 class="section-title">{{ inputLabel }}</h4>
      <slot name="input" />
    </div>
    <div class="action-section">
      <slot name="actions">
        <el-button type="primary" :loading="loading" @click="$emit('submit')">
          {{ displayActionText }}
        </el-button>
      </slot>
    </div>
    <div v-if="hasOutput" class="output-section" :aria-busy="loading">
      <h4 class="section-title">{{ outputLabel }}</h4>
      <slot name="output" />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

const props = defineProps({
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
    default: ''
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

const displayActionText = computed(() => props.actionText || t('common.execute'))
</script>
