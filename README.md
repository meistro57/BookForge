# BookForge

[![BookForge CI](https://github.com/meistro57/BookForge/actions/workflows/ci.yml/badge.svg)](https://github.com/meistro57/BookForge/actions/workflows/ci.yml)
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)](https://github.com/meistro57/BookForge/actions)
[![Astro Version](https://img.shields.io/badge/Astro-5.0%20Static-ff5e00.svg?logo=astro&logoColor=white)](https://astro.build/)
[![TypeScript](https://img.shields.io/badge/TypeScript-Strict-3178c6.svg?logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Accessibility](https://img.shields.io/badge/WCAG-2.1%20AA-blueviolet.svg)](https://www.w3.org/WAI/standards-guidelines/wcag/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

> **"A calm, distraction-free static web reader engineered to turn a manuscript of raw Markdown into a proper reading room."**

---

<div align="center">
  <img width="809" height="562" alt="BookForge Blueprint Reader Interface" src="https://github.com/user-attachments/assets/3ca02474-6ca5-483a-ac6c-690405bacfc9" />
</div>

---

**Turn a folder of Markdown chapters into a proper reading experience.**

BookForge is a static web reader built for books written and maintained as Markdown files. Its first publication is:

> **You’re Not Broken, You’re Broadband**  
> *Twenty Years of Reverse Engineering an ADHD Brain*  
> by Mark J. Hubrich

Instead of dumping a manuscript onto a long webpage, BookForge creates a calm, responsive reading environment with ordered chapters, navigation, reader controls, and locally saved progress.

The book remains the main event. The website simply gives it a better room.

---

## Project Status

BookForge is currently in early development.

The project is being built in small, testable phases so that every stage produces something usable before additional features are added.

---

## Core Goals

- Render Markdown files as ordered book chapters
- Create a distraction-free reading layout
- Preserve the manuscript’s parts and chapter structure
- Support desktop, tablet, and mobile reading
- Remember reader preferences and progress locally
- Produce a fully static website
- Deploy cleanly to Apache or GitHub Pages
- Avoid databases, accounts, and unnecessary frameworks

---

## Technology

- [Astro](https://astro.build/)
- Markdown content collections
- Plain CSS
- Minimal client-side JavaScript
- Browser `localStorage`
- Static HTML output

BookForge does not require a database or permanently running Node.js server.

---

## Planned Reader Features

- Book landing page
- Table of contents grouped by part
- One clean URL per chapter
- Previous and next chapter navigation
- Responsive reading layout
- Adjustable font size
- Adjustable line spacing
- Adjustable reading width
- Serif and sans-serif type options
- Light, warm-paper, and dark themes
- Reading-progress indicator
- Continue Reading button
- Saved chapter and scroll position
- Completed-chapter markers
- Keyboard navigation
- Slide-out table of contents
- Print-friendly formatting
- Accessible semantic HTML

Reader settings and progress will remain private inside the visitor’s browser.

---

## Manuscript Structure

The first BookForge publication contains front matter followed by twenty chapters:

```text
PART ONE: THE WOUND
01. The Kid in the Hallway
02. The Diagnosis That Explained Everything and Fixed Nothing
03. The Labeling Trap

PART TWO: THE REFRAME
04. You’re Not Broken, You’re Broadband
05. The Neurodivergent Advantage
06. The Wandering Mind
07. Volunteer Souls
08. Famous Minds

PART THREE: THE PRACTICAL
09. Time Blindness
10. Starting
11. Emotional Weather
12. Hyperfocus on Purpose
13. Building Systems That Fit

PART FOUR: THE LIFE
14. Relationships
15. Work, and the Job You Don’t Hate
16. Women and ADHD
17. Raising One, Teaching One
18. Across a Lifetime
19. Identity
20. Finding Your Tribe
```

---

## Project Structure

The planned project layout is:

```text
bookforge/
├── public/
│   ├── images/
│   └── audio/
├── src/
│   ├── components/
│   ├── content/
│   │   └── chapters/
│   ├── layouts/
│   ├── pages/
│   └── styles/
├── astro.config.mjs
├── package.json
└── README.md
```

Markdown manuscript files belong in:

```text
src/content/chapters/
```

Each file will contain YAML frontmatter describing its title, order, chapter number, and book part.

Example:

```markdown
---
title: "The Kid in the Hallway"
chapterNumber: 1
partNumber: 1
partTitle: "The Wound"
order: 1
description: "The hallway desk, the Challenger launch, and finding work that fit."
---

# Chapter 1

Chapter text begins here.
```

---

## Development

### Requirements

- Node.js 20 or newer
- npm

### Install

```bash
git clone https://github.com/meistro57/bookforge.git
cd bookforge
npm install
```

### Start the development server

```bash
npm run dev
```

Astro will display the local development address in the terminal.

### Create a production build

```bash
npm run build
```

The finished static website will be generated in:

```text
dist/
```

### Preview the production build

```bash
npm run preview
```

---

## Build Phases

- [x] **Phase 1: Project Bootstrap** — Astro project setup, global styles, directory structure.
- [x] **Phase 2: Manuscript Content System** — Markdown content collection, metadata schema, chapter ordering.
- [x] **Phase 3: Core Chapter Reader** — Dynamic routes, calm reading column, previous/next chapter navigation.
- [x] **Phase 4: Homepage and Contents** — Hero cover artwork, about section, grouped table of contents.
- [x] **Phase 5: Reader Controls** — Themes (Light, Warm, Dark), font size, line spacing, width controls, FOUC prevention script.
- [x] **Phase 6: Reading Progress** — Progress bar, scroll position memory, completion markers, overall progress tracking.
- [x] **Phase 7: Navigation Polish** — Sticky header, slide-out TOC panel, heading anchors, keyboard shortcuts, back-to-top control.
- [x] **Phase 8: Visual Identity** — Blueprint styling, companion track section for "The Wrong Drawing" with audio player & lyrics.
- [x] **Phase 9: Accessibility and Metadata** — Skip-to-content, WCAG contrast compliance, OpenGraph/Twitter cards, XML sitemaps, robots.txt, custom 404, print stylesheet.
- [x] **Phase 10: Static Deployment** — Apache subdirectory base path configuration (`/broadband/`), `.htaccess` rules, deployment script (`scripts/deploy.sh`), GitHub Actions CI/CD workflow.

---

## Design Principles

### The manuscript comes first

Decorative textures and industrial styling belong around the reading experience, not behind the body text.

### Static by default

A book should not require a database, account system, or application server merely to be read.

### Local and private

Reading progress and display preferences stay inside the reader’s browser.

### Accessible from the beginning

Keyboard navigation, visible focus states, semantic HTML, readable contrast, and responsive layouts are core requirements rather than final-pass decorations.

### Useful before elaborate

A plain reader that works is more valuable than a magnificent interface that remains unfinished.

---

## Deployment

BookForge produces clean static HTML, CSS, assets, and JavaScript.

Target location: `https://quantummindsunited.com/broadband/`

### Apache Subdirectory Deployment Guide

1. **Base Path Configuration**  
   Astro is configured with `base: '/broadband'` in `astro.config.mjs`. All links, scripts, stylesheets, cover art, and audio files are scoped automatically under `/broadband/`.

2. **Deploying `dist/` Contents & `.htaccess`**  
   Copy the contents of `dist/` into the target directory on your Apache web server (e.g. `/var/www/html/broadband/`). Ensure `dist/.htaccess` is copied.

3. **Directory & File Permissions**  
   Set permissions to standard web server defaults:
   ```bash
   find /var/www/html/broadband -type d -exec chmod 755 {} +
   find /var/www/html/broadband -type f -exec chmod 644 {} +
   ```

4. **Apache `.htaccess` Features (`public/.htaccess`)**
   - **HTTPS Redirection**: Forces HTTPS connection.
   - **Cache Control**: Sets long-lived immutable caching for hashed Astro assets (`_astro/*`) and 0-second cache for HTML files to ensure instant updates.
   - **Compression**: Enables `mod_deflate` Gzip/Brotli compression for HTML, CSS, JS, SVG, and JSON.
   - **Fallback & Trailing Slashes**: Direct chapter URLs (e.g., `/broadband/chapter/the-kid-in-the-hallway/`) resolve cleanly without 404 errors on refresh.

5. **Automated Bash Deployment Script**  
   Run the automated deployment script from the project root:
   ```bash
   ./scripts/deploy.sh /var/www/html/broadband
   ```
   This script builds the project, stops on error (`set -e`), backs up existing deployments, syncs `dist/` contents, and applies permissions.

6. **GitHub Actions Deployment (`.github/workflows/deploy.yml`)**  
   An automated GitHub Actions workflow is provided. Pushing to `main` builds the project and uploads the static `dist/` bundle as an artifact for automated deployment.

---

## Future Possibilities

Once the core reader is stable, BookForge may grow to include:

- Full-book search
- Private bookmarks and highlights
- Shareable quote cards
- Narrated chapters
- Audio position memory
- EPUB generation
- PDF generation
- Reusable support for other Markdown books

These features remain outside the initial build so the forge does not become a swamp.

---

## Author

**Mark J. Hubrich**

Steel detailer, fabricator, writer, builder, and chronic investigator of how complicated things fit together.

---

## License

A software license will be selected before the first public release.

The BookForge source code and the manuscript published through it may use separate licenses. The manuscript remains the intellectual property of its author.
