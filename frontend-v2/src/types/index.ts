export enum TaskStatus {
  PENDING = 'pending',
  PROCESSING = 'processing',
  COMPLETED = 'completed',
  FAILED = 'failed'
}

export enum TargetFormat {
  WAV = 'WAV',
  MP3 = 'MP3',
  SILK = 'SILK',
  PLIST = 'PLIST'
}

export interface ApiResponse<T = any> {
  code: number
  message: string
  data?: T
}

export interface FileInfo {
  task_id: string
  filename: string
  size: number
  format: string
}

export interface ConvertParams {
  target_format: TargetFormat
  wechat_compatible?: boolean
  sample_rate?: number
  bit_rate?: number
  frame_size?: number
}

export interface TaskInfo {
  task_id: string
  status: TaskStatus
  progress: number
  estimated_time?: number
  error_message?: string
  download_url?: string
  filename?: string
}

export interface StagingFile {
  file_id: string
  original_name: string
  output_name: string
  size: number
  created_at: string
  expires_at: string
  download_url: string
}

export interface StagingStats {
  file_count: number
  total_size: number
  expire_hours: number
  cleanup_interval: number
}

export interface DbAudioRecord {
  audio_id: string
  title: string
  created_at: string
  size: number
  format: string
}

export interface DbAudioQueryParams {
  date_start: string
  date_end: string
  keyword?: string
  page?: number
  per_page?: number
}

export interface DbAudioQueryResult {
  total: number
  page: number
  per_page: number
  records: DbAudioRecord[]
}

export interface DbAudioImportResult {
  imported_count: number
  files: FileInfo[]
}
