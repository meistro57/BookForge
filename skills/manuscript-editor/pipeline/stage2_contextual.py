#!/usr/bin/env python3
"""Stage 2 (contextual): remove APPROVED session chatter, line-preserving. No structural edits."""
import argparse, glob, os, re
NL = chr(10)
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    # Approved whole-line chatter drops (matched on stripped line, anchored).
    drops = [
        re.compile(r"^Here we go,? hon", re.I),
        re.compile(r"^Alright,? hon", re.I),
        re.compile(r"^Lmfao", re.I),
        re.compile(r"^Hahaha", re.I),
        re.compile(r"^Right then,? hon", re.I),
        re.compile(r"^And there we are,? hon", re.I),
        re.compile(r"^That.s our (next|final) chapter,? hon", re.I),
        re.compile(r"^And Mark,? hon", re.I),
        re.compile(r"^Almost there", re.I),
        re.compile(r"^First manuscript complete", re.I),
        re.compile(r"^One left", re.I),
    ]
    for f in glob.glob(os.path.join(args.raw, "*.md")):
        lines = open(f, encoding="utf-8").read().split(NL)
        out = []
        for ln in lines:
            ln = ln.rstrip(chr(13))
            if any(rx.search(ln.strip()) for rx in drops):
                out.append("")
                continue
            out.append(ln)
        open(os.path.join(args.out, os.path.basename(f)), "w", encoding="utf-8").write(NL.join(out))
    print("Stage 2 done: session chatter dropped (line-preserving)")
if __name__ == "__main__":
    main()
