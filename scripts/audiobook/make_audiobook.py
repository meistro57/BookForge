#!/usr/bin/env python3
"""BookForge audiobook pipeline: narrate Astro chapter Markdown with a cloned
Chatterbox voice and publish per-chapter MP3s, a full MP3/M4B, and a manifest
the Astro reader can play.

Chapters come from ``src/content/books/<book>/chapters/*.md`` and are ordered by
frontmatter ``order``. Every paragraph is cached by hash in ``audiobook-build/``
so an interrupted run resumes and an edit only re-voices changed paragraphs.

  python3 scripts/audiobook/make_audiobook.py --list
  python3 scripts/audiobook/make_audiobook.py --script-only
  python3 scripts/audiobook/make_audiobook.py --only "the-kid-in-the-hallway" --max-paragraphs 8
  python3 scripts/audiobook/make_audiobook.py --narrator "Eli C. Tric" --publish
  python3 scripts/audiobook/make_audiobook.py --only "the-kid-in-the-hallway" --redo "words from a bad spot"

Published layout (all paths relative to ``public/audio/<book>/``):

  audiobook-manifest.json                     # narrators, tracks, durations
  <narrator-slug>/chapters/<chapter-slug>.mp3 # one loudness-normalized track per chapter
  <narrator-slug>/full-audiobook.mp3          # complete book for streaming
  <narrator-slug>/full-audiobook.m4b          # chapter markers + cover for mobile players
"""
import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

SR = 24000
PCM = ["-ar", str(SR), "-ac", "1", "-c:a", "pcm_s16le"]
PAUSE = {"para": 0.55, "heading": 0.9, "track_start": 1.0, "track_end": 2.0}
NUMBERS = (
    "Zero One Two Three Four Five Six Seven Eight Nine Ten Eleven Twelve "
    "Thirteen Fourteen Fifteen Sixteen Seventeen Eighteen Nineteen Twenty"
).split()
ONES = {w.lower(): i for i, w in enumerate(NUMBERS)}
TENS = {"twenty": 20, "thirty": 30, "forty": 40, "fifty": 50}
ROOT = Path(__file__).resolve().parents[2]
DEFAULT_BOOK = "youre-not-broken-youre-broadband"


# ---------------------------------------------------------------- text -> speech script

def number_word(n):
    n = int(n)
    if n < len(NUMBERS):
        return NUMBERS[n]
    tens, ones = divmod(n, 10)
    tens_word = {2: "Twenty", 3: "Thirty", 4: "Forty", 5: "Fifty"}.get(tens, str(tens * 10))
    return f"{tens_word}-{NUMBERS[ones]}" if ones else tens_word


def word_number(token):
    token = token.lower().replace("-", " ").strip()
    if token.isdigit():
        return int(token)
    parts = token.split()
    if len(parts) == 1:
        return ONES.get(parts[0], TENS.get(parts[0]))
    if len(parts) == 2:
        tens = TENS.get(parts[0]) or ONES.get(parts[0], 0) * 10
        return tens + (ONES.get(parts[1]) or 0)
    return None


def chapter_number_from_body(body):
    """Prefer the number in the chapter's own '# Chapter Twenty' heading.

    Some books (The Meistro Manual) store a part-relative `chapterNumber` in
    frontmatter, so trusting it alone would call chapter 20 'Chapter Four'.
    """
    for line in body.splitlines():
        m = re.match(r"^\s*#{1,2}\s+Chapter\s+([A-Za-z\-]+|\d+)\b", line, re.I)
        if m:
            return word_number(m.group(1))
    return None


def roman_to_int(s):
    vals = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100}
    total = 0
    for a, b in zip(s, s[1:] + " "):
        v = vals[a]
        total += -v if vals.get(b, 0) > v else v
    return total


def spoken_title(title):
    """'Part III: Mapping...' -> 'Part Three. Mapping...'; colons become pauses."""
    m = re.match(r"^(Part)\s+([IVXL]+)\b[:.]?\s*(.*)$", title, re.I)
    if m:
        n = roman_to_int(m.group(2).upper())
        title = f"Part {NUMBERS[n] if n < len(NUMBERS) else n}: {m.group(3)}"
    return re.sub(r"\s*:\s*", ". ", title, count=1).strip()


def inline(text):
    """Strip Markdown inline syntax and symbols TTS reads badly."""
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"\[[^\]]*\]:\s*\S+", "", text)              # reference link defs
    text = re.sub(r"\[\^[^\]]*\]", "", text)                    # footnote refs
    text = re.sub(r"`([^`]*)`", r"\1", text)
    text = re.sub(r"(\*\*|__)(.+?)\1", r"\2", text)
    text = re.sub(r"(?<![\w*])[*_](?!\s)(.+?)(?<!\s)[*_](?![\w*])", r"\1", text)
    text = re.sub(r"_{3,}", "", text)                           # fill-in blanks
    text = re.sub(r"<[^>]+>", " ", text)                        # stray html
    text = text.replace("—", ", ").replace("–", ", ")
    text = text.replace("→", ", then ").replace("←", ", from ").replace("↔", " and ")
    text = text.replace(" · ", ": ").replace("·", ", ").replace("•", "")
    text = text.replace("&", " and ").replace("%", " percent")
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"\s+([,.;:!?])", r"\1", text)
    text = re.sub(r"([,.;:])\1+", r"\1", text)
    return text


def table_lines(rows):
    cells = [[c.strip() for c in r.strip().strip("|").split("|")] for r in rows]
    cells = [r for r in cells if not all(re.fullmatch(r":?-{2,}:?", c) for c in r if c)]
    if len(cells) < 2:
        return [inline(" ".join(cells[0]))] if cells else []
    head, body = cells[0], cells[1:]
    out = []
    for row in body:
        parts = [f"{inline(h).rstrip('.?:')}: {inline(c).rstrip('.')}"
                 for h, c in zip(head, row) if inline(c)]
        if parts:
            out.append(". ".join(parts) + ".")
    return out


def clean_part_title(title):
    """Strip a leading 'PART I:' because the announcement already says the number."""
    if not title:
        return ""
    stripped = re.sub(r"^(Part)\s+([IVXL]+|\d+)\b[:.]?\s*", "", title, flags=re.I)
    return spoken_title(stripped)


def strip_leading_headings(lines):
    """Drop leading book/chapter headings that the frontmatter announcement covers."""
    i = 0
    while i < len(lines) and (not lines[i].strip() or re.match(r"^\s*#{1,2}\s+", lines[i])):
        i += 1
    return lines[i:]


def norm(text):
    return re.sub(r"[^a-z0-9]+", " ", (text or "").lower()).strip()


def chapter_lines(body, book):
    """Skip repeated front-of-chapter boilerplate (book title, volume line)."""
    lines = strip_leading_headings(body.splitlines())
    title = norm(book.get("title"))
    subtitle = norm(book.get("subtitle"))
    while lines:
        s = lines[0].strip()
        if not s:
            lines = lines[1:]
            continue
        low = norm(s)
        if (title and low == title) or (subtitle and low == subtitle):
            lines = lines[1:]
            continue
        if re.match(r"^volume\s+\w+\s*:", s, re.I):
            lines = lines[1:]
            continue
        break
    return lines


def redundant_heading(text, skip, announce_norm=""):
    low = norm(text)
    if low in skip:
        return True
    if len(low) > 3 and announce_norm and low in announce_norm:
        return True
    if re.match(r"^chapter\s+(one|two|three|four|five|six|seven|eight|nine|ten|\d+)$", low):
        return True
    if re.match(r"^part\s+(one|two|three|four|five|\d+)$", low):
        return True
    return False


def blocks(lines):
    """Yield (kind, text) for one chapter body. kind is 'heading' or 'para'."""
    buf, table = [], []

    def flush():
        if buf:
            text = inline(" ".join(buf))
            if re.search(r"\w", text):
                yield ("para", text if re.search(r"[.!?:;\"')\]”’]$", text) else text + ".")
            buf.clear()

    for line in list(lines) + [""]:
        s = line.strip()
        if not s or s.startswith("data:image") or re.match(r"^!\[[^\]]*\]\(data:", s):
            yield from flush()
            continue
        if s.startswith("|"):
            yield from flush()
            table.append(s)
            continue
        if table:
            for t in table_lines(table):
                yield ("para", t)
            table = []
        m = re.match(r"^(#{1,6})\s+(.*)$", s)
        if m:
            yield from flush()
            yield ("heading", spoken_title(inline(m.group(2))) + ".")
        elif re.fullmatch(r"(-{3,}|\*{3,}|_{3,})", s):
            yield from flush()
        elif re.match(r"^([-*+]|\d+[.)])\s+", s):
            yield from flush()
            buf.append(re.sub(r"^[-*+]\s+", "", s))
            yield from flush()
        else:
            buf.append(re.sub(r"^>\s?", "", s))


def coalesce_blocks(raw_blocks, min_chars=90, max_chars=240):
    """Merge short consecutive 'para' blocks into natural multi-sentence paragraphs
    so 1-3 word lines ('I failed it.', 'Perhaps.') are never sent alone to TTS."""
    out = []
    cur_text = ""
    for kind, text in raw_blocks:
        if kind == "heading":
            if cur_text:
                if len(cur_text) < 40 and out and out[-1][0] == "para":
                    out[-1] = ("para", f"{out[-1][1]} {cur_text}")
                else:
                    out.append(("para", cur_text))
                cur_text = ""
            out.append((kind, text))
        else:
            if not cur_text:
                cur_text = text
            elif len(cur_text) < min_chars or len(cur_text) + 1 + len(text) <= max_chars or len(text) < 40:
                cur_text = f"{cur_text} {text}"
            else:
                out.append(("para", cur_text))
                cur_text = text
    if cur_text:
        if len(cur_text) < 40 and out and out[-1][0] == "para":
            out[-1] = ("para", f"{out[-1][1]} {cur_text}")
        else:
            out.append(("para", cur_text))
    return out


def parse_frontmatter(md_text):
    meta, body = {}, md_text
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", md_text, re.S)
    if not m:
        return meta, body
    raw_yaml, body = m.group(1), m.group(2)
    for line in raw_yaml.splitlines():
        kv = re.match(r"^([A-Za-z0-9_]+)\s*:\s*(.*)$", line.strip())
        if not kv:
            continue
        k, v = kv.group(1), kv.group(2).strip().strip('"').strip("'")
        if v.lower() == "null" or v == "":
            meta[k] = None
        elif v.lower() in ("true", "false"):
            meta[k] = v.lower() == "true"
        elif re.fullmatch(r"-?\d+", v):
            meta[k] = int(v)
        else:
            meta[k] = v
    return meta, body


def slugify(text):
    return re.sub(r"[^a-z0-9]+", "-", (text or "").lower()).strip("-") or "narrator"


def load_book(book_slug, chapters_dir):
    book_json = ROOT / "src" / "content" / "books" / book_slug / "book.json"
    if not book_json.exists():
        sys.exit(f"book.json not found: {book_json}")
    book = json.loads(book_json.read_text(encoding="utf-8"))
    if not chapters_dir.exists():
        sys.exit(f"chapters directory not found: {chapters_dir}")

    entries = []
    for path in sorted(chapters_dir.glob("*.md")):
        meta, body = parse_frontmatter(path.read_text(encoding="utf-8"))
        entries.append({
            "order": meta.get("order", 999),
            "slug": meta.get("slug") or path.stem,
            "title": meta.get("title") or path.stem,
            "chapterNumber": meta.get("chapterNumber"),
            "partNumber": meta.get("partNumber"),
            "partTitle": meta.get("partTitle"),
            "isFrontMatter": bool(meta.get("isFrontMatter")),
            "body": body,
        })
    entries.sort(key=lambda e: e["order"])

    tracks = []
    seen_parts = set()
    book_title = norm(book.get("title"))
    book_subtitle = norm(book.get("subtitle"))
    part_norms = set()
    for e in entries:
        if e["partTitle"]:
            p_word = number_word(e["partNumber"] or 0)
            p_title = clean_part_title(e["partTitle"])
            part_norms |= {norm(e["partTitle"]), norm(p_title), norm(f"Part {p_word}"),
                           norm(f"Part {p_word}. {p_title}")}
    for e in entries:
        announce = []
        skip = {book_title, book_subtitle, norm(e["title"]), norm(spoken_title(e["title"]))}
        skip |= part_norms
        chapter_num = chapter_number_from_body(e["body"]) or e["chapterNumber"]
        if e["partNumber"] not in (None, 0) and e["partNumber"] not in seen_parts:
            seen_parts.add(e["partNumber"])
            p_word = number_word(e["partNumber"])
            p_title = clean_part_title(e["partTitle"])
            announce.append(("heading", f"Part {p_word}." + (f" {p_title}." if p_title else "")))
            skip |= {norm(e["partTitle"]), norm(p_title), norm(f"Part {p_word}"),
                     norm(f"Part {p_word}. {p_title}")}
        if chapter_num:
            c_word = number_word(chapter_num)
            label = f"Chapter {c_word}"
            title_text = spoken_title(e["title"])
            spoken = label + "." if norm(title_text) == norm(label) else f"{label}. {title_text}."
            announce.append(("heading", spoken))
            skip |= {norm(label), norm(f"Chapter {chapter_num}")}
        else:
            announce.append(("heading", f"{spoken_title(e['title'])}."))

        announce_norm = " ".join(norm(text) for _, text in announce)
        raw_body = list(blocks(chapter_lines(e["body"], book)))
        body = coalesce_blocks(raw_body)
        body = [
            (kind, text) for kind, text in body
            if not (kind == "heading" and redundant_heading(text, skip, announce_norm))
            and not (kind == "para" and re.match(r"^volume\s+\w+\s*:", text, re.I))
        ]
        e["blocks"] = announce + body
        tracks.append(e)
    return book, tracks


# ---------------------------------------------------------------- audio synthesis

def ffmpeg(*args, data=None):
    return subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *args],
                          input=data, capture_output=True, check=True)


def duration(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "csv=p=0", str(path)], capture_output=True, text=True)
    return float(out.stdout.strip())


_FULL_MODEL = None


def get_full_model():
    global _FULL_MODEL
    if _FULL_MODEL is None:
        import torch
        from chatterbox.tts import ChatterboxTTS
        device = "cuda" if torch.cuda.is_available() else "cpu"
        _FULL_MODEL = ChatterboxTTS.from_pretrained(device=device)
    return _FULL_MODEL


def split_chunks(text, max_chars=260):
    sentences = re.split(r"(?<=[.!?…])\s+", text.strip())
    chunks, cur = [], ""
    for s in sentences:
        if cur and len(cur) + len(s) + 1 > max_chars and len(cur) >= 40:
            chunks.append(cur)
            cur = s
        else:
            cur = f"{cur} {s}".strip()
    if cur:
        if len(cur) < 35 and chunks:
            chunks[-1] = f"{chunks[-1]} {cur}"
        else:
            chunks.append(cur)
    return chunks


def atempo_filter(tempo):
    return ["-af", f"atempo={tempo}"] if abs(tempo - 1.0) > 1e-3 else []


def speak(text, args, dest, retries=3):
    if args.engine == "full":
        import io
        import torch
        import torchaudio
        model = get_full_model()
        pieces = []
        sil = torch.zeros(1, int(model.sr * 0.2))
        for idx, chunk in enumerate(split_chunks(text)):
            words = max(len(chunk.split()), 1)
            max_expected_s = max(4.5, words * 0.85 + 2.5)
            for attempt in range(4):
                torch.manual_seed(42 + idx + attempt * 17)
                wav = model.generate(
                    chunk,
                    audio_prompt_path=str(args.ref_audio),
                    exaggeration=args.exaggeration,
                    cfg_weight=args.cfg_weight,
                ).cpu()
                if wav.shape[1] / model.sr <= max_expected_s:
                    break
            pieces += [wav, sil]
        full_wav = torch.cat(pieces[:-1], dim=1)
        buf = io.BytesIO()
        torchaudio.save(buf, full_wav, model.sr, format="wav")
        ffmpeg("-i", "pipe:0", *atempo_filter(args.tempo), *PCM, str(dest), data=buf.getvalue())
        return

    body = json.dumps({"input": text, "voice": args.voice, "response_format": "wav"}).encode()
    req = urllib.request.Request(f"{args.server}/audio/speech", data=body,
                                 headers={"Content-Type": "application/json"})
    for attempt in range(1, retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=600) as r:
                wav = r.read()
            ffmpeg("-i", "pipe:0", *atempo_filter(args.tempo), *PCM, str(dest), data=wav)
            return
        except (urllib.error.URLError, subprocess.CalledProcessError, TimeoutError) as e:
            if attempt == retries:
                raise RuntimeError(f"TTS failed after {retries} tries: {e}") from e
            time.sleep(5 * attempt)


def silence(out, seconds):
    path = out / "cache" / f"silence_{seconds:.2f}.wav"
    if not path.exists():
        ffmpeg("-f", "lavfi", "-i", f"anullsrc=r={SR}:cl=mono", "-t", f"{seconds}", *PCM, str(path))
    return path


def cache_key_prefix(args):
    if args.engine == "full":
        return (f"full500m:{args.ref_audio.name}:ex{args.exaggeration:.2f}"
                f":cfg{args.cfg_weight:.2f}:spd{args.tempo:.2f}")
    return f"server:{args.server}:{args.voice}:spd{args.tempo:.2f}"


def render_track(n, track, args, out, stats):
    cache = out / "cache"
    seq = [silence(out, PAUSE["track_start"])]
    items = track["blocks"]
    if args.max_paragraphs:
        items = items[:args.max_paragraphs]
    prefix = cache_key_prefix(args)
    for kind, text in items:
        key = hashlib.sha1(f"{prefix}\n{text}".encode()).hexdigest()[:16]
        clip = cache / f"{key}.wav"
        if not clip.exists():
            t0 = time.time()
            speak(text, args, clip)
            stats["made"] += 1
            stats["gen_s"] += time.time() - t0
            stats["audio_s"] += duration(clip)
        else:
            stats["cached"] += 1
        seq += [clip, silence(out, PAUSE["heading" if kind == "heading" else "para"])]
    seq[-1] = silence(out, PAUSE["track_end"])

    listfile = cache / f"track_{n:02d}.txt"
    listfile.write_text("".join(f"file '{p.resolve()}'\n" for p in seq))
    raw = cache / f"track_{n:02d}.wav"
    ffmpeg("-f", "concat", "-safe", "0", "-i", str(listfile), "-c", "copy", str(raw))

    norm = out / "tracks" / f"{n:02d} - {track['slug']}.wav"
    ffmpeg("-i", str(raw), "-af", "loudnorm=I=-19:TP=-3:LRA=11", *PCM, str(norm))
    mp3 = out / "tracks" / f"{n:02d} - {track['slug']}.mp3"
    ffmpeg("-i", str(norm), "-c:a", "libmp3lame", "-b:a", "96k",
           "-metadata", f"title={track['title']}", "-metadata", f"track={n}",
           "-metadata", f"album={args.title}", "-metadata", f"artist={args.author}", str(mp3))
    return norm, mp3


def human_duration(seconds):
    total = int(round(seconds))
    hours, rem = divmod(total, 3600)
    minutes, secs = divmod(rem, 60)
    return f"{hours}:{minutes:02d}:{secs:02d}" if hours else f"{minutes}:{secs:02d}"


def concat_files(paths, dest, codec_args):
    dest.parent.mkdir(parents=True, exist_ok=True)
    listfile = dest.parent / f"{dest.stem}_concat.txt"
    listfile.write_text("".join(f"file '{p.resolve()}'\n" for p in paths))
    ffmpeg("-f", "concat", "-safe", "0", "-i", str(listfile), *codec_args, str(dest))
    return dest


def build_full_mp3(wavs, args, out):
    dest = out / "tracks" / "full-audiobook.mp3"
    return concat_files(wavs, dest, ["-c:a", "libmp3lame", "-b:a", "96k",
                                     "-metadata", f"title={args.title}",
                                     "-metadata", f"album={args.title}",
                                     "-metadata", f"artist={args.author}",
                                     "-metadata", "genre=Audiobook"])


def build_m4b(wavs, tracks, args, out):
    meta = [";FFMETADATA1", f"title={args.title}", f"album={args.title}",
            f"artist={args.author}", f"album_artist={args.author}", "genre=Audiobook", ""]
    start = 0
    for wav, t in zip(wavs, tracks):
        end = start + int(duration(wav) * 1000)
        meta += ["[CHAPTER]", "TIMEBASE=1/1000", f"START={start}", f"END={end}",
                 f"title={t['title']}", ""]
        start = end
    meta_file = out / "cache" / "chapters.txt"
    meta_file.write_text("\n".join(meta))
    all_file = out / "cache" / "all.txt"
    all_file.write_text("".join(f"file '{w.resolve()}'\n" for w in wavs))

    m4b = out / "tracks" / "full-audiobook.m4b"
    cmd = ["-f", "concat", "-safe", "0", "-i", str(all_file), "-i", str(meta_file)]
    if args.cover and args.cover.exists():
        cmd += ["-i", str(args.cover), "-map", "0:a", "-map", "2:v",
                "-c:v", "mjpeg", "-disposition:v", "attached_pic"]
    else:
        cmd += ["-map", "0:a"]
    cmd += ["-map_metadata", "1", "-map_chapters", "1",
            "-c:a", "aac", "-b:a", "64k", "-movflags", "+faststart", "-f", "mp4", str(m4b)]
    ffmpeg(*cmd)
    return m4b


# ---------------------------------------------------------------- publish + manifest

def publish(args, tracks, chapter_mp3s, full_mp3, m4b, durations):
    audio_root = args.public_dir / "audio" / args.book
    narrator_dir = audio_root / args.narrator_slug
    tracks_dir = narrator_dir / "chapters"
    tracks_dir.mkdir(parents=True, exist_ok=True)

    for track in tracks:
        src = chapter_mp3s[track["slug"]]
        shutil.copy2(src, tracks_dir / f"{track['slug']}.mp3")
    keep = {f"{t['slug']}.mp3" for t in tracks}
    for stale in tracks_dir.glob("*.mp3"):
        if stale.name not in keep:
            stale.unlink()

    full_mp3_rel = full_m4b_rel = None
    if full_mp3:
        shutil.copy2(full_mp3, narrator_dir / "full-audiobook.mp3")
        full_mp3_rel = f"{args.narrator_slug}/full-audiobook.mp3"
    if m4b:
        shutil.copy2(m4b, narrator_dir / "full-audiobook.m4b")
        full_m4b_rel = f"{args.narrator_slug}/full-audiobook.m4b"

    manifest_path = audio_root / "audiobook-manifest.json"
    manifest = {}
    if manifest_path.exists():
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            manifest = {}

    entry = {
        "name": args.narrator,
        "slug": args.narrator_slug,
        "engine": args.engine,
        "voice": args.voice,
        "generated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "fullMp3": full_mp3_rel,
        "m4b": full_m4b_rel,
        "chapters": [
            {
                "slug": t["slug"],
                "title": t["title"],
                "order": t["order"],
                "chapterNumber": t["chapterNumber"],
                "partNumber": t["partNumber"],
                "partTitle": t["partTitle"],
                "isFrontMatter": t["isFrontMatter"],
                "audioFile": f"{args.narrator_slug}/chapters/{t['slug']}.mp3",
                "duration": round(durations[t["slug"]], 3),
                "durationHuman": human_duration(durations[t["slug"]]),
            }
            for t in tracks
        ],
    }

    narrators = manifest.get("narrators") or []
    replaced = False
    for i, existing in enumerate(narrators):
        if existing.get("slug") == args.narrator_slug:
            narrators[i] = entry
            replaced = True
            break
    if not replaced:
        narrators.append(entry)

    manifest.update({
        "book": args.book,
        "title": args.title,
        "author": args.author,
        "generated": entry["generated"],
        "narrators": narrators,
    })
    if args.default or not manifest.get("defaultNarrator"):
        manifest["defaultNarrator"] = args.narrator
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"manifest: {manifest_path}")
    print(f"tracks:   {tracks_dir}")
    return manifest_path


# ---------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--book", default=DEFAULT_BOOK,
                    help=f"book slug under src/content/books (default: {DEFAULT_BOOK})")
    ap.add_argument("--chapters-dir", type=Path,
                    help="override the chapter Markdown directory")
    ap.add_argument("--out", type=Path, help="build workspace (default: audiobook-build/<book>)")
    ap.add_argument("--public-dir", type=Path, default=ROOT / "public",
                    help="static assets root used by --publish (default: public)")
    ap.add_argument("--engine", choices=["full", "server"], default="full",
                    help="'full' Chatterbox 500M, or 'server' Chatterbox-Turbo HTTP")
    ap.add_argument("--ref-audio", type=Path, help="reference voice WAV for --engine full")
    ap.add_argument("--exaggeration", type=float, default=0.62)
    ap.add_argument("--cfg-weight", type=float, default=0.32)
    ap.add_argument("--tempo", type=float, default=0.88, help="playback tempo multiplier")
    ap.add_argument("--voice", help="server voice name (default: first word of narrator)")
    ap.add_argument("--server", default="http://127.0.0.1:8890/v1")
    ap.add_argument("--narrator", help="narrator display name (default: book.json audiobook.narrator)")
    ap.add_argument("--title", help="book title (default: book.json title)")
    ap.add_argument("--author", help="book author (default: book.json author)")
    ap.add_argument("--cover", type=Path, help="cover image for the M4B (default: book.json cover)")
    ap.add_argument("--only", action="append", help="only chapters whose title/slug contains this")
    ap.add_argument("--max-paragraphs", type=int, help="voice only the first N blocks per chapter")
    ap.add_argument("--redo", action="append", metavar="SNIPPET",
                    help="delete cached clips whose text contains SNIPPET so they are re-voiced")
    ap.add_argument("--list", action="store_true", help="list chapters and word counts, then exit")
    ap.add_argument("--script-only", action="store_true", help="write narration text, no audio")
    ap.add_argument("--publish", action="store_true",
                    help="copy audio into public/audio/<book>/ and update the manifest")
    ap.add_argument("--default", action="store_true",
                    help="make this narrator the manifest defaultNarrator")
    args = ap.parse_args()

    chapters_dir = args.chapters_dir or (ROOT / "src" / "content" / "books" / args.book / "chapters")
    book, tracks = load_book(args.book, chapters_dir)

    audiobook = book.get("audiobook") or {}
    args.title = args.title or book.get("title") or args.book
    args.author = args.author or book.get("author") or ""
    args.narrator = args.narrator or audiobook.get("narrator") or "Narrator"
    args.narrator_slug = slugify(args.narrator)
    args.voice = args.voice or audiobook.get("voice") or args.narrator_slug.split("-")[0]
    ref_override = audiobook.get("refAudio")
    if not args.ref_audio and ref_override:
        candidate = ROOT / ref_override
        if candidate.exists():
            args.ref_audio = candidate
    if not args.ref_audio:
        for candidate in (f"{args.voice}_voice_ref_continuous.wav", f"{args.voice}_voice_ref.wav"):
            path = ROOT / "voices" / candidate
            if path.exists():
                args.ref_audio = path
                break
        else:
            args.ref_audio = ROOT / "voices" / f"{args.voice}_voice_ref_continuous.wav"
    if not args.cover:
        cover_rel = book.get("cover")
        if cover_rel:
            path = args.public_dir / cover_rel
            args.cover = path if path.exists() else None
    args.out = args.out or (ROOT / "audiobook-build" / args.book)

    numbered = list(enumerate(tracks, 1))
    if args.only:
        selected, seen_slugs = [], set()
        for wanted in args.only:
            low = wanted.lower()
            exact = [(n, t) for n, t in numbered if t["slug"].lower() == low]
            matches = exact or [
                (n, t) for n, t in numbered
                if low in t["title"].lower() or low in t["slug"].lower()
            ]
            for n, t in matches:
                if t["slug"] not in seen_slugs:
                    seen_slugs.add(t["slug"])
                    selected.append((n, t))
        if not selected:
            sys.exit("no chapter matched --only")
        numbered = selected

    words = lambda t: sum(len(x.split()) for _, x in t["blocks"])
    if args.list:
        for n, t in numbered:
            print(f"{n:3d}  {words(t):6d} words  ~{words(t) / 155:5.1f} min  "
                  f"{t['slug']:42s} {t['title']}")
        total = sum(words(t) for _, t in numbered)
        print(f"total {total} words, ~{total / 155 / 60:.1f} h of audio")
        return

    for d in ("cache", "tracks", "script"):
        (args.out / d).mkdir(parents=True, exist_ok=True)

    if args.script_only:
        for n, t in numbered:
            body = "\n\n".join(f"[{k.upper()}] {x}" if k == "heading" else x
                               for k, x in t["blocks"])
            (args.out / "script" / f"{n:02d} - {t['slug']}.txt").write_text(body + "\n")
        print(f"wrote {len(numbered)} narration scripts to {args.out / 'script'}")
        return

    if args.engine == "full" and not args.ref_audio.exists():
        sys.exit(f"reference voice not found: {args.ref_audio}\n"
                 f"Create one with scripts/audiobook/prepare_voice_ref.sh")

    if args.redo:
        dropped = 0
        prefix = cache_key_prefix(args)
        for _, t in numbered:
            for _, text in t["blocks"]:
                if any(r.lower() in text.lower() for r in args.redo):
                    clip = args.out / "cache" / f"{hashlib.sha1(f'{prefix}\n{text}'.encode()).hexdigest()[:16]}.wav"
                    if clip.exists():
                        clip.unlink()
                        dropped += 1
        print(f"dropped {dropped} cached clip(s); they will be re-voiced now")

    stats = {"made": 0, "cached": 0, "gen_s": 0.0, "audio_s": 0.0}
    t_start = time.time()
    wavs, chapter_mp3s, durations = [], {}, {}
    for i, (n, t) in enumerate(numbered, 1):
        print(f"[{i}/{len(numbered)}] {t['title']} ({len(t['blocks'])} blocks)", flush=True)
        wav, mp3 = render_track(n, t, args, args.out, stats)
        wavs.append(wav)
        chapter_mp3s[t["slug"]] = mp3
        durations[t["slug"]] = duration(wav)
        if stats["gen_s"]:
            rtf = stats["audio_s"] / stats["gen_s"]
            left = sum(words(tt) for _, tt in numbered[i:]) / 155 * 60 / rtf
            print(f"    new {stats['made']}  cached {stats['cached']}  speed {rtf:.1f}x realtime"
                  f"  ~{left / 60:.0f} min left", flush=True)

    published_all = not args.only and not args.max_paragraphs
    full_mp3 = m4b = None
    if published_all:
        full_mp3 = build_full_mp3(wavs, args, args.out)
        m4b = build_m4b(wavs, [t for _, t in numbered], args, args.out)
        print(f"full mp3: {full_mp3}")
        print(f"m4b:      {m4b}  ({duration(m4b) / 3600:.1f} h)")

    if args.publish and published_all:
        publish(args, [t for _, t in numbered], chapter_mp3s, full_mp3, m4b, durations)
    elif args.publish:
        print("skipped --publish: run without --only/--max-paragraphs for a complete publish")

    print(f"tracks in {args.out / 'tracks'}  (elapsed {(time.time() - t_start) / 60:.1f} min)")


if __name__ == "__main__":
    main()
