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

const PART_NUMBER_WORDS = [
  'One',
  'Two',
  'Three',
  'Four',
  'Five',
  'Six',
  'Seven',
  'Eight',
  'Nine',
  'Ten',
  'Eleven',
  'Twelve',
  'Thirteen',
  'Fourteen',
  'Fifteen',
  'Sixteen',
  'Seventeen',
  'Eighteen',
  'Nineteen',
  'Twenty',
];

const BACK_MATTER_PATTERN = /^(epilogue|conclusion|afterword|postscript|a note|notes?|acknowledg)/i;

export function isAppendixChapter(chapter: ChapterEntry): boolean {
  return /^appendix\b/i.test(chapter.data.title);
}

export function isBackMatterChapter(chapter: ChapterEntry): boolean {
  const slug = getChapterSlug(chapter);
  return BACK_MATTER_PATTERN.test(chapter.data.title) || BACK_MATTER_PATTERN.test(slug);
}

/** Strip a redundant "PART I:" style prefix from a part title. */
function stripPartPrefix(partTitle: string): string {
  const stripped = partTitle
    .replace(/^part\s+[ivxlcdm\d]+\s*(?:[:\-–—.]\s*)?/i, '')
    .trim();
  return stripped || partTitle.trim();
}

export function formatPartTitle(partNumber: number | null, partTitle: string): string {
  const title = stripPartPrefix(partTitle);
  if (partNumber === null) return title;
  const word = PART_NUMBER_WORDS[partNumber - 1] || partNumber.toString();
  return title ? `Part ${word}: ${title}` : `Part ${word}`;
}

export function formatPartHeader(partNumber: number | null, partTitle: string): string {
  const title = stripPartPrefix(partTitle);
  if (partNumber === null) return title.toUpperCase();
  const word = PART_NUMBER_WORDS[partNumber - 1] || partNumber.toString();
  return title ? `PART ${word.toUpperCase()} — ${title.toUpperCase()}` : `PART ${word.toUpperCase()}`;
}

/** Short badge used in tables of contents, e.g. "Ch. 06", "Appx A", "FM". */
export function getChapterBadge(chapter: ChapterEntry): string {
  if (isAppendixChapter(chapter)) {
    const match = /^appendix\s+([a-z0-9]+)/i.exec(chapter.data.title);
    return match ? `Appx ${match[1].toUpperCase()}` : 'Appx';
  }
  if (chapter.data.isFrontMatter) return 'FM';
  if (chapter.data.chapterNumber !== null && chapter.data.chapterNumber !== undefined) {
    return `Ch. ${chapter.data.chapterNumber.toString().padStart(2, '0')}`;
  }
  return '—';
}

/** Long label used for reading progress and continue-reading links. */
export function getChapterLongLabel(chapter: ChapterEntry): string {
  if (isAppendixChapter(chapter)) {
    const match = /^appendix\s+([a-z0-9]+)/i.exec(chapter.data.title);
    return match ? `Appendix ${match[1].toUpperCase()}` : 'Appendix';
  }
  if (isBackMatterChapter(chapter)) return chapter.data.title;
  if (chapter.data.isFrontMatter) return 'Front Matter';
  if (chapter.data.chapterNumber !== null && chapter.data.chapterNumber !== undefined) {
    return `Chapter ${chapter.data.chapterNumber}`;
  }
  return chapter.data.title;
}

function getChapterGroup(chapter: ChapterEntry): { key: string; title: string; partNumber: number | null } {
  if (chapter.data.partNumber !== null && chapter.data.partNumber !== undefined) {
    return {
      key: 'part-' + chapter.data.partNumber,
      title: chapter.data.partTitle || `Part ${chapter.data.partNumber}`,
      partNumber: chapter.data.partNumber,
    };
  }
  if (isAppendixChapter(chapter)) {
    return { key: 'appendix', title: 'Appendices', partNumber: null };
  }
  if (isBackMatterChapter(chapter)) {
    return { key: 'backmatter', title: 'End Matter', partNumber: null };
  }
  if (chapter.data.isFrontMatter) {
    return { key: 'frontmatter', title: 'Front Matter', partNumber: null };
  }
  return { key: 'chapters', title: 'Chapters', partNumber: null };
}

/**
 * Returns all chapters for a book grouped by part, in reading order.
 */
export async function getChaptersGroupedByPart(bookSlug: string): Promise<PartGroup[]> {
  const chapters = await getAllChapters(bookSlug);
  const groups: Map<string, PartGroup> = new Map();

  for (const chapter of chapters) {
    const { key, title, partNumber } = getChapterGroup(chapter);

    if (!groups.has(key)) {
      groups.set(key, {
        partNumber,
        partTitle: title,
        chapters: [],
      });
    }
    groups.get(key)!.chapters.push(chapter);
  }

  return Array.from(groups.values());
}
