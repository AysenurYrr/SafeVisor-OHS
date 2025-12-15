import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig(({ mode }) => {
  // force load env vars for given mode
  const env = loadEnv(mode, process.cwd(), '');

  console.log('💡 VITE build mode:', mode);
  console.log('💡 VITE_API_BASE_URL:', env.VITE_API_BASE_URL);

  return {
    plugins: [react()],
    define: {
      'import.meta.env.VITE_API_BASE_URL': JSON.stringify(env.VITE_API_BASE_URL),
    },
  };
});
