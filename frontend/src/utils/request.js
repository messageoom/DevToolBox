import axios from 'axios'
import { ElMessage } from 'element-plus'

/**
 * 统一 API 客户端 —— 新代码请优先使用,替代在各视图重复 `import axios` + 重复的
 * `error.response?.data?.error || error.message` 错误提取样板。
 *
 * - baseURL 固定为 /api,调用方写相对路径(如 'file-upload/files')
 * - 响应拦截器自动解包 response.data,调用方直接拿到业务数据对象
 * - 错误自动 ElMessage.error 提示(仍会 reject,调用方可 try/catch 做额外处理)
 *
 * 用法:
 *   const data = await api.get('file-upload/files')          // data 即 response.data
 *   const res = await api.post('base64-tools/encode', {...}) // res 即 response.data
 *
 * 注:现有视图仍直接用 axios,未批量迁移(避免无测试兜底的大规模重构);
 * 新增工具页或重构旧页面时请改用本封装。
 */
const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
})

api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    const msg = error.response?.data?.error || error.message || '请求失败'
    ElMessage.error(msg)
    return Promise.reject(error)
  }
)

export default api
