# Git Workflow - Complete Guide

**Ultra Builder Pro 4.0** - Git workflow standards for version control and collaboration.

---

## ⚠️ CRITICAL: Workflow is Non-Negotiable

**THERE IS ONLY ONE WORKFLOW - Independent Task Branches**

```
main (always active, never frozen)
 ├── feat/task-1-xxx (create → complete → merge → delete)
 ├── feat/task-2-yyy (create → complete → merge → delete)
 └── feat/task-3-zzz (create → complete → merge → delete)
```

**FORBIDDEN**: Unified/long-lived feature branches, freezing main, delaying merges, any "Option 1 vs Option 2"

**WHY**: Production projects MUST keep main branch deployable. Hotfixes cannot wait for 31 tasks to complete. Each task is independently reversible.

---

## Branch Naming Conventions

**Standard patterns**:
- `feat/task-{id}-{description}` - Example: `feat/task-12-user-authentication`
- `fix/bug-{id}-{description}` - Example: `fix/bug-34-memory-leak`
- `refactor/{description}` - Example: `refactor/extract-validation-logic`
- `docs/{description}` - Example: `docs/update-api-reference`
- `test/{description}` - Example: `test/add-integration-tests`

**Rules**: Lowercase, hyphens (kebab-case), 3-5 words, include task/bug ID when available

---

## Commit Format (Conventional Commits)

### Format
```
<type>: <description>

[optional body]
[optional footer]
```

### Types

| Type | Description | Example |
|------|-------------|---------|
| **feat** | New feature | `feat: add user authentication with JWT` |
| **fix** | Bug fix | `fix: resolve memory leak in data processing` |
| **docs** | Documentation | `docs: update API documentation for v2.0` |
| **style** | Code style (formatting, no logic change) | `style: fix indentation in auth module` |
| **refactor** | Code refactoring (no feature/bug change) | `refactor: extract validation logic` |
| **perf** | Performance improvements | `perf: optimize database query with indexing` |
| **test** | Adding/updating tests | `test: add boundary tests for user registration` |
| **chore** | Maintenance tasks | `chore: upgrade React to v18` |

### Guidelines

**Subject line**:
- ✅ Start with lowercase type
- ✅ Use imperative mood ("add" not "added")
- ✅ No period at end
- ✅ Keep under 50 characters

**Body** (optional): Explain what and why, not how. Wrap at 72 characters.

**Footer** (optional): Reference issues (`Closes #123`), breaking changes (`BREAKING CHANGE: description`)

### Examples

**Simple**:
```
feat: add password reset functionality
```

**With body and footer**:
```
fix: resolve race condition in authentication

Added mutex lock to ensure atomic token refresh operations.

Fixes #234
```

---

## Git Safety Rules

### Tiered Risk Management

**Philosophy**: Balance safety with automation following Claude 4.x Best Practices: "Deliberately conservative approach **to prioritize safety**" - only for **truly dangerous** operations.

#### **🔴 Critical Risk - ALWAYS Require Confirmation**

1. **Force push to main/master**: `git push --force origin main` - ALWAYS ask user first
2. **Force push to protected branches**: Any branch with protection rules
3. **Delete unmerged branch**: Branch not merged to main - Confirm before deletion

**Rationale**: These operations can cause permanent data loss or affect team members.

#### **🟡 Medium Risk - Auto-Execute with Safety Checks**

4. **Hard reset on feature branch**: Auto-execute if current branch is not main/master and not shared
5. **Delete merged remote branch**: Auto-delete if already merged to main
6. **Rebase feature branch**: Auto-execute if branch has single author only

**Auto-execution logic**:
```bash
# Check if branch is merged (safe to delete)
git branch -r --merged main | grep "origin/$BRANCH"
  → If matched: Auto-delete (already in main)
  → If not matched: Require confirmation

# Check if branch is shared (safe to rebase)
git log origin/$BRANCH --format="%an" | sort -u | wc -l
  → If = 1: Auto-rebase (single author)
  → If > 1: Require confirmation (multiple contributors)

# Check if current branch is feature branch (safe to reset)
git branch --show-current | grep -vE "^(main|master|develop|release/.*)$"
  → If matched: Auto-reset (feature branch)
  → If not matched: Require confirmation (protected branch)
```

**Rationale**: "Implement changes rather than only suggesting" when operation is safe and reversible.

#### **🟢 Low Risk - Always Auto-Execute**

- ✅ Git add, commit, push to feature branches
- ✅ Create new branches
- ✅ Git stash, checkout, diff, log
- ✅ Delete local branches (easily recoverable)

### Standard Practices

- ✅ Always pull before push
- ✅ Review changes with `git diff` and `git status`
- ✅ Use `git stash` for incomplete work when switching branches
- ✅ Create backup branch before risky operations: `git branch backup-$(date +%Y%m%d-%H%M%S)`

---

## Common Git Workflows

### Feature Development
```bash
git checkout -b feat/task-123-new-feature
git add src/feature.ts
git commit -m "feat: implement basic feature logic"
git fetch origin && git rebase origin/main
git push origin feat/task-123-new-feature
# Create PR, merge, then:
git checkout main && git pull origin main
git branch -d feat/task-123-new-feature
```

### Bug Fix
```bash
git checkout main && git pull origin main
git checkout -b fix/bug-456-memory-leak
git add src/memory-management.ts
git commit -m "fix: resolve memory leak in cache cleanup"
git add tests/memory-management.test.ts
git commit -m "test: add test for memory leak prevention"
git push origin fix/bug-456-memory-leak
# After merge, backport if needed:
git checkout release/v1.0
git cherry-pick <commit-hash>
git push origin release/v1.0
```

### Hotfix (Production Emergency)
```bash
git checkout -b hotfix/critical-security-fix v1.2.3
git add src/security.ts
git commit -m "fix: patch SQL injection vulnerability"
npm test
git checkout main && git merge --no-ff hotfix/critical-security-fix && git push origin main
git checkout release/v1.2 && git merge --no-ff hotfix/critical-security-fix && git push origin release/v1.2
git tag v1.2.4 && git push origin v1.2.4
git branch -d hotfix/critical-security-fix
```

---

## Git Configuration

### User Configuration
```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
git config --global init.defaultBranch main
git config --global color.ui auto
git config --global core.editor "code --wait"
git config --global core.autocrlf input  # macOS/Linux
git config --global core.autocrlf true   # Windows
```

### Useful Aliases
```bash
git config --global alias.st status
git config --global alias.co checkout
git config --global alias.br branch
git config --global alias.lg "log --graph --pretty=format:'%Cred%h%Creset -%C(yellow)%d%Creset %s %Cgreen(%cr) %C(bold blue)<%an>%Creset' --abbrev-commit"
git config --global alias.last "log -1 HEAD"
git config --global alias.undo "reset HEAD~1 --soft"
git config --global alias.amend "commit --amend --no-edit"
```

---

## Best Practices Checklist

### Before Committing
- [ ] Run linter and tests
- [ ] Review changes with `git diff`
- [ ] Verify no sensitive data (API keys, passwords)
- [ ] Ensure commit message follows convention

### Before Pushing
- [ ] Pull latest changes from remote
- [ ] Resolve conflicts
- [ ] Run full test suite
- [ ] Verify branch name follows convention

### Before Merging
- [ ] Code review completed and approved
- [ ] All CI/CD checks passing
- [ ] Test coverage ≥80%
- [ ] Documentation updated if needed

---

## Troubleshooting

**Accidentally committed to wrong branch**:
```bash
git log  # Find commit hash
git checkout correct-branch && git cherry-pick <commit-hash>
git checkout wrong-branch && git reset --hard HEAD~1
```

**Undo last commit** (keep changes):
```bash
git reset --soft HEAD~1
```

**Merge conflict**:
```bash
git status  # See conflicted files
# Edit files to resolve conflicts (look for <<<<<<< HEAD markers)
git add conflicted-file.ts
git commit -m "fix: resolve merge conflict"
```

---

## Git Hooks

Git hooks enforced by **guarding-git-workflow** skill:
- **Pre-commit**: Run linter, quick tests, check sensitive data
- **Pre-push**: Run full test suite, check coverage, verify no direct push to main

---

**Remember**: Git is your safety net. Use it wisely and never fear experimenting—everything is recoverable.
