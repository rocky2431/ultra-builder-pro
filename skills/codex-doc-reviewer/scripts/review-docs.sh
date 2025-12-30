#!/bin/bash
# Codex Documentation Reviewer - Execution Script
# Calls codex CLI to review and enhance documentation
#
# Usage: ./review-docs.sh <doc_file> [--enhance] [--related <code_file>]
#   --enhance: Also generate enhanced content
#   --related: Related code file for accuracy check
#
# Environment:
#   CODEX_MIN_SCORE: Minimum score to pass (default: 80)
#   CODEX_TIMEOUT: Timeout in seconds (default: 120)

set -e

# Configuration
MIN_SCORE="${CODEX_MIN_SCORE:-80}"
TIMEOUT="${CODEX_TIMEOUT:-120}"
ENHANCE_MODE=false
RELATED_CODE=""

# Parse arguments
DOC_FILE=""
while [[ $# -gt 0 ]]; do
  case $1 in
    --enhance)
      ENHANCE_MODE=true
      shift
      ;;
    --related)
      RELATED_CODE="$2"
      shift 2
      ;;
    *)
      if [ -z "$DOC_FILE" ]; then
        DOC_FILE="$1"
      fi
      shift
      ;;
  esac
done

# Validate input
if [ -z "$DOC_FILE" ]; then
  echo "Usage: $0 <doc_file> [--enhance] [--related <code_file>]"
  exit 1
fi

if [ ! -f "$DOC_FILE" ]; then
  echo "Error: Document not found: $DOC_FILE"
  exit 1
fi

# Check codex availability
if ! command -v codex &> /dev/null; then
  echo "Error: codex CLI not found. Install with: npm install -g @openai/codex"
  exit 1
fi

# Get document content
DOC_CONTENT=$(cat "$DOC_FILE")

# Get related code if specified
CODE_CONTENT=""
if [ -n "$RELATED_CODE" ] && [ -f "$RELATED_CODE" ]; then
  CODE_CONTENT=$(cat "$RELATED_CODE")
fi

# Build the review prompt
REVIEW_PROMPT=$(cat <<EOF
You are a technical documentation expert. Review this documentation:

Document: $DOC_FILE
Content:
\`\`\`markdown
$DOC_CONTENT
\`\`\`

${CODE_CONTENT:+Related Code ($RELATED_CODE):
\`\`\`
$CODE_CONTENT
\`\`\`
}

Review across these dimensions:

1. **Technical Accuracy** (35 points)
   - Do code examples work?
   - Are API descriptions correct?
   - Does it match current code?

2. **Completeness** (30 points)
   - Are all features covered?
   - Is error handling documented?
   - Are configuration options listed?

3. **Clarity** (20 points)
   - Is structure clear?
   - Any ambiguity?

4. **Practicality** (15 points)
   - Sufficient examples?
   - Easy to get started?

Output JSON format:
{
  "score": {
    "accuracy": X,
    "completeness": X,
    "clarity": X,
    "practicality": X,
    "total": X
  },
  "issues": [
    {"section": "Section X", "issue": "description", "fix": "suggestion"}
  ],
  "missing": [
    "Missing content 1",
    "Missing content 2"
  ],
  "verdict": "PASS|ENHANCE|REWRITE"
}

PASS: total >= $MIN_SCORE
ENHANCE: total 60-79
REWRITE: total < 60
EOF
)

# Execute codex review
echo "📄 Codex Documentation Review: $DOC_FILE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Use codex exec for non-interactive execution (official syntax)
RESULT=$(timeout "$TIMEOUT" codex exec --json "$REVIEW_PROMPT" 2>&1) || {
  echo "⚠️ Codex review timed out or failed"
  exit 1
}

echo "$RESULT"
echo ""

# Parse verdict
VERDICT=$(echo "$RESULT" | jq -r '.verdict // "UNKNOWN"' 2>/dev/null || echo "UNKNOWN")

# Enhancement phase if requested and needed
if [ "$ENHANCE_MODE" = true ] && [ "$VERDICT" != "PASS" ]; then
  echo ""
  echo "📝 Generating enhancements..."
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

  ENHANCE_PROMPT=$(cat <<EOF
Based on review results, enhance this documentation:

Original Document:
\`\`\`markdown
$DOC_CONTENT
\`\`\`

Add the following:
1. More code examples (production-grade, no TODO)
2. FAQ section for common issues
3. Best practices recommendations
4. Troubleshooting guide

Requirements:
- All code examples must be production-grade
- Examples must handle errors properly
- Confidence level >= 90% for all content

Output the enhanced complete document.
EOF
)

  # Use codex exec for non-interactive execution (official syntax)
  ENHANCED=$(timeout "$TIMEOUT" codex exec "$ENHANCE_PROMPT" 2>&1) || {
    echo "⚠️ Enhancement generation failed"
  }

  if [ -n "$ENHANCED" ]; then
    ENHANCED_FILE="${DOC_FILE%.md}.enhanced.md"
    echo "$ENHANCED" > "$ENHANCED_FILE"
    echo "✅ Enhanced documentation written to: $ENHANCED_FILE"
  fi
fi

# Exit based on verdict
case "$VERDICT" in
  "PASS")
    echo "✅ Documentation PASSED review"
    exit 0
    ;;
  "ENHANCE")
    echo "⚠️ Documentation needs enhancement"
    exit 1
    ;;
  "REWRITE")
    echo "❌ Documentation needs rewrite"
    exit 2
    ;;
  *)
    echo "⚠️ Could not parse review result"
    exit 1
    ;;
esac
