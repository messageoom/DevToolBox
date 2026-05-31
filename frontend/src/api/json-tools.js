import api from './index'

export const formatJson = (jsonText) => api.post('/json-tools/format', { json_text: jsonText })
export const minifyJson = (jsonText) => api.post('/json-tools/minify', { json_text: jsonText })
export const validateJson = (jsonText) => api.post('/json-tools/validate', { json_text: jsonText })
export const escapeJson = (text) => api.post('/json-tools/escape', { text })
export const unescapeJson = (jsonString) => api.post('/json-tools/unescape', { json_string: jsonString })
