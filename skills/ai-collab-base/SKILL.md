---
name: ai-collab-base
description: "Shared collaboration protocol, modes, and prompt templates for AI collab skills. Consumed by gemini-collab, codex-collab, and ultra-verify as a shared foundation."
user-invocable: false
disable-model-invocation: true
---

# AI Collab Base

Shared foundation for dual/multi-AI collaboration skills. Contains the canonical versions of:

- `references/collab-protocol.md` — Core principles, session management, file output protocol, synthesis template, error handling
- `references/collaboration-modes.md` — 5 collaboration modes (review, understand, opinion, compare, free)
- `references/prompt-templates.md` — Generic prompt templates (no CLI syntax)

## Sync

Run `sync.sh` to copy canonical files to all consumer skills:

```bash
bash skills/ai-collab-base/sync.sh
```
