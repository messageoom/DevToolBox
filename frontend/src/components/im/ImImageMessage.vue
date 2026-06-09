<template>
  <div class="im-image-message" @click="$emit('preview')">
    <div class="image-wrap">
      <img
        class="image-thumbnail"
        :src="displaySrc"
        alt=""
        loading="lazy"
      />
    </div>
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
</style>
