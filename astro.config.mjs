import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

// Use '/' in local development so http://localhost:4321/ works directly,
// and '/broadband' for production static build or when PUBLIC_BASE_PATH is specified.
const isDev = process.env.NODE_ENV === 'development' || process.argv.includes('dev');
const basePath = process.env.PUBLIC_BASE_PATH || (isDev ? '/' : '/broadband');

// https://astro.build/config
export default defineConfig({
  site: 'https://quantummindsunited.com',
  base: basePath,
  output: 'static',
  integrations: [sitemap()],
});
