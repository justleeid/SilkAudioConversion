import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig({
  plugins: [vue()],

  resolve: {
    alias: {
      '@': resolve(__dirname, 'src')
    }
  },

  build: {
    rollupOptions: {
      output: {
        manualChunks(id: string) {
          if (id.includes('naive-ui')) return 'naive-ui'
          if (id.includes('vue') || id.includes('pinia')) return 'vue-vendor'
        }
      }
    }
  },

  server: {
    host: '0.0.0.0',
    port: 5174,
    proxy: {
      '/api': {
        // use 127.0.0.1 to avoid localhost DNS/IPv6 resolution issues
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        // increase proxy timeouts (ms)
        proxyTimeout: 60000,
        timeout: 60000
      }
    }
  }
})
