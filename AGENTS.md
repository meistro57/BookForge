# AGENTS.md

Static multi-book reading site built with Astro 7 (SSG), TypeScript, and plain CSS.
Six books are authored as Markdown and rendered into a calm reader UI. No database,
no server code, no client framework: client behavior is vanilla JS inside `.astro`
components.

## Commands

```bash
npm ci                  # CI install (package-lock.json is authoritative)
npm install             # local dev install
npm run dev             # dev server at http://localhost:4321/BookForge/
npm run build           # static output to dist/
npm run preview         # serve dist/ locally
./scripts/deploy.sh [TARGET_DIR] [BACKUP_DIR]   # builds, backs up, copies dist/
npm run audiobook:list     # chapter inventory + runtime estimate
npm run audiobook:script   # narration scripts to audiobook-build/<book>/script
npm run audiobook:sample   # synthesize a one-chapter sample
npm run audiobook:build    # synthesize + publish a book's audiobook
npm run audiobook:check    # Whisper QA over generated tracks
```

The audiobook scripts need `ffmpeg`, a Chatterbox venv, and (for QA)
`faster-whisper`. The npm scripts call `python3`, so activate that venv first or
run the scripts with its interpreter. See `scripts/audiobook/README.md`.

There is **no** lint, typecheck, or unit-test script, and no test runner configured.
The only automated gate is `.github/workflows/ci.yml`: `npm ci && npm run build`.
`npm run build` is the way to validate changes: it transpiles TS and enforces the Zod
content schemas, but it does **not** type-check (`@astrojs/check` is not installed).

Node 22 in CI. Deploys to GitHub Pages via `.github/workflows/deploy.yml` on push to
`main`/`master`, and can be rsync'd/copied to Apache (README covers both).

## Source layout and data flow

```
src/content/books/<book-slug>/book.json          # one collection entry per book
src/content/books/<book-slug>/chapters/*.md      # one collection entry per chapter
src/content.config.ts                            # glob loaders + Zod schemas
src/lib/books.ts                                 # list/sort/lookup books
src/lib/chapters.ts                              # chapter ordering, prev/next, part grouping
src/lib/theme.ts                                 # book palette -> CSS, storage namespace
src/lib/utils.ts                                 # getUrl() base-path helper
src/lib/audiobook.ts                             # build-time manifest loader + audio URL resolution
src/layouts/BookLayout.astro                     # shell: head/meta, header, footer, FOUC script
src/pages/index.astro                            # bookshelf (all books, sorted by `order`)
src/pages/books/[book]/index.astro               # book landing page + TOC + audiobook
src/pages/books/[book]/chapter/[slug].astro      # chapter reader
src/pages/content-check.astro                    # unlinked diagnostic table of loaded content
src/pages/404.astro
src/components/*.astro                           # header controls, TOC drawer, progress bar, QR,
                                                 # AudiobookSection, ChapterAudioPlayer
src/styles/global.css                            # design tokens, theme overrides, print styles
public/                                          # images, audio, .htaccess, robots.txt, favicon
scripts/audiobook/                               # TTS pipeline, Whisper QA, Turbo server
voices/                                          # reference WAVs (git-ignored) + README
manuscript/                                      # LEGACY raw source, not part of the build
```

Both dynamic routes use `getStaticPaths()` over the content collections, so every
book/chapter becomes a real static page at build time. Rendering flow: collection
entry -> `getBookSlug`/`getChapterSlug` -> URL built with `getUrl()` ->
`BookLayout` -> page component.

## Content model

`book.json` (schema in `src/content.config.ts`):

- Required: `slug`, `title`, `author`.
- Optional: `subtitle`, `description`, `badge`, `cover`, `ogImage`, `theme`, `audiobook`.
- `order` (default 999) sorts the bookshelf.
- `cover`/`ogImage` are paths **relative to `public/`** (e.g. `images/book_cover.jpg`),
  not `/BookForge/images/...`. They are run through `getUrl()` at render time.
- `theme.palette` (`bg`, `panel`, `textPrimary`, `textSecondary`, `accent`, `border`) and
  `theme.font` (`serif`, `sans`) generate a scoped `html[data-book-theme] {...}` block
  via `bookThemeStyle()`; the reader's transient theme (`data-theme`) overrides it.
- `theme.mood` is free-form metadata, not used for rendering.
- `audiobook.narrator` is the display name and the default narrator for the TTS
  pipeline. `audiobook.voice` (server voice name) and `audiobook.refAudio`
  (repo-relative reference WAV) are pipeline defaults, needed when the narrator
  name does not match the voice file (`Mark Hubrich` uses `voice: "meistro"`).

Chapter frontmatter (fields used across the 134 existing chapters; only `title` and
`order` are required):

```yaml
---
title: "..."            # required, used everywhere (cards, nav, header)
order: 1                # required, the ONLY thing that controls reading order
slug: "the-kid-in-the-hallway"   # effectively required, see gotchas
chapterNumber: 1        # optional/nullable, display only ("Chapter 1" badge)
partNumber: 1           # optional/nullable, drives TOC/landing grouping
partTitle: "THE WOUND"  # optional/nullable, part heading text
description: "..."      # optional, shown as subtitle on cards and chapter header
isFrontMatter: false    # default false; cards show "FM" instead of "Ch. NN",
                        # and its part bucket falls back to "Front Matter"
audioFile: "..."        # optional; site-relative override (e.g. audio/<book>/chapters/x.mp3)
audioDuration: "12:45"  # optional; display only
narrator: "Eli C. Tric" # optional; per-chapter narrator override
---
```

## Adding a book or chapter

1. Create `src/content/books/<new-slug>/book.json` with `slug`, `title`, `author`,
   `order`, `cover` and (optionally) `theme`.
2. Add `src/content/books/<new-slug>/chapters/*.md` with the frontmatter above.
   `order` must be unique within the book; existing books use a contiguous 0..N
   sequence with front matter first.
3. Put cover art in `public/images/` and reference it as `images/<file>`.
4. Run `npm run build`. Visit `/content-check/` in `npm run dev` to verify ordering,
   grouping, and previous/next links without reading the source.

No registration step exists anywhere: the glob loaders pick up new folders
automatically, and the bookshelf, routes, and TOC derive everything from the collections.

## Gotchas

- **`manuscript/` is dead weight.** It holds the original single-book markdown and is
  never read by Astro. Editing it changes nothing on the site. The live text is
  `src/content/books/youre-not-broken-youre-broadband/chapters/`.
- **`src/content/chapters/` is also unused** (only a `.gitkeep`). It is a leftover from
  the single-book layout. Real chapters live under each book folder.
- **Chapter `slug` is effectively mandatory.** The glob loader's `generateId` builds the
  id as `<book>/chapters/<filename>.md`, so a chapter without a `slug` frontmatter value
  would produce a URL containing `.md`. `getChapterSlug()` falls back to that id.
- **The book folder name must equal `book.json`'s `slug`.** Routes use `book.data.slug`
  while chapter lookup derives the book from the folder path in
  `getBookSlugFromChapter()`. A mismatch makes `getAllChapters()` return an empty list:
  the book page builds with no chapters and no chapter routes.
- **`order` drives everything.** `chapterNumber` is cosmetic; if `order` is wrong the
  TOC, prev/next, and "Start Reading" target are wrong even though numbers look right.
- **Part grouping collapses ungrouped chapters.** Any chapter with `partNumber` null or
  absent goes into a single bucket keyed `frontmatter` (title = `partTitle` or
  "Front Matter" or "General"). Two ungrouped chapters in different places still land in
  the same group.
- **Part names are hardcoded to five.** `formatPartHeader()` in
  `src/pages/books/[book]/index.astro` and `src/components/TocSlideout.astro` maps
  1..5 to ONE..FIVE and falls back to the raw number. That helper is duplicated in both
  files, edit both if you change it.
- **Every internal URL must go through `getUrl()`** (`src/lib/utils.ts`). The site is
  served from `base: '/BookForge'` with `trailingSlash: 'always'`, so a hardcoded
  `/books/...` href or `/images/...` src points outside the app and 404s. `getUrl()`
  passes absolute `http(s)://` URLs through untouched.
- **Canonical/OG/QR URLs hardcode the origin.** `https://meistro57.github.io` appears in
  `src/layouts/BookLayout.astro` and `src/components/QrCodeModal.astro`. Moving the site
  requires changing both (plus `site` in `astro.config.mjs`).
- **Chapter text often starts with its own `#` heading.** The page already renders the
  title from frontmatter, so H1s inside the body are normal here and not a bug.
- **`audioUrl` and `chapters` are the legacy path.** `AudiobookSection` uses them
  only when no manifest exists, and only for files that actually exist on disk.
  `chaptersUrl` is string-concatenated with `encodeURIComponent(file)`, so it must
  end with `/` (or be an absolute external URL). The manifest path has no such
  requirement.
- **`chaptersUrl` may be base-prefixed.** The broadband book stores
  `/BookForge/audio/`; `audiobookUrl()` and `audioAssetExists()` strip
  `import.meta.env.BASE_URL` before resolving, so both `/BookForge/audio/x.mp3`
  and `audio/x.mp3` map to `public/audio/x.mp3`.
- **The audiobook card is gated on `audiobook.enabled`.** `youre-not-broken` and
  `the-meistro-manual` have it on; others are off.
- **`.htaccess` lives in `public/` but is invisible to `dist` file copying assumptions.**
  Astro copies `public/.htaccess` into `dist/`, and `scripts/deploy.sh` re-copies it
  explicitly because `cp -r dist/*` skips dotfiles.
- **README's "Project Structure" section is stale** (it describes the old single-book
  layout). Trust `src/`, not the README tree, when navigating.
- **There is no `tsconfig.json`**, even though the README advertises "TypeScript Strict".
  Don't assume strict compiler options are enforced; only Astro's content schemas and
  the build itself are real gates.

## Styling and theming

- All colors, fonts, and reader metrics are CSS custom properties defined in
  `src/styles/global.css` (`--bg-color`, `--panel-bg`, `--text-primary`,
  `--text-secondary`, `--accent-color`, `--accent-hover`, `--border-color`,
  `--font-serif`, `--font-sans`, `--reader-font-size`, `--reader-line-height`,
  `--reader-max-width`, `--reader-font-family`). Components use these tokens instead of
  literal colors, which is what makes per-book palettes work.
- Reader preferences are applied as attributes on `<html>`: `data-theme` (light, warm,
  dark, slate, honey-bee), `data-font-size` (smaller, default, larger, xlarge),
  `data-line-spacing` (compact, comfortable, spacious), `data-reading-width` (narrow,
  standard, wide), `data-font-family` (serif, sans). Add new values in both the
  `ReaderControls.astro` buttons and the matching `html[data-*="..."]` rule in
  `global.css`.
- A book's `data-book-theme` palette is the default layer; the reader's `data-theme`
  overrides it.
- Styles are scoped per component (`<style>` in `.astro`). To style markdown output use
  `:global(...)` selectors inside `.prose-content`, as the chapter route does.
- Component styles are dense one-liners; match that style rather than reformatting.

## Client-side state

All state lives in `localStorage` under the namespace `bookforge:<bookSlug>:` where
`bookSlug` is the `data-book-slug` attribute on `<html>` (set by `BookLayout`).

| Key | Written by | Meaning |
| --- | --- | --- |
| `prefs` | `ReaderControls` | JSON of display preferences |
| `current_chapter` | `ReadingProgressBar` | last chapter slug opened |
| `current_chapter_title` / `current_chapter_num` | `ReadingProgressBar` | resume-card labels |
| `completed_chapters` | `ReadingProgressBar` | JSON array of finished slugs |
| `overall_progress` | `ReadingProgressBar` | integer percent |
| `last_read_timestamp` | `ReadingProgressBar` | epoch ms |
| `scroll_<slug>` | `ReadingProgressBar` | saved scroll offset per chapter |
| `audio_speed` | `ChapterAudioPlayer` | playback rate (0.85 to 1.5) |
| `audio_pos_<slug>` | `ChapterAudioPlayer` | per-chapter audio position in seconds |
| `audio_autoadvance` | `ChapterAudioPlayer` | `"1"` or `"0"` |
| `audio_narrator` | `AudiobookSection` | selected narrator slug |

A chapter is marked complete at >=90% scroll or on clicking the next-chapter link.
`ReaderControls` has a reset button that clears progress keys but preserves `prefs`.
The chapter audio player saves its position on `timeupdate`, `pause`, `pagehide`, and
tab hide, and clears it when the track ends.

FOUC prevention: an `is:inline` script at the top of `BookLayout.astro` reads `prefs`
and sets the `<html>` attributes before first paint. Any new reader preference must be
added there too, or it will flash on load.

Cross-component communication uses `window` events, e.g. chapter and landing-page QR
buttons dispatch `bookforge:open-share-modal`, which `QrCodeModal.astro` listens for.
The QR library (`qrcode`) is imported lazily inside the client script.

## Audiobook pipeline

`scripts/audiobook/` synthesizes audio from the chapter Markdown and publishes a
manifest that the reader consumes. It is a separate Python workflow, not part of
`npm run build`.

- `make_audiobook.py` reads `src/content/books/<book>/chapters/*.md` in `order`
  sequence, coalesces short lines into 90-240 char paragraphs, synthesizes through
  Chatterbox (`--engine full`) or the resident Turbo server (`--engine server`),
  normalizes to -19 LUFS, and writes a SHA-1 paragraph cache under
  `audiobook-build/<book>/cache/`.
- `--publish` writes `public/audio/<book>/<narrator-slug>/chapters/<chapter-slug>.mp3`,
  `full-audiobook.mp3`, `full-audiobook.m4b` (chapter markers + cover), and
  `public/audio/<book>/audiobook-manifest.json`. All paths inside the manifest are
  relative to `public/audio/<book>/`.
- Re-running a narrator replaces its manifest entry and deletes stale chapter MP3s.
  Running a new narrator appends an entry; the reader then shows narrator tabs.
- `check_track.py` transcribes generated WAVs with `faster-whisper` (`small.en`,
  int8, CPU) and prints `--redo` commands for mismatched spans.

Build-time wiring: `src/lib/audiobook.ts` reads the manifest with `node:fs` (cached
per book) and `loadAudiobookManifest()` prunes chapters and full-book files whose
assets are missing from `public/`. This is deliberate: the manifest may be
committed while the large audio is deployed out of band, and a CI build must not
render broken players. `AudiobookSection.astro` falls back to the legacy
`book.json` `audiobook.chapters` list when no manifest exists, and
`ChapterAudioPlayer.astro` renders only when `getChapterAudio()` resolves a file.

Audio files are **not committed**: `.gitignore` excludes `*.mp3`, `*.m4b`, and
`voices/*.wav`. Deploy `public/audio/` with `scripts/deploy.sh`/rsync (the existing
full-book recording is ~240 MB, over GitHub's per-file limit).

## Manuscript editing skill

`skills/manuscript-editor/` is a self-contained editorial workflow, not part of the
site build. Read `skills/manuscript-editor/SKILL.md` before touching prose cleanup.
`README.md` there documents the pipeline:

```bash
bash skills/manuscript-editor/pipeline/stage0_inventory.sh raw .
python3 skills/manuscript-editor/pipeline/stage1_mechanical.py --raw raw --out work/
python3 skills/manuscript-editor/pipeline/stage2_contextual.py --raw work/ --out work2/
python3 skills/manuscript-editor/tests/run_tests.py --raw raw --pub work2/
```

The regression script defaults to `--raw raw --pub publication_v5`, and those
directories are **not in the repo**, so the suite cannot run out of the box. The skill's
own rule: passing tests never certifies editorial quality, a separate independent review
is required. Stage 3/4 scripts are flag-only by design.

## Conventions

- TypeScript everywhere, explicit return types on exported helpers in `src/lib`.
- Paths in `src/` are relative imports (`../../lib/...`), no aliases configured.
- Every page/component uses 2-space indentation, single quotes in TS, double quotes in
  YAML frontmatter.
- Documentation and code comments are sparse; the manuscript skill is the one place with
  long-form prose.
- Git history: small, imperative commit subjects (e.g. "Make audiobook chapter list
  collapsible"), no ticket prefixes.
