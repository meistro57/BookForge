#!/usr/bin/env python3
"""Transcribe narrated BookForge chapters with faster-whisper and flag passages
where the audio does not match the narration script (skipped, garbled, invented).

Run with the interpreter that has faster-whisper installed:

  python3 scripts/audiobook/check_track.py              # all tracks for the default book
  python3 scripts/audiobook/check_track.py --all --book the-meistro-manual
  python3 scripts/audiobook/check_track.py 05 12        # specific track numbers

Each mismatch prints the script span, what Whisper heard, and a ready-to-run
``make_audiobook.py --redo`` command for the offending phrase.
"""
import argparse
import difflib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_BOOK = "youre-not-broken-youre-broadband"

# US/UK spellings and number words Whisper normalises differently: not errors.
EQUIV = {"recognize": "recognise", "realize": "realise", "judgment": "judgement",
         "1": "one", "2": "two", "3": "three", "4": "four", "5": "five"}


def words(text):
    text = re.sub(r"\[HEADING\]", " ", text)
    out = []
    for w in re.findall(r"[a-z0-9']+", text.lower()):
        w = w.strip("'")
        for us, uk in EQUIV.items():
            if w.startswith(us):
                w = uk + w[len(us):]
        out.append(w)
    return out


def script_for(script_dir, num):
    return next((script_dir.glob(f"{num} - *.txt")), None)


def check(model, build, num, min_gap):
    wav = build / "tracks" / f"{num}.wav"
    if not wav.exists():
        candidates = sorted((build / "tracks").glob(f"{num} - *.wav"))
        wav = candidates[0] if candidates else wav
    script = script_for(build / "script", num)
    if not wav.exists() or not script:
        print(f"{num}: missing track or script (run --script-only first)")
        return None

    segs, _ = model.transcribe(str(wav), beam_size=1)
    heard = words(" ".join(s.text for s in segs))
    want = words(script.read_text())
    sm = difflib.SequenceMatcher(a=want, b=heard, autojunk=False)
    ops = sm.get_opcodes()
    note = ""
    if ops and ops[-1][0] == "delete" and ops[-1][2] == len(want) and ops[-1][2] - ops[-1][1] > 50:
        want = want[:ops[-1][1]]
        sm = difflib.SequenceMatcher(a=want, b=heard, autojunk=False)
        ops = sm.get_opcodes()
        note = f", partial track: first {len(want)} words voiced"

    print(f"{script.stem}: match {sm.ratio():.1%} ({len(want)} words{note})")
    snippets = []
    for op, a1, a2, b1, b2 in ops:
        if op == "equal" or max(a2 - a1, b2 - b1) < min_gap:
            continue
        ctx = " ".join(want[max(0, a1 - 6):a2 + 6])
        print(f"  {op:7s} script: {' '.join(want[a1:a2])[:120]!r}")
        print(f"          heard:  {' '.join(heard[b1:b2])[:120]!r}")
        print(f"          near:   ...{ctx[:160]}...")
        snippet = " ".join(want[a1:a2])[:80]
        if snippet:
            snippets.append(snippet)
    return snippets


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("tracks", nargs="*", help="track numbers, e.g. 05 12")
    ap.add_argument("--book", default=DEFAULT_BOOK)
    ap.add_argument("--build-dir", type=Path,
                    help="build workspace (default: audiobook-build/<book>)")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--min-gap", type=int, default=3,
                    help="ignore mismatches shorter than N words")
    ap.add_argument("--model", default="small.en")
    args = ap.parse_args()

    build = args.build_dir or (ROOT / "audiobook-build" / args.book)
    if not (build / "tracks").is_dir():
        sys.exit(f"no tracks found in {build / 'tracks'} "
                 f"(run make_audiobook.py first)")

    if args.all:
        nums = sorted(p.name.split(" ")[0] for p in (build / "tracks").glob("[0-9][0-9]*.wav"))
    elif args.tracks:
        nums = [f"{int(n):02d}" for n in args.tracks]
    else:
        sys.exit("pass track numbers or --all")

    try:
        from faster_whisper import WhisperModel
    except ImportError:
        sys.exit("faster-whisper is not installed in this interpreter; "
                 "pip install faster-whisper")

    # CPU: the GPU build of faster-whisper here lacks libcublas.so.12.
    model = WhisperModel(args.model, device="cpu", compute_type="int8")
    redo = {}
    for n in nums:
        snippets = check(model, build, n, args.min_gap)
        if snippets:
            redo[n] = snippets

    if redo:
        print("\nRe-voice flagged spans:")
        for n, snippets in redo.items():
            script = script_for(build / "script", n)
            label = script.name if script else n
            slug = script.stem.split(" - ", 1)[1] if script and " - " in script.stem else n
            print(f"  # {label}")
            for snippet in snippets[:5]:
                print(f"  python3 scripts/audiobook/make_audiobook.py --book {args.book} "
                      f"--only {slug} --redo \"{snippet}\"")
    else:
        print("\nNo mismatches above the minimum gap.")


if __name__ == "__main__":
    main()
