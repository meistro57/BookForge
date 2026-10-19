import { getCollection, type CollectionEntry } from 'astro:content';
import { getUrl } from './utils';

export { getUrl };
export type ChapterEntry = CollectionEntry<'chapters'>;

/**
 * Derive the book slug a chapter belongs to from its filePath.
 * Chapters are stored under `src/content/books/<bookSlug>/chapters/*.md`, and the
 * glob loader's `id` is only the filename, so we read the parent folder from filePath.
 */
export function getBookSlugFromChapter(chapter: ChapterEntry): string {
  const fp = chapter.filePath || '';
  // filePath looks like: src/content/books/<slug>/chapters/<file>.md
  const parts = fp.split('/');
  const chaptersIdx = parts.indexOf('chapters');
  if (chaptersIdx > 0) {
    return parts[chaptersIdx - 1];
  }
  return chapter.id.split('/')[0];
}

/**
 * Returns all chapters for a given book, sorted in reading order by `order`.
 */
export async function getAllChapters(bookSlug: string): Promise<ChapterEntry[]> {
  const chapters = await getCollection('chapters');
  return chapters
    .filter((ch) => getBookSlugFromChapter(ch) === bookSlug)
    .sort((a, b) => a.data.order - b.data.order);
}

/**
 * Helper to get the canonical slug/id of a chapter entry.
 */
export function getChapterSlug(chapter: ChapterEntry): string {
  return chapter.data.slug || chapter.slug || chapter.id;
}

/**
 * Returns a single chapter by its slug within a book.
 */
export async function getChapterBySlug(bookSlug: string, slug: string): Promise<ChapterEntry | undefined> {
  const chapters = await getAllChapters(bookSlug);
  return chapters.find((ch) => getChapterSlug(ch) === slug);
}

/**
 * Returns previous chapter relative to current slug within a book, or undefined if at start.
 */
export async function getPreviousChapter(bookSlug: string, currentSlug: string): Promise<ChapterEntry | undefined> {
  const chapters = await getAllChapters(bookSlug);
  const index = chapters.findIndex((ch) => getChapterSlug(ch) === currentSlug);
  if (index > 0) {
    return chapters[index - 1];
  }
  return undefined;
}

/**
 * Returns next chapter relative to current slug within a book, or undefined if at end.
 */
export async function getNextChapter(bookSlug: string, currentSlug: string): Promise<ChapterEntry | undefined> {
  const chapters = await getAllChapters(bookSlug);
  const index = chapters.findIndex((ch) => getChapterSlug(ch) === currentSlug);
  if (index !== -1 && index < chapters.length - 1) {
    return chapters[index + 1];
  }
  return undefined;
}

export interface PartGroup {
  partNumber: number | null;
  partTitle: string;
  chapters: ChapterEntry[];
}

/**
 * Returns all chapters for a book grouped by part, in reading order.
 */
export async function getChaptersGroupedByPart(bookSlug: string): Promise<PartGroup[]> {
  const chapters = await getAllChapters(bookSlug);
  const groups: Map<string, PartGroup> = new Map();

  for (const chapter of chapters) {
    const key = chapter.data.partNumber !== undefined && chapter.data.partNumber !== null
      ? 'part-' + chapter.data.partNumber
      : 'frontmatter';
    const title = chapter.data.partTitle || (chapter.data.isFrontMatter ? 'Front Matter' : 'General');
    const num = chapter.data.partNumber ?? null;

    if (!groups.has(key)) {
      groups.set(key, {
        partNumber: num,
        partTitle: title,
        chapters: [],
      });
    }
    groups.get(key)!.chapters.push(chapter);
  }

  return Array.from(groups.values());
}
