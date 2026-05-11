<template>
  <el-card class="db-audio-import">
    <template #header>
      <div class="card-header">
        <span>数据库音频导入</span>
        <el-tag size="small" type="info">AI Agent 数据库</el-tag>
      </div>
    </template>

    <!-- 筛选条件 -->
    <div class="filter-area">
      <el-row :gutter="12" align="middle">
        <el-col :xs="24" :sm="8" :md="7">
          <el-form-item label="时间范围" class="compact-item">
            <el-date-picker
              v-model="dateRange"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              value-format="YYYY-MM-DD"
              style="width: 100%"
              size="default"
            />
          </el-form-item>
        </el-col>
        <el-col :xs="24" :sm="8" :md="7">
          <el-form-item label="关键字" class="compact-item">
            <el-input
              v-model="keyword"
              placeholder="搜索音频标题..."
              clearable
              @keyup.enter="handleQuery"
            />
          </el-form-item>
        </el-col>
        <el-col :xs="24" :sm="8" :md="4">
          <el-button type="primary" @click="handleQuery" :loading="querying">
            <el-icon><Search /></el-icon>
            查询
          </el-button>
          <el-button @click="handleClear">清空</el-button>
        </el-col>
      </el-row>
    </div>

    <!-- 查询结果 -->
    <div v-if="searched" class="result-area">
      <div class="result-header">
        <span class="result-count">
          查询结果（可多选，共 <strong>{{ total }}</strong> 条）
        </span>
        <el-button
          type="primary"
          size="small"
          :disabled="checkedIds.length === 0"
          :loading="importing"
          @click="handleImport"
        >
          批量导入 ({{ checkedIds.length }})
        </el-button>
      </div>

      <el-table
        ref="tableRef"
        :data="records"
        style="width: 100%"
        @selection-change="handleSelectionChange"
        v-loading="querying"
        max-height="400"
        size="small"
      >
        <el-table-column type="selection" width="40" />
        <el-table-column prop="title" label="标题" min-width="200" show-overflow-tooltip />
        <el-table-column prop="format" label="格式" width="70" align="center">
          <template #default="{ row }">
            <el-tag size="small">{{ row.format }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="大小" width="90">
          <template #default="{ row }">
            {{ formatFileSize(row.size) }}
          </template>
        </el-table-column>
        <el-table-column label="创建时间" width="160" align="center">
          <template #default="{ row }">
            {{ formatCreatedAt(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="试听" width="70" align="center">
          <template #default="{ row }">
            <el-button
              v-if="isPlayable(row.format)"
              :type="playingId === row.audio_id ? 'warning' : 'primary'"
              size="small"
              circle
              @click="togglePlay(row)"
            >
              <el-icon size="14">
                <VideoPause v-if="playingId === row.audio_id" />
                <VideoPlay v-else />
              </el-icon>
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <audio
        ref="audioRef"
        style="display:none"
        @ended="onPlayEnded"
        @error="onPlayError"
      />

      <div class="pagination-area" v-if="total > per_page">
        <el-pagination
          v-model:current-page="currentPage"
          :page-size="per_page"
          :total="total"
          layout="total, prev, pager, next, jumper"
          @current-change="handlePageChange"
          small
        />
      </div>

      <el-empty v-if="!querying && records.length === 0" description="没有查询到音频记录" />
    </div>

    <!-- 未查询时的提示 -->
    <div v-else class="hint-area">
      <el-empty description="输入筛选条件后点击「查询」搜索数据库中的音频记录" :image-size="80" />
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Search, VideoPlay, VideoPause } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import type { DbAudioRecord } from '@/types'
import { queryDbAudio, importDbAudio } from '@/api/convert'
import { useAppStore } from '@/stores/app'

const store = useAppStore()

// 默认时间范围：最近 30 天
const today = new Date()
const thirtyDaysAgo = new Date(today.getTime() - 30 * 24 * 60 * 60 * 1000)

const dateRange = ref<[string, string]>([
  formatDate(thirtyDaysAgo),
  formatDate(today)
])
const keyword = ref('')
const querying = ref(false)
const importing = ref(false)
const searched = ref(false)

// 查询结果
const records = ref<DbAudioRecord[]>([])
const total = ref(0)
const currentPage = ref(1)
const per_page = 20
const checkedIds = ref<string[]>([])

function formatDate(d: Date): string {
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${y}-${m}-${day}`
}

function handleSelectionChange(selection: DbAudioRecord[]) {
  checkedIds.value = selection.map((r) => r.audio_id)
}

async function handleQuery() {
  if (!dateRange.value || dateRange.value.length !== 2) {
    ElMessage.warning('请选择时间范围')
    return
  }

  querying.value = true
  searched.value = true
  checkedIds.value = []

  try {
    const response = await queryDbAudio({
      date_start: dateRange.value[0],
      date_end: dateRange.value[1],
      keyword: keyword.value || undefined,
      page: currentPage.value,
      per_page
    })

    if (response.data) {
      records.value = response.data.records
      total.value = response.data.total
    }
  } catch {
    records.value = []
    total.value = 0
  } finally {
    querying.value = false
  }
}

function handleClear() {
  dateRange.value = [formatDate(thirtyDaysAgo), formatDate(today)]
  keyword.value = ''
  records.value = []
  total.value = 0
  currentPage.value = 1
  checkedIds.value = []
  searched.value = false
}

async function handlePageChange(page: number) {
  currentPage.value = page
  await handleQuery()
}

async function handleImport() {
  if (checkedIds.value.length === 0) return

  importing.value = true
  try {
    const response = await importDbAudio(checkedIds.value)

    if (response.data) {
      // 导入成功，将文件添加到 store
      response.data.files.forEach((file) => {
        store.files.push(file)
        store.tasks.set(file.task_id, {
          task_id: file.task_id,
          status: 'pending' as any,
          progress: 0
        })
      })

      ElMessage.success(`已导入 ${response.data.imported_count} 个文件到转换队列`)
      checkedIds.value = []
    }
  } catch {
    // 错误已在拦截器中处理
  } finally {
    importing.value = false
  }
}

// 音频试听
const audioRef = ref<HTMLAudioElement | null>(null)
const playingId = ref<string | null>(null)

const PLAYABLE_FORMATS = ['WAV', 'MP3', 'M4A']

function isPlayable(format: string): boolean {
  return PLAYABLE_FORMATS.includes(format?.toUpperCase() || '')
}

function togglePlay(row: DbAudioRecord) {
  const audio = audioRef.value
  if (!audio) return

  if (playingId.value === row.audio_id) {
    audio.pause()
    playingId.value = null
    return
  }

  // 构建预览 URL
  const baseUrl = import.meta.env.DEV ? '' : window.location.origin
  audio.src = `${baseUrl}/api/db-audio/preview/${row.audio_id}`
  audio.play().catch(() => {
    ElMessage.warning('无法播放此音频文件')
  })
  playingId.value = row.audio_id
}

function onPlayEnded() {
  playingId.value = null
}

function onPlayError() {
  ElMessage.warning('音频预览失败，格式可能不受支持')
  playingId.value = null
}

function formatCreatedAt(isoStr: string): string {
  if (!isoStr) return '-'
  try {
    const d = new Date(isoStr)
    const y = d.getFullYear()
    const m = String(d.getMonth() + 1).padStart(2, '0')
    const day = String(d.getDate()).padStart(2, '0')
    const hh = String(d.getHours()).padStart(2, '0')
    const mm = String(d.getMinutes()).padStart(2, '0')
    const ss = String(d.getSeconds()).padStart(2, '0')
    return `${y}-${m}-${day} ${hh}:${mm}:${ss}`
  } catch {
    return isoStr
  }
}

function formatFileSize(bytes: number): string {
  if (!bytes || bytes === 0) return '0 B'
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}
</script>

<style scoped>
.db-audio-import {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 10px;
  font-weight: 600;
}

.filter-area {
  padding-bottom: 16px;
  border-bottom: 1px solid var(--el-border-color-light);
}

.compact-item :deep(.el-form-item) {
  margin-bottom: 0;
}

.compact-item :deep(.el-form-item__label) {
  font-size: 13px;
  padding-right: 8px;
}

.result-area {
  margin-top: 16px;
}

.result-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.result-count {
  font-size: 14px;
  color: var(--el-text-color-regular);
}

.pagination-area {
  display: flex;
  justify-content: center;
  margin-top: 16px;
}

.hint-area {
  padding: 20px 0;
}

@media (max-width: 768px) {
  .result-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }

  .filter-area :deep(.el-col) {
    margin-bottom: 8px;
  }
}
</style>
