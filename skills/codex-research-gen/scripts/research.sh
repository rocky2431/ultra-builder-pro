#!/bin/bash
# Codex Research Generator - Execution Script
# Calls codex CLI to generate evidence-based technical research
#
# Usage: ./research.sh "<topic>" [--context <context>] [--output <file>]
#
# Environment:
#   CODEX_MIN_CONFIDENCE: Minimum confidence (default: 90)
#   CODEX_TIMEOUT: Timeout in seconds (default: 300)

set -e

# Configuration
MIN_CONFIDENCE="${CODEX_MIN_CONFIDENCE:-90}"
TIMEOUT="${CODEX_TIMEOUT:-300}"
OUTPUT_DIR="${ULTRA_RESEARCH_DIR:-.ultra/docs/research}"

# Parse arguments
TOPIC=""
CONTEXT=""
OUTPUT_FILE=""
while [[ $# -gt 0 ]]; do
  case $1 in
    --context)
      CONTEXT="$2"
      shift 2
      ;;
    --output)
      OUTPUT_FILE="$2"
      shift 2
      ;;
    *)
      if [ -z "$TOPIC" ]; then
        TOPIC="$1"
      fi
      shift
      ;;
  esac
done

# Validate input
if [ -z "$TOPIC" ]; then
  echo "Usage: $0 \"<topic>\" [--context <context>] [--output <file>]"
  exit 1
fi

# Check codex availability
if ! command -v codex &> /dev/null; then
  echo "Error: codex CLI not found. Install with: npm install -g @openai/codex"
  exit 1
fi

# Derive output file if not specified
if [ -z "$OUTPUT_FILE" ]; then
  # Create slug from topic
  SLUG=$(echo "$TOPIC" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g' | sed 's/--*/-/g' | head -c 50)
  OUTPUT_FILE="$OUTPUT_DIR/research-$SLUG-$(date +%Y%m%d).md"
fi

# Ensure output directory exists
mkdir -p "$(dirname "$OUTPUT_FILE")"

# Build the research prompt
RESEARCH_PROMPT=$(cat <<EOF
You are a technical research expert. Analyze this topic:

Topic: $TOPIC
${CONTEXT:+Context: $CONTEXT}

Research Requirements:

1. **Evidence-Based Analysis**
   - Cite official documentation
   - Reference production case studies
   - Include benchmark data where available
   - Verify all claims are current (2024+)

2. **Confidence Assessment**
   - Rate each finding 0-100%
   - Explain confidence factors
   - Flag any speculation explicitly
   - Minimum $MIN_CONFIDENCE% confidence for recommendations

3. **Production Focus**
   - All code examples must be production-ready
   - No TODO, placeholder, or demo code
   - Include error handling
   - Consider scale and performance

4. **Actionable Output**
   - Specific implementation steps
   - Required dependencies with versions
   - Configuration examples
   - Migration path if replacing existing solution

5. **Trade-off Analysis**
   - Quantified pros and cons
   - Comparison with alternatives
   - Long-term maintenance considerations

Output format (Markdown):

# Research Report: $TOPIC

## Executive Summary
{One paragraph with key findings and recommendation}

## Overall Confidence: X%

## Evidence Analysis

| Claim | Source | Verified | Confidence |
|-------|--------|----------|------------|
| ... | ... | ... | ... |

## Recommendation

**Approach**: {specific recommendation}
**Confidence**: X%
**Rationale**: {evidence-based reasoning}

## Implementation Guide

### Prerequisites
- dep1@version
- dep2@version

### Step 1: {action}
\`\`\`
{production-ready code}
\`\`\`

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| ... | ... | ... | ... |

## Alternatives Considered

| Alternative | Pros | Cons | Why Not Chosen |
|-------------|------|------|----------------|
| ... | ... | ... | ... |

## Uncertainty Notes

Items with confidence < $MIN_CONFIDENCE%:
- {item}: {confidence}% - {reason}

## Next Steps

1. [ ] {action with owner}
2. [ ] {action with owner}
EOF
)

# Execute codex research
echo "🔬 Codex Research Generator"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Topic: $TOPIC"
echo "Min Confidence: $MIN_CONFIDENCE%"
echo "Output: $OUTPUT_FILE"
echo ""
echo "Generating research report..."
echo ""

# Use codex exec for non-interactive execution (official syntax)
RESULT=$(timeout "$TIMEOUT" codex exec "$RESEARCH_PROMPT" 2>&1) || {
  echo "⚠️ Codex research generation timed out or failed"
  exit 1
}

# Check for required sections
MISSING_SECTIONS=""
if ! echo "$RESULT" | grep -q "Executive Summary"; then
  MISSING_SECTIONS="$MISSING_SECTIONS\n- Missing Executive Summary"
fi
if ! echo "$RESULT" | grep -q "Confidence"; then
  MISSING_SECTIONS="$MISSING_SECTIONS\n- Missing Confidence rating"
fi
if ! echo "$RESULT" | grep -q "Implementation"; then
  MISSING_SECTIONS="$MISSING_SECTIONS\n- Missing Implementation Guide"
fi

if [ -n "$MISSING_SECTIONS" ]; then
  echo "⚠️ Research report may be incomplete:"
  echo -e "$MISSING_SECTIONS"
  echo ""
fi

# Write output
echo "$RESULT" > "$OUTPUT_FILE"

echo "✅ Research report written to: $OUTPUT_FILE"
echo ""
echo "📊 Next steps:"
echo "   1. Review confidence levels"
echo "   2. Verify cited sources"
echo "   3. Test code examples"
echo "   4. Present to stakeholders"
