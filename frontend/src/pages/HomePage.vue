<template>
  <div class="home-page">
    <el-container>
      <el-header class="header">
        <h1>🎵 SILK 音频转换</h1>
        <p class="subtitle">支持 SILK、WAV、MP3、AMR、M4A 多格式转换</p>
      </el-header>

      <el-main>
        <!-- 上传区域 -->
        <UploadArea />

        <!-- 转换设置 -->
        <ConvertSettings />

        <!-- 任务列表 -->
        <TaskList />

        <!-- 暂存区 -->
        <StagingPanel />
      </el-main>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import UploadArea from '@/components/UploadArea.vue';
import ConvertSettings from '@/components/ConvertSettings.vue';
import TaskList from '@/components/TaskList.vue';
import StagingPanel from '@/components/StagingPanel.vue';
</script>

<style scoped>
.home-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.header {
  background: rgba(255, 255, 255, 0.1) !important;
  color: white;
  text-align: center;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 30px 20px !important;
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
}

.header h1 {
  margin: 0;
  font-size: 2.5em;
  font-weight: bold;
}

.subtitle {
  margin: 10px 0 0 0;
  font-size: 0.95em;
  opacity: 0.9;
}

:deep(.el-main) {
  background: #f5f7fa;
  padding: 30px 20px;
}
</style>
