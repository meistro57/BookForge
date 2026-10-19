#!/usr/bin/env python3
"""Stage 4 (scientific): citation/factual verification. Manual + flag-only; never auto-alters."""
import argparse
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", required=True)
    args = ap.parse_args()
    print("Stage 4 (scientific) requires independent verification against original sources.")
    print("Do not auto-apply. Flag all citation claims for review (Appendix F etc.).")
if __name__ == "__main__":
    main()
