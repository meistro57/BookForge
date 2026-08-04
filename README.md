# BookForge

[![BookForge CI](https://github.com/meistro57/BookForge/actions/workflows/ci.yml/badge.svg)](https://github.com/meistro57/BookForge/actions/workflows/ci.yml)
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)](https://github.com/meistro57/BookForge/actions)
[![Astro Version](https://img.shields.io/badge/Astro-7.1%20Static-ff5e00.svg?logo=astro&logoColor=white)](https://astro.build/)
[![TypeScript](https://img.shields.io/badge/TypeScript-Strict-3178c6.svg?logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Accessibility](https://img.shields.io/badge/WCAG-2.1%20AA-blueviolet.svg)](https://www.w3.org/WAI/standards-guidelines/wcag/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

> **"A calm, distraction-free static web reader engineered to turn a manuscript of raw Markdown into a proper reading room."**

See a live example here:  https://quantummindsunited.com/BookForge/
---

<div align="center">
  <img width="809" height="562" alt="BookForge Reader Interface" src="https://github.com/user-attachments/assets/3ca02474-6ca5-483a-ac6c-690405bacfc9" />
</div>

---

**Turn a folder of Markdown chapters into a proper reading experience.**

BookForge is a static web reader built for books written and maintained as Markdown files. Its premier publication is:

> **You’re Not Broken, You’re Broadband**  
> *Twenty Years of Reverse Engineering an ADHD Brain*  
> by Mark J. Hubrich

Instead of dumping a manuscript onto a long webpage, BookForge creates a calm, responsive reading environment with ordered chapters, navigation, reader controls, audiobook integration, and locally saved progress.

The book remains the main event. The website simply gives it a better room.

---

## Project Status

**All 10 Core Build Phases are Fully Implemented and Deployed.**

BookForge is a fully functional, static web reader featuring full audiobook narration, dynamic typography controls, progress persistence, slide-out table of contents, accessible semantic markup, and automated multi-target static deployment.

---

## Core Features

- **Manuscript Renderer**: Renders Markdown files into structured, clean book chapters with custom YAML frontmatter validation.
- **Full Audiobook Reader**: Integrated full-length audiobook player (`AudiobookSection.astro`) featuring narration by Eli C. Tric.
- **Customizable Display Controls**:
  - **Themes**: Light, Warm Paper, and Dark modes with instant client-side FOUC prevention.
  - **Typography**: Toggle between Serif (`Merriweather`) and Sans-Serif (`Inter`) body typefaces.
  - **Layout**: Adjustable font size, line height spacing, and reading column widths (Narrow, Medium, Wide).
- **Reading Progress & Persistence**:
  - Remembers scroll position per chapter via browser `localStorage`.
  - Chapter completion checkmarks and overall manuscript completion percentage badge.
  - "Resume Reading" shortcut card on the homepage hero section.
- **Interactive Navigation**:
  - Slide-out table of contents drawer accessible anywhere in the reader.
  - Sticky reading header with progress bar and quick display control popouts.
  - Quick reader instructions modal ("How To Use").
  - Previous and Next chapter navigation buttons.
  - Keyboard shortcuts (`?` for help, `N` next, `P` prev, `T` table of contents, `Esc` dismiss).
- **Accessibility & SEO**:
  - Full WCAG 2.1 AA contrast compliance, keyboard focus rings, and skip-to-content links.
  - Automated XML sitemap generation (`@astrojs/sitemap`) and OpenGraph/Twitter card metadata.
  - Custom 404 error layout and print-optimized CSS stylesheet.

---

## Technology Stack

- **Framework**: [Astro 7.1](https://astro.build/) (Static Site Generation)
- **Language**: [TypeScript](https://www.typescriptlang.org/) (Strict Mode)
- **Styling**: Plain CSS3 with custom variables & design system tokens
- **Integrations**: `@astrojs/sitemap`
- **Client Logic**: Vanilla JavaScript (Zero heavy UI dependencies, local state saved in `localStorage`)
- **Deployment**: Apache Subdirectory & GitHub Pages

---

## Manuscript Structure

The manuscript contains front matter followed by twenty chapters divided across four parts:

```text
FRONT MATTER
00. Front Matter

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

```text
BookForge/
├── .github/
│   └── workflows/
│       ├── ci.yml               # Automated CI build checks
│       └── deploy.yml           # GitHub Pages deployment workflow
├── public/
│   ├── audio/                   # Audiobook MP3 recordings
│   ├── images/                  # Cover artwork and branding assets
│   ├── .htaccess                # Apache routing, caching, & HTTPS rules
│   ├── favicon.svg
│   └── robots.txt
├── manuscript/                  # Raw manuscript markdown source files
├── src/
│   ├── components/              # Interactive UI components
│   │   ├── AudiobookSection.astro
│   │   ├── ChapterNavigation.astro
│   │   ├── HowToUseCard.astro
│   │   ├── ReaderControls.astro
│   │   ├── ReadingProgressBar.astro
│   │   └── TocSlideout.astro
│   ├── content/
│   │   └── chapters/            # Processed chapter content collection
│   ├── layouts/
│   │   └── BookLayout.astro     # Main application shell & global head
│   ├── lib/
│   │   ├── chapters.ts          # Chapter sorting & collection helpers
│   │   └── utils.ts             # Base URL resolver utility
│   ├── pages/
│   │   ├── index.astro          # Landing page & manuscript outline
│   │   ├── 404.astro            # Custom 404 page
│   │   └── chapter/
│   │       └── [slug].astro     # Dynamic chapter reading route
│   ├── styles/
│   │   └── global.css           # Design tokens, themes, & global styles
│   └── content.config.ts        # Astro content collections schema definition
├── scripts/
│   └── deploy.sh                # Apache deployment shell script
├── astro.config.mjs             # Astro configuration (base path & sitemap)
├── package.json
├── LICENSE
└── README.md
```

---

## Development

### Requirements

- **Node.js**: v22 LTS or newer
- **npm**: v10 or newer

### Installation

```bash
# Clone the repository
git clone https://github.com/meistro57/BookForge.git
cd BookForge

# Install dependencies
npm install
```

### Development Server

Start the local development server:

```bash
npm run dev
```

Astro will start a local web server (typically at `http://localhost:4321/BookForge/`).

### Production Build

Compile the static website:

```bash
npm run build
```

The compiled static site output will be generated in the `dist/` directory.

### Preview Build Locally

Preview the production static build locally:

```bash
npm run preview
```

---

## Build Phases Roadmap

- [x] **Phase 1: Project Bootstrap** — Astro project setup, global styles, directory structure.
- [x] **Phase 2: Manuscript Content System** — Markdown content collection, metadata schema, chapter ordering.
- [x] **Phase 3: Core Chapter Reader** — Dynamic routes, calm reading column, previous/next chapter navigation.
- [x] **Phase 4: Homepage and Contents** — Hero cover artwork, about section, grouped table of contents.
- [x] **Phase 5: Reader Controls** — Themes (Light, Warm, Dark), font size, line spacing, width controls, FOUC prevention script.
- [x] **Phase 6: Reading Progress** — Progress bar, scroll position memory, completion markers, overall progress tracking.
- [x] **Phase 7: Navigation Polish** — Sticky header, slide-out TOC panel, heading anchors, keyboard shortcuts, back-to-top control.
- [x] **Phase 8: Visual Identity** — Blueprint styling, companion track section for "The Wrong Drawing" with audio player & lyrics.
- [x] **Phase 9: Accessibility and Metadata** — Skip-to-content, WCAG contrast compliance, OpenGraph/Twitter cards, XML sitemaps, robots.txt, custom 404, print stylesheet.
- [x] **Phase 10: Static Deployment** — Subdirectory base path configuration (`/BookForge/`), `.htaccess` rules, automated deployment script (`scripts/deploy.sh`), GitHub Actions CI/CD workflows.

---

## Deployment

BookForge builds into pure static HTML, CSS, client JS, and media assets.

### 1. Apache Subdirectory Deployment

Target URL: `https://quantummindsunited.com/BookForge/`

- **Base Path Configuration**: Configured with `base: '/BookForge'` and `trailingSlash: 'always'` in `astro.config.mjs`. All links and assets resolve under `/BookForge/`.
- **Deploying via Bash Script**:
  ```bash
  ./scripts/deploy.sh /var/www/html/BookForge
  ```
- **Deploying via Rsync**:
  ```bash
  rsync -avz --delete dist/ user@server:/var/www/html/BookForge/
  ```
- **Apache `.htaccess`**: Bundled in `public/.htaccess` to enforce HTTPS, handle long-term caching for hashed assets, gzip compression, and resolve clean URLs.

### 2. GitHub Pages Deployment

Automated GitHub Pages deployment is handled by `.github/workflows/deploy.yml` on every push to the `main` branch.

---

## License

- **Software**: Licensed under the [MIT License](LICENSE).
- **Manuscript Content**: *You’re Not Broken, You’re Broadband* text, audiobook audio, and manuscript files remain the intellectual property and Copyright © Mark J. Hubrich.

---

## Author

**Mark J. Hubrich**  
Steel detailer, fabricator, writer, builder, and chronic investigator of how complicated things fit together.
