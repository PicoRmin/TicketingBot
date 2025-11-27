import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { resolve } from "path";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": resolve(__dirname, "./src"),
    },
  },
  server: {
    port: 5173,
    host: true, // Allow external connections
    strictPort: false, // Try next available port if 5173 is taken
  },
  build: {
    outDir: "dist",
    sourcemap: true, // Enable source maps for production debugging
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ["react", "react-dom", "react-router-dom"],
          charts: ["recharts"],
          i18n: ["i18next", "react-i18next"],
        },
      },
    },
    chunkSizeWarningLimit: 1000, // Warn if chunk size exceeds 1000kb
  },
  preview: {
    port: 4173,
    host: true,
  },
});

