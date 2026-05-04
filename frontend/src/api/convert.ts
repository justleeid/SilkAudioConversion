import axios from 'axios';
import { ApiResponse, FileInfo, TaskInfo, ConvertParams, StagingFile, StagingStats, AppConfig } from '@/types';

const apiClient = axios.create({
  baseURL: 'http://127.0.0.1:8000/api',
});

/**
 * 上传文件
 */
export async function upload(files: File[]): Promise<ApiResponse<{ files: FileInfo[] }>> {
  const formData = new FormData();
  files.forEach(file => {
    formData.append('files', file);
  });

  const response = await apiClient.post<ApiResponse<{ files: FileInfo[] }>>('/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });

  return response.data;
}

/**
 * 开始转换
 */
export async function convert(taskId: string, params: ConvertParams): Promise<ApiResponse> {
  const response = await apiClient.post<ApiResponse>(`/convert/${taskId}`, params);
  return response.data;
}

/**
 * 查询转换状态
 */
export async function queryStatus(taskId: string): Promise<ApiResponse<TaskInfo>> {
  const response = await apiClient.get<ApiResponse<TaskInfo>>(`/status/${taskId}`);
  return response.data;
}

/**
 * 下载文件
 */
export async function download(taskId: string): Promise<void> {
  window.open(`http://127.0.0.1:8000/api/download/${taskId}`, '_blank');
}

/**
 * 合并 PLIST
 */
export async function mergePlist(taskIds: string[]): Promise<ApiResponse<{ file_id: string }>> {
  const response = await apiClient.post<ApiResponse<{ file_id: string }>>('/plist/merge', {
    task_ids: taskIds,
  });
  return response.data;
}

/**
 * 获取暂存区文件列表
 */
export async function getStaging(): Promise<ApiResponse<{ files: StagingFile[]; stats: StagingStats }>> {
  const response = await apiClient.get<ApiResponse<{ files: StagingFile[]; stats: StagingStats }>>('/staging');
  return response.data;
}

/**
 * 删除暂存文件
 */
export async function deleteStagingFile(fileId: string): Promise<ApiResponse> {
  const response = await apiClient.delete<ApiResponse>(`/staging/${fileId}`);
  return response.data;
}

/**
 * 清理过期文件
 */
export async function cleanupStaging(): Promise<ApiResponse<{ cleaned: number }>> {
  const response = await apiClient.post<ApiResponse<{ cleaned: number }>>('/staging/cleanup');
  return response.data;
}

/**
 * 获取系统配置
 */
export async function getConfig(): Promise<ApiResponse<AppConfig>> {
  const response = await apiClient.get<ApiResponse<AppConfig>>('/config');
  return response.data;
}
