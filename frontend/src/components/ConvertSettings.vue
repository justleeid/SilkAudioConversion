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
            <el-option label="PLIST" :value="TargetFormat.PLIST" />
          </el-select>
        </el-form-item>

        <!-- PLIST 专属提示 -->
        <el-alert
          v-if="settings.target_format === TargetFormat.PLIST"
          title="PLIST 模式：将选中的 SILK 文件合并转换为 iOS 预定义语音格式"
          type="info"
          :closable="false"
          show-icon
        />

        <!-- PLIST 输出文件名 -->
        <el-form-item v-if="settings.target_format === TargetFormat.PLIST" label="输出文件名">
          <el-input
            v-model="plistFilename"
            placeholder="请输入合并后的文件名"
            class="plist-filename-input"
          >
            <template #append>.plist</template>
          </el-input>
          <div class="hint">合并后的 PLIST 文件名称，用于暂存区识别</div>
        </el-form-item>

        <!-- PLIST 模式下的 SILK 文件选择 -->
        <div v-if="settings.target_format === TargetFormat.PLIST" class="plist-selection">
          <el-form-item label="选择 SILK 文件">
            <div class="silk-file-list">
              <div v-if="silkFiles.length === 0" class="no-silk-files">
                <el-empty description="没有可用的 SILK 文件，请先上传 SILK 文件" />
              </div>
              <div v-else class="selection-actions">
                <el-checkbox-group v-model="checkedSilkIds">
                  <div v-for="file in silkFiles" :key="file.task_id" class="silk-file-item">
                    <el-checkbox :label="file.task_id">
                      <span class="file-name">{{ file.filename }}</span>
                      <el-tag size="small" :type="file.source === 'staging' ? 'success' : 'info'" class="file-source-tag">
                        {{ file.source === 'staging' ? '暂存区' : '上传区' }}
                      </el-tag>
                      <span class="file-size">({{ formatFileSize(file.size) }})</span>
                    </el-checkbox>
                  </div>
                </el-checkbox-group>
              </div>
              <div v-if="silkFiles.length > 0" class="selection-toolbar">
                <el-button size="small" type="primary" @click="selectAllSilkFiles">
                  全选
                </el-button>
                <el-button size="small" @click="store.clearPlistSelection">
                  取消全选
                </el-button>
                <span class="selection-count">已选中 {{ checkedSilkIds.length }} 个文件</span>
              </div>
            </div>
          </el-form-item>
        </div>

        <!-- 采样率（PLIST 外均可设） -->
        <el-form-item v-if="settings.target_format !== TargetFormat.PLIST" label="采样率">
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
            :disabled="isConvertDisabled"
            @click="handleConvert"
          >
            {{ settings.target_format === TargetFormat.PLIST ? '合并为 PLIST' : '开始转换' }}
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, computed, watch, onMounted } from 'vue'
import { useAppStore } from '@/stores/app'
import type { StagingFile } from '@/types'
import { TargetFormat, TaskStatus } from '@/types'
import { ElMessage } from 'element-plus'
import { mergePlist, getStaging } from '@/api/convert'

const store = useAppStore()

// 默认设置
const settings = reactive({
  target_format: TargetFormat.WAV,
  sample_rate: 24000,
  bit_rate: 24000,
  frame_size: 20,
  wechat_compatible: true
})

// PLIST 输出文件名
const plistFilename = ref('voices.plist')
const stagingSilkFiles = ref<StagingFile[]>([])

type PlistSelectableFile = {
  task_id: string
  filename: string
  size: number
  source: 'upload' | 'staging'
}

// PLIST 模式下选中的 SILK 文件 ID
const checkedSilkIds = computed({
  get: () => Array.from(store.selectedForPlist),
  set: (newVal) => {
    store.clearPlistSelection()
    newVal.forEach((id) => store.togglePlistSelection(id))
  }
})

// 上传区可用的 SILK 文件列表
const uploadSilkFiles = computed<PlistSelectableFile[]>(() => {
  return store.files
    .filter((f) => {
    const task = store.tasks.get(f.task_id)
    return f.format.toLowerCase() === 'silk' && task?.status === TaskStatus.PENDING
  })
    .map((f) => ({
      task_id: f.task_id,
      filename: f.filename,
      size: f.size,
      source: 'upload' as const,
    }))
})

// 暂存区可用的 SILK 文件列表
const stagingSelectableSilkFiles = computed<PlistSelectableFile[]>(() => {
  return stagingSilkFiles.value.map((f) => ({
    task_id: f.file_id,
    filename: f.output_name || f.original_name,
    size: f.size,
    source: 'staging' as const,
  }))
})

// PLIST 可选择的全部 SILK 文件（去重）
const silkFiles = computed<PlistSelectableFile[]>(() => {
  const merged = [...stagingSelectableSilkFiles.value, ...uploadSilkFiles.value]
  const dedup = new Map<string, PlistSelectableFile>()
  for (const f of merged) {
    if (!dedup.has(f.task_id)) {
      dedup.set(f.task_id, f)
    }
  }
  return Array.from(dedup.values())
})

// 检查是否有正在转换的任务
const isConverting = computed(() => {
  return Array.from(store.tasks.values()).some(
    (task) => task.status === TaskStatus.PROCESSING
  )
})

const isConvertDisabled = computed(() => {
  if (isConverting.value) return true
  if (settings.target_format === TargetFormat.PLIST) {
    return silkFiles.value.length === 0
  }
  return !store.hasFiles
})

async function refreshStagingSilkFiles() {
  try {
    const response = await getStaging()
    const files = response.data?.files || []
    stagingSilkFiles.value = files.filter((f) => (f.output_name || '').toLowerCase().endsWith('.silk'))
  } catch {
    stagingSilkFiles.value = []
  }
}

function selectAllSilkFiles() {
  const allIds = silkFiles.value.map((f) => f.task_id)
  checkedSilkIds.value = allIds
}

watch(() => settings.target_format, async (val) => {
  if (val === TargetFormat.PLIST) {
    await refreshStagingSilkFiles()
  }
})

onMounted(async () => {
  await refreshStagingSilkFiles()
})

// 格式化文件大小
function formatFileSize(bytes: number): string {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(2) + ' MB'
}

// 开始转换
async function handleConvert() {
  if (settings.target_format !== TargetFormat.PLIST && !store.hasFiles) {
    ElMessage.warning('请先上传文件')
    return
  }

  // PLIST 模式：合并所有选中的 SILK 文件
  if (settings.target_format === TargetFormat.PLIST) {
    const validIds = new Set(silkFiles.value.map((f) => f.task_id))
    const selectedIds = checkedSilkIds.value.filter((id) => validIds.has(id))

    if (selectedIds.length === 0) {
      ElMessage.warning('请选择要合并的 SILK 文件')
      return
    }

    try {
      store.converting = true
      const response = await mergePlist({
        task_ids: selectedIds,
        output_filename: plistFilename.value
      })

      if (response.code === 0) {
        ElMessage.success('PLIST 合并成功')
        // 添加到任务列表
        if (response.data) {
          store.tasks.set(response.data.file_id, {
            task_id: response.data.file_id,
            status: TaskStatus.COMPLETED,
            progress: 100,
            download_url: response.data.download_url,
            filename: response.data.filename || plistFilename.value
          })
        }
        // 清空选择
        store.clearPlistSelection()
        await refreshStagingSilkFiles()
      } else {
        ElMessage.error(response.message || 'PLIST 合并失败')
      }
    } catch (error) {
      ElMessage.error('PLIST 合并失败')
    } finally {
      store.converting = false
    }
    return
  }

  // 普通转换模式（允许重新转换已完成的文件）
  const files = store.files.filter((f) => {
    const task = store.tasks.get(f.task_id)
    return task && task.status !== TaskStatus.PROCESSING
  })

  if (files.length === 0) {
    ElMessage.warning('没有可转换的文件')
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

.plist-selection {
  margin: 16px 0;
  padding: 16px;
  background-color: var(--el-fill-color-light);
  border-radius: 4px;
}

.silk-file-list {
  margin-top: 12px;
}

.no-silk-files {
  padding: 20px;
  text-align: center;
}

.selection-actions {
  max-height: 300px;
  overflow-y: auto;
}

.silk-file-item {
  margin-bottom: 12px;
  padding: 8px;
  background-color: var(--el-bg-color);
  border-radius: 4px;
  border: 1px solid var(--el-border-color);
}

.file-name {
  font-weight: 500;
}

.file-size {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  margin-left: 8px;
}

.file-source-tag {
  margin-left: 8px;
}

.selection-toolbar {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid var(--el-border-color);
  display: flex;
  align-items: center;
  gap: 8px;
}

.selection-count {
  font-size: 14px;
  color: var(--el-text-color-secondary);
  margin-left: auto;
}

.plist-filename-input {
  max-width: 320px;
}

@media (max-width: 768px) {
  .convert-settings :deep(.el-form-item) {
    flex-direction: column;
    align-items: flex-start;
  }

  .convert-settings :deep(.el-form-item__label) {
    width: auto !important;
    margin-bottom: 4px;
  }

  .convert-settings :deep(.el-select) {
    width: 100% !important;
  }

  .convert-settings :deep(.el-form-item__content) {
    width: 100%;
    margin-left: 0 !important;
  }

  .selection-actions {
    max-height: 200px;
  }

  .silk-file-item {
    padding: 6px;
  }

  .selection-toolbar {
    flex-wrap: wrap;
  }

  .plist-filename-input {
    max-width: 100%;
  }
}
</style>
