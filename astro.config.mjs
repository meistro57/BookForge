import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

// https://astro.build/config
export default defineConfig({
  output: 'static',
  site: 'https://quantummindsunited.com',
  base: '/BookForge',
  trailingSlash: 'always',
  integrations: [sitemap()],
});
