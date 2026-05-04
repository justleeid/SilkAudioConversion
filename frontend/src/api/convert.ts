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
  const response = await client.post<ApiResponse<{ task_id: string }>>(
    `/api/convert/${taskId}`,
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

/**
 * 合并 SILK 为 PLIST
 */
export async function mergePlist(params: {
  task_ids: string[]
  output_filename?: string
}): Promise<ApiResponse<{ file_id: string; filename: string; download_url: string }>> {
  const response = await client.post<ApiResponse<{ file_id: string; filename: string; download_url: string }>>(
    '/api/plist/merge',
    params
  )
  return response.data
}

/**
 * 从 PLIST 提取 SILK
 */
export async function extractPlist(fileId: string): Promise<ApiResponse<{ count: number; output_dir: string; files: string[] }>> {
  const response = await client.post<ApiResponse<{ count: number; output_dir: string; files: string[] }>>(
    '/api/plist/extract',
    { plist_file_id: fileId }
  )
  return response.data
}

/**
 * 查询暂存区
 */
export async function getStaging(): Promise<ApiResponse<{ files: import('@/types').StagingFile[]; stats: import('@/types').StagingStats }>> {
  const response = await client.get<ApiResponse<{ files: import('@/types').StagingFile[]; stats: import('@/types').StagingStats }>>('/api/staging')
  return response.data
}

/**
 * 删除暂存文件
 */
export async function deleteStagingFile(fileId: string): Promise<ApiResponse<null>> {
  const response = await client.delete<ApiResponse<null>>(`/api/staging/${fileId}`)
  return response.data
}

/**
 * 清理过期暂存文件
 */
export async function cleanupStaging(): Promise<ApiResponse<{ cleaned: number }>> {
  const response = await client.post<ApiResponse<{ cleaned: number }>>('/api/staging/cleanup')
  return response.data
}

/**
 * 获取应用配置
 */
export async function getConfig(): Promise<ApiResponse<import('@/types').AppConfig>> {
  const response = await client.get<ApiResponse<import('@/types').AppConfig>>('/api/config')
  return response.data
}
