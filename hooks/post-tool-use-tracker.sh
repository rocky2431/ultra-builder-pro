#!/bin/bash
# Ultra Builder Pro 4.1 - Post Tool Use Tracker
# Tracks file changes for context-aware skill activation

# Get project directory
PROJECT_DIR="${CLAUDE_PROJECT_DIR:-.}"
# If PROJECT_DIR already ends with .claude, don't add it again
if [[ "$PROJECT_DIR" == */.claude ]]; then
  CACHE_DIR="$PROJECT_DIR/cache"
else
  CACHE_DIR="$PROJECT_DIR/.claude/cache"
fi
RECENT_FILES="$CACHE_DIR/recent-files.json"

# Create cache directory if it doesn't exist
mkdir -p "$CACHE_DIR"

# Extract tool name and file path from tool result
# CLAUDE_TOOL_NAME and CLAUDE_TOOL_RESULT are provided by Claude Code
TOOL_NAME="${CLAUDE_TOOL_NAME:-}"
TOOL_RESULT="${CLAUDE_TOOL_RESULT:-}"

# Only track Edit, Write, and MultiEdit tools
if [[ "$TOOL_NAME" =~ ^(Edit|Write|MultiEdit)$ ]]; then
  # Try to extract file_path from JSON result using jq
  MODIFIED_FILE=$(echo "$TOOL_RESULT" | jq -r '.file_path // .path // empty' 2>/dev/null)

  # If jq didn't work or returned empty, try sed (macOS compatible)
  if [ -z "$MODIFIED_FILE" ]; then
    # Extract file_path using sed (works on both macOS and Linux)
    MODIFIED_FILE=$(echo "$TOOL_RESULT" | sed -n 's/.*"file_path"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | head -1)
  fi

  if [ -n "$MODIFIED_FILE" ]; then
    # Initialize or read existing cache
    if [ -f "$RECENT_FILES" ]; then
      CURRENT=$(cat "$RECENT_FILES")
    else
      CURRENT="[]"
    fi

    # Add file with timestamp
    TIMESTAMP=$(date +%s)
    NEW_ENTRY=$(jq -n \
      --arg file "$MODIFIED_FILE" \
      --arg time "$TIMESTAMP" \
      --arg tool "$TOOL_NAME" \
      '{file: $file, timestamp: $time, tool: $tool}')

    # Append and keep last 20 files
    echo "$CURRENT" | jq \
      --argjson entry "$NEW_ENTRY" \
      '. += [$entry] | .[-20:]' \
      > "$RECENT_FILES" 2>/dev/null

    # Optional: Log for debugging (commented out by default)
    # echo "Tracked: $TOOL_NAME -> $MODIFIED_FILE" >> "$CACHE_DIR/tracker.log"
  fi
fi

# Always exit successfully to not block workflow
exit 0
