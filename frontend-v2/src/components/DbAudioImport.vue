<template>
  <div class="space-y-3">
    <!-- Filters -->
    <div class="space-y-2">
      <!-- Source selector -->
      <div>
        <div class="text-xs text-gray-400 mb-1">数据源</div>
        <n-select
          v-model:value="source"
          :options="sourceOptions"
          size="small"
          @update:value="onSourceChange"
        />
      </div>
      <!-- Date range row -->
      <div>
        <div class="text-xs text-gray-400 mb-1">时间范围</div>
        <n-date-picker
          v-model:formatted-value="dateRange"
          type="daterange"
          :default-value="defaultRange"
          :show-confirm="false"
          clearable
          class="w-full"
        />
      </div>
      <!-- Keyword + buttons row -->
      <div class="flex gap-2 items-end">
        <n-input
          v-model:value="keyword"
          placeholder="搜索标题..."
          clearable
          class="flex-1"
          @keyup.enter="search"
        />
        <n-button type="primary" :loading="loading" @click="search">查询</n-button>
        <n-button @click="clear">清空</n-button>
      </div>
    </div>

    <!-- Results -->
    <template v-if="searched">
      <div class="flex items-center justify-between">
        <span class="text-xs text-gray-400">共 {{ total }} 条</span>
        <n-button
          size="small"
          type="primary"
          :disabled="checked.length === 0"
          :loading="importing"
          @click="doImport"
        >
          导入 ({{ checked.length }})
        </n-button>
      </div>

      <n-empty v-if="records.length === 0 && !loading" description="无匹配记录" size="small" />

      <div class="space-y-1 max-h-64 overflow-y-auto">
        <div
          v-for="row in records"
          :key="row.audio_id"
          class="flex items-center gap-2 px-3 py-2 rounded-lg bg-white dark:bg-[#1e1e22] border border-gray-100 dark:border-gray-800"
        >
          <n-checkbox
            :checked="checked.includes(row.audio_id)"
            size="small"
            @update:checked="toggleCheck(row.audio_id)"
          />
          <div class="flex-1 min-w-0">
            <template v-if="editingId === row.audio_id">
              <div class="flex items-center gap-1">
                <n-input v-model:value="editTitleValue" size="tiny" class="flex-1"
                  @keyup.enter="confirmEditTitle(row)" @keyup.escape="cancelEditTitle" />
                <n-button size="tiny" type="primary" @click="confirmEditTitle(row)">确定</n-button>
                <n-button size="tiny" @click="cancelEditTitle">取消</n-button>
              </div>
            </template>
            <div v-else class="text-sm text-gray-800 dark:text-gray-200 truncate">{{ row.title }}</div>
            <div class="flex items-center gap-2 text-xs text-gray-400">
              <span>{{ formatSize(row.size) }}</span>
              <n-tag :bordered="false" size="tiny">{{ row.format }}</n-tag>
              <span>{{ formatDate(row.created_at) }}</span>
            </div>
          </div>
          <n-button
            v-if="isPlayable(row.format)"
            size="tiny"
            quaternary
            @click="togglePlay(row)"
          >
            {{ playingId === row.audio_id ? '⏹' : '▶' }}
          </n-button>
          <!-- Admin actions -->
          <div v-if="adminEnabled" class="flex items-center gap-1 shrink-0">
            <n-button size="tiny" quaternary type="warning" @click="startEditTitle(row)">
              ✎
            </n-button>
            <n-button size="tiny" quaternary type="error" @click="doDeleteRecord(row)">
              ✕
            </n-button>
          </div>
        </div>
      </div>

      <audio ref="audioRef" class="hidden" @ended="playingId = null" />

      <n-pagination
        v-if="total > perPage"
        :page="page"
        :page-size="perPage"
        :item-count="total"
        size="small"
        class="justify-center mt-3"
        @update:page="onPage"
      />
    </template>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import {
  NDatePicker, NInput, NButton, NSelect, NCheckbox, NTag, NEmpty, NPagination,
  useMessage, useDialog
} from 'naive-ui'
import type { DbAudioRecord } from '@/types'
import { queryDbAudio, importDbAudio, getAdminStatus, deleteDbAudioRecord, updateDbAudioTitle } from '@/api/convert'
import { useAppStore } from '@/stores/app'

const store = useAppStore()
const message = useMessage()
const dialog = useDialog()

const today = new Date()
const defaultDate = new Date(today.getTime() - 30 * 24 * 3600 * 1000)
const fmt = (d: Date) => d.toISOString().slice(0, 10)

const source = ref('mssql')
const sourceOptions = [
  { label: 'MySQL', value: 'mysql' },
  { label: 'SQL Server', value: 'mssql' },
]
const dateRange = ref<[string, string]>([fmt(defaultDate), fmt(today)])
const defaultRange = ref<[number, number]>([defaultDate.getTime(), today.getTime()])
const keyword = ref('')
const loading = ref(false)
const importing = ref(false)
const searched = ref(false)

const records = ref<DbAudioRecord[]>([])
const total = ref(0)
const page = ref(1)
const perPage = 20
const checked = ref<string[]>([])

const audioRef = ref<HTMLAudioElement | null>(null)
const playingId = ref<string | null>(null)

// Admin mode
const adminEnabled = ref(false)
const editingId = ref<string | null>(null)
const editTitleValue = ref('')

function onSourceChange() {
  searched.value = false
  records.value = []
  total.value = 0
  checked.value = []
  page.value = 1
  store.saveDbAudioQueryCache({
    source: source.value,
    dateRange: [...dateRange.value] as [string, string],
    keyword: keyword.value,
    page: 1,
    perPage,
    searched: false,
    total: 0,
    records: [],
    checked: []
  })
}

function hydrateFromCache() {
  const cache = store.dbAudioQueryCache
  if (!cache) return false

  source.value = cache.source
  dateRange.value = [...cache.dateRange] as [string, string]
  keyword.value = cache.keyword
  page.value = cache.page
  searched.value = cache.searched
  records.value = cache.records as DbAudioRecord[]
  total.value = cache.total
  checked.value = [...cache.checked]
  return true
}

function syncCache() {
  store.saveDbAudioQueryCache({
    source: source.value,
    dateRange: [...dateRange.value] as [string, string],
    keyword: keyword.value,
    page: page.value,
    perPage,
    searched: searched.value,
    total: total.value,
    records: records.value,
    checked: checked.value
  })
}

function toggleCheck(id: string) {
  const i = checked.value.indexOf(id)
  if (i > -1) checked.value.splice(i, 1)
  else checked.value.push(id)
}

async function search() {
  if (!dateRange.value || dateRange.value.length !== 2) {
    message.warning('请选择时间范围')
    return
  }
  loading.value = true
  searched.value = true
  checked.value = []
  try {
    const r = await queryDbAudio({
      source: source.value,
      date_start: dateRange.value[0],
      date_end: dateRange.value[1],
      keyword: keyword.value || undefined,
      page: page.value,
      per_page: perPage
    })
    if (r.data) {
      records.value = r.data.records
      total.value = r.data.total
      syncCache()
    }
  } catch {
    records.value = []
    total.value = 0
    syncCache()
  } finally {
    loading.value = false
  }
}

function clear() {
  dateRange.value = [fmt(defaultDate), fmt(today)]
  keyword.value = ''
  records.value = []
  total.value = 0
  searched.value = false
  checked.value = []
  store.clearDbAudioQueryCache()
}

function onPage(p: number) { page.value = p; search() }

async function doImport() {
  if (!checked.value.length) return
  importing.value = true
  try {
    const r = await importDbAudio(checked.value, source.value)
    if (r.data) {
      r.data.files.forEach((f) => {
        store.files.push(f)
        store.tasks.set(f.task_id, { task_id: f.task_id, status: 'pending' as any, progress: 0 })
      })
      message.success(`已导入 ${r.data.imported_count} 个文件`)
      checked.value = []
      syncCache()
    }
  } catch { /**/ }
  finally { importing.value = false }
}

function isPlayable(fmt: string) { return ['WAV', 'MP3', 'M4A'].includes(fmt?.toUpperCase() ?? '') }

function togglePlay(row: DbAudioRecord) {
  const a = audioRef.value; if (!a) return
  if (playingId.value === row.audio_id) { a.pause(); playingId.value = null; return }
  a.src = `/api/db-audio/preview/${row.audio_id}?source=${source.value}`
  a.play().catch(() => message.warning('无法播放'))
  playingId.value = row.audio_id
}

function formatSize(b: number) {
  if (b < 1024) return b + ' B'
  if (b < 1048576) return (b / 1024).toFixed(1) + ' KB'
  return (b / 1048576).toFixed(1) + ' MB'
}

function formatDate(s: string) {
  if (!s) return ''
  return s.replace('T', ' ').slice(0, 19)
}

// -- Admin actions --

async function checkAdminStatus() {
  try {
    const r = await getAdminStatus()
    adminEnabled.value = r.data?.admin_enabled ?? false
  } catch { adminEnabled.value = false }
}

function startEditTitle(row: DbAudioRecord) {
  editingId.value = row.audio_id
  editTitleValue.value = row.title === '(无标题)' ? '' : row.title
}

function cancelEditTitle() {
  editingId.value = null
  editTitleValue.value = ''
}

async function confirmEditTitle(row: DbAudioRecord) {
  const v = editTitleValue.value.trim()
  if (!v) { message.warning('标题不能为空'); return }
  try {
    const r = await updateDbAudioTitle(row.audio_id, v, source.value)
    if (r.code === 0) {
      message.success('标题已更新')
      cancelEditTitle()
      await search()
    } else {
      message.error(r.message || '修改失败')
    }
  } catch { message.error('修改失败') }
}

async function doDeleteRecord(row: DbAudioRecord) {
  dialog.warning({
    title: '确认删除',
    content: `将删除「${row.title}」的音频记录及关联聊天记录，此操作不可恢复。`,
    positiveText: '删除',
    negativeText: '取消',
    onPositiveClick: async () => {
      try {
        const r = await deleteDbAudioRecord(row.audio_id, source.value)
        if (r.code === 0) {
          message.success('已删除')
          checked.value = checked.value.filter((id) => id !== row.audio_id)
          await search()
          syncCache()
        } else {
          message.error(r.message || '删除失败')
        }
      } catch { message.error('删除失败') }
    }
  })
}

onMounted(() => {
  hydrateFromCache()
  checkAdminStatus()
})
</script>
