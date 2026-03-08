#!/bin/bash
# Sync canonical shared files from ai-collab-base to all consumer skills.
# Run from any directory — uses script location to find paths.

set -euo pipefail

BASE="$(cd "$(dirname "$0")/references" && pwd)"
SKILLS_DIR="$(cd "$(dirname "$0")/.." && pwd)"

echo "Syncing from: $BASE"

for skill in gemini-collab codex-collab ultra-verify; do
  target="${SKILLS_DIR}/${skill}/references"
  if [ -d "$target" ]; then
    cp "$BASE/collab-protocol.md" "$target/"
    echo "  ✓ ${skill}/references/collab-protocol.md"

    if [ "$skill" != "ultra-verify" ]; then
      cp "$BASE/collaboration-modes.md" "$target/"
      echo "  ✓ ${skill}/references/collaboration-modes.md"
    fi
  else
    echo "  ✗ ${skill}/references/ not found — skipping"
  fi
done

echo "Done."
