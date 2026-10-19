#!/usr/bin/env python3
"""Stage 3 (structural): heading hierarchy, front matter, filenames. NOT run during chatter cleanup.
This stage is FLAGGED for later work, not auto-applied. See SKILL.md."""
import argparse
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", required=True)
    args = ap.parse_args()
    print("Stage 3 (structural) is a REVIEW workflow, not an auto-transform.")
    print("Do not apply heading/front-matter/filename changes during chatter cleanup.")
    print("Flag them for a structural review pass (see SKILL.md Stage 3).")
if __name__ == "__main__":
    main()
