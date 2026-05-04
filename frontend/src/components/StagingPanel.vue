<template>
  <div class="staging-panel">
    <div v-if="stats" class="staging-bar">
      <span class="staging-title">暂存区</span>
      <span class="staging-info">
        {{ stats.file_count }} 个文件 |
        {{ formatSize(stats.total_size) }} |
        {{ stats.expire_hours }}h 后过期
      </span>
      <el-button size="small" @click="refreshStaging" :loading="loading">
        刷新
      </el-button>
      <el-button size="small" type="warning" @click="handleCleanup">
        清理过期
      </el-button>
      <el-button size="small" type="danger" @click="showList = !showList">
        {{ showList ? '收起' : '展开' }}
      </el-button>
    </div>

    <!-- 暂存文件列表 -->
    <el-collapse-transition>
      <div v-if="showList" class="staging-list">
        <div v-if="files.length === 0" class="empty-hint">
          暂存区暂无文件
        </div>
        <div
          v-for="file in files"
          :key="file.file_id"
          class="staging-item"
        >
          <div class="staging-file-info">
            <span class="staging-file-name">{{ file.output_name || file.original_name }}</span>
            <span class="staging-file-size">{{ formatSize(file.size) }}</span>
            <span class="staging-file-time">
              过期: {{ formatTime(file.expires_at) }}
            </span>
          </div>
          <div class="staging-actions">
            <a
              :href="getDownloadUrl(file.file_id)"
              class="download-link"
              target="_blank"
            >
              <el-button size="small" type="primary">
                下载
              </el-button>
            </a>
            <el-button
              size="small"
              type="danger"
              @click="handleDelete(file.file_id)"
            >
              删除
            </el-button>
          </div>
        </div>
      </div>
    </el-collapse-transition>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import type { StagingFile, StagingStats } from '@/types'
import { getStaging, deleteStagingFile, cleanupStaging, download } from '@/api/convert'
import { ElMessage, ElMessageBox } from 'element-plus'

const files = ref<StagingFile[]>([])
const stats = ref<StagingStats | null>(null)
const showList = ref(false)
const loading = ref(false)

async function refreshStaging() {
  loading.value = true
  try {
    const response = await getStaging()
    if (response.data) {
      files.value = response.data.files
      stats.value = response.data.stats
      if (files.value.length > 0) {
        showList.value = true
      }
    }
  } catch (error) {
    files.value = []
  } finally {
    loading.value = false
  }
}

async function handleDelete(fileId: string) {
  try {
    await ElMessageBox.confirm('确认删除该暂存文件？', '提示', {
      type: 'warning'
    })
    const response = await deleteStagingFile(fileId)
    if (response.code === 0) {
      ElMessage.success('文件已删除')
      await refreshStaging()
    } else {
      ElMessage.error(response.message || '删除失败')
    }
  } catch (error) {
    // 用户取消
  }
}

async function handleCleanup() {
  try {
    const response = await cleanupStaging()
    if (response.code === 0) {
      ElMessage.success(response.message || '清理完成')
      await refreshStaging()
    } else {
      ElMessage.error(response.message || '清理失败')
    }
  } catch (error) {
    ElMessage.error('清理失败')
  }
}

function getDownloadUrl(fileId: string): string {
  return download(fileId)
}

function formatSize(bytes: number): string {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

function formatTime(isoTime: string): string {
  const date = new Date(isoTime)
  return date.toLocaleString()
}

onMounted(() => {
  refreshStaging()
})
</script>

<style scoped>
.staging-panel {
  margin-top: 20px;
}

.staging-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background-color: var(--el-fill-color-light);
  border-radius: 8px;
  flex-wrap: wrap;
}

.staging-title {
  font-weight: 600;
  font-size: 14px;
}

.staging-info {
  font-size: 13px;
  color: var(--el-text-color-secondary);
  flex: 1;
}

.staging-list {
  margin-top: 12px;
}

.empty-hint {
  padding: 20px;
  text-align: center;
  color: var(--el-text-color-secondary);
}

.staging-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  margin-bottom: 8px;
  background-color: var(--el-bg-color);
  border: 1px solid var(--el-border-color);
  border-radius: 8px;
}

.staging-file-info {
  display: flex;
  gap: 16px;
  flex: 1;
  align-items: center;
}

.staging-file-name {
  font-weight: 500;
}

.staging-file-size {
  font-size: 13px;
  color: var(--el-text-color-secondary);
}

.staging-file-time {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.staging-actions {
  display: flex;
  gap: 8px;
}

@media (max-width: 768px) {
  .staging-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }

  .staging-file-info {
    flex-direction: column;
    align-items: flex-start;
    gap: 4px;
  }
}
</style>
