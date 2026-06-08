<template>
  <div class="im-image-message" @click="$emit('preview')">
    <div class="image-wrap">
      <img
        class="image-thumbnail"
        :src="displaySrc"
        :alt="filename"
        loading="lazy"
      />
    </div>
    <div v-if="showFilename" class="image-filename">{{ filename }}</div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  url: {
    type: String,
    required: true,
  },
  thumbnail: {
    type: String,
    default: '',
  },
  filename: {
    type: String,
    default: '',
  },
})

defineEmits(['preview'])

const displaySrc = computed(() => {
  return props.thumbnail || props.url
})

const showFilename = computed(() => {
  if (!props.filename) return false
  // Hide filename if it looks like a hash (e.g. "a1b2c3d4e5.png" with a long hex prefix)
  const nameWithoutExt = props.filename.replace(/\.[^.]+$/, '')
  return nameWithoutExt.length > 12 || !/^[a-f0-9]+$/.test(nameWithoutExt)
})
</script>

<style scoped>
.im-image-message {
  display: inline-block;
  cursor: pointer;
  max-width: 280px;
}

.image-wrap {
  overflow: hidden;
  border-radius: var(--dt-radius-md);
  box-shadow: var(--dt-shadow-sm);
  transition: box-shadow 0.2s ease;
}

.im-image-message:hover .image-wrap {
  box-shadow: var(--dt-shadow-md);
}

.image-thumbnail {
  display: block;
  max-width: 280px;
  max-height: 280px;
  width: auto;
  height: auto;
  object-fit: cover;
  border-radius: var(--dt-radius-md);
}

.image-filename {
  font-size: var(--dt-font-size-xs);
  color: var(--dt-text-secondary);
  margin-top: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 280px;
}
</style>
