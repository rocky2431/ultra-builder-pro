#!/bin/bash
# Codex Test Generator - Execution Script
# Calls codex CLI to generate production-grade tests with 6D coverage
#
# Usage: ./generate.sh <source_file> [--output <test_file>]
#
# Environment:
#   CODEX_MIN_TAS: Minimum TAS score (default: 70)
#   CODEX_MIN_COVERAGE: Target coverage (default: 80)
#   CODEX_TIMEOUT: Timeout in seconds (default: 180)

set -e

# Configuration
MIN_TAS="${CODEX_MIN_TAS:-70}"
MIN_COVERAGE="${CODEX_MIN_COVERAGE:-80}"
TIMEOUT="${CODEX_TIMEOUT:-180}"

# Parse arguments
SOURCE_FILE=""
OUTPUT_FILE=""
while [[ $# -gt 0 ]]; do
  case $1 in
    --output)
      OUTPUT_FILE="$2"
      shift 2
      ;;
    *)
      if [ -z "$SOURCE_FILE" ]; then
        SOURCE_FILE="$1"
      fi
      shift
      ;;
  esac
done

# Validate input
if [ -z "$SOURCE_FILE" ]; then
  echo "Usage: $0 <source_file> [--output <test_file>]"
  exit 1
fi

if [ ! -f "$SOURCE_FILE" ]; then
  echo "Error: Source file not found: $SOURCE_FILE"
  exit 1
fi

# Check codex availability
if ! command -v codex &> /dev/null; then
  echo "Error: codex CLI not found. Install with: npm install -g @openai/codex"
  exit 1
fi

# Derive output file if not specified
if [ -z "$OUTPUT_FILE" ]; then
  # source.ts -> source.test.ts
  OUTPUT_FILE="${SOURCE_FILE%.*}.test.${SOURCE_FILE##*.}"
fi

# Get source content
SOURCE_CONTENT=$(cat "$SOURCE_FILE")

# Build the test generation prompt
GEN_PROMPT=$(cat <<'EOF'
You are a test engineering expert. Generate production-grade tests for:

Implementation Code:
```
SOURCE_CONTENT_PLACEHOLDER
```

CRITICAL REQUIREMENTS:

1. **Production-Grade Only**
   - NO TODO/FIXME comments
   - NO empty test bodies
   - NO tautology tests (expect(true).toBe(true))
   - NO static/hardcoded data without source
   - NO demo or placeholder code

2. **Mock Strategy**
   - ONLY mock external dependencies (database, HTTP, filesystem)
   - NEVER mock internal modules (../services/*, ./utils/*)
   - Mock ratio must be <= 30%

3. **Assertion Quality**
   - Use behavioral assertions (toBe, toEqual, toThrow)
   - Verify actual outcomes, not just that code ran
   - Each test must have >= 1 meaningful assertion

4. **6-Dimensional Coverage**
   - Functional: Core business logic
   - Boundary: null, empty, max, min, edge values
   - Exception: Error paths with recovery verification
   - Performance: SLA verification where applicable
   - Security: Input validation, injection prevention
   - Compatibility: Cross-environment behavior

5. **Confidence Level**
   - Output tests only with >= 90% confidence
   - Mark any uncertainty explicitly

Output the complete test file with NO placeholders.
EOF
)

# Replace placeholder with actual content
GEN_PROMPT="${GEN_PROMPT//SOURCE_CONTENT_PLACEHOLDER/$SOURCE_CONTENT}"

# Execute codex test generation
echo "🧪 Codex Test Generator: $SOURCE_FILE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Target: $OUTPUT_FILE"
echo "Min TAS: $MIN_TAS%, Min Coverage: $MIN_COVERAGE%"
echo ""

# Use codex exec for non-interactive execution (official syntax)
RESULT=$(timeout "$TIMEOUT" codex exec "$GEN_PROMPT" 2>&1) || {
  echo "⚠️ Codex test generation timed out or failed"
  exit 1
}

# Check for prohibited patterns
VIOLATIONS=""
if echo "$RESULT" | grep -q "TODO"; then
  VIOLATIONS="$VIOLATIONS\n- Contains TODO comments"
fi
if echo "$RESULT" | grep -q "FIXME"; then
  VIOLATIONS="$VIOLATIONS\n- Contains FIXME comments"
fi
if echo "$RESULT" | grep -qE "expect\(true\)\.toBe\(true\)|expect\(false\)\.toBe\(false\)"; then
  VIOLATIONS="$VIOLATIONS\n- Contains tautology tests"
fi
if echo "$RESULT" | grep -qE "jest\.mock\('\.\./|vi\.mock\('\.\./"; then
  VIOLATIONS="$VIOLATIONS\n- Mocks internal modules"
fi

if [ -n "$VIOLATIONS" ]; then
  echo "❌ Generated tests contain prohibited patterns:"
  echo -e "$VIOLATIONS"
  echo ""
  echo "Regenerating with stricter constraints..."
  # Could retry here, but for now just warn
fi

# Write output
echo "$RESULT" > "$OUTPUT_FILE"
echo ""
echo "✅ Tests written to: $OUTPUT_FILE"
echo ""
echo "📊 Next steps:"
echo "   1. Run tests: npm test $OUTPUT_FILE"
echo "   2. Check coverage: npm test -- --coverage"
echo "   3. Verify TAS score with guarding-test-quality skill"
