import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

const books = defineCollection({
  loader: glob({ pattern: '**/book.json', base: './src/content/books' }),
  schema: z.object({
    slug: z.string(),
    title: z.string(),
    author: z.string(),
    subtitle: z.string().optional(),
    description: z.string().optional(),
    badge: z.string().optional(),
    cover: z.string().optional(),
    ogImage: z.string().optional(),
    theme: z
      .object({
        palette: z
          .object({
            bg: z.string().optional(),
            panel: z.string().optional(),
            textPrimary: z.string().optional(),
            textSecondary: z.string().optional(),
            accent: z.string().optional(),
            border: z.string().optional(),
          })
          .optional(),
        font: z
          .object({
            serif: z.string().optional(),
            sans: z.string().optional(),
          })
          .optional(),
        mood: z.string().optional(),
      })
      .optional(),
    audiobook: z
      .object({
        enabled: z.boolean().default(false),
        narrator: z.string().optional(),
        audioUrl: z.string().optional(),
        chaptersUrl: z.string().optional(),
        chapters: z
          .array(
            z.object({
              title: z.string(),
              file: z.string(),
            })
          )
          .optional(),
      })
      .optional(),
    order: z.number().default(999),
  }),
});

const chapters = defineCollection({
  loader: glob({
    pattern: '**/chapters/*.md',
    base: './src/content/books',
    // Chapters live under <book>/chapters/<file>.md and share generic filenames
    // (ch-1.md ... ch-N.md) across multiple books. Derive a globally unique id
    // from the full path so entries don't collide in the content collection, and
    // so getBookSlugFromChapter can recover the owning book slug.
    generateId: ({ entry }) => {
      const parts = entry.split('/');
      const chaptersIdx = parts.indexOf('chapters');
      if (chaptersIdx > 0) {
        return parts.slice(0, chaptersIdx + 1).join('/') + '/' + parts[chaptersIdx + 1];
      }
      return entry;
    },
  }),
  schema: z.object({
    title: z.string(),
    chapterNumber: z.number().optional().nullable(),
    partNumber: z.number().optional().nullable(),
    partTitle: z.string().optional().nullable(),
    description: z.string().optional(),
    order: z.number(),
    isFrontMatter: z.boolean().default(false),
    slug: z.string().optional(),
  }),
});

export const collections = {
  books,
  chapters,
};
