import { posts, url } from '../lib/posts';

export function GET() {
  return new Response(JSON.stringify(posts.map(p => ({ title: p.title, subtitle: p.subtitle, description: p.description, category: p.category, tags: p.tags, date: p.date, url: url(p) }))), { headers: { 'Content-Type': 'application/json; charset=utf-8' } });
}
