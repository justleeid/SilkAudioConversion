<template>
  <div class="upload-area">
    <el-upload
      drag
      multiple
      :auto-upload="false"
      :show-file-list="false"
      :on-change="handleFileChange"
      accept=".silk,.wav,.mp3,.amr,.m4a"
    >
      <el-icon class="el-icon--upload"><upload-filled /></el-icon>
      <div class="el-upload__text">
        拖拽文件到此处或 <em>点击上传</em>
      </div>
      <template #tip>
        <div class="el-upload__tip">
          支持 SILK、WAV、MP3、AMR、M4A 格式，单个文件最大 50MB，最多 50 个文件
        </div>
      </template>
    </el-upload>

    <!-- 文件列表 -->
    <div v-if="store.files.length > 0" class="file-list">
      <div class="file-list-header">
        <el-checkbox
          :model-value="allChecked"
          :indeterminate="indeterminate"
          @change="toggleSelectAll"
        />
        <span>已选择 {{ store.files.length }} 个文件</span>
        <div class="header-actions">
          <el-button
            v-if="selectedIds.size > 0"
            size="small"
            type="danger"
            @click="handleBatchDelete"
          >
            删除选中 ({{ selectedIds.size }})
          </el-button>
          <el-button size="small" @click="store.clearCompletedTasks()">
            清除已完成
          </el-button>
        </div>
      </div>

      <div
        v-for="file in store.files"
        :key="file.task_id"
        class="file-item"
      >
        <el-checkbox
          :model-value="selectedIds.has(file.task_id)"
          @change="toggleSelect(file.task_id)"
          class="file-checkbox"
        />
        <div class="file-info">
          <el-icon class="file-icon"><document /></el-icon>
          <div class="file-details">
            <div class="file-name">{{ file.filename }}</div>
            <div class="file-meta">
              <span>{{ formatFileSize(file.size) }}</span>
              <el-tag size="small" type="info">{{ file.format.toUpperCase() }}</el-tag>
            </div>
          </div>
        </div>
        <el-button
          size="small"
          type="danger"
          :icon="Delete"
          circle
          @click="store.removeFile(file.task_id)"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useAppStore } from '@/stores/app'
import { ElMessage, ElMessageBox } from 'element-plus'
import { UploadFilled, Document, Delete } from '@element-plus/icons-vue'

const store = useAppStore()

// 多选状态
const selectedIds = ref<Set<string>>(new Set())

const allChecked = computed(() => {
  if (store.files.length === 0) return false
  return selectedIds.value.size === store.files.length
})

const indeterminate = computed(() => {
  return selectedIds.value.size > 0 && selectedIds.value.size < store.files.length
})

function toggleSelect(taskId: string) {
  const next = new Set(selectedIds.value)
  if (next.has(taskId)) {
    next.delete(taskId)
  } else {
    next.add(taskId)
  }
  selectedIds.value = next
}

function toggleSelectAll(val: boolean) {
  if (val) {
    selectedIds.value = new Set(store.files.map((f) => f.task_id))
  } else {
    selectedIds.value = new Set()
  }
}

async function handleBatchDelete() {
  if (selectedIds.value.size === 0) return
  try {
    await ElMessageBox.confirm(
      `确认删除选中的 ${selectedIds.value.size} 个文件？`,
      '批量删除',
      { type: 'warning' }
    )
    store.removeFiles([...selectedIds.value])
    selectedIds.value = new Set()
    ElMessage.success('已删除选中文件')
  } catch {
    // 用户取消
  }
}

// 文件大小限制：50MB
const MAX_FILE_SIZE = 50 * 1024 * 1024

// 处理文件选择
async function handleFileChange(file: any) {
  // 验证文件大小
  if (file.size > MAX_FILE_SIZE) {
    ElMessage.error(`文件 ${file.name} 超出 50MB 限制`)
    return
  }

  // 验证文件格式
  const ext = file.name.split('.').pop()?.toLowerCase()
  if (!['silk', 'wav', 'mp3', 'amr', 'm4a'].includes(ext)) {
    ElMessage.error(`不支持的文件格式: ${ext}`)
    return
  }

  // 上传文件
  const success = await store.uploadFiles([file.raw])
  if (success) {
    ElMessage.success('文件上传成功')
  }
}

// 格式化文件大小
function formatFileSize(bytes: number): string {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(2) + ' MB'
}
</script>

<style scoped>
.upload-area {
  margin-bottom: 20px;
}

.file-list {
  margin-top: 20px;
}

.file-list-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
  padding: 10px;
  background-color: var(--el-fill-color-light);
  border-radius: 4px;
  font-weight: 500;
  flex-wrap: wrap;
}

.header-actions {
  display: flex;
  gap: 8px;
  margin-left: auto;
}

.file-item {
  display: flex;
  align-items: center;
  padding: 12px;
  margin-bottom: 8px;
  background-color: var(--el-bg-color);
  border: 1px solid var(--el-border-color);
  border-radius: 4px;
  transition: box-shadow 0.2s;
  gap: 10px;
}

.file-checkbox {
  flex-shrink: 0;
}

.file-item:hover {
  box-shadow: var(--el-box-shadow-light);
}

.file-info {
  display: flex;
  align-items: center;
  flex: 1;
}

.file-icon {
  font-size: 32px;
  margin-right: 12px;
  color: var(--el-color-primary);
}

.file-details {
  flex: 1;
}

.file-name {
  font-weight: 500;
  margin-bottom: 4px;
}

.file-meta {
  display: flex;
  gap: 8px;
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

@media (max-width: 768px) {
  .file-item {
    flex-wrap: wrap;
    gap: 8px;
  }

  .file-info {
    flex: 1 1 100%;
  }

  .file-icon {
    font-size: 24px;
    margin-right: 8px;
  }

  .file-list-header {
    flex-wrap: wrap;
    gap: 8px;
  }

  .header-actions {
    width: 100%;
    margin-left: 0;
  }
}
</style>
