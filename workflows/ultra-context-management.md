# Context Management - Efficiency Guide

**Ultra Builder Pro 4.0** - Keep sessions efficient through smart context management.

---

## Overview

Effective context management ensures Claude operates within token limits while maintaining high-quality responses. Official Claude Code best practices emphasize specificity and strategic information retrieval.

---

## Keep Sessions Efficient

### Provide Specific Instructions (Official Best Practice)

**Claude performs best with concrete, detailed instructions.**

**Good Example** ✅:
```
"Write unit tests for getUserById() in src/auth.ts covering the edge case
where user is logged out and session has expired, avoid mocks for internal services"
```

**Bad Example** ❌:
```
"add tests for auth"
```

**Why specificity matters**:
- Reduces back-and-forth clarification
- Enables targeted tool usage
- Minimizes context consumption
- Produces accurate results faster

---

### Use Precise File References

**Always reference files explicitly**:

- ✅ **Use tab-completion** for accurate paths
- ✅ **Reference specific line numbers**: `src/auth.ts:45`
- ✅ **Quote exact function names**: "Fix the `getUserById` function"

**Example**:
```
❌ "There's a problem in the auth file"
✅ "The getUserById function at src/auth.ts:127 throws an error when
    userId is null - add null check before database query"
```

---

## Dynamic Context Retrieval

**Official strategy**: Avoid reading entire files. Use targeted searches and reads.

### Strategy 1: Search Before Reading

**Pattern**:
```
1. Grep("function getUserById") → Identify which files contain it
2. Read(file, offset=120, limit=50) → Read only relevant section
```

**Example**:
```typescript
// ❌ Inefficient: Read entire 500-line file
Read("src/services/userService.ts")

// ✅ Efficient: Find first, then read targeted section
Grep(pattern="function getUserById", type="ts")
Read("src/services/userService.ts", offset=120, limit=30)
```

**Benefits**: Consumes 10x fewer tokens, faster response time

---

### Strategy 2: Use Specialized Agents for Exploration

**When to delegate to agents**:

- ✅ **ultra-research-agent**: Technical investigation, solution comparison
- ✅ **ultra-architect-agent**: Architecture analysis, system design
- ✅ **ultra-performance-agent**: Performance optimization, bottleneck identification
- ✅ **ultra-qa-agent**: Test strategy design, coverage planning

**Why use agents**:
- Agents parallelize searches internally
- Specialized knowledge domains
- Structured research output
- Don't clutter main conversation

---

### Strategy 3: Leverage Parallel Tool Invocation

**Official guidance**: Maximum 4 independent tool calls per message.

**Example**:
```
// ❌ Sequential: 4x latency
Read(package.json) → Read(tsconfig.json) → Read(vite.config.ts) → Read(.env)

// ✅ Parallel: 1x latency
Single message with 4 tool calls (package.json, tsconfig.json, vite.config.ts, .env)
```

**When to use parallel**:
- ✅ Reading multiple config files
- ✅ Grepping multiple patterns independently

**When NOT to use**:
- ❌ Dependent operations: Grep result → Read specific file
- ❌ Sequential logic: Create file → Edit file

---

## Context Compaction Strategies

### 1. Summarize After Each Task

**After completing a task**, create a concise summary:

**Template**:
```markdown
## Task: [Name]

**Completed**: [Key changes with file paths]
**Technical Decisions**: [Key choices made]
**Technical Debt**: [TODOs if any]
**Next Steps**: [What's next]
```

**Benefits**: Quick reference without re-reading code, documents decisions for future

---

### 2. Remove Redundancy

**Delete duplicate information**:

```
❌ Redundant: Show full function 3 times (150 lines)
✅ Efficient: Show once + describe changes (50 lines + descriptions)
```

**Practice**: Don't repeat full code unless necessary, use diffs or descriptions for small changes

---

### 3. Use Structured Notes

**Prefer structured formats** for quick scanning:

**Markdown tables**:
```markdown
| Feature | Status | Notes |
|---------|--------|-------|
| Authentication | ✅ Complete | JWT-based, RS256 |
| Authorization | 🚧 In Progress | Role-based |
```

**Checklists**:
```markdown
- [x] All tests passing (coverage 87%)
- [x] Security audit complete
- [ ] Environment variables configured
```

---

## Proactive Context Compression

**NEW**: The **compressing-context** skill automatically manages context to prevent overflow and maximize session capacity.

### How It Works

**Triggers**: After 5+ completed tasks, token usage >120K, or before /ultra-test /ultra-deliver

**Process**: Identify compressible content → Generate summaries (15K→500 tokens) → Archive to `.ultra/context-archive/` → Replace verbose content

### Benefits

- **Session capacity**: 10-15 tasks → 20-30 tasks (2x increase)
- **Token savings**: 40-60% compression ratio, 50-100K freed per compression
- **Example**: 145K tokens → 62K tokens (57% reduction)

### Archive Management

**Location**: `.ultra/context-archive/session-{timestamp}.md`

**Contents**: Task summaries, technical decisions, code snippets (if critical)

**Access**: `Read(".ultra/context-archive/session-2025-11-15.md")` or `Grep("Task #5", { path: ".ultra/context-archive/" })`

### Best Practice

**Always accept** when: 10+ task projects, long sessions (>2h), token usage >120K

**Result**: Handle 20-30 tasks per session without overflow

---

## Context Overflow Prevention

> **Note**: With **compressing-context** skill, overflow is now rare. Proactive compression typically maintains token usage <140K even when handling 20+ tasks. The overflow handler below provides safety monitoring but triggers far less frequently.

**context-overflow-handler** skill monitors token usage:

### Four-Tier Monitoring

| Tier | Token Range | Status | Action |
|------|-------------|--------|--------|
| 🟢 Safe | <140K | Normal | Continue normally |
| 🟡 Warning | 140K-170K | Caution | Consider compaction |
| 🟠 Danger | 170K-190K | Alert | Immediate compaction needed |
| 🔴 Critical | >190K | Emergency | Emergency compaction or restart |

### Compaction Techniques

**Auto-suggested when**: Token usage >150K, reading large files (>5000 lines), or after major operations

**1. Summarize conversation history**:
```
Generate concise summary → Start new session with summary as context
```

**2. Archive to external files**:
```
Move research to .ultra/docs/research/
Move decisions to .ultra/docs/decisions/
Keep only essential context in conversation
```

**3. Segmented file reading**:
```typescript
// ❌ Read entire 10,000-line file
Read("src/large-file.ts")

// ✅ Read in segments
Read("src/large-file.ts", offset=0, limit=1000)
Read("src/large-file.ts", offset=1000, limit=1000)
```

---

## Project Structure for Context Efficiency

**Organize information hierarchically**:

```
.ultra/
├── docs/
│   ├── prd.md                    # Product requirements
│   ├── tech.md                   # Technical design
│   ├── research/                 # Research reports
│   └── decisions/                # Architecture decision records
├── tasks/
│   └── tasks.json                # Current tasks (active context)
└── config.json                   # Project config
```

**Benefits**: Information is findable, decisions are documented, research is archived, tasks are tracked

---

## Memory Organization (CLAUDE.md)

**Official hierarchy** (from highest to lowest precedence):

1. **Enterprise**: `/Library/Application Support/ClaudeCode/CLAUDE.md` (macOS) - Organization-wide policies
2. **User**: `~/.claude/CLAUDE.md` - Personal preferences (**Ultra Builder Pro 4.0 location**)
3. **Project**: `./.claude/CLAUDE.md` - Project-specific guidelines, team-shared, version controlled

**Best practices**:
- Keep user-level CLAUDE.md concise (use @import)
- Use project-level for team-specific rules
- Don't duplicate content across levels

---

## MCP for Context Efficiency

**When MCP is more context-efficient**:

### Large File Intelligent Handling


**Efficiency comparison**:
- **Large files (>5K lines)**: Read fails (35K tokens) → built-in tools succeeds (500 tokens)
- **Cross-file search**: Grep+Read (50K tokens) → built-in tools find_referencing_symbols (5K tokens)
- **Official docs**: WebFetch (15K tokens) → Context7 (5K tokens)


---

## Context Management Best Practices Summary

1. **Be specific in requests** - Detailed instructions reduce back-and-forth
2. **Search before reading** - Grep → Read targeted section
3. **Use parallel tool calls** - Read multiple files in single message
4. **Delegate to agents** - Use specialized agents for complex research
5. **Summarize after tasks** - Create concise summaries for future reference
6. **Remove redundancy** - Don't repeat full code unnecessarily
7. **Use structured notes** - Tables, checklists, bullet points
8. **Monitor token usage** - context-overflow-handler provides alerts
9. **Archive to files** - Move detailed info to .ultra/docs/
10. **Use MCP strategically** - built-in tools for large codebases, Context7 for docs
11. **Trust compressing-context** - Accept compression after 5+ tasks for 2x session capacity

---

**Remember**: Context management is not about rationing information—it's about smart information retrieval and organization.
