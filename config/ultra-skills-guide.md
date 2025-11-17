# Skills System - Complete Guide

**Ultra Builder Pro 4.0** - Automated quality enforcement through model-invoked skills.

---

## Overview

Skills are **model-invoked**—Claude autonomously decides when to use them based on your request and each Skill's description. This is official Claude Code behavior, not a custom feature.

---

## How Skills Work (Official Claude Code)

### Activation Mechanism

1. **Automatic Discovery**: All Skills in `~/.claude/skills/` are automatically discovered and loaded into context
2. **Description Matching**: Claude analyzes your request and matches it against each Skill's `description` field
3. **Autonomous Invocation**: When a Skill's description matches your request, Claude invokes it automatically
4. **No Manual Control**: You cannot manually activate/deactivate Skills—activation is purely based on relevance

### Official Configuration Format

Each skill is defined in `~/.claude/skills/skill-name/SKILL.md` with YAML frontmatter:

```yaml
---
name: skill-name              # Required: lowercase, hyphens, max 64 chars
description: "..."            # Required: clear description for matching (max 1024 chars)
allowed-tools: Tool1, Tool2   # Optional: restrict tool access
---

# Skill content in markdown
```

**Official fields** (only these are supported):
- `name`: Skill identifier
- `description`: How Claude decides when to invoke
- `allowed-tools`: Tool permissions (optional)

---

## Available Skills (10 total)

### 1. guarding-code-quality

**Description**: "Detects code quality violations (SOLID, DRY, KISS, YAGNI) when writing or editing code. Provides refactoring suggestions and quality feedback."

**Purpose**:
- Real-time SOLID/DRY/KISS/YAGNI violation detection
- Suggests refactoring opportunities
- Enforces quality standards before commit

**Auto-triggers when**:
- Editing code files (`.js`, `.ts`, `.py`, `.java`, `.go`, etc.)
- Creating new functions/classes
- PR reviews

**Key checks**:
- Single Responsibility (functions >50 lines)
- DRY violations (duplicate code >3 lines)
- Complexity >10
- Magic numbers
- Code smells

**Location**: `~/.claude/skills/guarding-code-quality/SKILL.md`

---

### 2. guarding-git-safety

**Description**: "Prevents dangerous git operations (force push, hard reset, rebase) that could cause data loss. Requires confirmation before destructive commands on main branches."

**Purpose**:
- Prevents accidental data loss
- Enforces safe git practices
- Requires user confirmation for dangerous operations

**Auto-triggers when**:
- About to run `git push --force`
- About to run `git reset --hard`
- About to run `git rebase` on shared branches
- About to delete remote branches

**Blocked operations** (require confirmation):
- Force push to main/master
- Hard reset
- Rebasing shared branches
- Deleting remote branches

**Location**: `~/.claude/skills/guarding-git-safety/SKILL.md`

---

### 3. guarding-ui-design

**Description**: "Prevents UI anti-patterns and suggests design improvements. TRIGGERS: When editing .tsx/.jsx/.vue/.css/.scss files or discussing UI/styling. ENFORCES: Avoids default fonts and clichés. SUGGESTS: Design principles (typography, color, motion, backgrounds). OUTPUT: User messages in Chinese at runtime; keep this file English-only."

**Purpose**:
- Prevent distributional convergence ("AI slop" appearance)
- Guide toward cohesive, maintainable aesthetics
- Support multiple design systems (Material Design, Tailwind, Chakra UI, etc.)

**Auto-triggers when**:
- Editing UI files (`.tsx`, `.jsx`, `.vue`, `.css`, `.scss`)
- Discussing UI components or styling
- Creating new frontend components

**Enforced (hard constraints)**:
- Avoid default fonts (Inter, Roboto, Open Sans, Lato, system-ui)
- Avoid purple gradients on white backgrounds
- Avoid hard-coded colors (use design tokens/CSS variables)
- Avoid inconsistent spacing

**Suggested (directional guidance)**:
- Typography: 3x+ size jumps, high-contrast font pairing
- Color: Design tokens, one dominant color with accents
- Motion: CSS-only first, orchestrated page load animations
- Design systems: Support Material Design, Tailwind, Chakra UI, Ant Design, custom
- Component libraries: MUI, Ant Design, Chakra, Radix, shadcn/ui
- Accessibility: WCAG 2.1 AA compliance

**Location**: `~/.claude/skills/guarding-ui-design/SKILL.md`

---

### 4. automating-e2e-tests

**Description**: "E2E test code generation via Playwright CLI. Auto-activates when keywords 'E2E test', 'browser automation', or 'Playwright' are mentioned."

**Purpose**: Generate Playwright test code (TypeScript), run via `npx playwright test`

**Auto-triggers when**: Keywords "E2E test", "browser automation", "Playwright" mentioned

**Capabilities**:
- Generates Playwright test code (TypeScript)
- Runs tests via Bash: `npx playwright test`
- Returns results in Chinese

**Token Cost**: ~100 tokens (frontmatter only, loads on-demand)

**Complete reference**: `~/.claude/skills/automating-e2e-tests/REFERENCE.md`

**Location**: `~/.claude/skills/automating-e2e-tests/SKILL.md`

---

### 5. syncing-docs

**Description**: "Auto-syncs documentation and manages knowledge archival. TRIGGERS when completing features, running /ultra-deliver, discussing documentation, or making architecture changes."

**Purpose**:
- Ensure documentation stays synchronized
- Archive important decisions
- Track technical debt

**Auto-triggers when**:
- Feature completion
- Running /ultra-deliver
- Discussing documentation
- Making architecture changes

**Actions**:
- Suggest updating README/API docs
- Archive decisions to `.ultra/docs/decisions/`
- Record technical debt
- Capture lessons learned

**Templates provided**:
- Decision logs (ADRs)
- Technical debt tracking
- Lessons learned format

**Location**: `~/.claude/skills/syncing-docs/SKILL.md`

---

### 6. guarding-test-coverage

**Description**: "Ensures comprehensive 6-dimensional test coverage. TRIGGERS when running /ultra-test, discussing testing/coverage, or marking features complete. BLOCKS task completion until all 6 dimensions covered."

**Purpose**:
- Enforce 6-dimensional test coverage
- Ensure 80% coverage minimum
- Block completion if tests insufficient

**Auto-triggers when**:
- Running /ultra-test
- Discussing testing or coverage
- Marking features as complete
- Before merging to main

**Six dimensions enforced**:
1. Functional (core logic)
2. Boundary (edge cases)
3. Exception (error handling)
4. Performance (load tests)
5. Security (input validation, injection prevention)
6. Compatibility (cross-browser, cross-platform)

**Coverage requirements**:
- Overall: ≥80%
- Critical paths: 100%
- Branch coverage: ≥75%

**Location**: `~/.claude/skills/guarding-test-coverage/SKILL.md`

---

### 7. routing-serena-operations

**Description**: "Intelligent router to Serena MCP based on file size, operation type, and task analysis. TRIGGERS: Before Read/Edit/Write operations on large files, or when discussing code understanding/refactoring. ACTIONS: Route to Serena MCP for optimal efficiency. BLOCKS: Unsafe text-based operations on large files."

**Purpose**:
- Route operations to optimal tools (Serena MCP vs built-in) based on file size and task type
- Prevent token overflow and errors on large files (>5000 lines)
- Provide explicit Serena MCP command examples

**Auto-triggers when**:
- About to use Read/Edit/Write tools on files >5000 lines
- Discussing cross-file refactoring or symbol-level operations
- Large codebase exploration tasks

**Key routing**:
- File size: <5K lines (Read) | 5-8K lines (suggest Serena) | >8K lines (enforce Serena)
- Operation type: Cross-file rename (enforce Serena) | Architecture understanding (suggest Serena)
- Project scale: >100 files (suggest Serena for exploration)

**Location**: `~/.claude/skills/routing-serena-operations/SKILL.md`

---

### 8. compressing-context

**Description**: "Proactively compresses context to prevent overflow. TRIGGERS: After 5+ tasks, OR token usage >120K. ACTIONS: Summarize completed tasks (15K→500 tokens), archive to .ultra/context-archive/. BLOCKS: ultra-dev if >170K without compression."

**Purpose**: Prevent context overflow, enable 20-30 tasks/session (vs 10-15 without)

**Auto-triggers when**: 5+ completed tasks, token usage >120K/140K/170K, before ultra-test/deliver

**Key thresholds**:
- <120K: Safe
- 120-140K: Suggest compression
- 140-170K: Strongly recommend
- >170K: BLOCK ultra-dev, ENFORCE compression

**Result**: 40-60% token savings, 50-100K freed per compression

**Location**: `~/.claude/skills/compressing-context/SKILL.md`

---

### 9. guiding-workflow

**Description**: "Guides next steps based on project state and Scenario B routing. TRIGGERS: After phase completion or user asks 'what's next'. ACTIONS: Detect research/plan/dev/test status via filesystem, detect Scenario B project type from ultra-research output, suggest the next /ultra-* command. OUTPUT: User messages in Chinese at runtime; keep this file English-only."

**Purpose**:
- Suggest the next logical command based on project state
- Detect project state via filesystem signals
- Support Scenario B intelligent routing (adapt suggestions based on project type)
- Prevent workflow skipping by proactive guidance

**Auto-triggers when**:
- After a phase completes (research, plan, dev, test, deliver)
- User asks for guidance or next steps
- User seems uncertain after command completion
- After /ultra-research completes (detect project type for tailored suggestions)

**State detection** (filesystem-based):
- Specification files: `specs/product.md`, `specs/architecture.md` (or old format: `.ultra/docs/prd.md`, `.ultra/docs/tech.md`)
- Research files: `.ultra/docs/research/*.md`
- Task plan: `.ultra/tasks/tasks.json`
- Code changes: `git status`
- Test files: `*.test.*`, `*.spec.*`
- Active changes: `.ultra/changes/task-*/`

**Scenario B integration** (NEW):

Detects project type from recent /ultra-research execution and adapts next-step suggestions accordingly.

**Detection mechanism**:
1. Reads latest research report in `.ultra/docs/research/`
2. Identifies project type keywords in report metadata or content
3. Maps to one of 4 project types: New Project, Incremental Feature, Tech Decision, Custom Flow

**Project type routing**:

| Project Type | Detected Keywords | Next-Step Strategy |
|--------------|-------------------|-------------------|
| **New Project** | "New Project" | Suggest `/ultra-plan` after all 4 rounds complete |
| **Incremental Feature** | "Incremental Feature" | Suggest `/ultra-plan` after Round 2-3 complete |
| **Tech Decision** | "Tech Decision" | Suggest validating choice or proceeding to implementation |
| **Custom Flow** | "Custom" | Suggest next step based on user-selected rounds completed |

**Suggestion examples** (Chinese output at runtime):

**After New Project research** (4 rounds complete):
```
Current status:
- ✅ Research complete (4-round full process)
- ✅ specs/product.md 100% complete
- ✅ specs/architecture.md 100% complete

Suggested next step: /ultra-plan
Rationale: Specifications complete, can start task planning
```

**After Incremental Feature research** (2 rounds complete):
```
Current status:
- ✅ Solution exploration complete (Round 2)
- ✅ Technology selection complete (Round 3)
- ✅ specs/product.md partially complete

Suggested next step: /ultra-plan
Rationale: Incremental feature requirements clear, can plan implementation tasks
```

**After Tech Decision research** (1 round complete):
```
Current status:
- ✅ Technology selection complete (Round 3)
- ✅ specs/architecture.md updated

Suggested next step: /ultra-plan or direct implementation
Rationale: Tech stack determined, can plan implementation tasks
```

**OUTPUT: User messages in Chinese at runtime; keep this file English-only.**

**Integration with ultra-research**:
- ultra-research saves project type to research report metadata
- guiding-workflow reads metadata when triggered
- Adapts suggestions to match user's chosen research flow
- Prevents suggesting skipped rounds (e.g., don't suggest Round 1 for Incremental Feature)

**Output format** (in Chinese at runtime):
- Current project state summary (bullet points)
- Next step recommendation with clear rationale
- Optional: Alternative paths if multiple valid next steps

**Location**: `~/.claude/skills/guiding-workflow/SKILL.md`

---

### 10. enforcing-workflow

**Description**: "Enforces mandatory independent-branch workflow. TRIGGERS when discussing git branches, workflow strategy, or task management. BLOCKS any suggestion of unified/long-lived branches or workflow 'options'. ENFORCES one-task-one-branch-merge-delete cycle. OUTPUT: User messages in Chinese at runtime; keep this file English-only."

**Purpose**:
- Prevent AI from suggesting alternative workflows that violate mandatory strategy
- Enforce independent-branch workflow (one-task-one-branch-merge-delete)
- Block unified/batch branch strategies
- Ensure main branch stays deployable for hotfixes

**Auto-triggers when**:
- Discussing git workflow or branch strategy
- AI is about to suggest workflow "options" or "choices"
- Discussion involves multiple tasks and branch management
- Keywords: "unified", "batch", "option", "workflow choice", "merge timing"

**Enforcement rules**:

**IMMEDIATELY BLOCK if AI attempts to**:
- Present workflow alternatives ("Option 1 vs Option 2", "Workflow A vs Workflow B")
- Suggest unified/long-lived branches for multiple tasks
- Recommend delaying merges until "all tasks complete"
- Suggest freezing main branch for batch deployment
- Propose "feature branch with multiple tasks"

**ENFORCE mandatory workflow**:
```
main (always active, never frozen)
 ├── feat/task-1-xxx (create → complete → merge → delete)
 ├── feat/task-2-yyy (create → complete → merge → delete)
 └── feat/task-3-zzz (create → complete → merge → delete)
```

**Rules**:
- Each task = independent branch (`feat/task-{id}-{description}`)
- Complete task → merge to main → delete branch
- Main branch always deployable (for hotfixes)
- NO unified branches, NO batch merges, NO workflow choices

**Rationale** (why mandatory):
1. **Production Reality**: Hotfixes cannot wait for feature completion
2. **Parallel Work**: Multiple developers work independently
3. **Isolated Rollbacks**: Problematic features can be reverted independently
4. **Continuous Deployment**: Main always deployable enables CD/CD
5. **Code Review**: Smaller, focused PRs are easier to review

**Output format**:
- Warning header (⚠️ Workflow Non-Negotiable Reminder)
- Explanation of mandatory workflow
- Forbidden patterns list

**OUTPUT: User messages in Chinese at runtime; keep this file English-only.**
- Rationale
- Reference to documentation

**Location**: `~/.claude/skills/enforcing-workflow/SKILL.md`

---

## Skills Best Practices

### Writing Effective Skill Descriptions

Based on official Claude Code best practices:

1. **Be specific**: Include concrete trigger conditions
   - Good: "TRIGGERS when editing .tsx/.jsx files or discussing UI components"
   - Bad: "Helps with UI work"

2. **Use action keywords**: TRIGGERS, MONITORS, ENFORCES, BLOCKS, SUGGESTS
   - Makes matching more reliable

3. **Include examples**: Mention specific scenarios
   - "USE WHEN: User completes research/plan/dev/test"

---

## Skills Modes

Ultra Builder Pro supports two documentation styles for Skills. Choose based on token budget and precision needs.

### 1) Slim Mode (recommended)
- Keep `SKILL.md` minimal: Purpose, When, Do, Don't, Outputs
- Include negative triggers (what NOT to trigger on) to reduce false positives
- Move detailed rules/examples to `guidelines/` and reference via `@import` when needed
- Benefits: Lower steady-state token footprint; fewer misfires

### 2) Verbose Mode
- Self-contained `SKILL.md` with detailed rules and examples
- Higher token cost; useful for teams without separate guidelines

Default: `skills.mode = "slim"` (see CLAUDE.md Project Config Overrides). Keep all `SKILL.md` files English-only; at runtime, user-visible messages should be in Chinese (simplified).

**Complete configuration guide**: `@config/ultra-skills-modes.md` for migration, best practices, and token efficiency comparison

4. **Third person**: Write in third person for clarity
   - Good: "Detects code quality violations"
   - Bad: "I detect code quality violations"

5. **Length limit**: Max 1024 characters for description
   - Keep it concise but specific

### SKILL.md Content Guidelines

Based on official best practices:

1. **Keep under 500 lines**: Split larger content into reference files
2. **Use English for system instructions**: Optimal AI performance
3. **Chinese for user-facing output**: As per Language Protocol
4. **Progressive disclosure**: Reference detailed docs externally
5. **Concrete examples**: Show input/output patterns

---

## Skills vs Agents

### When to Use Skills

- **Automated quality checks**: SOLID violations, code smells
- **Safety enforcement**: Git workflow guards
- **Standards enforcement**: UI design rules, test coverage
- **Continuous monitoring**: Context overflow, performance

### When to Use Agents

- **Complex research tasks**: Technology comparisons
- **Architecture design**: System design decisions
- **Deep analysis**: Performance bottleneck investigation
- **Strategic planning**: Test strategy design

**Key difference**: Skills are **reactive guards**, Agents are **proactive experts**.

---

## Troubleshooting Skills

### Skill Not Triggering

**Possible causes**:
1. Description too vague → Make more specific
2. Missing trigger keywords → Add TRIGGERS, USE WHEN
3. SKILL.md too long (>500 lines) → Split into smaller files
4. Wrong language mixing → Use English for instructions

**Fix**: Update skill description with clearer trigger conditions

### Skill Triggering Too Often

**Possible causes**:
1. Description too broad → Narrow down scope
2. Too many trigger keywords → Be more selective

**Fix**: Refine description to be more specific

### Multiple Skills Conflicting

**Solution**: Skills can run concurrently—conflicts are rare. If they occur, adjust allowed-tools to create boundaries.

---

## Skills Configuration Reference

### Official Documentation

- Skills overview: https://docs.claude.com/en/docs/agents-and-tools/agent-skills/skills-overview
- Best practices: https://docs.claude.com/en/docs/agents-and-tools/agent-skills/best-practices

### Example Skill Structure

```
~/.claude/skills/
├── code-quality-guardian/
│   ├── SKILL.md              # Main skill file (<500 lines)
│   ├── reference.md          # Detailed reference (optional)
│   └── examples.md           # Code examples (optional)
├── git-workflow-guardian/
│   └── SKILL.md
└── [... 7 more skills]
```

---

**Remember**: Skills are your automated quality guardians. They work silently in the background, ensuring standards are met without manual intervention.
