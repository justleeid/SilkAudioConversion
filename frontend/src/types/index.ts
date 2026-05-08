/**
 * 前端类型定义
 * 参考 development.md 第 4.1.3 节、PRD.md 第 5 节
 */

/**
 * 任务状态枚举
 */
export enum TaskStatus {
  PENDING = 'pending',
  PROCESSING = 'processing',
  COMPLETED = 'completed',
  FAILED = 'failed'
}

/**
 * 目标格式枚举
 */
export enum TargetFormat {
  WAV = 'WAV',
  MP3 = 'MP3',
  SILK = 'SILK',
  PLIST = 'PLIST'
}

/**
 * API 响应泛型接口
 */
export interface ApiResponse<T = any> {
  code: number
  message: string
  data?: T
}

/**
 * 文件信息接口
 */
export interface FileInfo {
  task_id: string
  filename: string
  size: number
  format: string
}

/**
 * 转换请求参数接口
 */
export interface ConvertParams {
  target_format: TargetFormat
  wechat_compatible?: boolean
  sample_rate?: number
  bit_rate?: number
  frame_size?: number
}

/**
 * 任务信息接口
 */
export interface TaskInfo {
  task_id: string
  status: TaskStatus
  progress: number
  estimated_time?: number
  error_message?: string
  download_url?: string
  filename?: string
}

/**
 * 上传进度接口
 */
export interface UploadProgress {
  loaded: number
  total: number
  percentage: number
}

/**
 * PLIST 合并请求
 */
export interface PlistMergeRequest {
  task_ids: string[]
  output_filename?: string
  include_metadata?: boolean
}

/**
 * PLIST 提取请求
 */
export interface PlistExtractRequest {
  plist_file_id: string
}

/**
 * 暂存区文件信息
 */
export interface StagingFile {
  file_id: string
  original_name: string
  output_name: string
  size: number
  created_at: string
  expires_at: string
  download_url: string
}

/**
 * 暂存区统计
 */
export interface StagingStats {
  file_count: number
  total_size: number
  expire_hours: number
  cleanup_interval: number
}

/**
 * 暂存区响应
 */
export interface StagingResponse {
  files: StagingFile[]
  stats: StagingStats
}

/**
 * 应用配置
 */
export interface AppConfig {
  supported_formats: string[]
  max_file_size: number
  max_file_count: number
  sample_rates: number[]
  bit_rates: number[]
  frame_sizes: number[]
  cache_expire_hours: number
  max_concurrent_tasks: number
}
