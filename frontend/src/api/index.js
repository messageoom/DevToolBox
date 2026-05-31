import axios from 'axios'
import { ElMessage } from 'element-plus'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' }
})

api.interceptors.response.use(
  response => response.data,
  error => {
    const message = error.response?.data?.error || '请求失败，请稍后重试'
    ElMessage.error(message)
    return Promise.reject(new Error(message))
  }
)

export default api
