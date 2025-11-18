---
name: syncing-docs
description: "Syncs documentation and manages knowledge archival. TRIGGERS: After /ultra-research completion, feature completion, architecture changes, running /ultra-deliver, detecting [NEEDS CLARIFICATION] markers filled, major technology decisions. ACTIONS: Suggest update specs/product.md or specs/architecture.md, propose ADR creation in docs/decisions/, detect spec-code drift. DO NOT TRIGGER: Minor code changes, formatting edits, test-only changes, git operations without code impact."
allowed-tools: Read, Write, Glob, Grep
---

# Documentation Guardian

## Purpose
Ensure documentation stays synchronized with code and decisions.

## When
- After /ultra-research completion (CRITICAL - check specs/)
- Feature completion (check spec-code consistency)
- Architecture changes (check specs/architecture.md)
- /ultra-deliver execution (final sync check)

## Do

### File Detection (Backward Compatible)
- Check if specs/product.md exists → Use specs/ (new projects)
- Fallback to docs/prd.md if specs/ doesn't exist (old projects)
- Check if specs/architecture.md exists → Use specs/ (new projects)
- Fallback to docs/tech.md if specs/ doesn't exist (old projects)

### Post-Research Checks
1. Does research introduce new requirements?
   - New projects: Suggest update to specs/product.md
   - Old projects: Suggest update to docs/prd.md
2. Does research affect technology choices?
   - New projects: Suggest update to specs/architecture.md
   - Old projects: Suggest update to docs/tech.md
3. Is this a major decision? Suggest ADR creation in docs/decisions/

### Spec-Code Drift Detection
- Compare specs/product.md user stories with implemented features
- Check if architecture.md matches actual code structure
- Flag [NEEDS CLARIFICATION] markers that remain unfilled

### General Documentation
- Detect outdated docs (README/API docs)
- Recommend tech-debt entries when shortcuts taken
- Suggest lessons-learned after major features

### Auto-Create Documentation Files

**Safe auto-creation** (no confirmation needed):
- ADRs in `.ultra/docs/decisions/` (numbered sequentially ADR-001, ADR-002, etc.)
- Tech debt entries in `.ultra/docs/tech-debt.md` (append mode)
- Research reports in `.ultra/docs/research/` (timestamped filenames)

**Auto-creation logic**:
1. Check if file path is in `.ultra/docs/` → Safe to create
2. Use template from `.ultra-template/docs/` if available
3. Number ADRs sequentially by checking existing files
4. Show creation summary after completion (Chinese output)

**Rationale**: "Implement changes rather than only suggesting" (Claude 4.x Best Practices)

## Don't
- Do not create files outside `.ultra/docs/` directory without confirmation
- Do not overwrite existing files without checking content similarity
- Do not trigger on minor code changes
- Do not force old projects to migrate to specs/ (suggest only)

## Outputs

**Language**: Chinese (simplified) at runtime

**OUTPUT: User messages in Chinese at runtime; keep this file English-only.**

**Format**:
- File path with clear indication (specs/ or docs/)
- Reason for update (what changed)
- Specific sections to update
- ADR template if needed

**Content to convey**:
- Technology selection changed → Suggest update specs/architecture.md Technology Stack section
- Research found new requirements → Suggest add user stories to specs/product.md
- Major architecture decision → Suggest create ADR in docs/decisions/
- Detected old project structure → Suggest update docs/prd.md or consider migrating to specs/

## Migration Suggestion (Optional)

When detecting old projects without specs/:
- Suggest (don't force) migration to spec-driven structure
- Convey: Old doc structure detected, consider migrating to new specs/ system
- Only suggest once per session
