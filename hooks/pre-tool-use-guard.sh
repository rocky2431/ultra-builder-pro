#!/bin/bash
# Ultra Builder Pro 4.3.3 - PreToolUse Guard Hook
# Intercepts dangerous operations before execution
# Protects against: force push, hard reset, clean -fd, etc.

set -e

# Tool information from Claude Code
TOOL_NAME="${CLAUDE_TOOL_NAME:-}"
TOOL_INPUT="${CLAUDE_TOOL_INPUT:-}"

# Only guard Bash tool
if [ "$TOOL_NAME" != "Bash" ]; then
  exit 0
fi

# Extract command from tool input
COMMAND=$(echo "$TOOL_INPUT" | jq -r '.command // empty' 2>/dev/null)

if [ -z "$COMMAND" ]; then
  # Fallback to sed extraction
  COMMAND=$(echo "$TOOL_INPUT" | sed -n 's/.*"command"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | head -1)
fi

if [ -z "$COMMAND" ]; then
  exit 0
fi

# ============================================
# Dangerous Git Commands Detection
# ============================================

DANGEROUS_PATTERNS=(
  # Force push (can lose remote history)
  "git push.*--force"
  "git push.*-f[^a-z]"
  "git push -f$"

  # Hard reset (can lose local changes)
  "git reset --hard"

  # Force clean (can delete untracked files permanently)
  "git clean.*-fd"
  "git clean.*-f.*-d"

  # Checkout discard all (can lose all uncommitted changes)
  "git checkout -- \."
  "git checkout \."

  # Interactive rebase (not supported in non-interactive mode)
  "git rebase -i"
  "git rebase --interactive"

  # Force delete branch
  "git branch -D"

  # Reflog expire (can lose recovery options)
  "git reflog expire"

  # GC prune (can permanently delete objects)
  "git gc --prune"

  # Filter-branch (rewrites history)
  "git filter-branch"
)

# Protected branches - extra warning for these
PROTECTED_BRANCHES="main|master|develop|release"

# Check for dangerous patterns
for pattern in "${DANGEROUS_PATTERNS[@]}"; do
  if echo "$COMMAND" | grep -qE "$pattern"; then

    # Special handling for force push to protected branches
    if echo "$pattern" | grep -q "push.*force\|push.*-f"; then
      if echo "$COMMAND" | grep -qE "($PROTECTED_BRANCHES)"; then
        cat <<EOF

🚨 CRITICAL: Force Push to Protected Branch Blocked

**Command**: $COMMAND
**Risk**: Force pushing to main/master/develop can cause:
  - Loss of commit history for all collaborators
  - CI/CD pipeline breaks
  - Merge conflicts for entire team

**guarding-git-workflow enforcement**: This operation requires explicit user confirmation.

**If you really need this**, ask the user to:
1. Confirm they understand the consequences
2. Notify team members before proceeding
3. Consider using \`--force-with-lease\` instead

EOF
        exit 2  # Block execution
      fi
    fi

    # Standard dangerous command warning
    cat <<EOF

⚠️ DANGEROUS GIT COMMAND DETECTED

**Command**: $COMMAND
**Pattern Matched**: $pattern

**Potential Risks**:
- Data loss that may be unrecoverable
- History rewriting affecting collaborators
- Unintended file deletions

**guarding-git-workflow suggests**:
- Ensure you have a backup or stash
- Confirm this is the intended operation
- Consider safer alternatives

**Proceeding with caution...**

EOF
    # Exit 0 to allow but warn (exit 2 would block)
    exit 0
  fi
done

# ============================================
# Sensitive File Access Detection
# ============================================

SENSITIVE_PATTERNS=(
  "\.env"
  "credentials"
  "secret"
  "password"
  "\.pem$"
  "\.key$"
  "id_rsa"
  "\.p12$"
)

for pattern in "${SENSITIVE_PATTERNS[@]}"; do
  if echo "$COMMAND" | grep -qiE "$pattern"; then
    cat <<EOF

🔐 SENSITIVE FILE ACCESS DETECTED

**Command**: $COMMAND
**Pattern**: $pattern

**Reminder**: Be cautious with sensitive files.
- Never commit credentials to git
- Use environment variables for secrets
- Check .gitignore includes sensitive patterns

EOF
    exit 0
  fi
done

# ============================================
# Destructive Commands Detection
# ============================================

DESTRUCTIVE_PATTERNS=(
  "rm -rf /"
  "rm -rf \*"
  "rm -rf ~"
  "rm -rf \$HOME"
  "> /dev/sda"
  "mkfs\."
  "dd if=.*/dev/"
)

for pattern in "${DESTRUCTIVE_PATTERNS[@]}"; do
  if echo "$COMMAND" | grep -qE "$pattern"; then
    cat <<EOF

🛑 DESTRUCTIVE COMMAND BLOCKED

**Command**: $COMMAND
**Reason**: This command could cause system-wide damage.

**Action**: Command execution blocked for safety.

EOF
    exit 2  # Block execution
  fi
done

# All checks passed
exit 0
