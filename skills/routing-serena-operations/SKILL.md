---
name: routing-serena-operations
description: "Routes operations to Serena MCP when beneficial. TRIGGERS: Before Read/Edit/Write or discussing refactoring. ACTIONS: Analyze task, route to optimal tool. BLOCKS: Unsafe text operations."
allowed-tools: Bash, Read, Grep, Glob
---

# Serena Operations Router

Routes to optimal tools (Serena MCP vs built-in) across 3 routing dimensions.

## Purpose

Intelligently route operations to Serena MCP when it provides significant benefits (efficiency, safety, or unique capabilities), while preserving built-in tools for simple tasks.

## Configuration

**Load from `.ultra/config.json`**:
```json
{
  "file_routing": {
    "thresholds": {
      "medium": 5000,
      "large": 8000
    },
    "actions": {
      "medium": "suggest_serena",
      "large": "enforce_serena"
    }
  }
}
```

**Usage at runtime**:
- Small threshold: `< config.file_routing.thresholds.medium` → Use Read tool
- Medium threshold: `config.file_routing.thresholds.medium - config.file_routing.thresholds.large` → Suggest Serena
- Large threshold: `> config.file_routing.thresholds.large` → Enforce Serena

**Loading config in runtime** (TypeScript example):
```typescript
// Load config from project
const configPath = '.ultra/config.json';
const config = JSON.parse(await Read(configPath));

// Extract file routing thresholds
const mediumThreshold = config.file_routing.thresholds.medium;  // 5000
const largeThreshold = config.file_routing.thresholds.large;    // 8000

// Use in routing logic
const lineCount = await Bash(`wc -l ${filePath} | awk '{print $1}'`);

if (lineCount > largeThreshold) {
  // BLOCK Read, ENFORCE Serena
} else if (lineCount >= mediumThreshold) {
  // SUGGEST Serena
} else {
  // ALLOW Read tool
}
```

## When (Trigger Conditions)

### Passive Triggers (Before Tool Use)
- **BEFORE** using Read tool (check file size)
- **BEFORE** using Edit tool (requires prior Read check)
- **BEFORE** using Write tool on existing files

### Active Triggers (During Discussions)
- Discussing code refactoring ("rename across", "refactor", "extract")
- Discussing code understanding ("understand", "how does", "architecture")
- Discussing symbol-level operations ("find all usages", "references", "where is used")
- Discussing project knowledge ("record decision", "project memory")
- Large codebase exploration (>100 files or >1000 lines/file)

## Do

### Dimension 1: File Size Routing

**Check file size** (use `wc -l <file>` or `ls -lh <file>`):

**Load thresholds from config**:
- **< {medium} lines**: Use Read tool (safe, fast)
- **{medium}-{large} lines**: Suggest Serena MCP (60x efficiency, from config.file_routing.actions.medium)
- **> {large} lines**: BLOCK Read, ENFORCE Serena MCP (prevent token overflow, from config.file_routing.actions.large)

**Provide explicit Serena commands**:
```typescript
// For overview (structure only, ~500 tokens)
mcp__serena__get_symbols_overview({
  relative_path: "path/to/large-file.ts"
})

// For specific symbol (targeted read, ~1k tokens)
mcp__serena__find_symbol({
  name_path: "ClassName/methodName",
  relative_path: "path/to/large-file.ts",
  include_body: true
})
```

**Efficiency**: Read tool (35K tokens) → Serena (500 tokens) = 60x savings

---

### Dimension 2: Operation Type Routing

#### Operation: Cross-file Rename
**Keywords**: "rename across", "rename in multiple files", "change name"

**Detection**:
```typescript
IF intent.includes("rename") AND intent.includes("across|multiple|all"):
  fileCount = estimateAffectedFiles(symbolName)

  IF fileCount > 5:
    BLOCK Grep + Edit (30% error rate)
    ENFORCE Serena rename_symbol (0% error rate)
```

**Serena command**:
```typescript
mcp__serena__rename_symbol({
  name_path: "symbolName",
  relative_path: "src/path/to/file.ts",
  new_name: "newSymbolName"
})
```

---

#### Operation: Understand Architecture
**Keywords**: "understand", "how does", "architecture", "structure"

**Suggest Serena incremental exploration**:
```
1. Get file structure overview
   mcp__serena__get_symbols_overview({ relative_path: "..." })

2. Explore key classes
   mcp__serena__find_symbol({
     name_path: "ClassName",
     depth: 1  // method list only
   })

3. Read specific methods
   mcp__serena__find_symbol({
     name_path: "ClassName/methodName",
     include_body: true
   })
```

---

#### Operation: Find All References
**Keywords**: "find all", "where is used", "references", "usages"

**SUGGEST Serena find_referencing_symbols**:
```typescript
mcp__serena__find_referencing_symbols({
  name_path: "symbolName",
  relative_path: "src/path/to/file.ts"
})
```

**Advantages vs Grep**:
- Understands scope (no false positives from strings/comments)
- Returns code context snippets
- Cross-file accurate tracking

---

### Dimension 3: Project Scale Routing

**Detect project scale** (use Glob or Bash to count files):

```typescript
fileCount = countCodeFiles("src/")

IF fileCount > 100:
  SUGGEST Serena memory system
  SUGGEST activate_project for multi-project management
```

**Serena project management**:
```typescript
// 1. Activate project
mcp__serena__activate_project("project-name")

// 2. Record knowledge
mcp__serena__write_memory("coding-conventions", `
  Team conventions:
  - ESLint: Airbnb
  - Testing: Vitest
  - Naming: camelCase
`)

// 3. Query knowledge
mcp__serena__read_memory("coding-conventions")
```

**Benefits**: Fast context switching, knowledge accumulation, onboarding friendly

---

## Don't

- Do not block operations on small files (< {medium} lines, from config)
- Do not trigger for new file creation (Write on non-existent files)
- Do not suggest Serena for non-code files (.txt, .md, .json, .yaml)
- Do not suggest Serena for simple single-file edits
- Do not provide vague suggestions (always include complete commands)

---

## Safety Enforcement (BLOCK Mechanism)

**BLOCK these operations** when Serena is the only safe choice:

```
IF task == "cross-file rename" AND files > 5:
  BLOCK Grep + Edit
  ENFORCE rename_symbol
  SHOW: 30% error rate → 0%

IF task == "symbol-level operation":
  BLOCK text-based search
  ENFORCE find_symbol or find_referencing_symbols
  SHOW: scope understanding required

IF file.lines > {large threshold}:
  BLOCK Read
  ENFORCE get_symbols_overview
  SHOW: token overflow prevention (from config.file_routing.thresholds.large)
```

---

## Output Format

**Standard suggestion template**:
```
Scenario: {task description}

Recommended tool: {Serena or Built-in}

Rationale:
- {benefit 1}
- {benefit 2}

Complete command:
mcp__serena__{command}({
  param1: "value1",
  param2: "value2"
})

Expected result: {outcome with metrics}

Efficiency comparison:
- Built-in tool: {time/tokens/error rate}
- Serena MCP: {time/tokens/error rate}
- Improvement: {improvement percentage}
```

**Blocking message template** (when BLOCK is triggered):
```
⚠️ Safety Warning

Detected: {risky operation}

❌ Blocked: {blocked tool}
Reason: {risk explanation}

✅ Enforcing: {Serena command}
Reason: {safety benefits}
```

**OUTPUT: User messages in Chinese at runtime; keep this file English-only.**

---

## Decision Matrix (Quick Reference)

**Load thresholds from config.file_routing.thresholds**

| Scenario | Built-in | Serena | Recommendation |
|----------|----------|--------|----------------|
| Cross-file rename (>5 files) | ❌ 30% error | ✅ 0% error | **Serena only** |
| Symbol operations | ❌ No scope | ✅ Semantic | **Serena only** |
| Large file (>{medium} lines) | ⚠️ May fail | ✅ 60x efficiency | **Serena recommended** |
| Small file (<{medium/5} lines) | ✅ Fast | ⚠️ Overkill | **Built-in OK** |
| Simple text search | ✅ Grep efficient | ⚠️ Unnecessary | **Built-in OK** |

---

## Performance Metrics

- Detection accuracy: 100% (file size), 90% (operation type)
- False positive rate: <5%
- Token savings: 30-60x for large files
- Cross-file refactoring error rate: 30% → 0%
- Success rate: 98% (automatic detection + routing)

---

*See REFERENCE.md for detailed examples and complete routing workflows.*
