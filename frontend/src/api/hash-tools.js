import api from './index'

export const getAlgorithms = () => api.get('/hash-tools/algorithms')
export const generateHash = (text, algorithm = 'sha256') => api.post('/hash-tools/generate', { text, algorithm })
export const generateFileHash = (formData) => api.post('/hash-tools/generate-file', formData, { headers: { 'Content-Type': 'multipart/form-data' } })
export const verifyHash = (text, expectedHash, algorithm) => api.post('/hash-tools/verify', { text, expected_hash: expectedHash, algorithm })
