import { getCollection, type CollectionEntry } from 'astro:content';

export type ChapterEntry = CollectionEntry<'chapters'>;

/**
 * Returns a clean, base-aware URL for any path.
 */
export function getUrl(path: string = ''): string {
  const base = import.meta.env.BASE_URL || '/';
  const cleanBase = base.endsWith('/') ? base : base + '/';
  const cleanPath = path.startsWith('/') ? path.slice(1) : path;
  return `${cleanBase}${cleanPath}`;
}

/**
 * Returns all chapters sorted reliably in reading order (by `order` field ascending).
 */
export async function getAllChapters(): Promise<ChapterEntry[]> {
  const chapters = await getCollection('chapters');
  return chapters.sort((a, b) => a.data.order - b.data.order);
}

/**
 * Helper to get the canonical slug/id of a chapter entry.
 */
export function getChapterSlug(chapter: ChapterEntry): string {
  return chapter.data.slug || chapter.slug || chapter.id;
}

/**
 * Returns a single chapter by its slug.
 */
export async function getChapterBySlug(slug: string): Promise<ChapterEntry | undefined> {
  const chapters = await getAllChapters();
  return chapters.find((ch) => getChapterSlug(ch) === slug);
}

/**
 * Returns previous chapter relative to current slug, or undefined if at start.
 */
export async function getPreviousChapter(currentSlug: string): Promise<ChapterEntry | undefined> {
  const chapters = await getAllChapters();
  const index = chapters.findIndex((ch) => getChapterSlug(ch) === currentSlug);
  if (index > 0) {
    return chapters[index - 1];
  }
  return undefined;
}

/**
 * Returns next chapter relative to current slug, or undefined if at end.
 */
export async function getNextChapter(currentSlug: string): Promise<ChapterEntry | undefined> {
  const chapters = await getAllChapters();
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
 * Returns all chapters grouped by part in reading order.
 */
export async function getChaptersGroupedByPart(): Promise<PartGroup[]> {
  const chapters = await getAllChapters();
  const groups: Map<string, PartGroup> = new Map();

  for (const chapter of chapters) {
    const key = chapter.data.partNumber !== undefined && chapter.data.partNumber !== null
      ? `part-${chapter.data.partNumber}`
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
