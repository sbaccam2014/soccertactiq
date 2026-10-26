import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig(({ command }) => ({
  plugins: [react(), tailwindcss()],
  // Production builds are served by Django/whitenoise under /static/
  // (see backend/README build step), so built asset URLs must live
  // under that same prefix. index.html itself is served separately by
  // soccertactiq.views.spa_index at the site root, not through /static/. In dev
  // (`vite`/`vite dev`), keep the default root base so Vite serves its
  // own dev-server assets normally.
  base: command === 'build' ? '/static/' : '/',
  server: {
    // Forward API + allauth headless + Django admin requests to the local
    // Django dev server so the browser only ever talks to one origin
    // (localhost:5173) during `npm run dev`. Session cookies/CSRF therefore
    // behave the same in dev as they will in production, where Django
    // serves both the API and the built frontend from one origin.
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      '/_allauth': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      '/admin': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      '/static': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
}))
