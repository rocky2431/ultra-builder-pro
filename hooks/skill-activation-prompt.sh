#!/bin/bash
# Ultra Builder Pro 4.3.3 - Skill Auto-Activation Hook
# Runs on UserPromptSubmit to suggest relevant skills

cd "$(dirname "$0")"

# Read JSON input from stdin
INPUT_JSON=$(cat)

# Extract prompt from JSON using jq
USER_PROMPT=$(echo "$INPUT_JSON" | jq -r '.prompt // empty' 2>/dev/null)

# Debug logging (uncomment to enable)
# echo "[DEBUG $(date '+%H:%M:%S')] DIR=$CLAUDE_PROJECT_DIR" >> /tmp/skill-hook-debug.log
# echo "[DEBUG $(date '+%H:%M:%S')] PROMPT=$USER_PROMPT" >> /tmp/skill-hook-debug.log

# Exit if no prompt
if [ -z "$USER_PROMPT" ]; then
  exit 0
fi

# Export for TypeScript
export CLAUDE_USER_PROMPT="$USER_PROMPT"

# Fallback: If CLAUDE_PROJECT_DIR is not set, try to detect it
if [ -z "$CLAUDE_PROJECT_DIR" ]; then
  # Check if we're in a project with .claude directory
  if [ -d "$PWD/.claude" ]; then
    export CLAUDE_PROJECT_DIR="$PWD"
  elif [ -d "$HOME/.claude" ]; then
    export CLAUDE_PROJECT_DIR="$HOME/.claude"
  fi
fi

# Run TypeScript hook (use npx to find ts-node from local node_modules)
npx ts-node skill-activation-prompt.ts 2>/dev/null
