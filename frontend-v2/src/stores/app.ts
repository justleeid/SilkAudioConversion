import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { FileInfo, TaskInfo, ConvertParams } from '@/types'
import { upload, convert, queryStatus } from '@/api/convert'
import { TaskStatus } from '@/types'

export interface DbAudioQueryCache {
  source: string
  dateRange: [string, string]
  keyword: string
  page: number
  perPage: number
  searched: boolean
  total: number
  records: any[]
  checked: string[]
}

export const useAppStore = defineStore('app', () => {
  const files = ref<FileInfo[]>([])
  const tasks = ref<Map<string, TaskInfo>>(new Map())
  const uploading = ref(false)
  const converting = ref(false)
  const selectedForPlist = ref<Set<string>>(new Set())
  const dbAudioQueryCache = ref<DbAudioQueryCache | null>(null)

  const hasFiles = computed(() => files.value.length > 0)

  const completedTasks = computed(() =>
    Array.from(tasks.value.values()).filter((t) => t.status === TaskStatus.COMPLETED)
  )

  const activeTasks = computed(() =>
    Array.from(tasks.value.values()).filter(
      (t) => t.status === TaskStatus.PENDING || t.status === TaskStatus.PROCESSING
    )
  )

  async function uploadFiles(fileList: File[]) {
    uploading.value = true
    try {
      const response = await upload(fileList)
      if (response.data) {
        files.value.push(...response.data.files)
        response.data.files.forEach((file) => {
          tasks.value.set(file.task_id, {
            task_id: file.task_id,
            status: TaskStatus.PENDING,
            progress: 0
          })
        })
      }
      return true
    } catch {
      return false
    } finally {
      uploading.value = false
    }
  }

  async function startConversion(taskId: string, params: ConvertParams) {
    try {
      converting.value = true
      const response = await convert(taskId, params)
      if (response.data) {
        const task = tasks.value.get(taskId)
        if (task) task.status = TaskStatus.PROCESSING
        pollTaskStatus(taskId)
      }
      return true
    } catch {
      return false
    } finally {
      converting.value = false
    }
  }

  async function pollTaskStatus(taskId: string) {
    const poll = async () => {
      try {
        const response = await queryStatus(taskId)
        if (response.data) {
          tasks.value.set(taskId, response.data)
          const status = response.data.status
          if (status === TaskStatus.PENDING || status === TaskStatus.PROCESSING) {
            setTimeout(poll, 1000)
          }
        }
      } catch {
        // continue polling on transient errors
      }
    }
    await poll()
  }

  function removeFile(taskId: string) {
    const idx = files.value.findIndex((f) => f.task_id === taskId)
    if (idx > -1) files.value.splice(idx, 1)
    tasks.value.delete(taskId)
    selectedForPlist.value.delete(taskId)
  }

  function clearCompletedTasks() {
    completedTasks.value.forEach((task) => {
      tasks.value.delete(task.task_id)
      const idx = files.value.findIndex((f) => f.task_id === task.task_id)
      if (idx > -1) files.value.splice(idx, 1)
    })
  }

  function reset() {
    files.value = []
    tasks.value.clear()
    uploading.value = false
    converting.value = false
    selectedForPlist.value.clear()
  }

  function togglePlistSelection(taskId: string) {
    if (selectedForPlist.value.has(taskId)) {
      selectedForPlist.value.delete(taskId)
    } else {
      selectedForPlist.value.add(taskId)
    }
  }

  function clearPlistSelection() {
    selectedForPlist.value.clear()
  }

  function saveDbAudioQueryCache(cache: DbAudioQueryCache) {
    dbAudioQueryCache.value = {
      ...cache,
      dateRange: [...cache.dateRange] as [string, string],
      checked: [...cache.checked],
      records: cache.records.map((r) => ({ ...r }))
    }
  }

  function clearDbAudioQueryCache() {
    dbAudioQueryCache.value = null
  }

  // Staging version counter for cross-panel reactivity
  const stagingVersion = ref(0)
  function triggerStagingRefresh() { stagingVersion.value++ }

  return {
    files, tasks, uploading, converting, selectedForPlist, stagingVersion,
    dbAudioQueryCache,
    hasFiles, completedTasks, activeTasks,
    uploadFiles, startConversion, removeFile, clearCompletedTasks,
    reset, togglePlistSelection, clearPlistSelection,
    triggerStagingRefresh,
    saveDbAudioQueryCache, clearDbAudioQueryCache
  }
})
