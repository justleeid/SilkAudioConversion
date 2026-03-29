/**
 * 应用状态管理
 * 参考 development.md 第 2.1 节（Pinia）
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { FileInfo, TaskInfo, ConvertParams } from '@/types'
import { upload, convert, queryStatus } from '@/api/convert'
import { TaskStatus } from '@/types'

export const useAppStore = defineStore('app', () => {
  // 状态
  const files = ref<FileInfo[]>([])
  const tasks = ref<Map<string, TaskInfo>>(new Map())
  const uploading = ref(false)
  const converting = ref(false)

  // 计算属性
  const hasFiles = computed(() => files.value.length > 0)
  const completedTasks = computed(() =>
    Array.from(tasks.value.values()).filter((t) => t.status === TaskStatus.COMPLETED)
  )
  const activeTasks = computed(() =>
    Array.from(tasks.value.values()).filter(
      (t) => t.status === TaskStatus.PENDING || t.status === TaskStatus.PROCESSING
    )
  )

  // Actions
  /**
   * 上传文件
   */
  async function uploadFiles(fileList: File[]) {
    try {
      uploading.value = true
      const response = await upload(fileList)

      if (response.data) {
        files.value.push(...response.data.files)
        // 初始化任务状态
        response.data.files.forEach((file) => {
          tasks.value.set(file.task_id, {
            task_id: file.task_id,
            status: TaskStatus.PENDING,
            progress: 0
          })
        })
      }

      return true
    } catch (error) {
      console.error('上传失败:', error)
      return false
    } finally {
      uploading.value = false
    }
  }

  /**
   * 开始转换
   */
  async function startConversion(taskId: string, params: ConvertParams) {
    try {
      converting.value = true
      const response = await convert(taskId, params)

      if (response.data) {
        // 更新任务状态
        const task = tasks.value.get(taskId)
        if (task) {
          task.status = TaskStatus.PROCESSING
        }

        // 开始轮询状态
        pollTaskStatus(taskId)
      }

      return true
    } catch (error) {
      console.error('转换失败:', error)
      return false
    } finally {
      converting.value = false
    }
  }

  /**
   * 轮询任务状态
   */
  async function pollTaskStatus(taskId: string) {
    const poll = async () => {
      try {
        const response = await queryStatus(taskId)

        if (response.data) {
          tasks.value.set(taskId, response.data)

          // 如果任务仍在进行，继续轮询
          if (
            response.data.status === TaskStatus.PENDING ||
            response.data.status === TaskStatus.PROCESSING
          ) {
            setTimeout(poll, 1000)
          }
        }
      } catch (error) {
        console.error('查询状态失败:', error)
      }
    }

    await poll()
  }

  /**
   * 移除文件
   */
  function removeFile(taskId: string) {
    const index = files.value.findIndex((f) => f.task_id === taskId)
    if (index > -1) {
      files.value.splice(index, 1)
    }
    tasks.value.delete(taskId)
  }

  /**
   * 清除已完成的任务
   */
  function clearCompletedTasks() {
    completedTasks.value.forEach((task) => {
      tasks.value.delete(task.task_id)
      const index = files.value.findIndex((f) => f.task_id === task.task_id)
      if (index > -1) {
        files.value.splice(index, 1)
      }
    })
  }

  /**
   * 重置状态
   */
  function reset() {
    files.value = []
    tasks.value.clear()
    uploading.value = false
    converting.value = false
  }

  return {
    // 状态
    files,
    tasks,
    uploading,
    converting,
    // 计算属性
    hasFiles,
    completedTasks,
    activeTasks,
    // Actions
    uploadFiles,
    startConversion,
    removeFile,
    clearCompletedTasks,
    reset
  }
})
