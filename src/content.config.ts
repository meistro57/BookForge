import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

const chapters = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/chapters' }),
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
  chapters,
};
