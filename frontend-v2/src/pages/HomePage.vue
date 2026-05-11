<template>
  <div class="h-screen flex flex-col overflow-hidden bg-gray-50 dark:bg-[#101014]">
    <!-- Header -->
    <header class="shrink-0 flex items-center justify-between px-6 py-3 bg-white dark:bg-[#1e1e22] border-b border-gray-200 dark:border-gray-800">
      <div class="flex items-center gap-3">
        <h1 class="text-lg font-semibold text-gray-900 dark:text-gray-100">Silk 音频转换器</h1>
        <n-tag size="small" :bordered="false" type="info">v2</n-tag>
      </div>
      <n-button size="small" quaternary @click="$emit('toggleDark')">
        <template #icon>
          <span class="text-lg">{{ isDark ? '🌙' : '☀️' }}</span>
        </template>
      </n-button>
    </header>

    <!-- Three-column body -->
    <div class="flex-1 flex flex-col lg:flex-row min-h-0">
      <!-- Col 1: File input -->
      <div class="flex-[3] min-w-0 overflow-y-auto border-r border-gray-200 dark:border-gray-800">
        <FileInputPanel />
      </div>

      <!-- Col 2: Convert settings -->
      <div class="flex-[2] min-w-0 overflow-y-auto border-r border-gray-200 dark:border-gray-800">
        <ConvertPanel />
      </div>

      <!-- Col 3: Results & staging -->
      <div class="flex-[3] min-w-0 overflow-y-auto">
        <ResultPanel />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { NTag, NButton } from 'naive-ui'
import FileInputPanel from '@/components/FileInputPanel.vue'
import ConvertPanel from '@/components/ConvertPanel.vue'
import ResultPanel from '@/components/ResultPanel.vue'

defineProps<{ isDark: boolean }>()
defineEmits<{ toggleDark: [] }>()
</script>
