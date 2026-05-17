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
    chunkSizeWarningLimit: 1000,
    rollupOptions: {
      output: {
        manualChunks: (id) => {
          if (id.includes('node_modules')) {
            if (id.includes('antd') || id.includes('@ant-design')) return 'vendor-antd';
            if (id.includes('echarts') || id.includes('recharts')) return 'vendor-charts';
            if (id.includes('d3')) return 'vendor-d3';
            if (id.includes('leaflet')) return 'vendor-leaflet';
            if (id.includes('react-pivottable') || id.includes('xlsx') || id.includes('jspdf')) return 'vendor-reports';
            if (id.includes('framer-motion')) return 'vendor-motion';
            if (id.includes('i18next')) return 'vendor-i18n';
            if (id.includes('react-router')) return 'vendor-router';
            if (id.includes('react-dom') || id.includes('react/')) return 'vendor-react';
            return 'vendor';
          }
        },
      },
    },
  },
});
