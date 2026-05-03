/**
 * 通知工具函数
 * 参考 PRD.md 第 2.1.6 节、ui.md 第 6 节
 */
import { ElMessage, ElNotification } from 'element-plus'

/**
 * 成功通知
 */
export function showSuccess(message: string, title?: string) {
  if (title) {
    ElNotification({
      title,
      message,
      type: 'success',
      duration: 3000
    })
  } else {
    ElMessage.success(message)
  }
}

/**
 * 错误通知
 */
export function showError(message: string, title?: string) {
  if (title) {
    ElNotification({
      title,
      message,
      type: 'error',
      duration: 5000
    })
  } else {
    ElMessage.error(message)
  }
}

/**
 * 警告通知
 */
export function showWarning(message: string, title?: string) {
  if (title) {
    ElNotification({
      title,
      message,
      type: 'warning',
      duration: 4000
    })
  } else {
    ElMessage.warning(message)
  }
}

/**
 * 信息通知
 */
export function showInfo(message: string, title?: string) {
  if (title) {
    ElNotification({
      title,
      message,
      type: 'info',
      duration: 3000
    })
  } else {
    ElMessage.info(message)
  }
}

/**
 * 转换完成通知
 */
export function showConversionComplete(filename: string) {
  ElNotification({
    title: '转换完成',
    message: `文件 ${filename} 已成功转换`,
    type: 'success',
    duration: 4000,
    position: 'bottom-right'
  })
}

/**
 * 转换失败通知
 */
export function showConversionError(filename: string, error?: string) {
  ElNotification({
    title: '转换失败',
    message: `文件 ${filename} 转换失败${error ? `: ${error}` : ''}`,
    type: 'error',
    duration: 6000,
    position: 'bottom-right'
  })
}

/**
 * 上传成功通知
 */
export function showUploadSuccess(count: number) {
  ElNotification({
    title: '上传成功',
    message: `成功上传 ${count} 个文件`,
    type: 'success',
    duration: 3000,
    position: 'bottom-right'
  })
}

/**
 * 上传失败通知
 */
export function showUploadError(error: string) {
  ElNotification({
    title: '上传失败',
    message: error,
    type: 'error',
    duration: 5000,
    position: 'bottom-right'
  })
}