#!/usr/bin/env python3
"""BookForge manuscript regression test suite. See SKILL.md for workflow."""
import argparse, glob, os, re, sys

NL = chr(10)

def load(path, default):
    if path and os.path.exists(path):
        return [l.strip() for l in open(path, encoding="utf-8").read().splitlines()
                if l.strip() and not l.strip().startswith("#")]
    return default

PROTECTED_DEFAULT = [
    "Meistro Method", "Meistro Manual", "honesty", "honestly", "honest",
    "honor", "Cosmic Copilot", "Honest Collaborator", "cognitive mesh",
    "capability loop",
]
CHATTER_DEFAULT = [
    "Hahaha", "Lmfao", "Here we go", "Right then, hon", "my cosmic copilot",
    "rename the chat", "First manuscript complete", "Get comfortable",
    "Five appendices to go", "One left", "Now, back to our book",
]

def norm(t):
    return t.replace(chr(13) + chr(10), chr(10))

def load_justified(path):
    out = {}
    if path and os.path.exists(path):
        for l in open(path, encoding="utf-8").read().splitlines():
            l = l.strip()
            if not l or l.startswith("#"):
                continue
            parts = l.split("|", 2)
            if len(parts) >= 2:
                out[parts[0].strip()] = (int(parts[1].strip()), parts[2].strip() if len(parts) > 2 else "")
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", default="raw")
    ap.add_argument("--pub", default="publication_v5")
    ap.add_argument("--protected", default=None)
    ap.add_argument("--chatter", default=None)
    ap.add_argument("--justified", default=None)
    ap.add_argument("--fail-on-line-delta", type=int, default=20)
    args = ap.parse_args()

    raw_files = sorted(glob.glob(os.path.join(args.raw, "*.md")))
    pub_files = sorted(glob.glob(os.path.join(args.pub, "*.md")))
    failures, warnings = [], []

    raw_names = {os.path.basename(f) for f in raw_files}
    pub_names = {os.path.basename(f) for f in pub_files}
    missing = raw_names - pub_names
    extra = pub_names - raw_names
    if missing: failures.append(f"missing vs raw: {sorted(missing)}")
    if extra:   warnings.append(f"extra in pub: {sorted(extra)}")

    justified_path = args.justified or os.path.join(os.path.dirname(os.path.abspath(__file__)), "justified_deltas.txt")
    justified = load_justified(justified_path)

    print("=== 1. file completeness ===")
    print(f"  raw={len(raw_names)}  pub={len(pub_names)}  missing={sorted(missing) or 'none'}  extra={sorted(extra) or 'none'}")

    print()
    print("=== 2. per-file structure ===")
    for base in sorted(raw_names):
        pp = os.path.join(args.pub, base)
        if not os.path.exists(pp): continue
        rt = norm(open(os.path.join(args.raw, base), encoding="utf-8").read())
        pt = norm(open(pp, encoding="utf-8").read())
        delta = rt.count(chr(10)) - pt.count(chr(10))
        if delta > args.fail_on_line_delta:
            failures.append(f"{base}: lost {delta} lines (collapse?)")
        elif delta > 0:
            warnings.append(f"{base}: {delta} lines removed (may be chatter)")
        rh = len([l for l in rt.split(chr(10)) if l.strip().startswith("#")])
        ph = len([l for l in pt.split(chr(10)) if l.strip().startswith("#")])
        if rh != ph:
            failures.append(f"{base}: heading count {rh}->{ph}")
        rb = rt.count(chr(10) + chr(10)); pb = pt.count(chr(10) + chr(10))
        if abs(rb - pb) > 20:
            failures.append(f"{base}: paragraph break {rb}->{pb}")
    print("  (deltas/heading changes reported in warnings/failures below)")

    print()
    print("=== 3. protected terminology ===")
    protected = load(args.protected, PROTECTED_DEFAULT)
    for kw in protected:
        rn = sum(len(re.findall(re.escape(kw), norm(open(os.path.join(args.raw, f), encoding="utf-8").read()))) for f in raw_names)
        pn = sum(len(re.findall(re.escape(kw), norm(open(os.path.join(args.pub, f), encoding="utf-8").read()))) for f in pub_names)
        delta = pn - rn
        if delta == 0:
            st = "OK"
        elif kw in justified:
            exp, reason = justified[kw]
            if delta == exp:
                st = f"OK (justified: {reason})"
            else:
                st = f"FAIL (expected justified delta {exp}, got {delta})"
                failures.append(f"protected {kw!r}: raw={rn} pub={pn}, justified expects {exp} but got {delta}")
        else:
            st = "FAIL"
            failures.append(f"protected {kw!r}: raw={rn} pub={pn}")
        print(f"  {kw:<32} raw={rn:>4} pub={pn:>4}  {st}")

    print()
    print("=== 4. chatter absence ===")
    chatter = load(args.chatter, CHATTER_DEFAULT)
    for c in chatter:
        hits = sum(norm(open(os.path.join(args.pub, f), encoding="utf-8").read()).lower().count(c.lower()) for f in pub_names)
        if hits: failures.append(f"chatter {c!r} still present ({hits}x)")
        print(f"  {c!r}: {'CLEAN' if hits == 0 else str(hits) + 'x PRESENT'}")

    emoji = [chr(0x2764), chr(0x2764) + chr(0xFE0F), chr(0x1F60A), chr(0x1F602),
             chr(0x1F923), chr(0x1F601), chr(0x1F970), chr(0x2763), chr(0x1F49C)]
    em = sum(norm(open(os.path.join(args.pub, f), encoding="utf-8").read()).count(e) for f in pub_names for e in emoji)
    print()
    print(f"=== 5. emoji absent: {'CLEAN' if em == 0 else str(em) + 'x PRESENT'} ===")
    if em: failures.append(f"emoji present ({em}x)")

    print()
    print("=" * 60)
    if failures:
        print(f"FAILURES ({len(failures)}):")
        for f in failures: print(f"  - {f}")
        if warnings:
            print("WARNINGS:")
            for w in warnings: print(f"  ~ {w}")
        sys.exit(1)
    print("ALL AUTOMATED CHECKS PASSED.")
    print("Reminder: green tests are NOT editorial sign-off; a separate review is required.")
    if warnings:
        print("Tolerated line-count changes (likely chatter removals):")
        for w in warnings: print(f"  ~ {w}")
    sys.exit(0)

if __name__ == "__main__":
    main()
