<template>
  <div class="staging-panel">
    <div v-if="stats" class="staging-bar">
      <div class="staging-left">
        <span class="staging-title">暂存区</span>
      </div>

      <div class="staging-center">
        <span class="staging-stats">
          <span>{{ stats.file_count }} 个文件</span>
          <span class="stats-sep">|</span>
          <span>{{ formatSize(stats.total_size) }}</span>
          <span class="stats-sep">|</span>
          <span>{{ stats.expire_hours }}h 后过期</span>
        </span>
      </div>

      <div class="staging-controls">
        <div class="collapse-wrap">
          <el-button size="small" @click="showList = !showList">{{ showList ? '收起' : '展开' }}</el-button>
        </div>

        <div class="action-buttons" v-show="showList">
          <el-button size="small" @click="refreshStaging" :loading="loading"><el-icon><Refresh /></el-icon>刷新</el-button>
          <el-button size="small" type="warning" @click="handleCleanup">清理过期</el-button>
          <el-button v-if="checkedIds.length > 0" size="small" type="danger" @click="handleBatchDelete">删除选中 ({{ checkedIds.length }})</el-button>
        </div>
      </div>
    </div>

    <el-collapse-transition>
      <div v-if="showList" class="staging-list">
        <div v-if="files.length === 0" class="empty-hint">暂存区暂无文件</div>

        <div v-if="files.length > 0" class="selection-bar">
          <el-checkbox :model-value="allChecked" :indeterminate="indeterminate" @change="handleSelectAll">全选</el-checkbox>
        </div>

        <el-checkbox-group v-model="checkedIds">
          <div v-for="file in files" :key="file.file_id" class="staging-item">
            <el-checkbox :value="file.file_id" class="staging-checkbox" />

            <div class="staging-file-info">
              <div v-if="renamingId === file.file_id" class="rename-input-group">
                <el-input v-model="renameValue" size="small" class="rename-input" @keyup.enter="confirmRename(file)" @keyup.escape="cancelRename" />
                <el-button size="small" type="primary" @click="confirmRename(file)">确定</el-button>
                <el-button size="small" @click="cancelRename">取消</el-button>
              </div>
              <template v-else>
                <span class="staging-file-name" @dblclick="startRename(file)" :title="getDisplayName(file)">{{ getDisplayName(file) }}</span>
                <span class="staging-file-size">{{ formatSize(file.size) }}</span>
                <span class="staging-file-time">过期: {{ formatTime(file.expires_at) }}</span>
              </template>
            </div>

            <div class="staging-actions">
              <a :href="getDownloadUrl(file.file_id)" class="download-link" target="_blank"><el-button size="small" type="primary" :icon="Download">下载</el-button></a>
              <el-button size="small" @click="startRename(file)" title="重命名"><el-icon><Edit /></el-icon></el-button>
              <el-button size="small" type="danger" :icon="Delete" @click="handleDelete(file.file_id)">删除</el-button>
            </div>
          </div>
        </el-checkbox-group>
      </div>
    </el-collapse-transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import type { StagingFile, StagingStats } from '@/types'
import { getStaging, deleteStagingFile, batchDeleteStagingFiles, renameStagingFile, cleanupStaging, download } from '@/api/convert'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Refresh, Edit, Delete, Download } from '@element-plus/icons-vue'

const files = ref<StagingFile[]>([])
const stats = ref<StagingStats | null>(null)
const showList = ref(false)
const loading = ref(false)

// 多选状态
const checkedIds = ref<string[]>([])

// 重命名状态
const renamingId = ref<string | null>(null)
const renameValue = ref('')

// 全选计算
const allChecked = computed(() => {
  if (files.value.length === 0) return false
  return checkedIds.value.length === files.value.length
})

const indeterminate = computed(() => {
  return checkedIds.value.length > 0 && checkedIds.value.length < files.value.length
})

function handleSelectAll(val: boolean) {
  if (val) {
    checkedIds.value = files.value.map(f => f.file_id)
  } else {
    checkedIds.value = []
  }
}

async function refreshStaging() {
  loading.value = true
  try {
    const response = await getStaging()
    if (response.data) {
      files.value = response.data.files
      stats.value = response.data.stats
      console.debug('refreshStaging() response files:', response.data.files)
      if (files.value.length > 0) {
        showList.value = true
      }
      // 清除已不存在的选中项
      const validIds = new Set(files.value.map(f => f.file_id))
      checkedIds.value = checkedIds.value.filter((id) => validIds.has(id))
    }
  } catch (error) {
    files.value = []
  } finally {
    loading.value = false
  }
}

async function handleDelete(fileId: string) {
  try {
    await ElMessageBox.confirm('确认删除该暂存文件？', '提示', { type: 'warning' })
    const response = await deleteStagingFile(fileId)
    if (response.code === 0) {
      ElMessage.success('文件已删除')
      checkedIds.value = checkedIds.value.filter((id) => id !== fileId)
      await refreshStaging()
    } else {
      ElMessage.error(response.message || '删除失败')
    }
  } catch (error) {
    // 用户取消
  }
}

async function handleBatchDelete() {
  if (checkedIds.value.length === 0) return
  try {
    await ElMessageBox.confirm(
      `确认删除选中的 ${checkedIds.value.length} 个暂存文件？`,
      '批量删除',
      { type: 'warning' }
    )
    const ids = [...checkedIds.value]
    const response = await batchDeleteStagingFiles(ids)
    if (response.code === 0) {
      ElMessage.success(response.message || '批量删除完成')
      checkedIds.value = []
      await refreshStaging()
    } else {
      ElMessage.error(response.message || '批量删除失败')
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

// 重命名
function startRename(file: StagingFile) {
  renamingId.value = file.file_id
  // 预填当前显示名，去掉扩展名方便编辑
  const name = file.output_name || file.original_name
  const dotIndex = name.lastIndexOf('.')
  renameValue.value = dotIndex > -1 ? name.substring(0, dotIndex) : name
}

function cancelRename() {
  renamingId.value = null
  renameValue.value = ''
}

async function confirmRename(file: StagingFile) {
  if (!renameValue.value.trim()) {
    ElMessage.warning('文件名不能为空')
    return
  }
  try {
    const response = await renameStagingFile(file.file_id, renameValue.value.trim())
    if (response.code === 0) {
      ElMessage.success('重命名成功')
      cancelRename()
      await refreshStaging()
    } else {
      ElMessage.error(response.message || '重命名失败')
    }
  } catch (error) {
    ElMessage.error('重命名失败')
  }
}

function getDownloadUrl(fileId: string): string {
  return download(fileId)
}

function getDisplayName(file: StagingFile): string {
  return file.output_name || file.original_name
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
}

.staging-left {
  display: flex;
  align-items: center;
  min-width: 0;
  flex-shrink: 0;
}

.staging-center {
  flex: 1;
  min-width: 0;
  display: flex;
  justify-content: center;
}

.staging-controls {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 6px;
  flex-shrink: 0;
}

.collapse-wrap {
  display: flex;
  justify-content: flex-end;
}

.action-buttons {
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 8px;
}

.staging-title {
  font-weight: 600;
  font-size: 15px;
  white-space: nowrap;
}

.staging-stats {
  font-size: 13px;
  color: var(--el-text-color-secondary);
  min-width: 0;
  white-space: nowrap;
}

.stats-sep {
  margin: 0 6px;
  opacity: 0.5;
}

.toggle-btn {
  flex-shrink: 0;
}

.staging-bar-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  margin-top: 8px;
  flex-wrap: wrap;
}

.actions-left {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.staging-list {
  margin-top: 12px;
}

.empty-hint {
  padding: 20px;
  text-align: center;
  color: var(--el-text-color-secondary);
}

.selection-bar {
  padding: 8px 12px;
  margin-bottom: 8px;
  background-color: var(--el-fill-color);
  border-radius: 6px;
}

.staging-item {
  display: flex;
  align-items: center;
  padding: 12px;
  margin-bottom: 8px;
  background-color: var(--el-bg-color);
  border: 1px solid var(--el-border-color);
  border-radius: 8px;
  gap: 12px;
  font-size: 14px;
  line-height: 1.5;
}

.staging-checkbox {
  flex-shrink: 0;
}

.staging-file-info {
  display: flex;
  gap: 16px;
  flex: 1;
  align-items: center;
  min-width: 0;
  font-size: 14px;
  line-height: 1.5;
}

.staging-file-name {
  display: inline-block;
  font-weight: 500;
  color: var(--el-text-color-primary);
  cursor: pointer;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 220px;
  padding: 2px 6px;
  border-radius: 4px;
  transition: background-color 0.15s;
}

.staging-file-name:hover {
  background-color: var(--el-fill-color-light);
}

.staging-file-size {
  font-size: 13px;
  color: var(--el-text-color-secondary);
  flex-shrink: 0;
}

.staging-file-time {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  flex-shrink: 0;
}

.rename-input-group {
  display: flex;
  align-items: center;
  gap: 6px;
  flex: 1;
}

.rename-input {
  max-width: 200px;
}

.staging-actions {
  display: flex;
  gap: 8px;
  align-items: center;
  flex-shrink: 0;
  line-height: 1.5;
}

.download-link {
  text-decoration: none;
}

@media (max-width: 768px) {
  .staging-bar {
    padding: 10px 12px;
    flex-wrap: wrap;
    align-items: flex-start;
  }

  .staging-left {
    order: 1;
  }

  .staging-center {
    order: 3;
    width: 100%;
    justify-content: flex-start;
  }

  .staging-controls {
    order: 2;
    width: 100%;
    align-items: flex-end;
  }

  .action-buttons {
    gap: 6px;
  }

  .action-buttons .el-button,
  .collapse-wrap .el-button {
    font-size: 12px;
    padding: 5px 10px;
  }

  .staging-item {
    flex-wrap: wrap;
    padding: 10px;
    gap: 8px;
  }

  .staging-file-info {
    flex-direction: column;
    align-items: flex-start;
    gap: 4px;
    flex: 1;
    min-width: 0;
  }

  .staging-file-name {
    max-width: 100%;
  }

  .staging-actions {
    width: 100%;
    justify-content: flex-end;
    gap: 4px;
  }

  .staging-actions .el-button {
    font-size: 12px;
    padding: 5px 8px;
  }
}
</style>
