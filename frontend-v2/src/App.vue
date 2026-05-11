<template>
  <n-config-provider :theme="isDark ? darkTheme : null" :locale="zhCN" :date-locale="dateZhCN">
    <n-message-provider>
      <n-dialog-provider>
        <HomePage @toggle-dark="toggleDark" :is-dark="isDark" />
      </n-dialog-provider>
    </n-message-provider>
  </n-config-provider>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { darkTheme, zhCN, dateZhCN } from 'naive-ui'
import { NConfigProvider, NMessageProvider, NDialogProvider } from 'naive-ui'
import HomePage from '@/pages/HomePage.vue'

const isDark = ref(false)

function toggleDark() {
  isDark.value = !isDark.value
  updateHtmlClass()
}

function updateHtmlClass() {
  document.documentElement.classList.toggle('dark', isDark.value)
}

// 跟随系统暗色模式
const mq = window.matchMedia('(prefers-color-scheme: dark)')
function onSystemDarkChange(e: MediaQueryListEvent) {
  isDark.value = e.matches
  updateHtmlClass()
}

onMounted(() => {
  isDark.value = mq.matches
  updateHtmlClass()
  mq.addEventListener('change', onSystemDarkChange)
})

onUnmounted(() => {
  mq.removeEventListener('change', onSystemDarkChange)
})
</script>
