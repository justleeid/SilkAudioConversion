/**
 * API 通用响应格式
 */
export interface ApiResponse<T = any> {
  code: number;
  message: string;
  data?: T;
}

/**
 * 文件信息
 */
export interface FileInfo {
  task_id: string;
  filename: string;
  file_size: number;
  file_type: string;
  upload_url: string;
}

/**
 * 任务状态枚举
 */
export enum TaskStatus {
  PENDING = 'PENDING',
  PROCESSING = 'PROCESSING',
  COMPLETED = 'COMPLETED',
  FAILED = 'FAILED',
}

/**
 * 任务信息
 */
export interface TaskInfo {
  task_id: string;
  status: TaskStatus;
  progress: number;
  download_url?: string;
  error_message?: string;
}

/**
 * 目标格式枚举
 */
export enum TargetFormat {
  SILK = 'SILK',
  WAV = 'WAV',
  MP3 = 'MP3',
  AMR = 'AMR',
  M4A = 'M4A',
}

/**
 * 转换参数
 */
export interface ConvertParams {
  target_format: TargetFormat | string;
  sample_rate?: number;
  bit_rate?: number;
  frame_size?: number;
  wechat_compatible?: boolean;
}

/**
 * 暂存文件信息
 */
export interface StagingFile {
  file_id: string;
  original_name: string;
  output_name: string;
  size: number;
  created_at: string;
  expires_at: string;
  download_url: string;
}

/**
 * 暂存区统计
 */
export interface StagingStats {
  file_count: number;
  total_size: number;
  expire_hours: number;
  cleanup_interval: number;
}

/**
 * 应用配置
 */
export interface AppConfig {
  supported_formats: string[];
  sample_rates: number[];
  bit_rates: number[];
  frame_sizes: number[];
  cache_expire_hours: number;
}
