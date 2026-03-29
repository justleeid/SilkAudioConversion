/**
 * Axios 客户端配置
 * 参考 development.md 第 4.1.2 节
 */
import axios from 'axios'
import type { ApiResponse } from '@/types'
import { ElMessage } from 'element-plus'

// 创建 Axios 实例
// 动态构建后端 URL，支持 localhost 和局域网访问
const getBaseURL = () => {
  // 在开发环境，使用 Vite proxy，所以使用空字符串（相对路径）
  if (import.meta.env.DEV) {
    return ''
  }
  // 在生产环境，后端和前端在同一地址
  return window.location.origin
}

const client = axios.create({
  baseURL: getBaseURL(),
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
client.interceptors.request.use(
  (config) => {
    // 可以在这里添加认证 token
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
client.interceptors.response.use(
  (response) => {
    const data = response.data as ApiResponse

    // 检查业务错误码
    if (data.code !== 0) {
      ElMessage.error(data.message || '请求失败')
      return Promise.reject(new Error(data.message))
    }

    return response
  },
  (error) => {
    // 处理网络错误
    let message = '网络错误，请稍后重试'

    if (error.response) {
      // 服务器返回错误
      const status = error.response.status
      switch (status) {
        case 400:
          message = '请求参数错误'
          break
        case 401:
          message = '未授权访问'
          break
        case 403:
          message = '禁止访问'
          break
        case 404:
          message = '资源不存在'
          break
        case 413:
          message = '文件大小超出限制'
          break
        case 500:
          message = '服务器内部错误'
          break
        default:
          message = error.response.data?.message || `请求失败 (${status})`
      }
    } else if (error.request) {
      // 请求已发出但没有收到响应
      message = '服务器无响应，请检查网络连接'
    }

    ElMessage.error(message)
    return Promise.reject(error)
  }
)

export default client
