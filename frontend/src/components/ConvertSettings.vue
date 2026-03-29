<template>
  <div class="convert-settings">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>转换设置</span>
        </div>
      </template>

      <el-form label-width="100px">
        <!-- 目标格式 -->
        <el-form-item label="目标格式">
          <el-select v-model="settings.target_format" placeholder="选择目标格式">
            <el-option label="WAV" :value="TargetFormat.WAV" />
            <el-option label="MP3" :value="TargetFormat.MP3" />
            <el-option label="SILK" :value="TargetFormat.SILK" />
          </el-select>
        </el-form-item>

        <!-- 采样率 -->
        <el-form-item label="采样率">
          <el-select v-model="settings.sample_rate" placeholder="选择采样率">
            <el-option label="8000 Hz" :value="8000" />
            <el-option label="16000 Hz" :value="16000" />
            <el-option label="24000 Hz" :value="24000" />
            <el-option label="44100 Hz" :value="44100" />
          </el-select>
        </el-form-item>

        <!-- 比特率（仅 SILK 编码） -->
        <el-form-item v-if="settings.target_format === TargetFormat.SILK" label="比特率">
          <el-select v-model="settings.bit_rate" placeholder="选择比特率">
            <el-option label="12000 bps" :value="12000" />
            <el-option label="16000 bps" :value="16000" />
            <el-option label="24000 bps" :value="24000" />
            <el-option label="32000 bps" :value="32000" />
          </el-select>
        </el-form-item>

        <!-- 帧大小（仅 SILK 编码） -->
        <el-form-item v-if="settings.target_format === TargetFormat.SILK" label="帧大小">
          <el-select v-model="settings.frame_size" placeholder="选择帧大小">
            <el-option label="20 ms" :value="20" />
            <el-option label="40 ms" :value="40" />
            <el-option label="60 ms" :value="60" />
          </el-select>
        </el-form-item>

        <!-- 微信兼容性（仅 SILK 编码） -->
        <el-form-item v-if="settings.target_format === TargetFormat.SILK" label="微信兼容">
          <el-switch v-model="settings.wechat_compatible" />
          <div class="hint">添加微信 SILK 头部（0x02 字节）</div>
        </el-form-item>

        <!-- 操作按钮 -->
        <el-form-item>
          <el-button
            type="primary"
            :loading="store.converting"
            :disabled="!store.hasFiles || isConverting"
            @click="handleConvert"
          >
            开始转换
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { reactive, computed } from 'vue'
import { useAppStore } from '@/stores/app'
import { TargetFormat, TaskStatus } from '@/types'
import { ElMessage } from 'element-plus'

const store = useAppStore()

// 默认设置
const settings = reactive({
  target_format: TargetFormat.WAV,
  sample_rate: 24000,
  bit_rate: 24000,
  frame_size: 20,
  wechat_compatible: true
})

// 检查是否有正在转换的任务
const isConverting = computed(() => {
  return Array.from(store.tasks.values()).some(
    (task) => task.status === TaskStatus.PROCESSING
  )
})

// 开始转换
async function handleConvert() {
  if (!store.hasFiles) {
    ElMessage.warning('请先上传文件')
    return
  }

  // 转换所有已上传的文件
  const files = store.files.filter((f) => {
    const task = store.tasks.get(f.task_id)
    return task?.status === 'pending'
  })

  if (files.length === 0) {
    ElMessage.warning('没有待转换的文件')
    return
  }

  // 批量转换
  for (const file of files) {
    await store.startConversion(file.task_id, {
      target_format: settings.target_format,
      sample_rate: settings.sample_rate,
      bit_rate: settings.bit_rate,
      frame_size: settings.frame_size,
      wechat_compatible: settings.wechat_compatible
    })
  }

  ElMessage.success(`已开始转换 ${files.length} 个文件`)
}
</script>

<style scoped>
.convert-settings {
  margin-bottom: 20px;
}

.card-header {
  font-weight: 600;
}

.hint {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  margin-top: 4px;
}
</style>
