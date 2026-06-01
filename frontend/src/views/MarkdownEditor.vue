<template>
  <MarkdownEditorContainer />
</template>

<script>
import MarkdownEditorContainer from '../components/markdown-editor/MarkdownEditorContainer.vue'

export default {
  name: 'MarkdownEditor',
  components: {
    MarkdownEditorContainer
  }
}
</script>

<style scoped>
/* Page-level styles can be added here */

@media (max-width: 768px) {
  :deep(.markdown-editor-page) {
    padding: 0 !important;
  }
}
</style>
