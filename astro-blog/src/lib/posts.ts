import fs from 'node:fs';
import path from 'node:path';
import legacy from '../data/legacy-posts.json';
import authored from '../data/posts.json';

export type Post = {
  slug: string; title: string; subtitle: string; description: string; date: string;
  category: string; tags: string[]; minutes: number; source?: string;
  kind: 'hub' | 'chapter' | 'article'; chapter?: string; body?: string; cover?: string;
};

const root = path.resolve('src/content');
export const posts: Post[] = [
  ...authored.map(p => ({ ...p, kind: 'article' as const })),
  ...(legacy as Post[]),
].sort((a, b) => b.date.localeCompare(a.date));

for (const p of posts) if (!/^[a-z0-9-]+$/.test(p.slug)) throw new Error('Invalid slug: ' + p.slug);

export const url = (p: Post) => `/notes/${p.slug}/`;
export const dot = (d: string) => d.replaceAll('-', '.');

// Breeze pages were frozen from the old Python build: the stored HTML is the whole <main> content.
export function legacyHtml(slug: string) {
  return fs.readFileSync(path.join(root, 'legacy', slug + '.html'), 'utf8');
}
export function bodyHtml(p: Post) {
  return fs.readFileSync(path.join(root, 'posts', p.body!), 'utf8');
}
