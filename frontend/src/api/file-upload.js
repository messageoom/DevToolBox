import api from './index'

export const upload = (formData) => api.post('/file-upload/upload', formData, { headers: { 'Content-Type': 'multipart/form-data' } })
export const getFiles = () => api.get('/file-upload/files')
export const deleteFile = (filename) => api.delete(`/file-upload/files/${filename}`)
