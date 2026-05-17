import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: { '@': path.resolve(__dirname, './src') },
  },
  server: {
    port: 3000,
    host: true,
    proxy: { '/api': { target: 'http://backend:8000', changeOrigin: true } },
  },
  build: {
    chunkSizeWarningLimit: 1500,
    // manualChunks olib tashlandi — qo'lda chunklash React peer dependency'lar
    // bilan ishlovchi kutubxonalarning yuklash tartibini buzayotgan edi
    // (createContext / version undefined xatolari). Rollup default chunking
    // import grafini hurmat qiladi va xavfsizroq.
  },
});
