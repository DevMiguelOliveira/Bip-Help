import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

const backend = process.env.BIPMANAGER_API_TARGET || 'http://127.0.0.1:8001'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    host: '0.0.0.0',
    port: 5173,
    strictPort: true,
    proxy: {
      '/auth': { target: backend, changeOrigin: true },
      '/franquias': { target: backend, changeOrigin: true },
      '^/tickets/.*': { target: backend, changeOrigin: true, ws: false },
      '/equipe': { target: backend, changeOrigin: true },
      '/usuarios': { target: backend, changeOrigin: true },
      '/uploads': { target: backend, changeOrigin: true },
      '/ws': { target: backend, changeOrigin: true, ws: true },
    },
  },
  preview: { host: '0.0.0.0' },
})
