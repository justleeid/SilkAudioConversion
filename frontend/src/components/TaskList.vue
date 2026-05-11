<template>
  <div class="task-list">
    <el-card v-if="allTasks.length > 0">
      <template #header>
        <div class="card-header">
          <span>转换任务</span>
          <el-tag>{{ allTasks.length }} 个任务</el-tag>
        </div>
      </template>

      <div
        v-for="task in allTasks"
        :key="task.task_id"
        class="task-item"
      >
        <div class="task-header">
          <div class="task-info">
            <span class="task-id">{{ getTaskDisplayName(task) }}</span>
            <el-tag
              :type="getStatusTagType(task.status)"
              size="small"
            >
              {{ getStatusText(task.status) }}
            </el-tag>
          </div>

          <!-- 下载按钮 -->
          <el-button
            v-if="task.status === TaskStatus.COMPLETED && task.download_url"
            type="primary"
            size="small"
            @click="handleDownload(task)"
          >
            下载
          </el-button>
        </div>

        <!-- 进度条 -->
        <el-progress
          v-if="task.status === TaskStatus.PROCESSING"
          :percentage="task.progress"
          :status="(task.status as TaskStatus) === TaskStatus.COMPLETED ? 'success' : undefined"
        />

        <!-- 错误消息 -->
        <el-alert
          v-if="task.status === TaskStatus.FAILED && task.error_message"
          :title="task.error_message"
          type="error"
          :closable="false"
          show-icon
        />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted } from 'vue'
import { useAppStore } from '@/stores/app'
import { TaskStatus } from '@/types'
import type { StagingFile } from '@/types'
import { download, getStaging } from '@/api/convert'

const store = useAppStore()
const stagingFiles = ref<StagingFile[]>([])

// 所有任务
const allTasks = computed(() => Array.from(store.tasks.values()))

// 根据任务 ID 获取文件信息
function getFileById(taskId: string) {
  return store.files.find((f) => f.task_id === taskId)
}

// 获取任务显示名称
function getTaskDisplayName(task: any): string {
  // 1. 优先 task.filename
  if (task.filename) return task.filename
  // 2. 查找上传文件
  const file = getFileById(task.task_id)
  if (file) return file.filename
  // 3. 查找暂存区
  const staging = stagingFiles.value.find((f) => f.file_id === task.task_id)
  if (staging) return staging.output_name || staging.original_name
  // 4. 降级显示 task_id 前8位
  return task.task_id.substring(0, 8) + '...'
}

async function loadStagingFiles() {
  try {
    const response = await getStaging()
    if (response.data) {
      stagingFiles.value = response.data.files
    }
  } catch {}
}

onMounted(() => {
  loadStagingFiles()
})

// 获取状态标签类型
function getStatusTagType(status: TaskStatus): '' | 'success' | 'warning' | 'danger' | 'info' {
  switch (status) {
    case TaskStatus.PENDING:
      return 'info'
    case TaskStatus.PROCESSING:
      return 'warning'
    case TaskStatus.COMPLETED:
      return 'success'
    case TaskStatus.FAILED:
      return 'danger'
    default:
      return 'info'
  }
}

// 获取状态文本
function getStatusText(status: TaskStatus): string {
  switch (status) {
    case TaskStatus.PENDING:
      return '等待中'
    case TaskStatus.PROCESSING:
      return '转换中'
    case TaskStatus.COMPLETED:
      return '已完成'
    case TaskStatus.FAILED:
      return '失败'
    default:
      return '未知'
  }
}

// 处理下载
function handleDownload(task: any) {
  const url = download(task.task_id)
  window.open(url, '_blank')
}
</script>

<style scoped>
.task-list {
  margin-top: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.task-item {
  padding: 16px;
  margin-bottom: 12px;
  background-color: var(--el-fill-color-lighter);
  border-radius: 4px;
}

.task-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.task-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.task-id {
  font-weight: 500;
}

.el-progress {
  margin-top: 8px;
}

.el-alert {
  margin-top: 8px;
}

@media (max-width: 768px) {
  .task-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }

  .task-info {
    flex-wrap: wrap;
  }
}
</style>
