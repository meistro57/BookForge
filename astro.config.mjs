import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

// https://astro.build/config
export default defineConfig({
  output: 'static',
  site: 'https://meistro57.github.io',
  base: '/BookForge',
  trailingSlash: 'always',
  integrations: [sitemap()],
});
