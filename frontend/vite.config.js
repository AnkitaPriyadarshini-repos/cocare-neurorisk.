import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// During development the React app runs on :5173 and forwards /api calls to the FastAPI backend on :8000.
export default defineConfig({
  plugins: [react()],
  server: {
    host: true, // lets you open the app from a phone on the same Wi-Fi
    proxy: { '/api': 'http://127.0.0.1:8000' },
  },
})
