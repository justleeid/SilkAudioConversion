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
 * API 响应泛类接口
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
}

/**
 * 上传进度接口
 */
export interface UploadProgress {
  loaded: number
  total: number
  percentage: number
}