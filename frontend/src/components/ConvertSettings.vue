<template>
  <div class="convert-settings">
    <el-card class="card-border">
      <template #header>
        <div class="card-header">
          <span>⚙️ 转换设置</span>
        </div>
      </template>

      <el-form label-width="100px">
        <!-- 目标格式 -->
        <el-form-item label="目标格式">
          <el-select v-model="targetFormat" placeholder="选择目标格式">
            <el-option label="SILK" value="SILK" />
            <el-option label="WAV" value="WAV" />
            <el-option label="MP3" value="MP3" />
          </el-select>
        </el-form-item>

        <!-- 转换按钮 -->
        <el-form-item>
          <el-button
            type="primary"
            @click="handleConvert"
            :disabled="selectedFiles.length === 0"
          >
            开始转换
          </el-button>
          <el-button @click="downloadSelectedFiles">下载结果</el-button>
        </el-form-item>

        <!-- PLIST 合并模式 -->
        <el-divider>PLIST 文件合并</el-divider>

        <el-form-item label="选择模式">
          <el-button-group>
            <el-button
              :type="selectMode === 'all' ? 'primary' : 'default'"
              @click="selectAllForPlist"
            >
              全选
            </el-button>
            <el-button
              :type="selectMode === 'none' ? 'primary' : 'default'"
              @click="clearPlistSelection"
            >
              清空
            </el-button>
          </el-button-group>
        </el-form-item>

        <!-- SILK 文件选择（包含上传和暂存区） -->
        <el-form-item label="选择文件">
          <el-checkbox-group v-model="selectedSilkIds">
            <!-- 上传区的 SILK 文件 -->
            <div class="file-group">
              <div class="group-title">📁 已上传文件</div>
              <el-checkbox
                v-for="file in uploadedSilkFiles"
                :key="file.task_id"
                :label="file.task_id"
              >
                {{ file.filename }}
              </el-checkbox>
            </div>

            <!-- 暂存区的 SILK 文件 -->
            <div v-if="stagingSilkFiles.length > 0" class="file-group">
              <div class="group-title">💾 暂存区文件</div>
              <el-checkbox
                v-for="file in stagingSilkFiles"
                :key="file.file_id"
                :label="file.file_id"
              >
                {{ file.output_name }}
              </el-checkbox>
            </div>
          </el-checkbox-group>
        </el-form-item>

        <!-- 合并按钮 -->
        <el-form-item>
          <el-button
            type="success"
            @click="handleMergePlist"
            :disabled="selectedSilkIds.length < 2"
          >
            合并为 PLIST
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useAppStore } from '@/stores/app';
import * as convertApi from '@/api/convert';
import { ElMessage } from 'element-plus';

const store = useAppStore();
const targetFormat = ref('SILK');
const selectedSilkIds = ref<string[]>([]);
const selectMode = ref<string>('none');
const stagingFiles = ref<any[]>([]);

const selectedFiles = computed(() => {
  return store.files.filter(f => selectedSilkIds.value.includes(f.task_id));
});

const uploadedSilkFiles = computed(() => {
  return store.files.filter(f => f.filename.toLowerCase().endsWith('.silk'));
});

const stagingSilkFiles = computed(() => {
  return stagingFiles.value.filter(f => f.output_name.endsWith('.silk'));
});

// 初始化时加载暂存区文件
onMounted(async () => {
  try {
    const response = await convertApi.getStaging();
    if (response.code === 0 && response.data) {
      stagingFiles.value = response.data.files;
    }
  } catch (error) {
    console.error('加载暂存区失败:', error);
  }
});

async function handleConvert() {
  for (const file of selectedFiles.value) {
    await store.convert(file.task_id, targetFormat.value);
  }
  ElMessage.success('转换任务已创建');
}

function selectAllForPlist() {
  selectedSilkIds.value = [
    ...uploadedSilkFiles.value.map(f => f.task_id),
    ...stagingSilkFiles.value.map(f => f.file_id),
  ];
  selectMode.value = 'all';
}

function clearPlistSelection() {
  selectedSilkIds.value = [];
  selectMode.value = 'none';
}

async function handleMergePlist() {
  try {
    const response = await convertApi.mergePlist(selectedSilkIds.value);
    if (response.code === 0) {
      ElMessage.success('PLIST 合并成功');
      selectedSilkIds.value = [];
      // 刷新暂存区
      const stagingResponse = await convertApi.getStaging();
      if (stagingResponse.code === 0 && stagingResponse.data) {
        stagingFiles.value = stagingResponse.data.files;
      }
    }
  } catch (error) {
    ElMessage.error('PLIST 合并失败');
  }
}

function downloadSelectedFiles() {
  for (const file of selectedFiles.value) {
    store.downloadFile(file.task_id);
  }
}
</script>

<style scoped>
.convert-settings {
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

.file-group {
  margin: 10px 0;
  padding: 10px;
  background: #f5f7fa;
  border-radius: 4px;
}

.group-title {
  font-weight: bold;
  margin-bottom: 8px;
  color: #606266;
}

:deep(.el-checkbox) {
  display: block;
  margin: 5px 0;
}
</style>
