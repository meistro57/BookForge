/**
 * Returns a clean, base-aware URL for any path using import.meta.env.BASE_URL.
 */
export function getUrl(path: string = ''): string {
  const base = import.meta.env.BASE_URL || '/BookForge/';
  const cleanBase = base.endsWith('/') ? base : base + '/';
  const cleanPath = path.startsWith('/') ? path.slice(1) : path;
  return `${cleanBase}${cleanPath}`;
}
