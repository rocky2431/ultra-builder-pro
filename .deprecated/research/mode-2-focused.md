## Mode 2: Focused Technology Research (Quick Reference)

**Usage**:
```bash
/ultra-research "React vs Vue for enterprise dashboard"
```

**Implementation**: Delegates to **ultra-research-agent** for execution

**Workflow** (executed by agent):
1. Parallel information gathering (4-8 tools in one message)
2. Six-dimension evaluation with evidence citations
3. Risk assessment (🔴 Critical / 🟠 High / 🟡 Medium)
4. Generate structured report (7 required items)
5. Auto-update `specs/architecture.md`
6. Save research report to `.ultra/docs/research/`

**Duration**: 10-15 minutes

**Use when**: You have a specific technology question during development, not building specs from scratch

**Agent Details**: See `@agents/ultra-research-agent.md` for complete research methodology

---
