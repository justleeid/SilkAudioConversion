import client from './client'
import type {
  ApiResponse, FileInfo, ConvertParams, TaskInfo,
  StagingFile, StagingStats,
  DbAudioQueryParams, DbAudioQueryResult, DbAudioImportResult
} from '@/types'

// -- 上传 & 转换 --

export async function upload(files: File[]): Promise<ApiResponse<{ files: FileInfo[] }>> {
  const fd = new FormData()
  files.forEach((f) => fd.append('files', f))
  const { data } = await client.post('/api/upload', fd, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
  return data
}

export async function convert(taskId: string, params: ConvertParams): Promise<ApiResponse<{ task_id: string }>> {
  const { data } = await client.post(`/api/convert/${taskId}`, params)
  return data
}

export async function queryStatus(taskId: string): Promise<ApiResponse<TaskInfo>> {
  const { data } = await client.get(`/api/convert/${taskId}/status`)
  return data
}

// -- PLIST --

export async function mergePlist(params: {
  task_ids: string[]
  output_filename?: string
}): Promise<ApiResponse<{ file_id: string; filename: string; download_url: string }>> {
  const { data } = await client.post('/api/plist/merge', params)
  return data
}

// -- 暂存区 --

export async function getStaging(): Promise<ApiResponse<{ files: StagingFile[]; stats: StagingStats }>> {
  const { data } = await client.get('/api/staging')
  return data
}

export async function deleteStagingFile(fileId: string): Promise<ApiResponse<null>> {
  const { data } = await client.delete(`/api/staging/${fileId}`)
  return data
}

export async function batchDeleteStagingFiles(fileIds: string[]): Promise<ApiResponse<{ deleted: number }>> {
  const { data } = await client.post('/api/staging/batch-delete', { file_ids: fileIds })
  return data
}

export async function renameStagingFile(fileId: string, name: string): Promise<ApiResponse<{ file_id: string; name: string }>> {
  const { data } = await client.post(`/api/staging/${fileId}/rename`, { name })
  return data
}

export async function cleanupStaging(): Promise<ApiResponse<{ cleaned: number }>> {
  const { data } = await client.post('/api/staging/cleanup')
  return data
}

// -- 数据库音频 --

export async function queryDbAudio(params: DbAudioQueryParams): Promise<ApiResponse<DbAudioQueryResult>> {
  const { data } = await client.get('/api/db-audio/query', { params })
  return data
}

export async function importDbAudio(audioIds: string[], source: string = 'mysql'): Promise<ApiResponse<DbAudioImportResult>> {
  const { data } = await client.post('/api/db-audio/import', { audio_ids: audioIds, source })
  return data
}

// -- 数据库管理 --

export async function getAdminStatus(): Promise<ApiResponse<{ admin_enabled: boolean }>> {
  const { data } = await client.get('/api/db-audio/admin/status')
  return data
}

export async function deleteDbAudioRecord(audioId: string, source: string): Promise<ApiResponse<{ affected: number }>> {
  const { data } = await client.delete(`/api/db-audio/record/${audioId}`, { params: { source } })
  return data
}

export async function updateDbAudioTitle(audioId: string, title: string, source: string): Promise<ApiResponse<{ affected: number }>> {
  const { data } = await client.put(`/api/db-audio/record/${audioId}/title`, { title, source })
  return data
}
