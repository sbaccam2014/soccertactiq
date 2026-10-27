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
    // Listen on all network interfaces (not just localhost) so other
    // devices on the same Wi-Fi (e.g. a phone) can reach the dev
    // server at http://<your-mac's-LAN-IP>:5173 — "localhost" on a
    // phone always means the phone itself, never this machine.
    host: true,
    // Vite's dev server rejects requests whose Host header isn't on
    // this allowlist. Add your Mac's LAN IP here (check with
    // `ipconfig getifaddr en0`) alongside localhost/127.0.0.1 so phone
    // requests aren't blocked. This changes whenever you switch
    // networks/your router reassigns an IP.
    allowedHosts: ['localhost', '127.0.0.1', '192.168.4.37'],
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
