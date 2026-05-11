<template>
  <div>
    <n-upload
      multiple
      :show-file-list="false"
      accept=".silk,.wav,.mp3,.amr,.m4a"
      directory-dnd
      @change="handleChange"
    >
      <n-upload-dragger>
        <div class="py-8 text-center">
          <span class="text-3xl">📁</span>
          <p class="mt-3 text-sm text-gray-600 dark:text-gray-400">
            拖拽文件到此处或 <span class="text-blue-500 font-medium">点击上传</span>
          </p>
          <p class="mt-1 text-xs text-gray-400">
            SILK / WAV / MP3 / AMR / M4A，单文件 ≤50MB，最多 50 个
          </p>
        </div>
      </n-upload-dragger>
    </n-upload>
  </div>
</template>

<script setup lang="ts">
import { NUpload, NUploadDragger, useMessage } from 'naive-ui'
import { useAppStore } from '@/stores/app'

const store = useAppStore()
const message = useMessage()

const MAX_SIZE = 50 * 1024 * 1024
const ALLOWED = ['silk', 'wav', 'mp3', 'amr', 'm4a']

async function handleChange(options: { file: any; fileList: any[]; event?: Event }) {
  const file = options.file

  if (file.file.size > MAX_SIZE) {
    message.error(`文件 ${file.name} 超出 50MB 限制`)
    return
  }

  const ext = file.name.split('.').pop()?.toLowerCase()
  if (!ext || !ALLOWED.includes(ext)) {
    message.error(`不支持的文件格式: .${ext}`)
    return
  }

  const ok = await store.uploadFiles([file.file as File])
  if (ok) {
    message.success('上传成功')
  } else {
    message.error('上传失败')
  }
}
</script>
