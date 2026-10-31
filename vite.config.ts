import path from 'path';
import {defineConfig} from 'vite';

export default defineConfig(() => {
  return {
    resolve: {
      alias: {
        '@': path.resolve(__dirname, '.'),
      },
    },
    server: {
      port: 3000,
      host: '0.0.0.0',
      // HMR is disabled in AI Studio via DISABLE_HMR env var.
      hmr: process.env.DISABLE_HMR !== 'true',
      watch: process.env.DISABLE_HMR === 'true' ? null : {},
    },
    build: {
      rollupOptions: {
        input: {
          main: path.resolve(__dirname, 'index.html'),
          language: path.resolve(__dirname, 'language.html'),
          home: path.resolve(__dirname, 'home.html'),
          buses: path.resolve(__dirname, 'buses.html'),
          busDetails: path.resolve(__dirname, 'bus-details.html'),
          help: path.resolve(__dirname, 'help.html'),
          profile: path.resolve(__dirname, 'profile.html'),
          settings: path.resolve(__dirname, 'settings.html'),
        },
      },
    },
  };
});
