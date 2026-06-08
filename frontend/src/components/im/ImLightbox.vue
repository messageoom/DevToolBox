<template>
  <Teleport to="body">
    <Transition name="lightbox-fade">
      <div
        v-if="visible && images.length > 0"
        class="im-lightbox"
        @click.self="handleBackdropClick"
      >
        <!-- Top bar -->
        <div class="im-lightbox__topbar">
          <span class="im-lightbox__counter">
            {{ t('tools.im.imageOf', { current: currentIndex + 1, total: images.length }) }}
          </span>
          <div class="im-lightbox__actions">
            <button
              class="im-lightbox__btn"
              :title="t('common.download')"
              @click="handleDownload"
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                <polyline points="7 10 12 15 17 10" />
                <line x1="12" y1="15" x2="12" y2="3" />
              </svg>
            </button>
            <button
              class="im-lightbox__btn im-lightbox__btn--close"
              :title="t('common.close')"
              @click="emit('close')"
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <line x1="18" y1="6" x2="6" y2="18" />
                <line x1="6" y1="6" x2="18" y2="18" />
              </svg>
            </button>
          </div>
        </div>

        <!-- Navigation: Previous -->
        <button
          v-if="currentIndex > 0"
          class="im-lightbox__nav im-lightbox__nav--prev"
          @click.stop="emit('prev')"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="15 18 9 12 15 6" />
          </svg>
        </button>

        <!-- Main image -->
        <div class="im-lightbox__stage" @click.self="handleBackdropClick">
          <Transition :name="slideDirection" mode="out-in">
            <img
              :key="currentImage?.url"
              :src="currentImage?.url"
              :alt="currentImage?.filename || ''"
              class="im-lightbox__image"
            />
          </Transition>
        </div>

        <!-- Navigation: Next -->
        <button
          v-if="currentIndex < images.length - 1"
          class="im-lightbox__nav im-lightbox__nav--next"
          @click.stop="emit('next')"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="9 18 15 12 9 6" />
          </svg>
        </button>

        <!-- Bottom thumbnail strip -->
        <div v-if="images.length > 1" class="im-lightbox__strip">
          <button
            v-for="(img, idx) in images"
            :key="idx"
            class="im-lightbox__thumb"
            :class="{ 'im-lightbox__thumb--active': idx === currentIndex }"
            @click.stop="emit('go-to', idx)"
          >
            <img
              v-if="img.thumbnail || img.url"
              :src="img.thumbnail || img.url"
              :alt="img.filename || ''"
            />
            <span v-else class="im-lightbox__thumb-dot"></span>
          </button>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { computed, ref, watch, onMounted, onBeforeUnmount } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

const props = defineProps({
  visible: {
    type: Boolean,
    default: false,
  },
  images: {
    type: Array,
    default: () => [],
  },
  currentIndex: {
    type: Number,
    default: 0,
  },
})

const emit = defineEmits(['close', 'next', 'prev', 'go-to'])

const previousIndex = ref(0)

watch(() => props.currentIndex, (newIdx, oldIdx) => {
  previousIndex.value = oldIdx ?? 0
})

const slideDirection = computed(() => {
  return props.currentIndex > previousIndex.value ? 'lightbox-slide-left' : 'lightbox-slide-right'
})

const currentImage = computed(() => {
  if (props.images.length === 0) return null
  return props.images[props.currentIndex] || null
})

function handleBackdropClick() {
  emit('close')
}

function handleDownload() {
  const img = currentImage.value
  if (!img?.url) return
  const link = document.createElement('a')
  link.href = img.url
  link.download = img.filename || 'image'
  link.target = '_blank'
  link.rel = 'noopener noreferrer'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

function handleKeydown(e) {
  if (!props.visible) return
  if (e.key === 'Escape') {
    emit('close')
  } else if (e.key === 'ArrowLeft') {
    if (props.currentIndex > 0) emit('prev')
  } else if (e.key === 'ArrowRight') {
    if (props.currentIndex < props.images.length - 1) emit('next')
  }
}

onMounted(() => {
  document.addEventListener('keydown', handleKeydown)
})

onBeforeUnmount(() => {
  document.removeEventListener('keydown', handleKeydown)
})
</script>

<style scoped>
/* Overlay */
.im-lightbox {
  position: fixed;
  inset: 0;
  z-index: 2000;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.85);
  user-select: none;
  -webkit-user-select: none;
}

/* Top bar */
.im-lightbox__topbar {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--dt-spacing-md);
  z-index: 1;
}

.im-lightbox__counter {
  color: rgba(255, 255, 255, 0.8);
  font-size: var(--dt-font-size-sm);
  font-weight: 500;
  background: rgba(0, 0, 0, 0.4);
  padding: var(--dt-spacing-xs) var(--dt-spacing-sm);
  border-radius: var(--dt-radius-sm);
}

.im-lightbox__actions {
  display: flex;
  align-items: center;
  gap: var(--dt-spacing-xs);
}

/* Buttons */
.im-lightbox__btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border: none;
  border-radius: var(--dt-radius-sm);
  background: rgba(255, 255, 255, 0.12);
  color: rgba(255, 255, 255, 0.9);
  cursor: pointer;
  transition: background var(--dt-transition-fast), color var(--dt-transition-fast);
}

.im-lightbox__btn:hover {
  background: rgba(255, 255, 255, 0.25);
  color: #ffffff;
}

.im-lightbox__btn svg {
  width: 20px;
  height: 20px;
}

/* Navigation arrows */
.im-lightbox__nav {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  z-index: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  border: none;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.12);
  color: rgba(255, 255, 255, 0.9);
  cursor: pointer;
  transition: background var(--dt-transition-fast), color var(--dt-transition-fast);
}

.im-lightbox__nav:hover {
  background: rgba(255, 255, 255, 0.25);
  color: #ffffff;
}

.im-lightbox__nav svg {
  width: 24px;
  height: 24px;
}

.im-lightbox__nav--prev {
  left: var(--dt-spacing-md);
}

.im-lightbox__nav--next {
  right: var(--dt-spacing-md);
}

/* Stage */
.im-lightbox__stage {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  padding: 60px 64px 72px;
  pointer-events: none;
}

.im-lightbox__image {
  max-width: 90vw;
  max-height: 80vh;
  object-fit: contain;
  border-radius: var(--dt-radius-sm);
  pointer-events: auto;
}

/* Bottom thumbnail strip */
.im-lightbox__strip {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--dt-spacing-xs);
  padding: var(--dt-spacing-sm) var(--dt-spacing-md);
  background: linear-gradient(transparent, rgba(0, 0, 0, 0.5));
}

.im-lightbox__thumb {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border: 2px solid transparent;
  border-radius: var(--dt-radius-sm);
  overflow: hidden;
  background: rgba(255, 255, 255, 0.1);
  cursor: pointer;
  transition: border-color var(--dt-transition-fast), transform var(--dt-transition-fast);
  flex-shrink: 0;
}

.im-lightbox__thumb:hover {
  transform: scale(1.1);
  border-color: rgba(255, 255, 255, 0.5);
}

.im-lightbox__thumb--active {
  border-color: var(--dt-primary);
  transform: scale(1.1);
}

.im-lightbox__thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.im-lightbox__thumb-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.5);
}

/* Fade transition */
.lightbox-fade-enter-active,
.lightbox-fade-leave-active {
  transition: opacity var(--dt-transition-base);
}

.lightbox-fade-enter-from,
.lightbox-fade-leave-to {
  opacity: 0;
}

/* Slide left transition (navigating forward) */
.lightbox-slide-left-enter-active,
.lightbox-slide-left-leave-active {
  transition: opacity 0.25s ease, transform 0.25s ease;
}

.lightbox-slide-left-enter-from {
  opacity: 0;
  transform: translateX(30px);
}

.lightbox-slide-left-leave-to {
  opacity: 0;
  transform: translateX(-30px);
}

/* Slide right transition (navigating backward) */
.lightbox-slide-right-enter-active,
.lightbox-slide-right-leave-active {
  transition: opacity 0.25s ease, transform 0.25s ease;
}

.lightbox-slide-right-enter-from {
  opacity: 0;
  transform: translateX(-30px);
}

.lightbox-slide-right-leave-to {
  opacity: 0;
  transform: translateX(30px);
}
</style>
