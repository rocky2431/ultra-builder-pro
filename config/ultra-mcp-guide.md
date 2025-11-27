# MCP Complete Guide

**Ultra Builder Pro 4.1** - Model Context Protocol servers for specialized capabilities.

---

## Overview

**MCP Positioning**: Enhancement, not replacement. Use MCP when built-in tools have limitations.

**Core Philosophy**: Choose tools for delivery quality, not for tool showcase.

---

## CRITICAL: MCP Tools Require Explicit Invocation

**MCP tools DO NOT auto-activate. You must explicitly instruct Claude to use them.**

**Examples**:
- "Help me with React hooks" → Context7 NOT used
- "Use Context7 to fetch React hooks documentation" → Context7 used
- "Use Exa to search for React patterns" → Exa used

---

## Installed MCP Servers

Based on `claude mcp list`:

1. **context7** - Official library documentation (version-specific API)
2. **exa** - AI semantic search (code context + web search, supports Chinese)

**Token Cost at Startup**: ~1,360 tokens

---

## Tool Selection Decision Tree

### Step 1: Can Built-in Tools Handle This?

**Built-in tools** (always try first):
- **File operations**: Read, Write, Edit
- **Code search**: Grep, Glob
- **Web access**: WebFetch, WebSearch
- **Shell operations**: Bash

**Use for**:
- All file operations
- Code searches
- Simple refactoring (Edit)
- Web page fetching

**If YES** → Use built-in tools, **STOP here**.
**If NO** → Proceed to Step 2.

---

### Step 2: Need Official Library Documentation?

**Context7 MCP** - Official library docs (React, Vue, Next.js)

**Use for**:
- ✅ Official library documentation
- ✅ Version-specific API reference
- ✅ Framework documentation

**If YES** → Use Context7 MCP.
**If NO** → Proceed to Step 3.

---

### Step 3: Need Code Search or Web Research?

**Exa MCP** - AI semantic search, supports Chinese

**Use for**:
- ✅ Real-world code examples
- ✅ Technical articles (EN/ZH)
- ✅ GitHub repository exploration
- ✅ Chinese content (CSDN, Juejin)

**If YES** → Use Exa MCP.

---

## Quick Reference: When to Use What

| Task | First Choice | Reason |
|------|-------------|--------|
| Read file | Read ✅ | Fast, simple |
| Search code | Grep ✅ | Native performance |
| Edit file | Edit ✅ | Precise modifications |
| Official React docs | Context7 MCP ✅ | Version-specific |
| Search best practices (EN/ZH) | Exa web_search ✅ | AI semantic, multi-language |
| Real-world code examples | Exa code_context ✅ | From actual projects |
| Analyze GitHub repo | WebFetch + Exa ✅ | README + discussions |

---

## MCP Tool Selection Guide

### Official Library Documentation (React, Vue, TypeScript, etc.)?
**→ Use Context7 MCP**

- **Tool**: `resolve-library-id` → `get-library-docs`
- **Example**: "Use Context7 to get React hooks documentation"
- **Best for**: Framework APIs, library references, version-specific docs

---

### Code Examples from GitHub / Real-World Implementations?
**→ Use Exa MCP - get_code_context_exa**

- **Tool**: `get_code_context_exa(query, tokensNum)`
- **Example**: "Use Exa get_code_context to find Next.js API route authentication examples"
- **Best for**: Open-source code, library implementations, real GitHub projects

---

### Technical Articles / Blog Posts / Tutorials?
**→ Use Exa MCP - web_search_exa**

- **Tool**: `web_search_exa(query, type, numResults)`
- **Example**: "Use Exa web_search to find React Server Components best practice articles"
- **Best for**: Technical blog posts, tutorials, discussions, general research

---

### Specific GitHub Repository Content?
**→ Use WebFetch**

- **Tool**: `WebFetch(url, prompt)`
- **Example**: "Fetch README from https://github.com/vercel/next.js"
- **Best for**: Direct repository access, README files, specific docs

---

## Tool Reference

### 1. Context7 MCP - Library Documentation

**When to use**:
- ✅ Need official library documentation
- ✅ Need version-specific API reference
- ✅ Comparing different library versions
- ✅ Looking for usage examples from official docs

**When NOT to use**:
- ❌ Internal project code → Use Grep
- ❌ General web search → Use WebSearch
- ❌ Tutorials/blog posts → Use WebFetch or Exa

**Key tools**:

#### `mcp__context7__resolve-library-id`
Convert library name to Context7-compatible ID.

**Usage Pattern**:
```typescript
// Step 1: Resolve library name to ID
mcp__context7__resolve-library-id(libraryName="react")
// Returns: "/facebook/react" (Context7 ID)
```

#### `mcp__context7__get-library-docs`
Get official documentation for a library.

**Usage Pattern**:
```typescript
// Step 2: Get docs with Context7 ID
mcp__context7__get-library-docs(
  context7CompatibleLibraryID="/facebook/react",
  topic="hooks",              // Optional: focus on specific topic
  tokens=5000                 // Optional: max tokens (default 5000)
)

// Version-specific docs
mcp__context7__get-library-docs(
  context7CompatibleLibraryID="/vercel/next.js/v14.3.0-canary.87",
  topic="routing"
)
```

**Complete Workflow**:
```
1. resolve-library-id("react") → "/facebook/react"
2. get-library-docs("/facebook/react", topic="hooks")
3. Use documentation to implement feature
```

---

### 2. Exa MCP - AI-Powered Search & Code Context

**What**: Semantic search engine with two specialized tools for different content types

**Key tools**:

1. **`web_search_exa(query, type?, numResults?, livecrawl?)`** - General web search
   - **Use for**: Blog posts, tutorials, technical articles, discussions
   - **Content**: Broader web content (Medium, dev.to, Stack Overflow, etc.)

2. **`get_code_context_exa(query, tokensNum?)`** - **Code-specific search**
   - **Use for**: GitHub repositories, library APIs, framework implementations
   - **Content**: Programming-optimized (actual code, not articles)
   - **Specialization**: Code examples, open-source projects, API usage patterns

**Tool Selection Guide**:

| Need | Correct Tool | Why |
|------|-------------|-----|
| Technical articles/blog posts | `web_search_exa` | Broader web content |
| Code examples from GitHub | `get_code_context_exa` | **Code-optimized search** |
| Library usage patterns | `get_code_context_exa` | **Programming-focused** |
| General research/tutorials | `web_search_exa` | All web content |

**Examples**:
```typescript
// General web search (articles, blogs)
mcp__exa__web_search_exa({
  query: "React Server Components patterns",
  type: "deep",           // "auto" | "fast" | "deep"
  numResults: 8,          // Default: 8
  livecrawl: "preferred"  // "fallback" | "preferred"
})

// Code-specific search (GitHub repos, frameworks)
mcp__exa__get_code_context_exa({
  query: "Next.js API route middleware authentication examples",
  tokensNum: 5000  // Default: 5000, range: 1000-50000
})
```

**Best For**:
- `web_search_exa`: Blog posts, tutorials, discussions, general research
- `get_code_context_exa`: **GitHub code, library implementations, real-world examples**

---

## Installation Guide

### Quick Start

Install Context7 and Exa:
```bash
claude mcp add context7
claude mcp add exa
```

Verify:
```bash
claude mcp list
# Should show: context7, exa
```

---

## MCP Usage by Command

### /ultra-init
- No MCP dependencies

### /ultra-research
- **Context7** - Official documentation
- **Exa** - AI semantic search (EN/ZH)

### /ultra-plan
- No MCP dependencies

### /ultra-dev
- **Context7** - API reference lookup
- **Exa** - Code examples

### /ultra-test
- No MCP dependencies

### /ultra-deliver
- No MCP dependencies

---

## Best Practices

1. ✅ **Built-in first**: Always try built-in tools before MCP
2. ✅ **Context7 for docs**: Use for official library documentation
3. ✅ **Exa for search**: Better than keyword search, supports Chinese
4. ✅ **Monitor token usage**: Keep MCP responses under 10K tokens
5. ✅ **Specific queries**: Narrow scope = faster responses

---

## Common Issues

### Issue: Context7 library not found

**Solution**: Try name variations, use Exa as fallback
```typescript
// Try variations
resolve-library-id("react")
resolve-library-id("facebook/react")
resolve-library-id("reactjs")

// If all fail, use Exa
mcp__exa__get_code_context_exa({ query: "React hooks API" })
```

---

### Issue: MCP not responding

**Solution**: Restart MCP server
```bash
claude mcp restart <server-name>
```

---

## Configuration

```bash
# Check installed MCPs
claude mcp list

# Restart MCP server
claude mcp restart context7

# View MCP logs
claude mcp logs context7

# Uninstall MCP
claude mcp remove <server-name>
```

---

**Remember**: MCP tools enhance built-in capabilities. Use strategically for specialized tasks.
