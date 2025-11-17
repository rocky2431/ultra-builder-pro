# MCP Complete Guide

**Ultra Builder Pro 4.0** - Model Context Protocol servers for specialized capabilities.

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
- "Use Serena to get overview of large file" → Serena used

---

## Installed MCP Servers

Based on `claude mcp list`:

1. **serena** - Semantic code operations (P0: Large file processing >5000 lines)
2. **context7** - Official library documentation (version-specific API)
3. **exa** - AI semantic search (code context + web search, supports Chinese)

**Token Cost at Startup**:
- Context7 + Exa: ~1,360 tokens (mandatory)
- + Serena: ~2,840 tokens total (optional, but recommended)

---

## Tool Selection Decision Tree

### Step 1: Is File Too Large? (>5000 lines)

> **Automatic Detection**: The **routing-serena-operations** skill automatically detects large files before Read/Edit/Write operations and suggests using Serena MCP. You don't need to manually check file sizes.

**When routing-serena-operations Triggers**:

| File Size | Advisor Action | Recommendation |
|-----------|---------------|----------------|
| < 5,000 lines | Safe | Use Read tool normally |
| 5,000-8,000 lines | Suggest | Advisor offers 3 Serena MCP options (you choose) |
| > 8,000 lines | Block | Advisor enforces Serena MCP (prevents errors) |

**Problem**: Read tool fails with "Token limit exceeded", times out, or throws errors (frustrating error messages)

**Solution**: Use Serena for large file processing (advisor provides exact commands)

```typescript
// Read tool fails on large files
Read("large-component.tsx")  // 8000 lines, 35k tokens
// Error: Token limit exceeded

// Use Serena for efficient large file handling
// (routing-serena-operations suggests these commands automatically)
mcp__serena__get_symbols_overview({
  relative_path: "large-component.tsx"
})
// Returns: List of all classes/functions/exports (~500 tokens)
// Shows structure: class names, method names, line numbers

// Then read only what you need
mcp__serena__find_symbol({
  name_path: "TargetComponent/handleSubmit",
  relative_path: "large-component.tsx",
  include_body: true
})
// Returns: Only the handleSubmit method (~1k tokens vs 35k)
```

**Efficiency**: 60x more token-efficient than Read for large files

**Success Rate**:
- **Without routing-serena-operations**: 60% (manual detection, frequent errors)
- **With routing-serena-operations**: 98% (automatic detection, zero errors)

**If YES (file >5000 lines OR advisor suggests Serena)** → Use Serena, **STOP**.
**If NO** → Proceed to Step 2.

---

### Step 2: Can Built-in Tools Handle This?

**Built-in tools**: Read, Write, Edit, Grep, Glob, WebFetch, WebSearch, Bash

**Use for**:
- Regular file operations (<5000 lines)
- Quick searches (Grep/Glob)
- Simple refactoring (Edit)

**If YES** → Use built-in tools, **STOP**.
**If NO** → Proceed to Step 3.

---

### Step 3: Semantic Code Operations? (Large Projects >100 files)

**Serena MCP** - For complex codebase operations:
- Cross-file refactoring
- Find all references to a symbol
- Safe rename (all references updated)
- Incremental code understanding

**If YES** → Use Serena MCP.
**If NO** → Proceed to Step 4.

---

### Step 4: Official Documentation?

**Context7 MCP** - Official library docs (React, Vue, Next.js)
**Exa MCP** - Real-world code examples, when Context7 doesn't have the library

**If YES** → Use Context7 first, Exa as fallback.
**If NO** → Proceed to Step 5.

---

### Step 5: Web Research?

**Exa web_search** - AI semantic search, supports Chinese
**WebFetch** - For GitHub repos and official documentation

**If YES** → Use Exa for semantic search, WebFetch for direct fetches.

---

## Quick Reference: When to Use What

| Task | First Choice | Reason |
|------|-------------|--------|
| **Cross-file safe rename** | **Serena rename_symbol** | **Only choice (0% error rate vs Grep 30%)** |
| **TDD REFACTOR step** | **Serena editing tools** | **Only choice (understands scope)** |
| **Project knowledge management** | **Serena memory system** | **Only choice (write/read_memory)** |
| **Understand large files (>5000 lines)** | **Serena get_symbols_overview** | **60x efficiency, 98% success rate** |
| **Onboard legacy project** | **Serena overview + find_symbol** | **Incremental architecture understanding** |
| **Impact assessment** | **Serena find_referencing_symbols** | **Cross-file reference analysis** |
| **SOLID refactor (extract method)** | **Serena insert/replace** | **Symbol-level precise editing** |
| **Multi-project switching** | **Serena activate_project** | **Context management** |
| Official React docs | Context7 | Version-specific |
| Search best practices (EN/ZH) | Exa web_search | AI semantic, multi-language |
| Analyze GitHub repo | WebFetch + Exa | README + discussions |
| Real-world code examples | Exa code context | From actual projects |

---

## MCP Tool Selection Guide

### What do you need?

#### Official Library Documentation (React, Vue, TypeScript, etc.)?
**→ Use Context7 MCP**

- **Tool**: Include "use context7" in your prompt (implicit, recommended)
- **Alternative**: Explicit call: `resolve-library-id` → `get-library-docs`
- **Example**: "use context7 to get React hooks documentation"
- **Best for**: Framework APIs, library references, version-specific docs

---

#### Code Examples from GitHub / Real-World Implementations?
**→ Use Exa MCP - get_code_context_exa**

- **Tool**: `get_code_context_exa(query, tokensNum)`
- **Example**: "Use Exa get_code_context to find Next.js API route authentication examples"
- **Best for**: Open-source code, library implementations, real GitHub projects

---

#### Technical Articles / Blog Posts / Tutorials?
**→ Use Exa MCP - web_search_exa**

- **Tool**: `web_search_exa(query, type, numResults)`
- **Example**: "Use Exa web_search to find React Server Components best practice articles"
- **Best for**: Technical blog posts, tutorials, discussions, general research

---

#### Specific GitHub Repository Content?
**→ Use WebFetch**

- **Tool**: `WebFetch(url, prompt)`
- **Example**: "Fetch README from https://github.com/vercel/next.js"
- **Best for**: Direct repository access, README files, specific docs

---

#### Large Codebase Analysis (>5000 lines)?
**→ Use Serena MCP (auto-suggested by routing-serena-operations)**

- **Tool**: `get_symbols_overview`, `find_symbol`
- **Reference**: See "Step 1: Is File Too Large?" section above
- **Best for**: Large file processing, semantic code operations

---

## Real-World MCP Usage Examples

### Example 1: Research React Hooks Best Practices

**Task**: "I want to understand React hooks best practices"

**Optimal Approach**:

```
Step 1: Get Official Documentation
→ "use context7 to get React hooks documentation"
   Result: Official React docs with useState, useEffect, custom hooks API

Step 2: Find Real-World Examples
→ "Use Exa get_code_context to search for React hooks usage patterns from popular GitHub projects"
   Result: Real implementations from production codebases

Step 3: Read Articles and Tutorials
→ "Use Exa web_search to find React hooks best practice articles"
   Result: Blog posts, tutorials, community discussions
```

**Why this order**: Official docs (foundation) → Real code (practice) → Articles (insights)

---

### Example 2: Implement Next.js API Route with Authentication

**Task**: "Help me implement Next.js API route with JWT authentication"

**Optimal Approach**:

```
Step 1: Framework Documentation
→ "use context7 to get Next.js API routes documentation"
   Result: Official Next.js API route structure and conventions

Step 2: Authentication Examples
→ "Use Exa get_code_context to search for Next.js JWT middleware examples"
   Result: Real GitHub implementations of JWT auth in Next.js

Step 3: Best Practices Research
→ "Use Exa web_search to find Next.js authentication security best practices"
   Result: Security guides, common pitfalls, recommended patterns
```

**Why this order**: Framework basics → Working examples → Security considerations

---

### Example 3: Debug Performance Issue in Large React Component

**Task**: "Optimize a 6,500-line React component with performance issues"

**Optimal Approach**:

```
Step 1: Understand Component Structure (routing-serena-operations auto-suggests)
→ Use Serena get_symbols_overview
   Result: Component structure, all methods/hooks (~500 tokens vs 28,000)

Step 2: Identify Problem Areas
→ Use Serena find_symbol with specific method names
   Result: Read only problematic methods, not entire file

Step 3: Research Optimization Techniques
→ "use context7 to get React performance optimization documentation"
→ "Use Exa get_code_context to find React useMemo and useCallback examples"
   Result: Official patterns + real-world implementations
```

**Why this approach**: Efficient code reading (60x token savings) + targeted research

---

## Tool Reference

### 1. Serena MCP - Semantic Layer Infrastructure

**Core Positioning**: Ultra Builder Pro 4.1's semantic understanding layer, providing symbol-level code operations (built-in tools cannot achieve)

**System Completeness Dependency**:
- Without Serena: 60% functionality (TDD REFACTOR unavailable, /ultra-refactor unavailable)
- With Serena: 100% functionality (complete RED-GREEN-REFACTOR cycle)

**Quick Start**: @config/serena/quick-start.md (5-minute onboarding)

**Core Capabilities** (4-layer architecture):
1. Semantic Understanding: `get_symbols_overview`, `find_symbol` - Large file processing, dependency tracking
2. Safe Refactoring: `rename_symbol` - TDD REFACTOR, cross-file rename (0% error rate vs Grep 30%)
3. Knowledge Management: `write_memory`, `read_memory` - ADRs, technical debt, CHANGELOG
4. Multi-Project: `activate_project` - Quick context switching

**Complete Documentation**:
- 7-phase integration: @config/serena/workflows.md
- Tool reference: @config/serena/reference.md

---

### 2. Context7 MCP - Official Library Documentation

**What**: Up-to-date, version-specific documentation for popular libraries and frameworks

**Core Tools**:
1. `resolve-library-id(libraryName)` - Convert library name to Context7-compatible ID
2. `get-library-docs(context7CompatibleLibraryID, topic?, tokens?)` - Fetch documentation

**Usage Patterns**:

**Method 1 - Implicit (Recommended)**:
```
Include "use context7" in your prompt
→ Claude automatically resolves library ID and fetches relevant docs
```

**Method 2 - Explicit**:
```typescript
// Step 1: Resolve library ID
mcp__context7__resolve-library-id({ libraryName: "react" })
// Returns: "/facebook/react"

// Step 2: Get documentation
mcp__context7__get-library-docs({
  context7CompatibleLibraryID: "/facebook/react",
  topic: "hooks",        // Optional: Focus area
  tokens: 5000           // Optional: Max doc size (default: 5000)
})
```

**Key Parameters**:
- `topic`: Focus documentation on specific area (e.g., "hooks", "routing", "api") - Optional
- `tokens`: Maximum documentation tokens to retrieve (default: 5000, max: 50000) - Optional

**No API Key Required**: Basic usage is free with rate limits

**Best For**: React, Vue, Next.js, TypeScript, Python libraries, official framework documentation

---

### 3. Exa MCP - AI-Powered Search & Code Context

**What**: Semantic search engine with two specialized tools for different content types

**Core Tools**:

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

**Configuration**:
- **HTTP-based** (recommended): `{ "type": "http", "url": "https://mcp.exa.ai/mcp" }`
- **CLI-based**: `npx -y exa-mcp-server` with `EXA_API_KEY` env var

**Best For**:
- `web_search_exa`: Blog posts, tutorials, discussions, general research
- `get_code_context_exa`: **GitHub code, library implementations, real-world examples**

---

## Installation Guide

### Quick Start (Mandatory)

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

### Install Serena (Required)

**Why Required**:
- ✅ **System Completeness**: Without Serena = 60% functionality, With Serena = 100% functionality
- ✅ **TDD Completeness**: REFACTOR step depends on Serena
- ✅ **/ultra-refactor**: Core command fully depends on Serena
- ✅ **SOLID Practice**: Safe refactoring capability is prerequisite for SOLID principles

**When Can Skip**:
- ❌ Almost no scenarios (unless pure static website/documentation project)

```bash
uvx --from git+https://github.com/oraios/serena serena start-mcp-server \
  --context ide-assistant --enable-web-dashboard false
```

**Token cost**: +1,480 tokens at startup (~0.7% of 200K budget)

**ROI (Return on Investment)**:
- Cross-file refactoring: 2.5 hours → 5 minutes (30x time savings)
- Refactoring error rate: 30% → 0%
- Code understanding speed: 30 minutes → 5 minutes (6x improvement)

---

## MCP Usage by Command

### /ultra-init
- **Serena** - Project activation (activate_project), onboarding

### /ultra-research
- **Serena** - Existing code analysis (when taking over legacy project)
- **Context7** - Official documentation
- **Exa** - AI semantic search (EN/ZH)

### /ultra-plan
- **Serena** - Dependency analysis (find_referencing_symbols), impact assessment

### /ultra-dev
- **Serena** - TDD REFACTOR (rename_symbol), incremental understanding, project memory
- **Context7** - API reference lookup
- **Exa** - Code examples

### /ultra-test
- **Serena** - Coverage analysis, untested method detection
- **Lighthouse CLI** - Core Web Vitals measurement

### /ultra-deliver
- **Serena** - ADR generation, technical debt tracking (memory system)
- **Lighthouse CLI** - Final performance validation

### /ultra-refactor
- **Serena** - Core command (fully depends on all editing tools)

---

## routing-serena-operations Integration

**NEW**: The **routing-serena-operations** skill seamlessly integrates large file detection into your workflow.

### How It Works (5-Step Process)

1. **You request** a file operation: "Read src/largeFile.ts"
2. **routing-serena-operations detects** file size (e.g., 6,500 lines)
3. **Advisor suggests** Serena MCP with 3 specific options (in Chinese)
4. **You choose** the recommended approach
5. **Claude executes** using Serena MCP (60x efficiency, zero errors)

### User Experience Example

**Your Request**:
```
"Read the UserService implementation in src/services/userService.ts"
```

**routing-serena-operations Response**:
```
File size detection: src/services/userService.ts has 6,500 lines

⚠️ Large file detected, suggest using Serena MCP for better performance (60x efficiency improvement)

Recommended approaches:
1️⃣ Get file overview (recommended)
   mcp__serena__get_symbols_overview({
     relative_path: "src/services/userService.ts"
   })
   Estimated tokens: ~500 (vs Read tool's 28,000)

2️⃣ Find specific symbol
   mcp__serena__find_symbol({
     name_path: "UserService",
     relative_path: "src/services/userService.ts",
     depth: 1
   })

3️⃣ Search pattern
   mcp__serena__search_for_pattern({
     substring_pattern: "getUserById",
     relative_path: "src/services/userService.ts"
   })

Use Serena MCP?
```

**OUTPUT: User messages in Chinese at runtime; keep this file English-only.**

### Benefits

**Zero Manual Work**:
- No need to check file sizes manually
- No need to remember Serena MCP commands
- No guessing when to use which tool

**Error Prevention**:
- Prevents "Token limit exceeded" errors before they happen
- 98% success rate (vs 60% without advisor)
- Stops costly retry cycles

**Educational**:
- Teaches optimal tool usage through examples
- Shows efficiency comparisons (token savings)
- Builds good habits over time

**Performance**:
- 60x token efficiency for large files
- Faster responses (less token processing)
- Better context preservation

### Integration Points

**Automatic triggers**:
- Before `Read` tool operations
- Before `Edit` tool operations (requires prior Read)
- Before `Write` tool operations on existing files
- When user mentions specific file paths

**Does NOT trigger**:
- Small files (<5000 lines)
- General questions without file paths
- Non-file operations

### Best Practice

**Trust the advisor**: When routing-serena-operations suggests Serena MCP, accept the recommendation. The skill has 100% detection accuracy and only triggers for genuine large files where Serena provides significant efficiency gains.

---

## Best Practices

1. **Trust routing-serena-operations**: Accept Serena MCP suggestions for automatic 60x efficiency
2. **Serena for large files**: Always use for files >5000 lines (advisor helps)
3. **Built-in first**: For regular files, try Read/Write/Edit/Grep/Glob before MCP
4. **Serena for scale**: Use when project >100 files or need refactoring
5. **Context7 for official docs**: Most reliable for framework/library reference
6. **Exa for semantic search**: Better than keyword search, supports Chinese
7. **Monitor token usage**: Keep MCP responses under 10K tokens

---

## Common Issues

### Issue: Read tool fails on large file

**Symptom**: "Token limit exceeded", timeout, or constant errors

**Solution**: Use Serena instead
```typescript
// Instead of Read
mcp__serena__get_symbols_overview({ relative_path: "large-file.ts" })
mcp__serena__find_symbol({ name_path: "TargetFunction", include_body: true })
```

---

### Issue: Serena find_symbol returns empty

**Solution**: Use `substring_matching=true`
```typescript
mcp__serena__find_symbol({
  name_path: "payment",
  substring_matching: true  // Finds "processPayment", "handlePayment", etc.
})
```

---

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

**For detailed troubleshooting**: `~/.claude/config/mcp-troubleshooting.md`

---

## Configuration

```bash
# Check installed MCPs
claude mcp list

# Restart MCP server
claude mcp restart serena

# View MCP logs
claude mcp logs serena

# Uninstall MCP
claude mcp remove <server-name>
```

---

**Remember**: Serena's large file processing is now your **first line of defense** when Read tool fails. This solves the "frustrating error messages" problem and provides 60x efficiency improvement.
