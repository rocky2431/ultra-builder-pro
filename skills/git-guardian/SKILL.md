---
name: git-guardian
description: "Git safety and workflow enforcement. TRIGGERS when performing git operations (commit, push, branch, merge, rebase, reset), discussing git/workflow/branch strategy, or about to execute dangerous git commands. Blocks critical risks, enforces independent-branch workflow."
allowed-tools: Read, Grep
---

# Git Guardian

## Purpose

Enforces git safety and workflow across two dimensions:
1. **Git Safety** - Prevent dangerous operations (force push, hard reset)
2. **Workflow Enforcement** - Mandate independent-branch workflow

## When

**Auto-triggers when**:
- Git operations: commit, push, branch, merge, rebase, reset, delete
- Discussing git workflow, branch strategy, or merge timing
- Keywords: "force push", "rebase", "reset --hard", "unified branch", "batch merge"

**Do NOT trigger for**:
- Code quality issues (handled by quality-guardian)
- Non-git file operations

## Do

### 1. Git Safety Prevention

**Load**: `REFERENCE.md` (Git Safety Rules section) when git operations detected

**Tiered Risk Management**:

**🔴 Critical Risk** (BLOCK immediately):
- `git push --force origin main/master`
- `git reset --hard` on main/shared branches
- Deleting main/master branch

**🟡 Medium Risk** (Require confirmation):
- `git rebase` on shared branches
- `git push origin --delete <branch>`
- `git commit --amend` on pushed commits
- Force push to any remote branch

**🟢 Low Risk** (Allow with reminder):
- Normal commit/push
- Local branch operations

**Output** (Chinese):
```
🔴 危险操作检测！

命令: git push --force origin main
风险: Critical - 可能覆盖团队代码

建议:
❌ 不要强制推送到 main
✅ 推送到功能分支: git push origin feat/task-123

参考: REFERENCE.md (Git Safety Rules)
```

### 2. Workflow Enforcement

**Load**: `REFERENCE.md` (Workflow is Non-Negotiable section) when discussing workflow

**ENFORCE (mandatory)**:
```
main (always active, never frozen)
 ├── feat/task-1 (create → complete → merge → delete)
 ├── feat/task-2 (create → complete → merge → delete)
 └── feat/task-3 (create → complete → merge → delete)
```

**BLOCK immediately if**:
- Suggesting unified/long-lived feature branches
- Recommending delayed merges ("wait until all tasks complete")
- Presenting workflow "options" or "alternatives"
- Proposing to freeze main branch

**Rationale**:
- Production needs hotfix capability
- Each task independently reversible
- Main always deployable

**Output** (Chinese):
```
⚠️ 工作流违规检测！

建议: 创建统一 feat/user-auth 分支处理多任务

❌ 违反强制工作流:
- 每任务独立分支
- 完成立即合并
- main 保持可部署

✅ 正确做法:
feat/task-1 → merge → delete
feat/task-2 → merge → delete

参考: REFERENCE.md (Workflow is Non-Negotiable)
```

## Don't

- ❌ Trigger for code quality issues
- ❌ Trigger for non-git file operations
- ❌ Allow "workflow options" discussions (enforce one way)

## Outputs

**Format** (Chinese):
- Risk level emoji (🔴/🟡/🟢)
- Brief violation summary
- Specific command/proposal detected
- Actionable recommendation
- Guideline reference

**Tone**: Firm for Critical risks (block), educational for Medium/Low risks

---

**Token Efficiency**: ~150 tokens (vs 290 for 2 separate Skills). Loads git workflow guidelines on-demand.
