#!/bin/bash

# Ultra Builder Pro 4.1 - System Consistency Validation Script
# Purpose: Automated checks for documentation and configuration consistency
# Usage: bash ~/.claude/.ultra-template/scripts/validate-consistency.sh

# Don't exit on error - we want to see all checks
# set -e

CLAUDE_DIR="$HOME/.claude"
PASS_COUNT=0
FAIL_COUNT=0
WARN_COUNT=0

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=========================================="
echo "Ultra Builder Pro 4.1 Consistency Validation"
echo "=========================================="
echo ""

# Function to report pass
pass() {
    echo -e "${GREEN}✓${NC} $1"
    ((PASS_COUNT++))
}

# Function to report fail
fail() {
    echo -e "${RED}✗${NC} $1"
    ((FAIL_COUNT++))
}

# Function to report warning
warn() {
    echo -e "${YELLOW}⚠${NC} $1"
    ((WARN_COUNT++))
}

# ==========================================
# CHECK 1: Skills Count Consistency
# ==========================================
echo "CHECK 1: Skills Count Consistency"
echo "------------------------------------------"

ACTUAL_SKILLS_COUNT=$(find "$CLAUDE_DIR/skills" -maxdepth 1 -type d ! -name "skills" | wc -l | tr -d ' ')
EXPECTED_SKILLS_COUNT=10

if [ "$ACTUAL_SKILLS_COUNT" -eq "$EXPECTED_SKILLS_COUNT" ]; then
    pass "Skills count matches: $ACTUAL_SKILLS_COUNT skills found"
else
    fail "Skills count mismatch: expected $EXPECTED_SKILLS_COUNT, found $ACTUAL_SKILLS_COUNT"
fi

# Verify all skills follow gerund naming convention
echo "  Checking naming conventions..."
NON_GERUND_SKILLS=$(find "$CLAUDE_DIR/skills" -maxdepth 1 -type d ! -name "skills" -exec basename {} \; | grep -v -E "(ing|routing)-" || true)
if [ -z "$NON_GERUND_SKILLS" ]; then
    pass "All skills follow gerund naming convention"
else
    fail "Non-gerund skills found: $NON_GERUND_SKILLS"
fi

echo ""

# ==========================================
# CHECK 2: Commands Count Consistency
# ==========================================
echo "CHECK 2: Commands Count Consistency"
echo "------------------------------------------"

ACTUAL_COMMANDS_COUNT=$(find "$CLAUDE_DIR/commands" -maxdepth 1 -name "ultra-*.md" | wc -l | tr -d ' ')
EXPECTED_COMMANDS_COUNT=10

if [ "$ACTUAL_COMMANDS_COUNT" -eq "$EXPECTED_COMMANDS_COUNT" ]; then
    pass "Commands count matches: $ACTUAL_COMMANDS_COUNT commands found"
else
    fail "Commands count mismatch: expected $EXPECTED_COMMANDS_COUNT, found $ACTUAL_COMMANDS_COUNT"
fi

# Verify all commands have ultra- prefix
echo "  Checking naming conventions..."
NON_ULTRA_COMMANDS=$(find "$CLAUDE_DIR/commands" -maxdepth 1 -name "*.md" ! -name "ultra-*.md" | wc -l | tr -d ' ')
if [ "$NON_ULTRA_COMMANDS" -eq 0 ]; then
    pass "All commands follow ultra- prefix convention"
else
    warn "$NON_ULTRA_COMMANDS commands without ultra- prefix found"
fi

echo ""

# ==========================================
# CHECK 3: @import Reference Integrity
# ==========================================
echo "CHECK 3: @import Reference Integrity"
echo "------------------------------------------"

BROKEN_IMPORTS=0

# Extract all @import references from CLAUDE.md
IMPORTS=$(grep -o '@[a-zA-Z0-9_/-]*\.md' "$CLAUDE_DIR/CLAUDE.md" | sed 's/@//' || true)

if [ -z "$IMPORTS" ]; then
    warn "No @import references found in CLAUDE.md"
else
    for IMPORT in $IMPORTS; do
        if [ -f "$CLAUDE_DIR/$IMPORT" ]; then
            pass "  ✓ $IMPORT exists"
        else
            fail "  ✗ $IMPORT missing"
            ((BROKEN_IMPORTS++))
        fi
    done

    if [ "$BROKEN_IMPORTS" -eq 0 ]; then
        pass "All @import references valid"
    else
        fail "$BROKEN_IMPORTS broken @import references found"
    fi
fi

echo ""

# ==========================================
# CHECK 4: Configuration File Existence
# ==========================================
echo "CHECK 4: Configuration File Existence"
echo "------------------------------------------"

CONFIG_FILE="$CLAUDE_DIR/.ultra-template/config.json"
if [ -f "$CONFIG_FILE" ]; then
    pass "Template config.json exists"

    # Validate JSON syntax
    if python3 -m json.tool "$CONFIG_FILE" > /dev/null 2>&1; then
        pass "config.json has valid JSON syntax"
    else
        fail "config.json has invalid JSON syntax"
    fi
else
    fail "Template config.json missing at $CONFIG_FILE"
fi

echo ""

# ==========================================
# CHECK 5: Config Values Match Documentation
# ==========================================
echo "CHECK 5: Config Values Match Documentation"
echo "------------------------------------------"

if [ -f "$CONFIG_FILE" ]; then
    # Check context thresholds
    CONTEXT_GREEN=$(python3 -c "import json; print(json.load(open('$CONFIG_FILE'))['context']['thresholds']['green'])" 2>/dev/null || echo "ERROR")
    if [ "$CONTEXT_GREEN" = "0.6" ] || [ "$CONTEXT_GREEN" = "0.60" ]; then
        pass "Context green threshold matches (0.60)"
    elif [ "$CONTEXT_GREEN" = "ERROR" ]; then
        fail "Unable to read context.thresholds.green from config"
    else
        warn "Context green threshold value: $CONTEXT_GREEN (expected 0.60)"
    fi

    # Check file routing thresholds
    FILE_MEDIUM=$(python3 -c "import json; print(json.load(open('$CONFIG_FILE'))['file_routing']['thresholds']['medium'])" 2>/dev/null || echo "ERROR")
    if [ "$FILE_MEDIUM" = "5000" ]; then
        pass "File routing medium threshold matches (5000)"
    elif [ "$FILE_MEDIUM" = "ERROR" ]; then
        fail "Unable to read file_routing.thresholds.medium from config"
    else
        warn "File routing medium threshold value: $FILE_MEDIUM (expected 5000)"
    fi

    # Check code quality thresholds
    MAX_FUNCTION_LINES=$(python3 -c "import json; print(json.load(open('$CONFIG_FILE'))['quality_gates']['code_quality']['max_function_lines'])" 2>/dev/null || echo "ERROR")
    if [ "$MAX_FUNCTION_LINES" = "50" ]; then
        pass "Code quality max_function_lines matches (50)"
    elif [ "$MAX_FUNCTION_LINES" = "ERROR" ]; then
        fail "Unable to read quality_gates.code_quality.max_function_lines from config"
    else
        warn "Code quality max_function_lines value: $MAX_FUNCTION_LINES (expected 50)"
    fi

    # Check test coverage thresholds
    OVERALL_COVERAGE=$(python3 -c "import json; print(json.load(open('$CONFIG_FILE'))['quality_gates']['test_coverage']['overall'])" 2>/dev/null || echo "ERROR")
    if [ "$OVERALL_COVERAGE" = "0.8" ] || [ "$OVERALL_COVERAGE" = "0.80" ]; then
        pass "Test coverage overall threshold matches (0.80)"
    elif [ "$OVERALL_COVERAGE" = "ERROR" ]; then
        fail "Unable to read quality_gates.test_coverage.overall from config"
    else
        warn "Test coverage overall threshold value: $OVERALL_COVERAGE (expected 0.80)"
    fi
else
    fail "Cannot validate config values: config.json missing"
fi

echo ""

# ==========================================
# CHECK 6: Chinese Hardcoding Detection
# ==========================================
echo "CHECK 6: Chinese Hardcoding Detection"
echo "------------------------------------------"

# Search for Chinese characters in system files (excluding user messages)
CHINESE_IN_SKILLS=$(grep -r -l '[\u4e00-\u9fff]' "$CLAUDE_DIR/skills/"*/SKILL.md 2>/dev/null | wc -l | tr -d ' ')
CHINESE_IN_COMMANDS=$(grep -r -l '[\u4e00-\u9fff]' "$CLAUDE_DIR/commands/" 2>/dev/null | wc -l | tr -d ' ')
CHINESE_IN_GUIDELINES=$(grep -r -l '[\u4e00-\u9fff]' "$CLAUDE_DIR/guidelines/" 2>/dev/null | wc -l | tr -d ' ')

TOTAL_CHINESE_FILES=$((CHINESE_IN_SKILLS + CHINESE_IN_COMMANDS + CHINESE_IN_GUIDELINES))

if [ "$TOTAL_CHINESE_FILES" -eq 0 ]; then
    pass "No Chinese hardcoding detected in system files"
else
    fail "Chinese characters detected in $TOTAL_CHINESE_FILES files"
    echo "  Skills: $CHINESE_IN_SKILLS files, Commands: $CHINESE_IN_COMMANDS files, Guidelines: $CHINESE_IN_GUIDELINES files"
fi

echo ""

# ==========================================
# CHECK 7: OUTPUT Directive Presence
# ==========================================
echo "CHECK 7: OUTPUT Directive Presence"
echo "------------------------------------------"

# Count all reference files (REFERENCE.md + reference/*.md) that should have OUTPUT directives
REFERENCE_MD_FILES=$(find "$CLAUDE_DIR/skills" -name "REFERENCE.md" | wc -l | tr -d ' ')
REFERENCE_DIR_FILES=$(find "$CLAUDE_DIR/skills" -path "*/reference/*.md" 2>/dev/null | wc -l | tr -d ' ')
TOTAL_REFERENCE_FILES=$((REFERENCE_MD_FILES + REFERENCE_DIR_FILES))

# Count files with OUTPUT directives
REFERENCE_MD_WITH_OUTPUT=$(find "$CLAUDE_DIR/skills" -name "REFERENCE.md" -exec grep -l "OUTPUT.*Chinese" {} \; 2>/dev/null | wc -l | tr -d ' ')
REFERENCE_DIR_WITH_OUTPUT=$(find "$CLAUDE_DIR/skills" -path "*/reference/*.md" -exec grep -l "OUTPUT.*Chinese" {} \; 2>/dev/null | wc -l | tr -d ' ')
TOTAL_WITH_OUTPUT=$((REFERENCE_MD_WITH_OUTPUT + REFERENCE_DIR_WITH_OUTPUT))

if [ "$TOTAL_REFERENCE_FILES" -eq 0 ]; then
    warn "No reference files found"
elif [ "$TOTAL_REFERENCE_FILES" -eq "$TOTAL_WITH_OUTPUT" ]; then
    pass "All $TOTAL_REFERENCE_FILES reference files have OUTPUT directives"
else
    MISSING=$((TOTAL_REFERENCE_FILES - TOTAL_WITH_OUTPUT))
    warn "$MISSING of $TOTAL_REFERENCE_FILES reference files missing OUTPUT directives"
fi

echo ""

# ==========================================
# SUMMARY
# ==========================================
echo "=========================================="
echo "VALIDATION SUMMARY"
echo "=========================================="
echo -e "${GREEN}Passed:${NC}  $PASS_COUNT"
echo -e "${YELLOW}Warnings:${NC} $WARN_COUNT"
echo -e "${RED}Failed:${NC}  $FAIL_COUNT"
echo ""

if [ "$FAIL_COUNT" -eq 0 ]; then
    echo -e "${GREEN}✓ All critical checks passed!${NC}"
    exit 0
else
    echo -e "${RED}✗ $FAIL_COUNT critical issues found${NC}"
    exit 1
fi
