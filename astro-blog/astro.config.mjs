import { defineConfig } from 'astro/config';
import react from '@astrojs/react';

export default defineConfig({
  site: 'https://atipiu.github.io',
  base: '/breeze-voice-workflow-skill',
  trailingSlash: 'always',
  build: { format: 'directory', assets: '_astro' },
  integrations: [react()],
  // Pages load on hover/tap-start so navigation feels instant.
  prefetch: { prefetchAll: true, defaultStrategy: 'hover' },
});
