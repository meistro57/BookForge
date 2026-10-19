# manuscript-editor — BookForge Editorial Skill

A reusable, staged workflow for cleaning and verifying Markdown manuscripts that
were drafted through AI conversation (e.g. *The Meistro Manual*).

## How to invoke

The skill is plain files on disk (no runtime install required). From this repo root:

```bash
# Stage 0: inventory + hash the untouched originals
bash skills/manuscript-editor/pipeline/stage0_inventory.sh raw .

# Stage 1: line-ending normalization (mechanical, isolated)
python3 skills/manuscript-editor/pipeline/stage1_mechanical.py --raw raw --out work/

# Stage 2: approved session-chatter drop (contextual, line-preserving)
python3 skills/manuscript-editor/pipeline/stage2_contextual.py --raw work/ --out work2/

# Regression: verify against originals (flags, never deletes)
python3 skills/manuscript-editor/tests/run_tests.py --raw raw --pub work2/
```

Stages 3 (structural) and 4 (scientific) are **flag-only** — they are documented
for a separate review pass and must NOT be auto-applied during chatter cleanup.

## Files

- `SKILL.md` — the full workflow and the reasoning behind every safeguard.
- `LESSONS_LEARNED.md` — postmortems of the real failures (regex corruption,
  title damage, sentence breakage, ordering errors).
- `tests/run_tests.py` — regression suite (structure, terminology, headings,
  chatter absence, emoji).
- `tests/justified_deltas.txt` — whitelist of explained, logged removals.
- `pipeline/` — staged scripts (stage0–stage4).

## The one rule

> **Automated tests certify mechanical requirements only.** They cannot certify
> editorial quality or scientific accuracy. A separate, independent editorial
> review is always required before a manuscript is declared clean.

## Authoritative locations

- BookForge content conventions: `src/content.config.ts`, `src/lib/chapters.ts`.
- Manuscript source-of-truth: `manuscript/` (numbered Markdown chapters).

This skill lives in the BookForge repo so it travels with future manuscripts and
stays discoverable to future sessions.