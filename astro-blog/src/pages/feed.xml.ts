import site from '../data/site.json';
import { posts, url } from '../lib/posts';

const x = (s: string) => s.replace(/[<>&'"]/g, c => ({ '<': '&lt;', '>': '&gt;', '&': '&amp;', "'": '&apos;', '"': '&quot;' })[c]!);
export function GET() {
  const base = site.url.replace(/\/$/, '');
  const items = posts.map(p => `<item><title>${x(p.title)}</title><link>${base + url(p)}</link><guid>${base + url(p)}</guid><description>${x(p.description)}</description><pubDate>${new Date(p.date + 'T01:00:00Z').toUTCString()}</pubDate></item>`).join('');
  return new Response(`<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0"><channel><title>${x(site.name)}</title><link>${base}</link><description>${x(site.description)}</description><language>zh-cn</language>${items}</channel></rss>`, { headers: { 'Content-Type': 'application/rss+xml; charset=utf-8' } });
}
