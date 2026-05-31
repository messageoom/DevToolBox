import api from './index'

export const getCurrent = () => api.get('/timestamp-tools/current')
export const convert = (timestamp) => api.post('/timestamp-tools/convert', { timestamp })
export const parse = (datetimeStr, format) => api.post('/timestamp-tools/parse', { datetime: datetimeStr, format })
export const calculate = (params) => api.post('/timestamp-tools/calculate', params)
export const getFormats = () => api.get('/timestamp-tools/formats')
