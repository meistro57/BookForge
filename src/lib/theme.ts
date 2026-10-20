import type { BookEntry } from './books';

/**
 * Compute the book's authored theme as a scoped CSS block string.
 * Scoped to html[data-book-theme] so the reader's transient theme
 * (Light / Warm Paper / Dark) can override the book palette via data-theme.
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

  const decls: string[] = [];
  for (const k of Object.keys(vars)) {
    decls.push(k + ':' + vars[k]);
  }

  // Default layer: applies only when no transient data-theme override is chosen.
  return 'html[data-book-theme] {' + decls.join(';') + ';}';
}

/**
 * Return the book slug used to namespace per-book localStorage keys.
 */
export function bookStorageNamespace(book: BookEntry): string {
  return book.data.slug || book.slug || book.id;
}

