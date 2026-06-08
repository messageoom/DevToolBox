import { ref } from 'vue'

export function useLightbox() {
  const visible = ref(false)
  const images = ref([])
  const currentIndex = ref(0)

  function open(imageList, startIndex = 0) {
    images.value = imageList
    currentIndex.value = startIndex
    visible.value = true
  }

  function close() {
    visible.value = false
  }

  function next() {
    if (currentIndex.value < images.value.length - 1) {
      currentIndex.value++
    }
  }

  function prev() {
    if (currentIndex.value > 0) {
      currentIndex.value--
    }
  }

  function goTo(index) {
    if (index >= 0 && index < images.value.length) {
      currentIndex.value = index
    }
  }

  return { visible, images, currentIndex, open, close, next, prev, goTo }
}
