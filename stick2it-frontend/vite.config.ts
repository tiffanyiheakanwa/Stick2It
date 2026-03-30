import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "path";
import { VitePWA } from 'vite-plugin-pwa'

export default defineConfig({
  plugins: [react(),
    VitePWA({
      registerType: 'autoUpdate'
    })
  ],
  resolve: {
    alias: {
      'react': path.resolve(__dirname, './node_modules/react'),
      'react-dom': path.resolve(__dirname, './node_modules/react-dom'),
      "@": path.resolve(__dirname, "./src"),
    },
  },
  server: {
    fs: {
      // This prevents Vite from searching for dependencies outside the frontend folder
      allow: ['.']
    }
  }
});
