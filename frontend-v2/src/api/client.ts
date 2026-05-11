import axios from 'axios'
import { useMessage } from 'naive-ui'

const api = axios.create({
  baseURL: ''
})

// 全局错误处理
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const msg = error.response?.data?.message || error.message || '请求失败'
    // 静默失败，由调用方处理或通过全局通知
    console.error('[API Error]', msg)
    return Promise.reject(error)
  }
)

export default api
