import { existsSync, readFileSync } from 'node:fs';
import path from 'node:path';
import { getUrl } from './utils';

/**
 * Manifest written by `scripts/audiobook/make_audiobook.py --publish`.
 * All file paths inside it are relative to `public/audio/<bookSlug>/`.
 */
export interface ManifestChapter {
  slug: string;
  title: string;
  order: number;
  chapterNumber?: number | null;
  partNumber?: number | null;
  partTitle?: string | null;
  isFrontMatter?: boolean;
  audioFile: string;
  duration?: number;
  durationHuman?: string;
}

export interface ManifestNarrator {
  name: string;
  slug: string;
  engine?: string;
  voice?: string;
  generated?: string;
  fullMp3?: string | null;
  m4b?: string | null;
  chapters: ManifestChapter[];
}

export interface AudiobookManifest {
  book: string;
  title: string;
  author: string;
  generated?: string;
  defaultNarrator?: string;
  narrators: ManifestNarrator[];
}

const manifestCache = new Map<string, AudiobookManifest | null>();

function stripBase(file: string): string {
  const clean = file.replace(/^\/+/, '');
  const base = (import.meta.env.BASE_URL || '/BookForge/').replace(/^\/+|\/+$/g, '');
  if (base && (clean === base || clean.startsWith(base + '/'))) {
    return clean.slice(base.length).replace(/^\/+/, '');
  }
  return clean;
}

function audioFileExists(bookSlug: string, file?: string | null): boolean {
  if (!file) return false;
  if (/^https?:\/\//i.test(file)) return true;
  const clean = stripBase(file).replace(/^audio\//, '');
  return existsSync(path.join(process.cwd(), 'public', 'audio', bookSlug, clean));
}

function explicitAudioExists(bookSlug: string, file?: string | null): boolean {
  if (!file) return false;
  if (/^https?:\/\//i.test(file)) return true;
  const clean = stripBase(file);
  const target = clean.startsWith('audio/')
    ? path.join(process.cwd(), 'public', clean)
    : path.join(process.cwd(), 'public', 'audio', bookSlug, clean);
  return existsSync(target);
}

/** Drop tracks whose audio is missing so a manifest committed without its media
 * (for example on a CI build) cannot render broken players. */
function pruneMissingAudio(bookSlug: string, manifest: AudiobookManifest): AudiobookManifest {
  const narrators = (manifest.narrators || [])
    .map((narrator) => ({
      ...narrator,
      fullMp3: audioFileExists(bookSlug, narrator.fullMp3) ? narrator.fullMp3 : null,
      m4b: audioFileExists(bookSlug, narrator.m4b) ? narrator.m4b : null,
      chapters: (narrator.chapters || []).filter((ch) => audioFileExists(bookSlug, ch.audioFile)),
    }))
    .filter((narrator) => narrator.chapters.length > 0);
  return { ...manifest, narrators };
}

/**
 * Read the published audiobook manifest for a book, or null when the book has
 * no generated audio. Build-time only: this touches the filesystem, so do not
 * import it from a client `<script>`.
 */
export function loadAudiobookManifest(bookSlug: string): AudiobookManifest | null {
  if (!bookSlug) return null;
  if (manifestCache.has(bookSlug)) return manifestCache.get(bookSlug) ?? null;

  const file = path.join(process.cwd(), 'public', 'audio', bookSlug, 'audiobook-manifest.json');
  let manifest: AudiobookManifest | null = null;
  if (existsSync(file)) {
    try {
      manifest = JSON.parse(readFileSync(file, 'utf-8')) as AudiobookManifest;
      manifest = pruneMissingAudio(bookSlug, manifest);
      if (manifest.narrators.length === 0) manifest = null;
    } catch (error) {
      console.warn('[audiobook] could not parse manifest', file, error);
      manifest = null;
    }
  }
  manifestCache.set(bookSlug, manifest);
  return manifest;
}

export function resolveNarrator(manifest: AudiobookManifest | null): ManifestNarrator | null {
  if (!manifest || manifest.narrators.length === 0) return null;
  const preferred = manifest.defaultNarrator;
  return manifest.narrators.find((n) => n.name === preferred) || manifest.narrators[0];
}

export interface ChapterAudio {
  audioFile: string;
  duration?: string;
  narrator?: string;
}

/**
 * Resolve the audio for one chapter. An explicit `audioFile` frontmatter value
 * wins; otherwise the default narrator's manifest entry is used.
 */
export function getChapterAudio(
  bookSlug: string,
  chapterSlug: string,
  explicitFile?: string,
  explicitDuration?: string,
  explicitNarrator?: string
): ChapterAudio | null {
  if (explicitFile) {
    if (!explicitAudioExists(bookSlug, explicitFile)) return null;
    return {
      audioFile: explicitFile,
      duration: explicitDuration,
      narrator: explicitNarrator,
    };
  }

  const manifest = loadAudiobookManifest(bookSlug);
  const narrator = resolveNarrator(manifest);
  const track = narrator?.chapters.find((ch) => ch.slug === chapterSlug);
  if (!track) return null;

  return {
    audioFile: track.audioFile,
    duration: track.durationHuman,
    narrator: narrator?.name,
  };
}

/**
 * Turn a manifest-relative path (or a site-relative/external path from
 * frontmatter) into a base-aware URL.
 */
export function audiobookUrl(bookSlug: string, file: string): string {
  if (/^https?:\/\//i.test(file)) return file;
  const clean = stripBase(file);
  if (clean.startsWith('audio/')) return getUrl(clean);
  return getUrl(`audio/${bookSlug}/${clean}`);
}

/** Whether a legacy `audioUrl`/`chaptersUrl` asset exists in `public/`. */
export function audioAssetExists(bookSlug: string, file?: string | null): boolean {
  return explicitAudioExists(bookSlug, file);
}
