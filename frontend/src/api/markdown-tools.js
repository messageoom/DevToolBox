import api from './index'

export const toHtml = (markdownText) => api.post('/markdown-tools/to-html', { markdown_text: markdownText })
export const toPlain = (markdownText) => api.post('/markdown-tools/to-plain', { markdown_text: markdownText })
export const escape = (text) => api.post('/markdown-tools/escape', { text })
export const unescape = (escapedText) => api.post('/markdown-tools/unescape', { escaped_text: escapedText })
export const extractLinks = (markdownText) => api.post('/markdown-tools/extract-links', { markdown_text: markdownText })
export const extractImages = (markdownText) => api.post('/markdown-tools/extract-images', { markdown_text: markdownText })
export const tableToMarkdown = (html) => api.post('/markdown-tools/table-to-markdown', { html })
export const validate = (markdownText) => api.post('/markdown-tools/validate', { markdown_text: markdownText })
export const getStats = (markdownText) => api.post('/markdown-tools/stats', { markdown_text: markdownText })
