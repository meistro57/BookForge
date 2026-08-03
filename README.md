# BookForge

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

### Phase 1: Project Bootstrap

Create the Astro project, global styles, folder structure, and temporary homepage.

### Phase 2: Manuscript Content System

Import the Markdown chapters, define their metadata, and establish reliable reading order.

### Phase 3: Core Chapter Reader

Render every chapter with a readable layout and previous/next navigation.

### Phase 4: Homepage and Contents

Build the book landing page and grouped table of contents.

### Phase 5: Reader Controls

Add themes, font controls, line spacing, and reading-width settings.

### Phase 6: Reading Progress

Save the current chapter, scroll position, completed chapters, and overall progress.

### Phase 7: Navigation Polish

Add a sticky header, keyboard navigation, and slide-out contents panel.

### Phase 8: Visual Identity

Apply the restrained industrial, steel-shop, and blueprint-inspired design.

### Phase 9: Accessibility and Metadata

Add accessibility checks, social metadata, print styles, sitemap, and page descriptions.

### Phase 10: Deployment

Prepare the static build for Apache, GitHub Pages, or another static host.

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

BookForge produces static HTML, CSS, and JavaScript.

The contents of `dist/` can be hosted on:

- Apache
- GitHub Pages
- Netlify
- Cloudflare Pages
- Vercel
- Any conventional static web host

The first planned public location is:

```text
https://quantummindsunited.com/broadband/
```

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
