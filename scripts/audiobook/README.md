# Audiobook pipeline

Turns BookForge chapter Markdown into per-chapter MP3s, a full-book MP3/M4B, and
the manifest the reader UI consumes. Chapters are read from
`src/content/books/<book>/chapters/*.md` and ordered by frontmatter `order`.

## Prerequisites

- `ffmpeg` and `ffprobe` on `PATH`
- Python 3 with a Chatterbox install for synthesis (`torch`, `chatterbox`)
- `faster-whisper` for the optional QA pass
- A voice reference WAV in `voices/` (see `voices/README.md`)

The npm scripts call `python3`. Activate the TTS venv first, or run the scripts
directly with its interpreter, for example
`~/.venv-chatterbox/bin/python scripts/audiobook/make_audiobook.py --list`.

## Quick start

```bash
npm run audiobook:list                      # chapter order, word counts, runtime estimate
npm run audiobook:script                    # narration text for proofing
npm run audiobook:sample                    # voice one chapter's first 8 blocks
npm run audiobook:build                     # synthesize + publish the default book
npm run audiobook:check                     # Whisper QA over every generated track
```

Every command accepts the book slug, for example
`python3 scripts/audiobook/make_audiobook.py --book the-meistro-manual --list`.
The default book is `youre-not-broken-youre-broadband`.

Useful flags:

| Flag | Effect |
| --- | --- |
| `--engine full\|server` | local Chatterbox 500M, or the resident Turbo server |
| `--narrator "Eli C. Tric"` | display name, also drives the output folder and voice lookup |
| `--ref-audio PATH` | explicit reference WAV |
| `--only SLUG` | restrict to chapters whose slug or title contains SLUG |
| `--max-paragraphs N` | sample only the first N spoken blocks per chapter |
| `--redo "phrase"` | drop cached clips containing the phrase, then re-voice |
| `--publish` | copy audio into `public/audio/<book>/` and update the manifest |
| `--default` | make this narrator the manifest's `defaultNarrator` |

## Output

Build workspace (git-ignored): `audiobook-build/<book>/`

```
cache/    per-paragraph WAV cache keyed by engine + voice params + text
script/   proofing text, also the reference for Whisper QA
tracks/   loudness-normalized WAV masters and tagged MP3s
```

Published assets: `public/audio/<book>/`

```
audiobook-manifest.json
<narrator-slug>/chapters/<chapter-slug>.mp3
<narrator-slug>/full-audiobook.mp3
<narrator-slug>/full-audiobook.m4b
```

Audio is loudness-normalized to `-19 LUFS` (`-3 dB TP`, `LRA 11`) before MP3
(96 kbps) and M4B (64 kbps AAC with chapter markers and cover art).

## Multi-narrator books

Publish each narrator in a separate run. Re-running an existing narrator replaces
that narrator's entry in the manifest and prunes chapter files that no longer
exist. The reader shows narrator tabs when more than one entry is present.

## QA and targeted re-synthesis

```bash
python3 scripts/audiobook/check_track.py --all --book the-meistro-manual
python3 scripts/audiobook/check_track.py 05 12
```

The checker prints a match score per track, the mismatched spans, and a ready
`--redo` command for each flagged phrase.

## Deployment note

Generated audio is not committed to git (the full-book MP3 exceeds GitHub's
per-file limit). `public/audio/` is deployed out of band, the same way the
existing broadband recording is. The Astro build prunes manifest entries whose
files are missing, so a build without the media renders no broken players.
