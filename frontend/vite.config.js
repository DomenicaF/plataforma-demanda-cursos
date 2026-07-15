import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// El proxy /api evita problemas de CORS en desarrollo redirigiendo al backend.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
