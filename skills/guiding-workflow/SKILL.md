---
name: guiding-workflow
description: "Suggests next logical command based on project state. Activates after phase completion, when user asks for guidance, or when session recovery is detected."
allowed-tools: Read, Glob
---

# Workflow Guide

Provides context-aware suggestions for next steps.

## Activation Context

This skill activates when:
- A workflow phase completes (init, research, plan, dev, test, deliver)
- User asks "what's next?" or similar
- User seems uncertain after command completion
- Session recovery detected (session-index.json exists)

## Session Recovery

When `.ultra/context-archive/session-index.json` exists:

1. Read last session information
2. Display recovery summary:

```
========================
检测到会话恢复
========================
上次会话：{timestamp}
已完成任务：{count} 个
关键决策：{decisions}

恢复点：Task #{nextTask}

建议：继续执行 /ultra-dev Task #{nextTask}
========================
```

3. Offer options: Resume / Start Fresh / View History

## Project State Detection

Check these filesystem signals:

| Signal | Location |
|--------|----------|
| Specifications | `specs/product.md`, `specs/architecture.md` |
| Research | `.ultra/docs/research/*.md` |
| Task plan | `.ultra/tasks/tasks.json` |
| Code changes | `git status` |
| Test files | `*.test.*`, `*.spec.*` |

## Workflow Suggestions

Based on project state:

| Current State | Suggested Next Step |
|---------------|---------------------|
| No `.ultra/` directory | `/ultra-init` |
| Specs have `[NEEDS CLARIFICATION]` | `/ultra-research` |
| Specs complete, no tasks.json | `/ultra-plan` |
| Tasks planned | `/ultra-dev` |
| Code committed | `/ultra-test` or next `/ultra-dev` |
| All tests pass | `/ultra-deliver` |

## Output Format

Provide suggestions in Chinese at runtime:

```
当前状态
========================
- ✅ {completed items}
- ⏳ {pending items}

建议下一步：{command}
原因：{rationale}
========================
```

**Example:**

```
当前状态
========================
- ✅ 研究完成 (4 轮完整流程)
- ✅ specs/product.md 100% 完成
- ✅ specs/architecture.md 100% 完成

建议下一步：/ultra-plan
原因：规格完整，可以开始任务规划
========================
```

## Project Type Adaptation

After `/ultra-research`, detect project type from research output:

| Type | Workflow Adaptation |
|------|---------------------|
| New Project | Full workflow (research → plan → dev → test → deliver) |
| Incremental Feature | Skip initial research, focus on implementation |
| Tech Decision | Validate choice before planning |

**Tone:** Helpful, action-oriented, concise
