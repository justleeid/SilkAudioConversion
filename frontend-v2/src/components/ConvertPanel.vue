<template>
  <div class="p-4 space-y-4">
    <h2 class="text-sm font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">转换设置</h2>

    <n-form label-placement="top" size="medium">
      <!-- Target format -->
      <n-form-item label="目标格式">
        <n-select
          v-model:value="fmt"
          :options="formatOptions"
          placeholder="选择目标格式"
        />
      </n-form-item>

      <!-- PLIST mode switcher -->
      <div v-if="fmt === 'PLIST'" class="space-y-4">
        <n-radio-group v-model:value="store.plistMode" size="medium">
          <n-radio-button value="merge">合并</n-radio-button>
          <n-radio-button value="split">拆分</n-radio-button>
        </n-radio-group>

        <!-- PLIST Merge Mode -->
        <template v-if="store.plistMode === 'merge'">
          <n-alert type="info" title="合并模式：将选中的 SILK 文件合并为 iOS 预定义语音格式" />

          <n-form-item label="输出文件名">
            <n-input v-model:value="plistName" placeholder="voices">
              <template #suffix>.plist</template>
            </n-input>
          </n-form-item>

          <div class="space-y-2">
            <div class="text-xs text-gray-500">选择 SILK 文件（上传区 + 暂存区）</div>
            <n-button size="small" quaternary @click="selectAllSilk()">全选</n-button>
            <div class="space-y-1 max-h-48 overflow-y-auto">
              <div
                v-for="f in silkFiles"
                :key="f.task_id"
                class="flex items-center gap-2 px-2 py-1 rounded bg-white dark:bg-[#1e1e22] border border-gray-100 dark:border-gray-800"
              >
                <n-checkbox
                  :checked="store.selectedForPlist.has(f.task_id)"
                  size="small"
                  @update:checked="store.togglePlistSelection(f.task_id)"
                />
                <span class="text-sm text-gray-800 dark:text-gray-200 truncate flex-1">{{ f.filename }}</span>
                <span class="text-xs text-gray-400">{{ formatSize(f.size) }}</span>
              </div>
            </div>
            <div class="text-xs text-gray-400">已选 {{ store.selectedForPlist.size }} 个</div>
          </div>
        </template>

        <!-- PLIST Split Mode -->
        <template v-if="store.plistMode === 'split'">
          <n-alert type="info" title="拆分模式：将一个成品 PLIST 文件拆分为多个独立文件" />

          <!-- Upload PLIST for split -->
          <n-upload
            :max="1"
            accept=".plist"
            :custom-request="handlePlistUpload"
            :show-file-list="false"
          >
            <n-button block>选择 PLIST 文件</n-button>
          </n-upload>

          <!-- Preview loading -->
          <n-spin v-if="store.splitLoading" size="small" class="w-full flex justify-center py-4" />

          <!-- Preview and split settings -->
          <template v-if="store.splitPreviewData && !store.splitLoading">
            <div class="text-xs text-gray-500">
              文件预览（共 {{ store.splitPreviewData.total_entries }} 个条目）
            </div>

            <!-- Entry list -->
            <div class="space-y-1 max-h-36 overflow-y-auto">
              <div
                v-for="entry in store.splitPreviewData.entries"
                :key="entry.key"
                class="flex items-center gap-2 px-2 py-1 rounded bg-white dark:bg-[#1e1e22] border border-gray-100 dark:border-gray-800"
              >
                <span class="text-sm text-gray-800 dark:text-gray-200 truncate flex-1">{{ entry.key }}</span>
                <span class="text-xs text-gray-400">{{ formatSize(entry.decoded_size) }}</span>
              </div>
            </div>

            <!-- Split settings -->
            <div class="space-y-3 pt-2 border-t border-gray-100 dark:border-gray-800">
              <div class="text-xs text-gray-500 font-medium">拆分设置</div>

              <n-form-item label="拆分数量" label-placement="left" size="small">
                <n-input-number
                  v-model:value="store.splitCount"
                  :min="1"
                  :max="store.splitPreviewData.total_entries"
                  size="small"
                  class="w-24"
                />
                <span v-if="store.splitCount === 1" class="ml-2 text-xs text-amber-500">
                  拆分为 1 个文件等于不拆分
                </span>
              </n-form-item>

              <!-- TODO: 手动分配模式暂未实现，后续版本支持 -->
              <!-- <n-form-item label="拆分方式" label-placement="left" size="small">
                <n-radio-group v-model:value="store.splitMode" size="small">
                  <n-radio value="even">均匀分配</n-radio>
                  <n-radio value="manual">手动分配</n-radio>
                </n-radio-group>
              </n-form-item> -->

              <n-form-item label="文件前缀" label-placement="left" size="small">
                <n-input v-model:value="store.outputPrefix" size="small" placeholder="split" />
              </n-form-item>

              <!-- Split preview -->
              <div v-if="store.splitMode === 'even'" class="space-y-1">
                <div class="text-xs text-gray-500">分配预览</div>
                <div class="max-h-36 overflow-y-auto space-y-1">
                  <div
                    v-for="(group, idx) in splitPreviewGroups"
                    :key="idx"
                    class="text-xs px-2 py-1 rounded bg-gray-50 dark:bg-gray-900"
                  >
                    {{ store.outputPrefix }}_{{ idx + 1 }}.plist（{{ group.count }} 个条目）
                  </div>
                </div>
              </div>
            </div>
          </template>
        </template>
      </div>

      <!-- Sample rate (non-PLIST) -->
      <n-form-item v-if="fmt !== 'PLIST'" label="采样率">
        <n-select
          v-model:value="sampleRate"
          :options="sampleRateOptions"
        />
      </n-form-item>

      <!-- Bit rate (SILK only) -->
      <n-form-item v-if="fmt === 'SILK'" label="比特率">
        <n-select
          v-model:value="bitRate"
          :options="bitRateOptions"
        />
      </n-form-item>

      <!-- Frame size (SILK only) -->
      <n-form-item v-if="fmt === 'SILK'" label="帧大小">
        <n-select
          v-model:value="frameSize"
          :options="frameSizeOptions"
        />
      </n-form-item>

      <!-- WeChat compatible (SILK only) -->
      <n-form-item v-if="fmt === 'SILK'" label="微信兼容">
        <n-switch v-model:value="wechatCompat" />
        <span class="ml-2 text-xs text-gray-400">添加微信 0x02 头部</span>
      </n-form-item>

      <!-- Convert button -->
      <n-button
        type="primary"
        block
        :loading="store.converting || store.splitLoading"
        :disabled="disabled"
        @click="handleConvert"
      >
        {{ buttonText }}
      </n-button>
    </n-form>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import {
  NForm, NFormItem, NSelect, NInput, NSwitch, NButton, NAlert, NCheckbox,
  NRadioGroup, NRadio, NRadioButton, NInputNumber, NUpload, NSpin,
  useMessage
} from 'naive-ui'
import type { UploadCustomRequestOptions } from 'naive-ui'
import { TargetFormat, TaskStatus } from '@/types'
import { useAppStore } from '@/stores/app'
import { mergePlist, getStaging, upload as uploadFiles } from '@/api/convert'
import type { StagingFile } from '@/types'

const store = useAppStore()
const message = useMessage()

const fmt = ref('WAV')
const sampleRate = ref(24000)
const bitRate = ref(24000)
const frameSize = ref(20)
const wechatCompat = ref(true)
const plistName = ref('voices')
const stagingSilk = ref<StagingFile[]>([])

const formatOptions = [
  { label: 'WAV', value: 'WAV' },
  { label: 'MP3', value: 'MP3' },
  { label: 'SILK', value: 'SILK' },
  { label: 'PLIST', value: 'PLIST' },
]

const sampleRateOptions = [
  { label: '8000 Hz', value: 8000 },
  { label: '16000 Hz', value: 16000 },
  { label: '24000 Hz', value: 24000 },
  { label: '44100 Hz', value: 44100 },
]

const bitRateOptions = [
  { label: '12000 bps', value: 12000 },
  { label: '16000 bps', value: 16000 },
  { label: '24000 bps', value: 24000 },
  { label: '32000 bps', value: 32000 },
]

const frameSizeOptions = [
  { label: '20 ms', value: 20 },
  { label: '40 ms', value: 40 },
  { label: '60 ms', value: 60 },
]

type Selectable = { task_id: string; filename: string; size: number }

const uploadSilk = computed<Selectable[]>(() =>
  store.files
    .filter((f) => {
      const t = store.tasks.get(f.task_id)
      return f.format.toLowerCase() === 'silk' && t?.status === TaskStatus.PENDING
    })
    .map((f) => ({ task_id: f.task_id, filename: f.filename, size: f.size }))
)

const stagingSelectable = computed<Selectable[]>(() =>
  stagingSilk.value.map((f) => ({
    task_id: f.file_id,
    filename: f.output_name || f.original_name,
    size: f.size,
  }))
)

const silkFiles = computed<Selectable[]>(() => {
  const m = new Map<string, Selectable>()
  for (const f of [...uploadSilk.value, ...stagingSelectable.value]) {
    if (!m.has(f.task_id)) m.set(f.task_id, f)
  }
  return Array.from(m.values())
})

const disabled = computed(() => {
  if (fmt.value === 'PLIST') {
    if (store.plistMode === 'merge') return store.selectedForPlist.size === 0
    // 拆分模式：需要有预览数据，且拆分数量 >= 2
    return !store.splitPreviewData || store.splitCount < 2
  }
  return !store.hasFiles
})

const buttonText = computed(() => {
  if (fmt.value === 'PLIST') {
    return store.plistMode === 'merge' ? '合并为 PLIST' : '开始拆分'
  }
  return '开始转换'
})

// Split preview groups for even mode
const splitPreviewGroups = computed(() => {
  if (!store.splitPreviewData) return []
  const total = store.splitPreviewData.total_entries
  const count = store.splitCount
  const base = Math.floor(total / count)
  const remainder = total % count
  return Array.from({ length: count }, (_, i) => ({
    count: base + (i < remainder ? 1 : 0)
  }))
})

async function loadStagingSilk() {
  try {
    const r = await getStaging()
    stagingSilk.value = (r.data?.files || []).filter((f) =>
      (f.output_name || '').toLowerCase().endsWith('.silk')
    )
  } catch { stagingSilk.value = [] }
}

function selectAllSilk() {
  const allIds = new Set(silkFiles.value.map((f) => f.task_id))
  const allSelected = allIds.size > 0 && Array.from(allIds).every((id) => store.selectedForPlist.has(id))
  if (allSelected) {
    store.clearPlistSelection()
  } else {
    store.clearPlistSelection()
    silkFiles.value.forEach((f) => store.togglePlistSelection(f.task_id))
  }
}

async function handlePlistUpload({ file }: UploadCustomRequestOptions) {
  if (!file.file) return

  try {
    // 使用底层 API 上传，不污染 store.files 列表
    const { upload } = await import('@/api/convert')
    const result = await upload([file.file])

    if (result.data?.files?.length) {
      const uploadedFile = result.data.files[0]
      // 加载预览
      const success = await store.loadPlistPreview(uploadedFile.task_id)
      if (success) {
        message.success('PLIST 文件已加载')
      } else {
        message.error('加载 PLIST 预览失败')
      }
    } else {
      message.error('上传失败')
    }
  } catch {
    message.error('上传失败')
  }
}

watch(() => fmt.value, (v) => {
  if (v === 'PLIST') {
    loadStagingSilk()
    store.setPlistMode('merge')
  } else {
    store.clearSplitState()
  }
})
watch(() => store.stagingVersion, () => { if (fmt.value === 'PLIST') loadStagingSilk() })

async function handleConvert() {
  if (fmt.value === 'PLIST') {
    if (store.plistMode === 'merge') {
      // Merge mode
      const ids = Array.from(store.selectedForPlist)
      if (!ids.length) { message.warning('请选择 SILK 文件'); return }
      store.converting = true
      try {
        const r = await mergePlist({ task_ids: ids, output_filename: plistName.value + '.plist' })
        if (r.code === 0 && r.data) {
          store.tasks.set(r.data.file_id, {
            task_id: r.data.file_id, status: TaskStatus.COMPLETED, progress: 100,
            download_url: r.data.download_url, filename: r.data.filename
          })
          message.success('PLIST 合并成功')
          store.clearPlistSelection()
        } else {
          message.error(r.message || '合并失败')
        }
      } catch { message.error('合并失败') }
      finally { store.converting = false }
    } else {
      // Split mode
      if (!store.splitPreviewData) { message.warning('请先上传 PLIST 文件'); return }
      store.splitLoading = true
      try {
        const success = await store.executePlistSplit()
        if (success) {
          message.success('PLIST 拆分成功')
          store.triggerStagingRefresh()
        } else {
          message.error('拆分失败')
        }
      } catch { message.error('拆分失败') }
      finally { store.splitLoading = false }
    }
    return
  }

  const targets = store.files.filter((f) => {
    const t = store.tasks.get(f.task_id)
    return t && t.status !== TaskStatus.PROCESSING
  })
  if (!targets.length) { message.warning('没有可转换的文件'); return }

  for (const f of targets) {
    await store.startConversion(f.task_id, {
      target_format: fmt.value as TargetFormat,
      sample_rate: sampleRate.value,
      bit_rate: bitRate.value,
      frame_size: frameSize.value,
      wechat_compatible: wechatCompat.value,
    })
  }
  message.success(`已开始转换 ${targets.length} 个文件`)
}

function formatSize(b: number) {
  if (b < 1024) return b + ' B'
  if (b < 1048576) return (b / 1024).toFixed(1) + ' KB'
  return (b / 1048576).toFixed(1) + ' MB'
}
</script>
