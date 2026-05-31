import api from './index'

export const mdToHtml = (markdownText) => api.post('/data-conversion/md-to-html', { markdown_text: markdownText })
export const htmlToMd = (htmlText) => api.post('/data-conversion/html-to-md', { html_text: htmlText })
export const mdToPdf = (markdownText, options = {}) => api.post('/data-conversion/md-to-pdf', { markdown_text: markdownText, ...options })
export const htmlToPdf = (htmlText, options = {}) => api.post('/data-conversion/html-to-pdf', { html_text: htmlText, ...options })
export const uploadPdf = (formData) => api.post('/data-conversion/upload-pdf', formData, { headers: { 'Content-Type': 'multipart/form-data' } })
export const pdfToMd = (filename) => api.post('/data-conversion/pdf-to-md', { filename })
