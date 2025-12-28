---
name: syncing-docs
description: "Keeps documentation synchronized with code and decisions. This skill activates after /ultra-research, feature completion, architecture changes, or /ultra-deliver."
---

# Documentation Synchronization

Ensures documentation reflects current reality.

## Activation Context

This skill activates during:
- After /ultra-research completion
- Feature completion
- Architecture changes
- /ultra-deliver execution
- Documentation-related discussions

## Resources

| Resource | Purpose |
|----------|---------|
| `scripts/doc_sync.py` | Check and manage documentation |
| `templates/adr-template.md` | ADR creation template |

## Documentation Management

### Check for Drift

```bash
python scripts/doc_sync.py check
```

### Create New ADR

```bash
python scripts/doc_sync.py create-adr <number> <title>
python scripts/doc_sync.py create-adr 5 "Use PostgreSQL for primary database"
```

### List All ADRs

```bash
python scripts/doc_sync.py list-adrs
```

## Documentation Locations

**New projects (specs/):**
- `specs/product.md` - Product requirements
- `specs/architecture.md` - Technical decisions

**Legacy projects (docs/):**
- `docs/prd.md` - Product requirements
- `docs/tech.md` - Technical decisions

**Always:**
- `.ultra/docs/decisions/` - ADRs (Architecture Decision Records)
- `.ultra/docs/research/` - Research reports

## Synchronization Tasks

### After Research

When research introduces new information:
- Update relevant specification file with findings
- Create ADR if major decision made
- Flag `[NEEDS CLARIFICATION]` for unresolved items

### After Feature Completion

Check alignment between:
- User stories in specs/product.md and implemented features
- Architecture in specs/architecture.md and actual code structure

### ADR Creation

Create ADRs for significant decisions:

```markdown
# ADR-{number}: {Title}

## Status
Accepted

## Context
{What situation led to this decision}

## Decision
{What we decided to do}

## Consequences
{What this means going forward}
```

**Auto-create in:** `.ultra/docs/decisions/ADR-{number}-{slug}.md`

## Drift Detection

Look for misalignment:
- Features in code not documented in specs
- Specs describing features not yet implemented
- Architecture docs not matching actual structure
- Stale markers: `[NEEDS CLARIFICATION]`, `[TODO]`, `[TBD]`

## Safe Auto-Creation

Create these files automatically:
- ADRs in `.ultra/docs/decisions/`
- Tech debt entries in `.ultra/docs/tech-debt.md`
- Research reports in `.ultra/docs/research/`

Number ADRs sequentially (ADR-001, ADR-002, etc.)

## Output Format

Provide updates in Chinese at runtime:

```
文档同步检查
========================

发现：
- {具体发现或建议}

建议更新：
- {文件路径}: {需要更新的内容}

========================
```

**Tone:** Helpful, proactive
