import api from './index'

export const encode = (text) => api.post('/base64-tools/encode', { text })
export const decode = (encodedText) => api.post('/base64-tools/decode', { encoded_text: encodedText })
export const validate = (text) => api.post('/base64-tools/validate', { text })
