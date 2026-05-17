<template>
  <div class="p-4 space-y-4">
    <h2 class="text-sm font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">文件输入</h2>

    <!-- Upload / DB Import tabs -->
    <n-tabs v-model:value="tab" type="segment" animated>
      <n-tab-pane name="local" tab="本地上传" />
      <n-tab-pane name="database" tab="数据库导入" />
    </n-tabs>
    <div v-show="tab === 'local'">
      <UploadArea />
    </div>
    <div v-show="tab === 'database'">
      <DbAudioImport />
    </div>

    <!-- Uploaded files list -->
    <div v-if="store.files.length > 0" class="space-y-2">
      <div class="flex items-center justify-between">
        <span class="text-xs text-gray-400">{{ store.files.length }} 个文件</span>
        <n-button size="tiny" quaternary type="error" @click="store.clearCompletedTasks()">
          清除已完成
        </n-button>
      </div>

      <div class="space-y-1">
        <div
          v-for="file in store.files"
          :key="file.task_id"
          class="flex items-center gap-3 px-3 py-2 rounded-lg bg-white dark:bg-[#1e1e22] border border-gray-100 dark:border-gray-800 hover:border-blue-200 dark:hover:border-blue-800 transition-colors"
        >
          <span class="text-gray-300 dark:text-gray-600 text-lg shrink-0">🎵</span>
          <div class="flex-1 min-w-0">
            <div class="text-sm text-gray-800 dark:text-gray-200 truncate">{{ file.filename }}</div>
            <div class="flex items-center gap-2 mt-0.5">
              <span class="text-xs text-gray-400">{{ formatSize(file.size) }}</span>
              <n-tag :bordered="false" size="tiny" type="info">{{ file.format.toUpperCase() }}</n-tag>
              <TaskStatusBadge :task-id="file.task_id" />
            </div>
          </div>
          <n-button size="tiny" quaternary type="error" @click="store.removeFile(file.task_id)">
            <template #icon><span>✕</span></template>
          </n-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { NTabs, NTabPane, NButton, NTag } from 'naive-ui'
import { useAppStore } from '@/stores/app'
import UploadArea from './UploadArea.vue'
import DbAudioImport from './DbAudioImport.vue'
import TaskStatusBadge from './TaskStatusBadge.vue'

const store = useAppStore()
const tab = ref('local')

function formatSize(bytes: number): string {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}
</script>
