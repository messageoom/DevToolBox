import api from './index'

export const encodeUrl = (url) => api.post('/url-tools/encode', { url })
export const decodeUrl = (encodedUrl) => api.post('/url-tools/decode', { encoded_url: encodedUrl })
export const parseUrl = (url) => api.post('/url-tools/parse', { url })
export const buildUrl = (components) => api.post('/url-tools/build', components)
export const validateUrl = (url) => api.post('/url-tools/validate', { url })
export const extractLinks = (text) => api.post('/url-tools/extract-links', { text })
export const urlToHar = (url, method = 'GET') => api.post('/url-tools/to-har', { url, method })
export const generateCurl = (har) => api.post('/url-tools/generate-curl', { har })
export const sendRequest = (url, method = 'GET', headers = {}, body = '') => api.post('/url-tools/send-request', { url, method, headers, body })
export const parseCurl = (curlCommand) => api.post('/url-tools/parse-curl', { curl_command: curlCommand })
export const executeCurl = (curlCommand) => api.post('/url-tools/execute-curl', { curl_command: curlCommand })
