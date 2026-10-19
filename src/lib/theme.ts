import type { BookEntry } from './books';

/**
 * Compute CSS custom properties (inline style string) from a book.json theme block.
 * Falls back to the global :root defaults for any missing value.
 */
export function bookThemeStyle(book: BookEntry): string {
  const palette = book.data.theme?.palette || {};
  const font = book.data.theme?.font || {};

  const vars: Record<string, string> = {};
  if (palette.bg) vars['--bg-color'] = palette.bg;
  if (palette.panel) vars['--panel-bg'] = palette.panel;
  if (palette.textPrimary) vars['--text-primary'] = palette.textPrimary;
  if (palette.textSecondary) vars['--text-secondary'] = palette.textSecondary;
  if (palette.accent) {
    vars['--accent-color'] = palette.accent;
    vars['--accent-hover'] = palette.accent;
  }
  if (palette.border) vars['--border-color'] = palette.border;
  if (font.serif) vars['--font-serif'] = font.serif;
  if (font.sans) vars['--font-sans'] = font.sans;

  const parts: string[] = [];
  for (const k of Object.keys(vars)) {
    parts.push(k + ':' + vars[k]);
  }
  return parts.join(';') + ';';
}

/**
 * Return the book slug used to namespace per-book localStorage keys.
 */
export function bookStorageNamespace(book: BookEntry): string {
  return book.data.slug || book.slug || book.id;
}
