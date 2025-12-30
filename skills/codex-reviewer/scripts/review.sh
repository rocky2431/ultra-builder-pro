#!/bin/bash
# Codex Code Reviewer - Execution Script
# Calls codex CLI to perform code review with 100-point scoring
#
# Usage: ./review.sh <file_path> [--auto]
#   --auto: Automatically execute without confirmation
#
# Environment:
#   CODEX_MIN_SCORE: Minimum score to pass (default: 80)
#   CODEX_TIMEOUT: Timeout in seconds (default: 120)

set -e

# Configuration
MIN_SCORE="${CODEX_MIN_SCORE:-80}"
TIMEOUT="${CODEX_TIMEOUT:-120}"
AUTO_MODE=false

# Parse arguments
FILE_PATH=""
for arg in "$@"; do
  case $arg in
    --auto)
      AUTO_MODE=true
      ;;
    *)
      if [ -z "$FILE_PATH" ]; then
        FILE_PATH="$arg"
      fi
      ;;
  esac
done

# Validate input
if [ -z "$FILE_PATH" ]; then
  echo "Usage: $0 <file_path> [--auto]"
  exit 1
fi

if [ ! -f "$FILE_PATH" ]; then
  echo "Error: File not found: $FILE_PATH"
  exit 1
fi

# Check codex availability
if ! command -v codex &> /dev/null; then
  echo "Error: codex CLI not found. Install with: npm install -g @openai/codex"
  exit 1
fi

# Get file content and diff if available
FILE_CONTENT=$(cat "$FILE_PATH")
DIFF_CONTENT=""
if git diff --quiet "$FILE_PATH" 2>/dev/null; then
  DIFF_CONTENT=$(git diff "$FILE_PATH" 2>/dev/null || echo "")
fi

# Build the review prompt
REVIEW_PROMPT=$(cat <<EOF
You are a strict code reviewer. Review this code file:

File: $FILE_PATH
Content:
\`\`\`
$FILE_CONTENT
\`\`\`

${DIFF_CONTENT:+Recent Changes:
\`\`\`diff
$DIFF_CONTENT
\`\`\`
}

Review across these dimensions:

1. **Correctness** (40 points)
   - Logic errors
   - Boundary conditions
   - Error handling

2. **Security** (30 points)
   - Input validation
   - Injection risks
   - Sensitive data exposure

3. **Performance** (20 points)
   - Time/space complexity
   - Redundant computation

4. **Maintainability** (10 points)
   - Code clarity
   - Naming conventions

Output JSON format:
{
  "score": {
    "correctness": X,
    "security": X,
    "performance": X,
    "maintainability": X,
    "total": X
  },
  "critical_issues": [
    {"line": N, "issue": "description", "fix": "suggestion"}
  ],
  "suggestions": [
    {"line": N, "issue": "description", "fix": "suggestion"}
  ],
  "verdict": "PASS|NEEDS_FIX|BLOCK"
}

PASS: total >= $MIN_SCORE, no critical issues
NEEDS_FIX: total 60-79, or 1-2 critical issues
BLOCK: total < 60, or 3+ critical issues
EOF
)

# Execute codex review
echo "🔍 Codex Code Review: $FILE_PATH"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Use codex exec for non-interactive execution (official syntax)
RESULT=$(timeout "$TIMEOUT" codex exec --json "$REVIEW_PROMPT" 2>&1) || {
  echo "⚠️ Codex review timed out or failed"
  exit 1
}

# Output result
echo "$RESULT"

# Parse verdict for exit code
VERDICT=$(echo "$RESULT" | jq -r '.verdict // "UNKNOWN"' 2>/dev/null || echo "UNKNOWN")

case "$VERDICT" in
  "PASS")
    echo "✅ Review PASSED"
    exit 0
    ;;
  "NEEDS_FIX")
    echo "⚠️ Review requires fixes"
    exit 1
    ;;
  "BLOCK")
    echo "❌ Review BLOCKED - critical issues found"
    exit 2
    ;;
  *)
    echo "⚠️ Could not parse review result"
    exit 1
    ;;
esac
