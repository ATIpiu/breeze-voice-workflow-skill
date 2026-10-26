import site from '../data/site.json';
import { posts, url } from '../lib/posts';

export function GET() {
  const base = site.url.replace(/\/$/, '');
  const paths = ['/', '/archive/', '/community/', '/about/', ...posts.map(url)];
  return new Response(`<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">${paths.map(p => `<url><loc>${base + p}</loc></url>`).join('')}</urlset>`, { headers: { 'Content-Type': 'application/xml; charset=utf-8' } });
}
