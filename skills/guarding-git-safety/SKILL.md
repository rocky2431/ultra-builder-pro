---
name: guarding-git-safety
description: "Prevents dangerous git operations causing data loss. TRIGGERS: Detecting 'git push --force', 'git reset --hard', 'git rebase -i', 'git clean -fd', 'rm -rf .git' commands or discussing force operations on main/master branches. ACTIONS: Display risk warning, require explicit confirmation, suggest safe alternatives. DO NOT TRIGGER: For normal git add/commit/push, branch operations on feature branches, git status/log/diff."
allowed-tools: Bash
---

# Git Workflow Guardian

## Auto-Trigger Conditions

**Dangerous Command Detection**:
- `git push --force` - Force push
- `git reset --hard` - Hard reset
- `git rebase -i` - Interactive rebase
- `git clean -fd` - Clean untracked files
- `rm -rf .git` - Delete repository

**Smart Reminders**:
- Before commit: Check staging area
- Before push: Check unpushed commits
- Before merge: Check conflicts

## Protection Workflow (Tiered Risk Management)

### 🔴 Critical Risk Operations - ALWAYS Require Confirmation
When detecting these commands:
- `git push --force origin main` (or master/develop)
- `git push --force` to protected branches
- `git push origin --delete <branch>` when branch not merged

Action:
1. Display confirmation prompt (in Chinese)
2. Explain risks and suggest safe alternatives
3. Require explicit "continue" confirmation
4. Proceed only after user confirms

### 🟡 Medium Risk Operations - Auto-Execute with Safety Checks
When detecting these commands on **feature branches**:
- `git reset --hard` (check: not on main/master)
- `git rebase` (check: single author only)
- `git push origin --delete <branch>` (check: already merged)

Action:
1. Verify safety conditions automatically
2. If safe: Execute immediately, show summary
3. If unsafe: Require confirmation (treat as Critical Risk)

### 🟢 Low Risk Operations - Always Auto-Execute
These commands never require confirmation:
- `git add`, `git commit`, `git push` to feature branches
- `git stash`, `git checkout`, `git diff`, `git log`
- Create new branches, delete local branches

## Output Format

- Language: **Chinese (simplified)** at runtime
- Provide: Risk level, affected scope, safe alternatives
- Require: Explicit confirmation keyword

## Related Documentation

**Git workflow standards**: See `REFERENCE.md` for:
- Branch naming conventions
- Commit message standards
- Safe git operations
- Recovery procedures
