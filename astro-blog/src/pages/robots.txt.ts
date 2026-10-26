import site from '../data/site.json';
export function GET() {
  return new Response(`User-agent: *\nAllow: /\nSitemap: ${site.url.replace(/\/$/, '')}/sitemap.xml\n`);
}
