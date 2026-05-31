import api from './index'

export const generate = (data, options = {}) => api.post('/qr-tools/generate', { data, ...options })
export const beautify = (data, options = {}) => api.post('/qr-tools/beautify', { data, ...options })
