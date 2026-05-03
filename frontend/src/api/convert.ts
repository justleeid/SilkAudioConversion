/**
 * 转换相关 API 方法
 * 参考 development.md 第 4.1.2 节、PRD.md 第 5 节
 */
import client from './client'
import type { ApiResponse, FileInfo, ConvertParams, TaskInfo } from '@/types'

/**
 * 上传文件
 */
export async function upload(files: File[]): Promise<ApiResponse<{ files: FileInfo[] }>> {
  const formData = new FormData()

  files.forEach((file) => {
    formData.append('files', file)
  })

  const response = await client.post<ApiResponse<{ files: FileInfo[] }>>('/api/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })

  return response.data
}

/**
 * 开始转换
 */
export async function convert(taskId: string, params: ConvertParams): Promise<ApiResponse<{ task_id: string }>> {
  const response = await client.post<ApiResponse<{ task_id: string }>>
    (`/api/convert/${taskId}`,
    params
  )

  return response.data
}

/**
 * 查询转换状态
 */
export async function queryStatus(taskId: string): Promise<ApiResponse<TaskInfo>> {
  const response = await client.get<ApiResponse<TaskInfo>>(`/api/convert/${taskId}/status`)

  return response.data
}

/**
 * 下载文件
 */
export function download(taskId: string): string {
  // 在开发环境使用相对路径，生产环境使用当前 origin
  const baseUrl = import.meta.env.DEV ? '' : window.location.origin
  return `${baseUrl}/api/download/${taskId}`
}