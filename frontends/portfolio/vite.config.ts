import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// 本地开发:把各 demo 的 iframe 路径(带尾斜杠)反代到本地 docker nginx(:8080),
// 与生产 nginx 行为一致。注意用尾斜杠键,避免命中门户 SPA 路由(/nexus 无斜杠)。
const demoProxy = 'http://localhost:8080'

export default defineConfig({
  base: '/',
  plugins: [react()],
  server: {
    port: 5180,
    proxy: {
      '/rag/': demoProxy,
      '/fc/': demoProxy,
      '/nexus/': demoProxy,
      '/doctomd/': demoProxy,
      '/iconforge/': demoProxy,
    },
  },
})
