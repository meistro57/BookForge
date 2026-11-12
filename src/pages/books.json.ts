import type { APIRoute } from 'astro';
import { existsSync } from 'node:fs';
import { join } from 'node:path';
import { listBooks, getBookSlug } from '../lib/books';
import { getAllChapters } from '../lib/chapters';

/**
 * Public catalogue feed: /BookForge/books.json
 *
 * Lets other sites (e.g. the Quantum Minds United homepage) show what's on the
 * BookForge shelf without scraping HTML. Built at compile time, so it is always
 * in sync with src/content/books/. Every URL is absolute.
 *
 * Thumbnails: if public/images/thumbs/<slug>.webp exists it is exposed as `thumb`
 * (small, fast). Otherwise consumers fall back to the full-size `cover`.
 */

export const prerender = true;

export const GET: APIRoute = async ({ site }) => {
  const base = (import.meta.env.BASE_URL || '/BookForge/').replace(/\/?$/, '/');
  const origin = (site?.toString() || 'https://meistro57.github.io/').replace(/\/$/, '');
  const abs = (p: string) => (/^https?:\/\//i.test(p) ? p : `${origin}${base}${p.replace(/^\//, '')}`);

  const books = await listBooks();

  const items = await Promise.all(
    books.map(async (book) => {
      const d = book.data;
      const slug = getBookSlug(book);
      const chapters = await getAllChapters(slug);
      const body = chapters.filter((c) => !c.data.isFrontMatter);
      const numbered = body.filter((c) => typeof c.data.chapterNumber === 'number');
      const thumbPath = `images/thumbs/${slug}.webp`;
      const hasThumb = existsSync(join(process.cwd(), 'public', thumbPath));
      const audio = d.audiobook;

      return {
        slug,
        title: d.title,
        subtitle: d.subtitle ?? null,
        author: d.author,
        description: d.description ?? null,
        badge: d.badge ?? null,
        url: abs(`books/${slug}/`),
        cover: d.cover ? abs(d.cover) : null,
        thumb: hasThumb ? abs(thumbPath) : null,
        accent: d.theme?.palette?.accent ?? null,
        mood: d.theme?.mood ?? null,
        chapters: numbered.length || body.length,
        audiobook: audio?.enabled
          ? { narrator: audio.narrator ?? null, tracks: audio.chapters?.length ?? 0 }
          : null,
        order: d.order,
      };
    })
  );

  return new Response(
    JSON.stringify({ name: 'BookForge', home: abs(''), generated: new Date().toISOString(), books: items }, null, 2),
    { headers: { 'Content-Type': 'application/json; charset=utf-8' } }
  );
};
