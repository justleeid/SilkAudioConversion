<template>
  <n-tag :bordered="false" size="tiny" :type="type">{{ text }}</n-tag>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { NTag } from 'naive-ui'
import { TaskStatus } from '@/types'
import { useAppStore } from '@/stores/app'

const props = defineProps<{ taskId: string }>()
const store = useAppStore()

const type = computed(() => {
  const task = store.tasks.get(props.taskId)
  if (!task) return 'default'
  switch (task.status) {
    case TaskStatus.PENDING: return 'info'
    case TaskStatus.PROCESSING: return 'warning'
    case TaskStatus.COMPLETED: return 'success'
    case TaskStatus.FAILED: return 'error'
    default: return 'default'
  }
})

const text = computed(() => {
  const task = store.tasks.get(props.taskId)
  if (!task) return ''
  switch (task.status) {
    case TaskStatus.PENDING: return '等待'
    case TaskStatus.PROCESSING: return '转换中'
    case TaskStatus.COMPLETED: return '完成'
    case TaskStatus.FAILED: return '失败'
    default: return ''
  }
})
</script>
