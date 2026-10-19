---
name: manuscript-editor
description: >-
  Editorial cleanup, structural editing, and verification workflow for BookForge
  manuscripts written as Markdown. Use when a manuscript needs conversational
  chatter scrubbed, structural normalization, terminology protection, or an
  independent editorial review. Applies to The Meistro Manual and future books.
---

# Manuscript Editor

Turn raw, conversation-derived Markdown manuscripts into clean, publication-ready
text without destroying the author voice, protected terminology, titles, headings,
case studies, or legitimate prose.

## The one rule that overrides everything

> **Never declare a manuscript clean merely because all automated tests pass.**
>
> Automated tests prove the absence of known defects. They cannot prove the
> quality of the prose. Only a separate, independent editorial review (a second
> agent, or a fresh read that ignores the test results) can declare a manuscript
> ready. Tests are a floor, not a verdict.

## When to use

- A manuscript was generated or drafted through AI conversation and carries
  session chatter (greetings, emoji, "hon", "Meistro", UI instructions).
- A manuscript needs structural normalization (heading hierarchy, line endings,
  filename conventions, front matter).
- Terminology, titles, or author-specific capitalisation must be preserved
  verbatim while other text is edited.
- Someone hands you a zip of Markdown chapters and asks for cleanup.

## Authoritative locations

- This file: `skills/manuscript-editor/SKILL.md` (workflow + reasoning).
- Lessons + failure postmortems: `skills/manuscript-editor/LESSONS_LEARNED.md`.
- Regression tests: `skills/manuscript-editor/tests/`.
- Staged pipeline: `skills/manuscript-editor/pipeline/`.
- BookForge content conventions: `src/content.config.ts` (frontmatter schema) and
  `src/lib/chapters.ts` (ordering).
- Manuscript source-of-truth: `manuscript/` (numbered Markdown chapters).

## The workflow (in order)

### Stage 0 — Inventory and protect

1. **Inventory** every source file. Record the exact list, byte size, and a
   deterministic reading order (front matter first, then numbered chapters, then
   appendices).
2. **Record SHA-256 hashes** of every original file and of the source archive
   (zip). Store them somewhere immutable — a `HASHES.txt` or the change log.
   Never edit an original; only ever copy it to a `raw/` mirror first.
3. **Identify the author voice and protected vocabulary.** Before touching anything,
   list the terms that must survive byte-for-byte: book title, series title,
   framework names ("cognitive mesh", "capability loop"), case-study headings,
   and any term that contains a word you are about to target.

### Stage 1 — Mechanical cleanup (separate, auditable)

1. **Normalize** line endings (CRLF → LF) as its own isolated operation.
2. **Remove chatter only where the signal is unambiguous**: whole-file openers,
   standalone emoji runs, and the address form of nicknames ("Meistro,",
   "hon,") — always with word boundaries.
3. **Emit a unified diff** for every file you changed, and a change log listing
   each removal with its source location and the exact text removed.

### Stage 2 — Context-aware editorial editing

1. **Read each fragment in place.** Do not global-find-replace. Session commentary
   often lacks an obvious marker ("Five appendices finished. One left.") and must
   be recognised from context, not regex.
2. **Remove writing-session commentary** (narrator speaking to the author about
   producing the book, references to "the next chapter we are writing", UI
   instructions), while preserving reader-facing prose and the book voice.
   The book informal "we" = author + reader stays; "we" = author + AI
   collaborator goes.
3. **Repair any sentence breakage** your removal caused. A dangling ", ." or
   "my ." left behind is a defect, not a finished edit.
4. **Log every edit** with before/after text so a reviewer can audit each hunk.

### Stage 3 — Structural editing

- Fix heading hierarchy (one H1 per chapter; do not repeat the book title as a
  second H1).
- Reconcile redundant front matter (multiple overlapping "intro" files).
- Normalise filenames and validate against BookForge frontmatter schema
  (`title`, `order`, `chapterNumber`, `partNumber`, `partTitle`, `isFrontMatter`).
- Regenerate/validate the table of contents against the actual chapter list.

### Stage 4 — Scientific / factual verification
- Independently verify citations and factual claims against original sources.
- Flag, never silently alter, any unverifiable reference.
- Mark clearly what is established research vs the book own working models.

### Stage 5 — Regression and hand-off
- Run the regression suite (below).
- Run a separate, independent editorial review — ideally a different agent —
  that reads the manuscript fresh and is not told the tests passed.
- Package the cleaned edition plus the diff and change log for independent
  verification.
- Never overwrite the original, the raw mirror, or prior versions. Create a new
  `publication_vN/` each revision.

## Safeguards (the reasoning, not just the regex)

1. **Word boundaries on both sides.** `\bhon\b` matches the nickname "hon" but
   never "honest", "honesty", "honor", "honey". A rule without a boundary eats
   substrings inside real words. Whenever you target a short token, ask: does a
   legitimate word contain this token? If yes, use boundaries.
2. **Protect titles before removing address terms.** "The Meistro Method" and
   "The Meistro Manual" must survive while bare "Meistro," (address) is removed.
   Decide case and context first: title-case with "The" is a proper noun;
   lowercase "my Meistro" or "cosmic copilot" is an address.
3. **Session fixes run on raw text, before generic clean.** If generic clean
   strips part of a phrase first, the later exact-match will silently fail.
   Apply exact session-commentary removals to the unmodified source, then run
   generic cleanup.
4. **Removal must not orphan text.** Deleting a marker ("Lmfao,") can leave the
   opening sentence fused to the marker, or strip a name and leave "my .".
   After every removal, inspect the surrounding sentence for breakage.
5. **A keyword-present check does not prove quality.** Verifying that "Meistro
   Method" count is 854 before and after only proves it was not deleted — not
   that nearby sentences were not mangled. Always pair count checks with
   human-readable spot checks of the changed regions.

## Use for the current manuscript

The Meistro Manual has already passed through multiple cleanup revisions.
Authoritative trees:
- Originals: the delivered zip (do not modify).
- `raw/` mirror of the originals.
- `publication_v4/` the current clean edition.
- `changelog_v4.md` the full edit log.

When resuming work, do not re-derive from memory. Read the hashes and the
changelog first, then decide the next stage (structural, scientific, or review).