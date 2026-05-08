<template>
  <div class="home-page">
    <!-- Header -->
    <header class="header">
      <div class="header-content">
        <h1 class="title">Silk 音频转换器</h1>
        <p class="subtitle">支持 SILK、WAV、MP3 格式互转</p>
      </div>
    </header>

    <!-- Main Content -->
    <main class="main-content">
      <div class="container">
        <!-- 上传区域 -->
        <section class="upload-section">
          <UploadArea />
        </section>

        <!-- 设置和文件列表 -->
        <section class="settings-section">
          <el-row :gutter="20">
            <el-col :xs="24" :sm="12">
              <ConvertSettings />
            </el-col>
            <el-col :xs="24" :sm="12">
              <!-- 文件列表和任务列表 -->
              <TaskList />
            </el-col>
          </el-row>
        </section>
      </div>
    </main>

    <!-- Footer -->
    <footer class="footer">
      <div class="container">
        <StagingPanel />
      </div>
      <p style="margin-top: 16px;">Silk Audio Converter © 2026</p>
    </footer>
  </div>
</template>

<script setup lang="ts">
import UploadArea from '@/components/UploadArea.vue'
import ConvertSettings from '@/components/ConvertSettings.vue'
import TaskList from '@/components/TaskList.vue'
import StagingPanel from '@/components/StagingPanel.vue'
</script>

<style scoped>
.home-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.header {
  background: linear-gradient(135deg, var(--el-color-primary) 0%, var(--el-color-primary-light-3) 100%);
  color: white;
  padding: 24px 20px;
  text-align: center;
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
}

.title {
  font-size: 36px;
  font-weight: 700;
  margin-bottom: 8px;
}

.subtitle {
  font-size: 16px;
  opacity: 0.9;
}

.main-content {
  flex: 1;
  padding: 40px 20px;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
}

.upload-section {
  margin-bottom: 40px;
}

.settings-section {
  margin-bottom: 40px;
}

.footer {
  background-color: var(--el-fill-color-light);
  padding: 20px;
  text-align: center;
  color: var(--el-text-color-secondary);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .header {
    padding: 20px 16px;
  }

  .title {
    font-size: 24px;
  }

  .subtitle {
    font-size: 13px;
  }

  .main-content {
    padding: 20px 10px;
  }

  .upload-section,
  .settings-section {
    margin-bottom: 20px;
  }
}

@media (max-width: 480px) {
  .header {
    padding: 14px 12px;
  }

  .title {
    font-size: 20px;
    margin-bottom: 4px;
  }

  .subtitle {
    font-size: 12px;
  }
}
</style>
