#!/usr/bin/env bash
# Stage 0: inventory + protect. Records file list, sizes, and SHA-256 hashes.
set -euo pipefail
SRC="${1:-raw}"
OUT="${2:-.}"
mkdir -p "$OUT"
HASHES="$OUT/HASHES.txt"
: > "$HASHES"
ls -1 "$SRC"/*.md | sort | while read -r f; do
  base=$(basename "$f")
  h=$(sha256sum "$f" | cut -d' ' -f1)
  bytes=$(stat -c%s "$f")
  printf '%s  %s  %s
' "$h" "$bytes" "$base" >> "$HASHES"
done
echo "Stage 0 complete: wrote $HASHES ($(wc -l < "$HASHES") files hashed)"
