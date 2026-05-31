import api from './index'

export const getAlgorithms = () => api.get('/crypto-tools/algorithms')
export const generateKey = (algorithm, params) => api.post(`/crypto-tools/${algorithm}/generate`, params)
export const encrypt = (algorithm, params) => api.post(`/crypto-tools/${algorithm}/encrypt`, params)
export const decrypt = (algorithm, params) => api.post(`/crypto-tools/${algorithm}/decrypt`, params)
export const sign = (algorithm, params) => api.post(`/crypto-tools/${algorithm}/sign`, params)
export const verify = (algorithm, params) => api.post(`/crypto-tools/${algorithm}/verify`, params)
