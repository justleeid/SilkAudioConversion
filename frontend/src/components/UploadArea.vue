<template>
  <div class="upload-area">
    <el-card class="card-border">
      <template #header>
        <div class="card-header">
          <span>📤 上传文件</span>
        </div>
      </template>

      <el-upload
        class="upload-component"
        drag
        action=""
        :auto-upload="false"
        multiple
        accept=".silk,.wav,.mp3,.amr,.m4a"
        @change="handleUpload"
      >
        <el-icon class="el-icon--upload"><DocumentCopy /></el-icon>
        <div class="el-upload__text">
          将文件拖到此处，或<em>点击上传</em>
        </div>
        <template #tip>
          <div class="el-upload__tip">
            支持的格式：SILK（.silk）、WAV（.wav）、MP3（.mp3）、AMR（.amr）、M4A（.m4a）
          </div>
        </template>
      </el-upload>

      <div v-if="files.length > 0" class="uploaded-files">
        <el-divider>已上传文件</el-divider>
        <el-tag
          v-for="file in files"
          :key="file.task_id"
          closable
          style="margin: 5px"
          @close="removeFile(file.task_id)"
        >
          {{ file.filename }}
        </el-tag>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { DocumentCopy } from '@element-plus/icons-vue';
import { useAppStore } from '@/stores/app';

const store = useAppStore();
const files = computed(() => store.files);

async function handleUpload(file: any) {
  const uploadFiles = new DataTransfer();
  uploadFiles.items.add(file.raw);

  await store.uploadFiles(uploadFiles.files);
}

function removeFile(taskId: string) {
  const index = store.files.findIndex(f => f.task_id === taskId);
  if (index > -1) {
    store.files.splice(index, 1);
  }
}
</script>

<style scoped>
.upload-area {
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

.upload-component {
  margin: 20px 0;
}

.uploaded-files {
  margin-top: 20px;
}
</style>
