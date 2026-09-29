import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { FileInfo, TaskInfo, ConvertParams } from '@/types'
import { upload, convert, queryStatus, previewPlist, splitPlist } from '@/api/convert'
import type { PlistPreviewData, PlistSplitParams } from '@/api/convert'
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

export type PlistMode = 'merge' | 'split'

export const useAppStore = defineStore('app', () => {
  const files = ref<FileInfo[]>([])
  const tasks = ref<Map<string, TaskInfo>>(new Map())
  const uploading = ref(false)
  const converting = ref(false)
  const selectedForPlist = ref<Set<string>>(new Set())
  const dbAudioQueryCache = ref<DbAudioQueryCache | null>(null)

  // PLIST 拆分相关状态
  const plistMode = ref<PlistMode>('merge')
  const selectedPlistFileId = ref<string | null>(null)
  const splitPreviewData = ref<PlistPreviewData | null>(null)
  const splitCount = ref(2)
  const splitMode = ref<'even' | 'manual'>('even')
  const outputPrefix = ref('split')
  const splitLoading = ref(false)

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
    const MAX_RETRIES = 10
    let retries = 0
    const poll = async () => {
      try {
        const response = await queryStatus(taskId)
        retries = 0
        if (response.data) {
          tasks.value.set(taskId, response.data)
          const status = response.data.status
          if (status === TaskStatus.PENDING || status === TaskStatus.PROCESSING) {
            setTimeout(poll, 1000)
          }
        }
      } catch {
        // 瞬时错误（网络抖动/后端短暂不可用）：继续轮询，超过上限后放弃并标记失败，
        // 避免任务永远停留在 processing
        retries += 1
        if (retries <= MAX_RETRIES) {
          setTimeout(poll, 1000 * Math.min(retries, 5))
          return
        }
        const task = tasks.value.get(taskId)
        if (task && (task.status === TaskStatus.PENDING || task.status === TaskStatus.PROCESSING)) {
          tasks.value.set(taskId, {
            ...task,
            status: TaskStatus.FAILED,
            error_message: '状态查询失败，请检查后端服务后重试'
          })
        }
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

  // PLIST 拆分相关方法
  function setPlistMode(mode: PlistMode) {
    plistMode.value = mode
  }

  async function loadPlistPreview(fileId: string) {
    splitLoading.value = true
    try {
      const response = await previewPlist(fileId)
      if (response.code === 0 && response.data) {
        splitPreviewData.value = response.data
        selectedPlistFileId.value = fileId
        // 重置拆分设置
        splitCount.value = 2
        splitMode.value = 'even'
        outputPrefix.value = 'split'
        return true
      }
      return false
    } catch {
      return false
    } finally {
      splitLoading.value = false
    }
  }

  async function executePlistSplit(): Promise<boolean> {
    if (!selectedPlistFileId.value || !splitPreviewData.value) return false

    splitLoading.value = true
    try {
      const params: PlistSplitParams = {
        plist_file_id: selectedPlistFileId.value,
        split_count: splitCount.value,
        split_mode: splitMode.value,
        output_prefix: outputPrefix.value
      }

      const response = await splitPlist(params)
      if (response.code === 0 && response.data) {
        // 清理拆分状态
        clearSplitState()
        return true
      }
      return false
    } catch {
      return false
    } finally {
      splitLoading.value = false
    }
  }

  function clearSplitState() {
    selectedPlistFileId.value = null
    splitPreviewData.value = null
    splitCount.value = 2
    splitMode.value = 'even'
    outputPrefix.value = 'split'
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
    // PLIST 拆分状态
    plistMode, selectedPlistFileId, splitPreviewData, splitCount, splitMode, outputPrefix, splitLoading,
    hasFiles, completedTasks, activeTasks,
    uploadFiles, startConversion, removeFile, clearCompletedTasks,
    reset, togglePlistSelection, clearPlistSelection,
    // PLIST 拆分方法
    setPlistMode, loadPlistPreview, executePlistSplit, clearSplitState,
    triggerStagingRefresh,
    saveDbAudioQueryCache, clearDbAudioQueryCache
  }
})
