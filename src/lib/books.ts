import { getCollection, type CollectionEntry } from 'astro:content';

export type BookEntry = CollectionEntry<'books'>;

/**
 * Returns all books sorted by the `order` field (ascending).
 */
export async function listBooks(): Promise<BookEntry[]> {
  const books = await getCollection('books');
  return books.sort((a, b) => a.data.order - b.data.order);
}

/**
 * Returns a single book by slug.
 */
export async function getBookBySlug(slug: string): Promise<BookEntry | undefined> {
  const books = await listBooks();
  return books.find((b) => b.data.slug === slug);
}

/**
 * Returns the canonical slug/id of a book entry.
 */
export function getBookSlug(book: BookEntry): string {
  return book.data.slug || book.slug || book.id;
}
