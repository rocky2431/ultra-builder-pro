#!/bin/bash
# Ultra Builder Pro 4.1 - Skill Auto-Activation Hook
# Runs on UserPromptSubmit to suggest relevant skills

cd "$(dirname "$0")"

# Run TypeScript hook (use npx to find ts-node from local node_modules)
npx ts-node skill-activation-prompt.ts
