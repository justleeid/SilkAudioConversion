<template>
  <div class="task-list">
    <el-card v-if="tasks.size > 0" class="card-border">
      <template #header>
        <div class="card-header">
          <span>📋 转换任务列表</span>
        </div>
      </template>

      <el-table :data="taskList" style="width: 100%">
        <el-table-column label="任务 ID" width="250">
          <template #default="scope">
            <code>{{ scope.row.task_id.substring(0, 8) }}</code>
          </template>
        </el-table-column>

        <el-table-column label="状态" width="100" align="center">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.status)">
              {{ scope.row.status }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column label="进度" width="150">
          <template #default="scope">
            <el-progress :percentage="scope.row.progress" />
          </template>
        </el-table-column>

        <el-table-column label="操作" width="200" align="center">
          <template #default="scope">
            <el-button
              v-if="scope.row.status === 'COMPLETED'"
              link
              type="primary"
              @click="downloadTask(scope.row.task_id)"
            >
              下载
            </el-button>
            <el-button
              v-if="scope.row.status === 'FAILED'"
              link
              type="danger"
              @click="showError(scope.row.error_message)"
            >
              查看错误
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-empty v-else description="暂无任务" />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useAppStore } from '@/stores/app';
import { ElMessage } from 'element-plus';
import { TaskStatus } from '@/types';

const store = useAppStore();

const taskList = computed(() => {
  return Array.from(store.tasks.values());
});

function getStatusType(status: string): string {
  const statusMap: Record<string, string> = {
    [TaskStatus.PENDING]: 'info',
    [TaskStatus.PROCESSING]: 'warning',
    [TaskStatus.COMPLETED]: 'success',
    [TaskStatus.FAILED]: 'danger',
  };
  return statusMap[status] || 'info';
}

function downloadTask(taskId: string) {
  store.downloadFile(taskId);
}

function showError(errorMessage?: string) {
  ElMessage.error(errorMessage || '未知错误');
}
</script>

<style scoped>
.task-list {
  margin-bottom: 20px;
}

.card-border {
  border: 1px solid #dcdfe6;
  border-radius: 4px;
}

.card-header {
  font-size: 16px;
  font-weight: bold;
  color: #333;
}

code {
  background: #f0f0f0;
  padding: 2px 6px;
  border-radius: 3px;
  font-family: monospace;
  font-size: 12px;
}
</style>
