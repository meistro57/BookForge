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
      })
      .optional(),
    order: z.number().default(999),
  }),
});

const chapters = defineCollection({
  loader: glob({ pattern: '**/chapters/*.md', base: './src/content/books' }),
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
