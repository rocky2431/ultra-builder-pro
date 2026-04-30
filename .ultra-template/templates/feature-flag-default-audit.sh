#!/usr/bin/env bash
# feature-flag-default-audit.sh
#
# Surface every `default off` / `enabled: false` / commented-out feature so the
# user knows what is *quietly* disabled. Catches the "agent shipped task by
# turning the feature off" failure mode v7 fixes.
#
# Usage:
#   bash .ultra/templates/feature-flag-default-audit.sh [path]
#
# Default path: src/  (override with first arg)
#
# PHILOSOPHY: enables C5 (Bounded Autonomy) — default-off without rationale is
# scope reduction in disguise; this surfaces it so the user can decide.

set -euo pipefail

ROOT="${1:-src}"
if [ ! -d "$ROOT" ]; then
  echo "[audit] path not found: $ROOT" >&2
  exit 1
fi

echo "## Feature-flag default audit"
echo "Path: $ROOT"
echo "Generated: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo ""

# Patterns we care about. Adjust per project conventions.
patterns=(
  '\benabled:\s*false\b'
  '\bdefault\s*[:=]\s*false\b'
  '\bDISABLED\s*=\s*true\b'
  '\bif\s*\(\s*false\s*\)'
  'FEATURE_[A-Z_]+\s*=\s*false'
)

found_any=0
for p in "${patterns[@]}"; do
  hits=$(grep -REn "$p" "$ROOT" \
    --include='*.ts' --include='*.tsx' \
    --include='*.js' --include='*.jsx' \
    --include='*.py' --include='*.go' \
    --include='*.rs' --include='*.sol' \
    --include='*.yaml' --include='*.yml' \
    --include='*.json' --include='*.toml' 2>/dev/null || true)

  if [ -n "$hits" ]; then
    found_any=1
    echo "### Pattern: $p"
    echo '```'
    echo "$hits"
    echo '```'
    echo ""
  fi
done

# Also surface TODO-style "off until later" markers
todo_hits=$(grep -REn '(TODO|FIXME).*(enable|turn on|flip on)' "$ROOT" 2>/dev/null || true)
if [ -n "$todo_hits" ]; then
  found_any=1
  echo "### TODOs to re-enable later"
  echo '```'
  echo "$todo_hits"
  echo '```'
  echo ""
fi

if [ "$found_any" -eq 0 ]; then
  echo "_No default-off features detected._"
  exit 0
fi

echo "---"
echo ""
echo "**Action**: For each entry above, confirm with the user whether it is:"
echo "- (A) Pre-launch: feature is built but gated until release — fine"
echo "- (B) Genuine kill-switch: stays off in normal operation — fine, document why"
echo "- (C) Hiding incomplete work: agent shipped task by turning it off — **must fix**"
