---
name: guarding-git-workflow
description: "Ensures safe git operations and consistent branch workflow. Activates during git commands (commit, push, merge, rebase, reset), branch strategy discussions, or workflow planning."
allowed-tools: Read, Grep
---

# Git Workflow Guardian

Maintains git safety and workflow consistency for production-grade development.

## Activation Context

This skill activates during:
- Git operations: commit, push, branch, merge, rebase, reset
- Branch strategy or workflow discussions
- Merge timing decisions

## Safe Git Workflow

### Branch Lifecycle

Each task follows this pattern:

```
main (always deployable)
 ├── feat/task-1 → complete → merge → delete
 ├── feat/task-2 → complete → merge → delete
 └── feat/task-3 → complete → merge → delete
```

**Why this works:**
- Main stays deployable for hotfixes
- Each task independently reversible
- Clean git history

### Operation Risk Levels

**High-risk operations** require user confirmation before proceeding:

| Operation | Risk | User Confirmation Required |
|-----------|------|---------------------------|
| `git push --force origin main` | Data loss on shared branch | Yes - explain impact first |
| `git reset --hard` on main | Loses uncommitted work | Yes - suggest stash alternative |
| `git rebase` on pushed branch | Rewrites shared history | Yes - explain downstream impact |
| Deleting remote branches | Permanent removal | Yes - confirm branch name |

**Standard operations** proceed with helpful context:

| Operation | Guidance |
|-----------|----------|
| Normal commit/push | Confirm conventional commit format |
| Local branch creation | Suggest naming: `feat/task-{id}-{slug}` |
| Merge to main | Remind: delete branch after merge |

### Example Interaction

When user requests `git push --force origin main`:

```
这个操作会重写 main 分支的共享历史记录，可能影响其他开发者的工作。

建议替代方案：
1. 使用 `git push --force-with-lease` (更安全的强制推送)
2. 创建新分支保存当前更改
3. 与团队沟通后再执行

是否继续执行强制推送？
```

## Workflow Guidance

When discussing branch strategies, guide toward independent branches:

**Recommended pattern:**
```
每个任务独立分支 → 完成即合并 → 合并后删除
```

**Why independent branches:**
- Smaller, focused code reviews
- Faster feedback loops
- Easier rollback if issues found
- Main always production-ready

## Output Format

Provide context in Chinese at runtime:
- Risk level indication for operations
- Clear explanation of potential impact
- Alternative approaches when safer options exist
- Confirmation prompts for high-risk operations

**Tone:** Informative and helpful, not alarming
