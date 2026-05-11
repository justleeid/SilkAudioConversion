<template>
  <div class="p-4 space-y-4">
    <h2 class="text-sm font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">任务与暂存</h2>

    <!-- Task list -->
    <div v-if="allTasks.length > 0" class="space-y-2">
      <div class="flex items-center justify-between">
        <span class="text-xs text-gray-400">{{ allTasks.length }} 个任务</span>
      </div>

      <div class="space-y-1">
        <div
          v-for="task in allTasks"
          :key="task.task_id"
          class="px-3 py-2.5 rounded-lg bg-white dark:bg-[#1e1e22] border border-gray-100 dark:border-gray-800"
        >
          <div class="flex items-center justify-between gap-2">
            <div class="flex items-center gap-2 min-w-0 flex-1">
              <span class="text-sm text-gray-800 dark:text-gray-200 truncate">{{ getTaskName(task) }}</span>
              <TaskStatusBadge :task-id="task.task_id" />
            </div>
            <n-button
              v-if="task.status === 'completed' && task.download_url"
              size="tiny"
              type="primary"
              ghost
              @click="downloadFile(task.task_id)"
            >
              下载
            </n-button>
          </div>
          <n-progress
            v-if="task.status === 'processing'"
            :percentage="task.progress"
            :height="4"
            :border-radius="2"
            class="mt-2"
          />
          <div
            v-if="task.status === 'failed' && task.error_message"
            class="mt-2 text-xs text-red-500 bg-red-50 dark:bg-red-900/20 px-2 py-1 rounded"
          >
            {{ task.error_message }}
          </div>
        </div>
      </div>
    </div>

    <n-divider />

    <!-- Staging area -->
    <div class="space-y-2">
      <div class="flex items-center justify-between">
        <span class="text-xs text-gray-400">
          暂存区 · {{ stats?.file_count ?? 0 }} 个文件 · {{ formatSize(stats?.total_size ?? 0) }}
        </span>
        <div class="flex gap-1">
          <n-button size="tiny" quaternary @click="refresh">
            <template #icon><span>🔄</span></template>
          </n-button>
          <n-button size="tiny" quaternary type="warning" @click="doCleanup">清理过期</n-button>
        </div>
      </div>

      <div v-if="files.length === 0" class="text-center text-xs text-gray-400 py-4">
        暂存区暂无文件
      </div>

      <template v-else>
        <!-- Select-all bar -->
        <div class="flex items-center gap-2 px-3 py-1.5 rounded bg-gray-100 dark:bg-gray-800">
          <n-checkbox
            :checked="allChecked"
            :indeterminate="indeterminate"
            size="small"
            @update:checked="toggleSelectAll"
          />
          <span class="text-xs text-gray-500 flex-1">全选</span>
          <n-button
            v-if="checkedIds.length > 0"
            size="tiny"
            type="error"
            quaternary
            @click="doBatchDelete"
          >
            删除选中 ({{ checkedIds.length }})
          </n-button>
        </div>

        <!-- File rows -->
        <div class="space-y-1">
          <div
            v-for="f in files"
            :key="f.file_id"
            class="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-white dark:bg-[#1e1e22] border border-gray-100 dark:border-gray-800 group"
          >
            <!-- Checkbox -->
            <n-checkbox
              :checked="checkedIds.includes(f.file_id)"
              size="small"
              @update:checked="toggleCheck(f.file_id)"
            />

            <!-- Name (inline rename) -->
            <template v-if="renamingId === f.file_id">
              <n-input
                v-model:value="renameValue"
                size="tiny"
                class="flex-1"
                @keyup.enter="confirmRename(f)"
                @keyup.escape="cancelRename"
              />
              <n-button size="tiny" type="primary" @click="confirmRename(f)">确定</n-button>
              <n-button size="tiny" @click="cancelRename">取消</n-button>
            </template>
            <template v-else>
              <span
                class="text-sm text-gray-800 dark:text-gray-200 truncate flex-1 cursor-pointer hover:text-blue-500 transition-colors"
                :title="f.output_name || f.original_name"
                @dblclick="startRename(f)"
              >
                {{ f.output_name || f.original_name }}
              </span>
            </template>

            <div class="flex flex-col items-end shrink-0 text-right leading-tight">
              <span class="text-xs text-gray-400">{{ formatSize(f.size) }}</span>
              <span class="text-[11px] text-gray-500 dark:text-gray-400" :title="f.expires_at">
                {{ formatExpireTime(f.expires_at) }}
              </span>
            </div>

            <!-- Action buttons (visible on hover) -->
            <div class="hidden group-hover:flex items-center gap-0.5">
              <a :href="`/api/download/${f.file_id}`" target="_blank" class="no-underline">
                <n-button size="tiny" quaternary type="primary">下载</n-button>
              </a>
              <n-button size="tiny" quaternary @click="startRename(f)">重命名</n-button>
              <n-button size="tiny" quaternary type="error" @click="doDelete(f.file_id)">删除</n-button>
            </div>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import {
  NButton, NCheckbox, NInput, NProgress, NDivider,
  useMessage, useDialog
} from 'naive-ui'
import { useAppStore } from '@/stores/app'
import type { StagingFile, StagingStats } from '@/types'
import {
  getStaging, deleteStagingFile, batchDeleteStagingFiles,
  renameStagingFile, cleanupStaging
} from '@/api/convert'
import TaskStatusBadge from './TaskStatusBadge.vue'

const store = useAppStore()
const message = useMessage()
const dialog = useDialog()

const files = ref<StagingFile[]>([])
const stats = ref<StagingStats | null>(null)
const checkedIds = ref<string[]>([])
const renamingId = ref<string | null>(null)
const renameValue = ref('')

// -- Select-all computed --
const allChecked = computed(() => files.value.length > 0 && checkedIds.value.length === files.value.length)
const indeterminate = computed(() => checkedIds.value.length > 0 && checkedIds.value.length < files.value.length)

function toggleCheck(id: string) {
  const i = checkedIds.value.indexOf(id)
  if (i > -1) checkedIds.value.splice(i, 1)
  else checkedIds.value.push(id)
}

function toggleSelectAll(val: boolean) {
  checkedIds.value = val ? files.value.map((f) => f.file_id) : []
}

// -- Task helpers --
const allTasks = computed(() =>
  Array.from(store.tasks.values()).sort((a, b) => {
    const order: Record<string, number> = { processing: 0, pending: 1, failed: 2, completed: 3 }
    return (order[a.status] ?? 9) - (order[b.status] ?? 9)
  })
)

function getTaskName(task: any): string {
  if (task.filename) return task.filename
  const f = store.files.find((x) => x.task_id === task.task_id)
  if (f) return f.filename
  const sf = files.value.find((x) => x.file_id === task.task_id)
  if (sf) return sf.output_name || sf.original_name
  return task.task_id.slice(0, 8) + '...'
}

function downloadFile(taskId: string) {
  window.open(`/api/download/${taskId}`, '_blank')
}

// -- Staging CRUD --
async function refresh() {
  try {
    const r = await getStaging()
    if (r.data) {
      files.value = r.data.files
      stats.value = r.data.stats
      // Prune checkedIds to only existing files
      const valid = new Set(r.data.files.map((f: StagingFile) => f.file_id))
      checkedIds.value = checkedIds.value.filter((id) => valid.has(id))
    }
  } catch { files.value = [] }
}

async function doDelete(fileId: string) {
  dialog.warning({
    title: '确认删除',
    content: '删除后无法恢复',
    positiveText: '删除',
    negativeText: '取消',
    onPositiveClick: async () => {
      try {
        await deleteStagingFile(fileId)
        checkedIds.value = checkedIds.value.filter((id) => id !== fileId)
        message.success('已删除')
        refresh()
        store.triggerStagingRefresh()
      } catch { message.error('删除失败') }
    }
  })
}

async function doBatchDelete() {
  if (!checkedIds.value.length) return
  dialog.warning({
    title: '批量删除',
    content: `确认删除选中的 ${checkedIds.value.length} 个文件？`,
    positiveText: '删除',
    negativeText: '取消',
    onPositiveClick: async () => {
      try {
        const ids = [...checkedIds.value]
        const r = await batchDeleteStagingFiles(ids)
        if (r.code === 0) {
          message.success(r.message || '批量删除完成')
          checkedIds.value = []
          refresh()
          store.triggerStagingRefresh()
        } else {
          message.error(r.message || '批量删除失败')
        }
      } catch { message.error('批量删除失败') }
    }
  })
}

async function doCleanup() {
  const r = await cleanupStaging()
  if (r.code === 0) { message.success(r.message || '清理完成'); refresh(); store.triggerStagingRefresh() }
  else message.error(r.message || '清理失败')
}

// -- Rename --
function startRename(f: StagingFile) {
  renamingId.value = f.file_id
  const name = f.output_name || f.original_name
  const dot = name.lastIndexOf('.')
  renameValue.value = dot > -1 ? name.substring(0, dot) : name
}

function cancelRename() {
  renamingId.value = null
  renameValue.value = ''
}

async function confirmRename(f: StagingFile) {
  const v = renameValue.value.trim()
  if (!v) { message.warning('文件名不能为空'); return }
  try {
    const r = await renameStagingFile(f.file_id, v)
    if (r.code === 0) { message.success('重命名成功'); cancelRename(); refresh(); store.triggerStagingRefresh() }
    else message.error(r.message || '重命名失败')
  } catch { message.error('重命名失败') }
}

function formatSize(b: number) {
  if (b < 1024) return b + ' B'
  if (b < 1048576) return (b / 1024).toFixed(1) + ' KB'
  return (b / 1048576).toFixed(1) + ' MB'
}

function formatExpireTime(value: string) {
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return '过期时间未知'
  const pad = (n: number) => String(n).padStart(2, '0')
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())} ${pad(date.getHours())}:${pad(date.getMinutes())}`
}

onMounted(refresh)

// Auto-refresh staging when tasks complete
let prevCompleteCount = 0
watch(allTasks, () => {
  const currentCount = allTasks.value.filter((t) => t.status === 'completed').length
  if (currentCount > prevCompleteCount) {
    refresh()
  }
  prevCompleteCount = currentCount
})
</script>
