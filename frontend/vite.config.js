import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    host: 'localhost',  // Listen on all network interfaces
    port: 5173,       // Specify the port (if different from 5173)
    strictPort: true, // Ensure Vite uses the specified port or fails
  },
});