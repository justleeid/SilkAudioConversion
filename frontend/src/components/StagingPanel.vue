<template>
  <div class="staging-panel">
    <el-card v-if="stagingFiles.length > 0" class="card-border">
      <template #header>
        <div class="card-header">
          <span>💾 暂存区文件</span>
          <el-button link type="primary" @click="refreshStaging">刷新</el-button>
        </div>
      </template>

      <el-table :data="stagingFiles" style="width: 100%">
        <el-table-column prop="output_name" label="文件名" width="250" />
        <el-table-column prop="size" label="大小" width="100" :formatter="formatSize" />
        <el-table-column prop="created_at" label="创建时间" width="180" :formatter="formatTime" />
        <el-table-column prop="expires_at" label="过期时间" width="180" :formatter="formatTime" />
        <el-table-column label="操作" width="150" align="center">
          <template #default="scope">
            <el-button link type="primary" @click="downloadFile(scope.row.file_id)">
              下载
            </el-button>
            <el-button link type="danger" @click="deleteFile(scope.row.file_id)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div style="margin-top: 15px; text-align: right">
        <el-button type="warning" @click="cleanupExpired">清理过期文件</el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import * as convertApi from '@/api/convert';
import { StagingFile } from '@/types';
import { ElMessage } from 'element-plus';

const stagingFiles = ref<StagingFile[]>([]);

function formatSize(row: any): string {
  const size = row.size;
  if (size < 1024) return size + ' B';
  if (size < 1024 * 1024) return (size / 1024).toFixed(2) + ' KB';
  return (size / (1024 * 1024)).toFixed(2) + ' MB';
}

function formatTime(row: any, column: any): string {
  const date = new Date(row[column.property]);
  return date.toLocaleString();
}

async function refreshStaging() {
  try {
    const response = await convertApi.getStaging();
    if (response.code === 0 && response.data) {
      stagingFiles.value = response.data.files;
      ElMessage.success('暂存区已刷新');
    }
  } catch (error) {
    ElMessage.error('刷新暂存区失败');
  }
}

async function deleteFile(fileId: string) {
  try {
    const response = await convertApi.deleteStagingFile(fileId);
    if (response.code === 0) {
      ElMessage.success('文件已删除');
      await refreshStaging();
    }
  } catch (error) {
    ElMessage.error('删除文件失败');
  }
}

async function downloadFile(fileId: string) {
  convertApi.download(fileId);
}

async function cleanupExpired() {
  try {
    const response = await convertApi.cleanupStaging();
    if (response.code === 0) {
      ElMessage.success(`已清理 ${response.data?.cleaned} 个过期文件`);
      await refreshStaging();
    }
  } catch (error) {
    ElMessage.error('清理失败');
  }
}

// 页面加载时获取暂存区文件
onMounted(async () => {
  await refreshStaging();
});
</script>

<style scoped>
.staging-panel {
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
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
