---
name: guiding-workflow
description: "Suggests next logical command based on project state. This skill activates after phase completion, when user asks for guidance, or when session recovery is detected."
---

# Workflow Guide

Provides context-aware suggestions for next development steps.

## Activation Context

This skill activates when:
- A workflow phase completes (init, research, plan, dev, test, deliver)
- User asks "what's next?" or similar
- User seems uncertain after command completion

## Resources

| Resource | Purpose |
|----------|---------|
| `scripts/detect_project_state.py` | Analyze project filesystem state |
| `references/workflow-commands.md` | Command reference documentation |

## Project State Detection

Run the detection script to analyze current state:

```bash
python scripts/detect_project_state.py [project-path]
python scripts/detect_project_state.py --json  # JSON output
```

### Filesystem Signals

| Signal | Location | Indicates |
|--------|----------|-----------|
| .ultra/ directory | `.ultra/` | Project initialized |
| Specifications | `.ultra/specs/product.md`, `.ultra/specs/architecture.md` | Requirements defined |
| Research | `.ultra/docs/research/*.md` | Investigation complete |
| Task plan | `.ultra/tasks/tasks.json` | Tasks defined |
| Code changes | `git status` | Active development |
| Test files | `*.test.*`, `*.spec.*` | Tests written |

## Workflow Suggestions

Based on detected state:

| Current State | Suggested Command | Reason |
|---------------|-------------------|--------|
| No `.ultra/` directory | `/ultra-init` | Initialize project |
| No specs | `/ultra-research` | Need requirements |
| Specs complete, no tasks | `/ultra-plan` | Ready for planning |
| Tasks planned | `/ultra-dev` | Start implementation |
| Tasks complete | `/ultra-test` | Quality validation |
| Tests pass | `/ultra-deliver` | Prepare deployment |

## Project Type Adaptation

After `/ultra-research`, detect project type from research output:

| Type | Workflow Adaptation |
|------|---------------------|
| New Project | Full workflow (research → plan → dev → test → deliver) |
| Incremental Feature | Skip initial research, focus on implementation |
| Tech Decision | Validate choice before planning |

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

**Tone:** Helpful, action-oriented, concise
