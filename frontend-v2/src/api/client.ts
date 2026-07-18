import axios from 'axios'

export function resolveApiBaseUrl(): string {
  const envBase = import.meta.env.VITE_API_BASE_URL
  if (envBase) {
    return envBase
  }

  if (typeof window !== 'undefined') {
    const host = window.location.hostname
    const isLocalDev = host === 'localhost' || host === '127.0.0.1'
    if (!isLocalDev) {
      return `${window.location.protocol}//${host}:8000`
    }
  }

  return ''
}

const api = axios.create({
  baseURL: resolveApiBaseUrl()
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
