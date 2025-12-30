#!/bin/bash
# Ultra Builder Pro 4.3.3 - SessionStart Initialization Hook
# Loads project context and displays session information at startup

# Get directories
PROJECT_DIR="${CLAUDE_PROJECT_DIR:-.}"
HOME_DIR="${HOME:-/Users/rocky243}"

# Determine .claude directory
if [[ "$PROJECT_DIR" == */.claude ]]; then
  CLAUDE_DIR="$PROJECT_DIR"
else
  CLAUDE_DIR="$PROJECT_DIR/.claude"
fi

# Global .claude directory
GLOBAL_CLAUDE_DIR="$HOME_DIR/.claude"

# Cache and logs directories
CACHE_DIR="$CLAUDE_DIR/cache"
LOGS_DIR="$CLAUDE_DIR/logs"

# Create directories if needed
mkdir -p "$CACHE_DIR" "$LOGS_DIR" 2>/dev/null

# ============================================
# Session Logging
# ============================================

SESSION_LOG="$LOGS_DIR/sessions.log"
SESSION_ID=$(date +%Y%m%d-%H%M%S)
echo "[$SESSION_ID] Session started at $(date -Iseconds)" >> "$SESSION_LOG" 2>/dev/null

# ============================================
# Clear Stale Cache
# ============================================

# Clean old recent-files cache (older than 24 hours)
RECENT_FILES="$CACHE_DIR/recent-files.json"
if [ -f "$RECENT_FILES" ]; then
  # Check file age (macOS compatible)
  FILE_AGE=$(($(date +%s) - $(stat -f %m "$RECENT_FILES" 2>/dev/null || echo 0)))
  if [ "$FILE_AGE" -gt 86400 ]; then
    rm -f "$RECENT_FILES"
  fi
fi

# Clean old review queue
REVIEW_QUEUE="$CACHE_DIR/codex-review-pending.json"
if [ -f "$REVIEW_QUEUE" ]; then
  FILE_AGE=$(($(date +%s) - $(stat -f %m "$REVIEW_QUEUE" 2>/dev/null || echo 0)))
  if [ "$FILE_AGE" -gt 86400 ]; then
    rm -f "$REVIEW_QUEUE"
  fi
fi

# ============================================
# Project Detection
# ============================================

PROJECT_NAME=""
PROJECT_TYPE=""
HAS_LOCAL_CONFIG=false

# Check for project-level .claude
if [ -d "$CLAUDE_DIR" ] && [ "$CLAUDE_DIR" != "$GLOBAL_CLAUDE_DIR" ]; then
  HAS_LOCAL_CONFIG=true
  PROJECT_NAME=$(basename "$(dirname "$CLAUDE_DIR")")
fi

# Detect project type from files
detect_project_type() {
  local dir="$1"

  if [ -f "$dir/package.json" ]; then
    # Check for specific frameworks
    if grep -q '"next"' "$dir/package.json" 2>/dev/null; then
      echo "Next.js"
    elif grep -q '"vue"' "$dir/package.json" 2>/dev/null; then
      echo "Vue"
    elif grep -q '"react"' "$dir/package.json" 2>/dev/null; then
      echo "React"
    else
      echo "Node.js"
    fi
  elif [ -f "$dir/Cargo.toml" ]; then
    echo "Rust"
  elif [ -f "$dir/go.mod" ]; then
    echo "Go"
  elif [ -f "$dir/requirements.txt" ] || [ -f "$dir/pyproject.toml" ]; then
    echo "Python"
  elif [ -f "$dir/foundry.toml" ] || [ -d "$dir/contracts" ]; then
    echo "Smart Contract"
  else
    echo "Unknown"
  fi
}

if [ "$PROJECT_DIR" != "." ] && [ "$PROJECT_DIR" != "$HOME_DIR/.claude" ]; then
  PROJECT_TYPE=$(detect_project_type "$PROJECT_DIR")
fi

# ============================================
# Load Task Status
# ============================================

TASKS_FILE="$CLAUDE_DIR/../.ultra/tasks/tasks.json"
PENDING_TASKS=0
IN_PROGRESS_TASKS=0

if [ -f "$TASKS_FILE" ]; then
  PENDING_TASKS=$(jq '[.tasks[] | select(.status == "pending")] | length' "$TASKS_FILE" 2>/dev/null || echo 0)
  IN_PROGRESS_TASKS=$(jq '[.tasks[] | select(.status == "in_progress")] | length' "$TASKS_FILE" 2>/dev/null || echo 0)
fi

# ============================================
# Check for Previous Session Context
# ============================================

# Look for recent session files
RECENT_SESSION=""
if [ -d "$LOGS_DIR" ]; then
  RECENT_SESSION=$(ls -t "$LOGS_DIR"/session-*.md 2>/dev/null | head -1)
fi

# ============================================
# Output Session Context
# ============================================

cat <<EOF

# [hooks] recent context

EOF

# Show previous session summary if exists
if [ -n "$RECENT_SESSION" ] && [ -f "$RECENT_SESSION" ]; then
  echo "📋 **Previous Session**: $(basename "$RECENT_SESSION")"
  # Show last 5 lines of previous session
  echo ""
  tail -10 "$RECENT_SESSION" 2>/dev/null | head -5
  echo ""
  echo "---"
  echo ""
fi

# Show project info if in a project
if [ -n "$PROJECT_NAME" ] && [ "$PROJECT_NAME" != ".claude" ]; then
  cat <<EOF
📁 **Project**: $PROJECT_NAME
🔧 **Type**: $PROJECT_TYPE
📍 **Config**: $([ "$HAS_LOCAL_CONFIG" = true ] && echo "Project-level" || echo "Global")

EOF
fi

# Show pending tasks if any
if [ "$PENDING_TASKS" -gt 0 ] || [ "$IN_PROGRESS_TASKS" -gt 0 ]; then
  cat <<EOF
📊 **Tasks**:
  - In Progress: $IN_PROGRESS_TASKS
  - Pending: $PENDING_TASKS

EOF
fi

# Check for recent errors
ERROR_HISTORY="$CACHE_DIR/error-history.json"
if [ -f "$ERROR_HISTORY" ]; then
  RECENT_ERRORS=$(jq 'length' "$ERROR_HISTORY" 2>/dev/null || echo 0)
  if [ "$RECENT_ERRORS" -gt 3 ]; then
    cat <<EOF
⚠️ **Notice**: $RECENT_ERRORS recent errors in cache. Consider reviewing.

EOF
  fi
fi

# Default message if no context
if [ -z "$PROJECT_NAME" ] && [ "$PENDING_TASKS" -eq 0 ]; then
  echo "No previous sessions found for this project yet."
fi

# Always exit successfully
exit 0
