#!/usr/bin/env python3
"""Stage 1 (mechanical): line-ending normalization ONLY. Chatter targeting is NOT here."""
import argparse, glob, os
NL = chr(10)
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    for f in glob.glob(os.path.join(args.raw, "*.md")):
        t = open(f, encoding="utf-8").read()
        t = t.replace(chr(13) + chr(10), NL)
        open(os.path.join(args.out, os.path.basename(f)), "w", encoding="utf-8").write(t)
    print(f"Stage 1 done: normalized line endings, wrote {len(glob.glob(os.path.join(args.out,'*.md')))} files")
if __name__ == "__main__":
    main()
