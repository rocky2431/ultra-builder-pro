# OpenSpec Research Report: Spec-Driven Development Analysis

**Date**: 2025-12-28
**Focus**: Core philosophy, directory structure, workflow patterns, context engineering, and anti-patterns prevention
**Purpose**: Extract actionable patterns for Claude Code development systems

---

## Executive Summary

OpenSpec implements a **spec-driven development (SDD)** framework that treats specifications as executable contracts preceding code implementation. The core innovation is a **two-folder architecture** separating source-of-truth specifications (`specs/`) from proposed changes (`changes/`), enabling delta-based context engineering that optimizes LLM token efficiency while maintaining audit trails. This approach addresses the fundamental problem of AI unpredictability when requirements exist only in chat history.

**Key Metrics**: 11k GitHub stars, 803 forks, active development (Dec 2025), MIT licensed, supports 20+ AI coding assistants including Claude Code.

---

## 1. Core Philosophy

### Fundamental Principle

> **"Agree on what to build before any code is written"**

OpenSpec addresses the core challenge that **LLMs are exceptional at pattern completion, but not at mind reading**. Vague prompts force models to guess at potentially thousands of unstated requirements, leading to unpredictable outputs.

### Philosophy in Three Parts

1. **Specifications as First-Class Artifacts**
   - Specs are not static documents but living, executable artifacts that evolve with the project
   - They become the shared source of truth between humans and AI agents
   - Specifications exist independently of implementation, enabling review and alignment before coding

2. **Intent Locking Before Implementation**
   - Structured change folders (proposals, tasks, spec updates) keep scope explicit and auditable
   - Human and AI stakeholders reach agreement on specs before work begins
   - Reduces AI hallucination and scope creep through upfront clarity

3. **Delta-Based Change Management**
   - Changes are isolated workspaces showing explicit diffs against current state
   - Enables granular tracking across multi-spec features without polluting source files
   - Supports parallel feature development without merge conflicts in core specs

### Comparative Positioning

| Approach | When It Works | When It Fails |
|----------|---------------|---------------|
| **Chat-history prompts** | Simple, one-shot tasks | Complex features, team collaboration, long-term maintenance |
| **OpenSpec (SDD)** | Feature additions, refactoring, brownfield codebases (1→n evolution) | Highly exploratory work, rapidly changing requirements, novel algorithms |
| **spec-kit** | Greenfield projects (0→1 creation) | Modifying existing features, cross-spec updates |
| **Kiro** | Single-feature development | Updates spanning multiple specifications |

**OpenSpec's niche**: Excels at modifying existing behavior (1→n) and cross-cutting changes, addressing gaps in greenfield-focused tools.

---

## 2. Directory Structure

### Complete Architecture

```
openspec/
├── specs/                          # SOURCE OF TRUTH (current state)
│   └── [domain]/                   # Capability groupings (e.g., auth, payments)
│       └── spec.md                 # Markdown requirements with scenarios
│
├── changes/                        # PROPOSALS (work in progress)
│   └── [feature-name]/             # Isolated change workspace
│       ├── proposal.md             # Why, what, impact, tradeoffs
│       ├── tasks.md                # Implementation checklist
│       ├── design.md               # Technical decisions (optional)
│       └── specs/                  # Specification deltas
│           └── [domain]/
│               └── spec.md         # ADDED/MODIFIED/REMOVED sections
│
├── archive/                        # HISTORY (completed changes)
│   └── [timestamp]-[feature]/      # Timestamped snapshots
│       └── [all files from changes/]
│
├── project.md                      # Project-wide conventions
│                                   # - Coding standards
│                                   # - Architectural patterns
│                                   # - Technology stack decisions
│                                   # - Naming conventions
│
└── AGENTS.md                       # AI assistant instructions
                                    # - Auto-generated from templates
                                    # - Shared across all AI tools
                                    # - Read-first context for agents
```

### Key Design Decisions

#### 1. Two-Folder Separation (specs/ vs changes/)

**Problem Solved**: In traditional workflows, proposed changes mix with current state, making diffs unclear and requiring careful tracking of what's approved vs. pending.

**Solution**:
- `specs/` = immutable truth (only updated via archive command)
- `changes/` = mutable proposals (iterated until alignment)

**Benefit**: Explicit scope separation; can list all pending changes (`openspec list`), review independently, and merge atomically.

#### 2. Domain-Based Spec Organization

**Structure**: `specs/[domain]/spec.md`

**Examples**:
- `specs/auth/spec.md` — Authentication, authorization, session management
- `specs/payments/spec.md` — Payment processing, refunds, invoicing
- `specs/notifications/spec.md` — Email, SMS, push notifications

**Rationale**:
- Groups related requirements by business capability
- Reduces cognitive load when reviewing changes
- Enables parallel work on different domains without conflicts

#### 3. Feature-Based Change Folders

**Structure**: `changes/[feature-name]/`

**Naming Convention**: Kebab-case descriptive names (e.g., `add-two-factor-authentication`, `fix-memory-leak-in-cache`)

**Contents**:
- `proposal.md` — Rationale, scope, impact analysis, tradeoffs
- `tasks.md` — Implementation checklist with dependencies
- `design.md` — Technical decisions, architecture diagrams (optional)
- `specs/[domain]/spec.md` — Delta showing only changes

**Rationale**:
- All change artifacts colocated in one folder
- Easy to archive or delete incomplete proposals
- Clear audit trail when changes are completed

#### 4. Timestamped Archive

**Structure**: `archive/[YYYY-MM-DD]-[feature-name]/`

**Purpose**:
- Historical record of all completed changes
- Enables rollback if needed
- Documents decision-making process over time
- Compliance and audit trail

---

## 3. Workflow Pattern

### Five-Phase Cycle

```
1. DRAFT        →  2. REVIEW & REFINE  →  3. ALIGN  →  4. IMPLEMENT  →  5. ARCHIVE
   (Proposal)       (Iterate specs)        (Approve)    (Execute)        (Merge)
```

#### Phase 1: Draft Proposal

**Command**: `/openspec:proposal [feature description]`

**AI Actions**:
1. Creates `changes/[feature-name]/` folder
2. Generates `proposal.md` with:
   - **Why**: Business justification
   - **What**: High-level description
   - **Impact**: Affected systems, risks, tradeoffs
3. Scaffolds `tasks.md` with preliminary checklist
4. Creates spec deltas in `specs/[domain]/spec.md` showing:
   - `## ADDED Requirements`
   - `## MODIFIED Requirements`
   - `## REMOVED Requirements`

**Example** (Two-Factor Authentication):
```markdown
# changes/add-two-factor-authentication/proposal.md

## Why
Current authentication relies solely on username/password, making accounts vulnerable to credential theft. Two-factor authentication (2FA) significantly reduces unauthorized access risk.

## What
Add OTP-based 2FA as optional security feature:
- SMS or authenticator app delivery
- Backup codes for account recovery
- Admin override capability

## Impact
- **Users**: Optional enrollment via settings
- **Auth flow**: Adds 2FA verification step after password
- **Database**: New tables for OTP secrets and backup codes
- **Dependencies**: Requires Twilio integration for SMS

## Tradeoffs
- Increased login friction for users enabling 2FA
- Ongoing SMS costs (~$0.0075 per message)
- Additional security surface (Twilio dependency)
```

**File Structure After Phase 1**:
```
changes/add-two-factor-authentication/
├── proposal.md
├── tasks.md
└── specs/
    └── auth/
        └── spec.md  # Delta with ADDED Requirements
```

#### Phase 2: Review & Refine

**Human-AI Iteration Loop**:

1. **Human reviews** `proposal.md` and spec deltas
2. **Requests clarifications**: "What happens if SMS delivery fails?"
3. **AI updates** specs with new scenarios:
   ```markdown
   #### Scenario: SMS Delivery Failure
   - **WHEN** Twilio reports delivery failure after 3 retries
   - **THEN** system falls back to backup codes and notifies user via email
   ```
4. **Human approves** or requests further refinement
5. Repeat until alignment achieved

**Common Refinements**:
- Edge case handling (network failures, concurrent logins)
- Performance requirements (OTP verification <500ms)
- Security constraints (rate limiting, secret rotation)
- UX considerations (remember device for 30 days)

#### Phase 3: Align

**Approval Checklist**:
- [ ] Proposal rationale is clear and justified
- [ ] All stakeholders reviewed spec deltas
- [ ] Tasks are feasible and well-scoped
- [ ] No [NEEDS CLARIFICATION] markers remain
- [ ] Validation passes: `openspec validate add-two-factor-authentication --strict`

**Command**: `openspec validate [change] --strict`

**Validation Checks**:
- All requirements have `### Requirement:` header
- Each requirement has at least one `#### Scenario:` block
- Delta format follows ADDED/MODIFIED/REMOVED structure
- No orphaned files in change folder

#### Phase 4: Implement

**Command**: `/openspec:apply [change-name]`

**AI Implementation Pattern**:

1. **Read context in order**:
   - `openspec/project.md` — conventions and stack
   - `specs/[domain]/spec.md` — current state
   - `changes/[change]/proposal.md` — what to build
   - `changes/[change]/tasks.md` — implementation steps

2. **Execute tasks sequentially**:
   ```markdown
   # tasks.md
   - [x] Create database migration for otp_secrets table
   - [x] Implement OTP generation service
   - [x] Add 2FA enrollment endpoint
   - [ ] Update login flow with OTP verification
   - [ ] Write unit tests for OTP service
   - [ ] Add E2E tests for 2FA flow
   ```

3. **Mark completion**: Check off tasks as implemented

**Key Principle**: Tasks.md is the **single source of truth** during implementation. AI follows checklist strictly rather than deviating into unrelated refactoring.

#### Phase 5: Archive

**Command**: `/openspec:archive [change-name]` or `openspec archive [change-name]`

**Archive Process**:

1. **Validate completion**:
   - All tasks marked complete
   - All tests passing
   - No [NEEDS CLARIFICATION] markers

2. **Merge spec deltas**:
   - Apply ADDED requirements to source specs
   - Replace MODIFIED requirements in source specs
   - Remove REMOVED requirements from source specs

3. **Create archive snapshot**:
   ```
   archive/2025-12-28-add-two-factor-authentication/
   ├── proposal.md
   ├── tasks.md
   └── specs/
       └── auth/
           └── spec.md  # Delta as it was before merge
   ```

4. **Clean up changes folder**:
   - Delete `changes/add-two-factor-authentication/`

5. **Update AGENTS.md** if project conventions changed

**Result**: Source specs updated, change archived, workspace cleaned.

---

## 4. Context Engineering

### Core Problem

**LLMs lack persistent memory**, leading to:
- Context decay over long sessions
- Inconsistent outputs when chat history grows
- Token cost escalation with full codebase injection

### OpenSpec's Solution: Delta-Based Context Strategy

#### Token Efficiency Through Deltas

**Traditional Approach** (inefficient):
```
LLM Context = Full codebase + Chat history + Current task
Token Cost: 50,000+ tokens per request
```

**OpenSpec Approach** (optimized):
```
LLM Context = project.md + Relevant spec.md + Change delta
Token Cost: 2,000-5,000 tokens per request
```

**Efficiency Gain**: 90%+ token reduction by focusing only on isolated spec deltas rather than full massive codebase.

#### Context Hierarchy (Read Order)

When AI begins any task, it consumes context in this priority order:

1. **Global Project Context** (`openspec/project.md`)
   - Technology stack (React 18, Node.js 20, PostgreSQL 15)
   - Coding standards (TypeScript strict mode, ESLint rules)
   - Architectural patterns (Clean Architecture, Dependency Injection)
   - Naming conventions (camelCase for variables, PascalCase for classes)

2. **Current State** (`specs/[domain]/spec.md`)
   - Existing requirements and scenarios
   - Behavioral contracts already implemented
   - Integration points with other domains

3. **Proposed Changes** (`changes/[feature]/`)
   - `proposal.md` — Why and what
   - `tasks.md` — How (implementation steps)
   - `specs/[domain]/spec.md` — Delta (ADDED/MODIFIED/REMOVED)

4. **Agent Instructions** (`AGENTS.md`)
   - Auto-generated prompts for AI tools
   - Workflow commands and conventions
   - Tool-specific integration points

#### Context as Executable Contract

**Specifications use semantic language** for deterministic parsing:

- **"The system SHALL..."** — Requirements (must be implemented)
- **"The system MUST..."** — Mandatory constraints (non-negotiable)
- **"The system SHOULD..."** — Recommended behavior (preferred but flexible)
- **"The system MAY..."** — Optional capabilities

**Example**:
```markdown
### Requirement: OTP Verification

The system SHALL verify one-time passwords within 500ms response time.

#### Scenario: Valid OTP Submitted
- **WHEN** user submits valid 6-digit OTP within 5-minute window
- **THEN** system authenticates user and issues session token

#### Scenario: Expired OTP
- **WHEN** user submits OTP after 5-minute expiration
- **THEN** system rejects with error "Code expired" and allows retry
```

#### Persistent Memory Through Specs

**Problem Solved**: Chat history is ephemeral; specs are durable.

**Implementation**:
- All decisions documented in `specs/` (source of truth)
- All change rationale preserved in `archive/` (historical record)
- All project conventions in `project.md` (shared context)

**Result**: New AI session can resume work by reading specs, no context reconstruction needed.

---

## 5. Anti-Patterns Prevented

### 1. Chat-History Dependency

**Problem**: Requirements buried in 50-message conversation, lost when session ends.

**OpenSpec Prevention**:
- All requirements in `specs/[domain]/spec.md`
- All change context in `changes/[feature]/proposal.md`
- Durable, version-controlled, searchable

### 2. Scope Creep

**Problem**: AI adds unrelated features or refactors unrelated code.

**OpenSpec Prevention**:
- `tasks.md` defines explicit scope
- Deltas show only changed requirements
- Approval gate before implementation (Phase 3: Align)

### 3. Implicit Assumptions

**Problem**: AI makes unstated assumptions about behavior, leading to misaligned implementations.

**OpenSpec Prevention**:
- Scenario blocks force explicit behavior documentation
- "WHEN → THEN" format removes ambiguity
- Review phase catches missing edge cases

**Example**:
```markdown
# Bad (implicit): "User can reset password"

# Good (explicit):
### Requirement: Password Reset

The system SHALL allow users to reset forgotten passwords via email.

#### Scenario: Valid Reset Request
- **WHEN** user requests password reset with registered email
- **THEN** system sends reset link valid for 1 hour

#### Scenario: Invalid Email
- **WHEN** user requests reset with unregistered email
- **THEN** system shows generic "Check email" message (security: no user enumeration)

#### Scenario: Expired Link
- **WHEN** user clicks reset link after 1 hour
- **THEN** system rejects with "Link expired" and offers new request
```

### 4. Undocumented Technical Debt

**Problem**: Quick hacks implemented without recording rationale, causing maintenance nightmares.

**OpenSpec Prevention**:
- `proposal.md` documents tradeoffs upfront
- `design.md` captures technical decisions
- Archive preserves "why" context for future maintainers

**Example** (`proposal.md` excerpt):
```markdown
## Tradeoffs

### SMS Provider Lock-in
We're coupling to Twilio API for MVP. Future refactoring to support multiple providers will require interface abstraction.

**Rationale**: Twilio has 99.95% uptime SLA and simplest integration. Multi-provider support adds 2 weeks to timeline for uncertain ROI.

**Exit Strategy**: When 2nd provider needed, extract `IOtpDeliveryService` interface with Twilio and competitor implementations.
```

### 5. Lost Context Across Tools

**Problem**: Different team members use different AI tools (Cursor, Claude Code, GitHub Copilot), leading to inconsistent outputs.

**OpenSpec Prevention**:
- `AGENTS.md` provides unified instructions for all AI tools
- Specs are tool-agnostic (markdown format)
- 20+ native integrations ensure consistent workflows

### 6. Uncontrolled Refactoring

**Problem**: AI refactors unrelated code while implementing feature, causing unexpected regressions.

**OpenSpec Prevention**:
- Deltas explicitly list MODIFIED requirements
- Anything not in delta is off-limits
- Tasks.md constrains scope to checklist items

### 7. Merge Conflicts in Collaborative Development

**Problem**: Multiple developers working on overlapping features cause spec conflicts.

**OpenSpec Prevention**:
- Change folders isolate proposed modifications
- Parallel changes don't touch `specs/` until archive
- Merge conflicts happen in proposal phase, not code phase

**Example** (Parallel Changes):
```
changes/add-two-factor-authentication/
  └── specs/auth/spec.md  # Delta A

changes/add-social-login/
  └── specs/auth/spec.md  # Delta B

# Both propose changes to specs/auth/spec.md
# Conflicts resolved in review phase before implementation
# Archive happens sequentially: A first, then B rebases on updated specs/
```

### 8. Incomplete Feature Implementation

**Problem**: AI implements 80% of feature, forgets edge cases, ships incomplete code.

**OpenSpec Prevention**:
- `tasks.md` checklist prevents partial completion
- Scenarios document all edge cases upfront
- Archive validation requires all tasks complete

### 9. Lack of Audit Trail

**Problem**: Six months later, no one remembers why certain decisions were made.

**OpenSpec Prevention**:
- `archive/` preserves full change history
- `proposal.md` documents decision rationale
- Git history shows spec evolution over time

**Example Query**: "Why did we choose Twilio over AWS SNS for SMS?"

**Answer**: `archive/2025-12-28-add-two-factor-authentication/proposal.md` → Tradeoffs section.

---

## 6. Spec Delta Format Specification

### Three Delta Types

#### 1. ADDED Requirements (New Capabilities)

**Format**:
```markdown
## ADDED Requirements

### Requirement: [Feature Name]
The system SHALL/MUST [behavior statement].

#### Scenario: [Context]
- **WHEN** [condition]
- **THEN** [expected outcome]

#### Scenario: [Another Context]
- **WHEN** [different condition]
- **THEN** [different outcome]
```

**Example**:
```markdown
## ADDED Requirements

### Requirement: Backup Codes

The system SHALL generate 10 single-use backup codes when user enables 2FA.

#### Scenario: User Loses Authenticator Device
- **WHEN** user cannot access OTP device but has backup code
- **THEN** system accepts backup code as alternative authentication factor

#### Scenario: All Backup Codes Consumed
- **WHEN** user has used all 10 backup codes
- **THEN** system prompts admin override or account recovery flow
```

#### 2. MODIFIED Requirements (Behavior Changes)

**Critical Rule**: Paste the **full updated requirement** (header + all scenarios). Partial deltas will drop previous details when archived.

**Format**:
```markdown
## MODIFIED Requirements

### Requirement: [Existing Name]  # Must match exactly (whitespace-insensitive)
[Complete updated description]

#### Scenario: [Updated or New]
- **WHEN** [updated condition]
- **THEN** [updated outcome]

#### Scenario: [Preserved]
- **WHEN** [unchanged condition]
- **THEN** [unchanged outcome]
```

**Example**:
```markdown
## MODIFIED Requirements

### Requirement: Login Flow  # Existing requirement in specs/auth/spec.md

The system SHALL authenticate users via username/password with optional 2FA.

#### Scenario: 2FA Enabled User Login
- **WHEN** user with 2FA submits valid password
- **THEN** system prompts for OTP before issuing session token

#### Scenario: 2FA Disabled User Login
- **WHEN** user without 2FA submits valid password
- **THEN** system issues session token immediately (existing behavior preserved)
```

**Common Error**: Submitting partial diff like "Add 2FA step" without including full requirement block.

#### 3. REMOVED Requirements (Deprecations)

**Format**:
```markdown
## REMOVED Requirements

### Requirement: [Deprecated Feature Name]

**Rationale**: [Why being removed]

**Migration**: [How users should adapt]
```

**Example**:
```markdown
## REMOVED Requirements

### Requirement: SMS-Only 2FA

**Rationale**: Deprecating SMS-exclusive 2FA in favor of authenticator app support due to SIM-swapping vulnerability concerns.

**Migration**: Existing SMS users will be prompted to enable authenticator app on next login. SMS will remain available as fallback until 2026-06-01.
```

#### 4. RENAMED Requirements (Name Changes Only)

**Format**:
```markdown
## RENAMED Requirements

- FROM: `### Requirement: [Old Name]`
- TO: `### Requirement: [New Name]`
```

**Example**:
```markdown
## RENAMED Requirements

- FROM: `### Requirement: Login`
- TO: `### Requirement: User Authentication`
```

### Validation Rules

**All requirements must**:
1. Use `### Requirement:` header (level-3)
2. Have at least one `#### Scenario:` block (level-4)
3. Use WHEN → THEN format for scenarios
4. Reside under `## ADDED|MODIFIED|REMOVED Requirements` section

**Command**: `openspec validate [change] --strict`

**Common Failures**:
- Missing scenario: "Requirement must have at least one scenario"
- Wrong heading level: Using bullets or bold instead of `####`
- Partial MODIFIED: Missing full requirement content
- Typo in requirement name: MODIFIED name doesn't match existing spec

---

## 7. Actionable Patterns for Claude Code Systems

### Pattern 1: Two-Folder Architecture

**Adopt**:
```
.ultra/
├── specs/                    # Current state (OpenSpec pattern)
│   ├── product.md
│   └── architecture.md
├── changes/                  # Proposed modifications (OpenSpec pattern)
│   └── [feature-name]/
│       ├── proposal.md
│       ├── tasks.md
│       └── specs/
│           └── [delta].md
└── archive/                  # Completed changes (OpenSpec pattern)
```

**Benefits**:
- Explicit separation of truth vs. proposals
- Parallel feature development without conflicts
- Clear audit trail

**Migration Path**: Keep existing `.ultra/specs/` as source of truth, add `.ultra/changes/` for new workflow.

### Pattern 2: Delta-Based Context Engineering

**Implement**:
- Instead of injecting full specs into every LLM call, inject only deltas
- Reduce token usage by 90%+
- Enable longer sessions before context overflow

**Example**:
```typescript
// Current (inefficient)
const context = readFullSpecs() + readFullTasks() + readFullDocs();

// OpenSpec pattern (efficient)
const context = readProjectMd() + readSpecDelta() + readTasksMd();
```

### Pattern 3: Scenario-Based Acceptance Criteria

**Adopt WHEN → THEN format**:
```markdown
### Requirement: User Registration

#### Scenario: Successful Registration
- **WHEN** user submits valid email and strong password
- **THEN** system creates account and sends verification email

#### Scenario: Duplicate Email
- **WHEN** user submits email already in system
- **THEN** system rejects with "Email already registered" error
```

**Benefits**:
- Forces explicit edge case documentation
- Removes ambiguity for LLM interpretation
- Directly translates to test scenarios

### Pattern 4: Approval Gate Before Implementation

**Current Ultra Builder Pro**: `/ultra-plan` → `/ultra-dev` (immediate implementation)

**OpenSpec Pattern**: `/ultra-plan` → **Review & Align** → `/ultra-dev`

**Implement**:
```bash
/ultra-plan [feature]
# AI generates proposal.md + tasks.md + spec deltas

# NEW STEP: Human reviews and approves
/ultra-validate [feature]  # Validates spec format
# Human approves via comment or command

/ultra-dev [feature]  # Only proceeds after approval
```

### Pattern 5: Archive Command for Context Compression

**Adopt**:
```bash
/ultra-archive [feature]
# Merges spec deltas into source specs
# Moves change folder to archive/[timestamp]-[feature]/
# Compresses context by removing completed change artifacts
```

**Benefits**:
- Natural context compression (aligns with existing `compressing-context` skill)
- Preserves decision history
- Enables session recovery from archive index

### Pattern 6: Project.md as Shared Context

**Implement**:
```
.ultra/
└── project.md  # New file (OpenSpec pattern)
    ├── Technology Stack
    ├── Coding Standards
    ├── Architectural Patterns
    ├── Naming Conventions
    └── Quality Gates
```

**Read-first pattern**: AI reads `project.md` before any task to load project conventions.

**Benefits**:
- Consistent AI behavior across sessions
- Reduces need to repeat conventions in every prompt
- Single source of truth for project standards

### Pattern 7: AGENTS.md Auto-Generation

**Adopt**:
```
.ultra/
└── AGENTS.md  # Auto-generated from ultra-skills
    ├── Available Commands
    ├── Workflow Phases
    ├── Quality Standards
    └── Tool Integration Points
```

**Use Case**: When user switches from Claude Code to Cursor or GitHub Copilot, `AGENTS.md` provides unified instructions.

### Pattern 8: Validation Command

**Implement**:
```bash
/ultra-validate [feature]
# Checks:
# - All requirements have scenarios
# - All tasks are achievable
# - No [NEEDS CLARIFICATION] markers
# - Spec format follows standards
```

**Benefits**:
- Catches incomplete specs before implementation
- Reduces wasted implementation cycles
- Forces specification quality

### Pattern 9: Task Completion Tracking

**Current**: `tasks.json` with status field

**OpenSpec Pattern**: `tasks.md` with checkboxes

**Adopt Hybrid**:
```markdown
# .ultra/tasks/[feature]/tasks.md

- [x] Create database migration
- [x] Implement service layer
- [ ] Add API endpoints
- [ ] Write tests
```

**Benefit**: Markdown format is more LLM-friendly, supports comments inline, easier to review.

### Pattern 10: Timestamped Archive with Index

**Implement**:
```
.ultra/
└── archive/
    ├── 2025-12-28-add-two-factor-auth/
    │   ├── proposal.md
    │   ├── tasks.md
    │   └── specs/
    └── archive-index.json  # Quick lookup
```

**Index Format**:
```json
{
  "2025-12-28-add-two-factor-auth": {
    "completed": "2025-12-28T14:30:00Z",
    "domains": ["auth"],
    "summary": "Added OTP-based 2FA with backup codes"
  }
}
```

**Benefits**:
- Fast historical lookup without reading full archives
- Enables "why was this decision made?" queries
- Supports compliance and audit requirements

---

## 8. Comparison: Ultra Builder Pro vs. OpenSpec

| Aspect | Ultra Builder Pro (Current) | OpenSpec Pattern | Recommendation |
|--------|----------------------------|------------------|----------------|
| **Spec Organization** | `specs/product.md`, `specs/architecture.md` | `specs/[domain]/spec.md` | Hybrid: Keep current for MVP, adopt domain-based for complex projects |
| **Change Management** | Direct edit specs → implement | Propose changes → review → implement | **Adopt**: Add `changes/` folder for review phase |
| **Context Compression** | Archive full task history | Archive change deltas only | **Adopt**: Delta-based archival saves tokens |
| **Task Format** | `tasks.json` (JSON structure) | `tasks.md` (Markdown checklist) | **Consider**: Markdown is more LLM-friendly |
| **Approval Gates** | Optional (can skip to dev) | Required validation step | **Adopt**: Add `/ultra-validate` command |
| **Project Context** | `.ultra/constitution.md` | `project.md` | **Align**: Rename or dual-maintain for compatibility |
| **Multi-Tool Support** | Claude Code focused | 20+ tools via AGENTS.md | **Enhance**: Generate AGENTS.md for cross-tool usage |
| **Archive Strategy** | Session-based compression | Feature-based archival | **Hybrid**: Both approaches have value |

---

## 9. Implementation Roadmap for Ultra Builder Pro

### Phase 1: Foundation (Week 1-2)

**Add OpenSpec-compatible structure**:
```bash
# New files to create
.ultra/
├── changes/            # New folder
├── archive/            # New folder (replace context-archive)
└── project.md          # New file (auto-generated from constitution.md)
```

**Commands to add**:
- `/ultra-propose [feature]` — Create change proposal (OpenSpec proposal pattern)
- `/ultra-validate [feature]` — Validate spec format before implementation

**Backward Compatibility**: Keep existing `.ultra/tasks/tasks.json`, add `.ultra/changes/` as optional path.

### Phase 2: Delta-Based Context (Week 3-4)

**Implement**:
- Spec delta format (ADDED/MODIFIED/REMOVED)
- Token-efficient context injection (only load deltas during `/ultra-dev`)
- Archive command with delta merging

**Metric**: Measure token reduction in typical workflows.

### Phase 3: Multi-Tool Support (Week 5-6)

**Generate AGENTS.md**:
- Auto-generated from Ultra Builder Pro Skills
- Include command reference, workflow phases, quality standards
- Test with Cursor, GitHub Copilot, Cline

**Benefit**: Users can switch AI tools without losing workflow consistency.

### Phase 4: Validation & Quality Gates (Week 7-8)

**Implement**:
- Scenario-based acceptance criteria validation
- Pre-implementation approval workflow
- Archive index for historical lookup

**Integration**: Enhance `guarding-quality` skill to validate spec format.

---

## 10. Key Takeaways

### For Claude Code Development Systems

1. **Separate Proposals from Truth**: Two-folder architecture prevents premature commitment
2. **Delta-Based Context**: 90%+ token reduction by focusing on changes, not full state
3. **Approval Gates**: Review phase before implementation catches misalignment early
4. **Scenario-Driven Specs**: WHEN → THEN format removes ambiguity for LLMs
5. **Archive as Memory**: Completed changes preserved for audit and learning
6. **Tool-Agnostic Design**: AGENTS.md enables workflow portability across 20+ AI tools

### For Spec-Driven Development

1. **Specs are First-Class Artifacts**: Not documentation afterthought, but development driver
2. **Alignment Before Implementation**: Agreement on "what" before "how" reduces waste
3. **Explicit Beats Implicit**: Scenario blocks force edge case documentation
4. **Durable Context**: Specs outlive chat history, enabling session recovery
5. **Brownfield-Ready**: Works for existing codebases, not just greenfield projects

### Anti-Patterns to Avoid

1. ❌ **Chat-history dependency**: Requirements must live in version-controlled specs
2. ❌ **Skipping review phase**: Implementing before alignment wastes cycles
3. ❌ **Partial MODIFIED deltas**: Always include full requirement content
4. ❌ **Scope creep**: Deltas define boundaries; anything outside is off-limits
5. ❌ **Missing scenarios**: Every requirement needs at least one WHEN → THEN block

---

## Sources

- [GitHub - Fission-AI/OpenSpec](https://github.com/Fission-AI/OpenSpec)
- [OpenSpec README](https://github.com/Fission-AI/OpenSpec/blob/main/README.md)
- [How to make AI follow your instructions more for free (OpenSpec) - DEV Community](https://dev.to/webdeveloperhyper/how-to-make-ai-follow-your-instructions-more-for-free-openspec-2c85)
- [Steering the Agentic Future: BMAD, Spec Kit, and OpenSpec - Medium](https://medium.com/@ap3617180/steering-the-agentic-future-a-technical-deep-dive-into-bmad-spec-kit-and-openspec-in-the-sdd-4f425f1f8d2b)
- [What Is Spec-Driven Development? Comparison of BMAD vs spec-kit vs OpenSpec - Redreamality's Blog](https://redreamality.com/blog/-sddbmad-vs-spec-kit-vs-openspec-vs-promptx/)
- [Diving Into Spec-Driven Development With GitHub Spec Kit - Microsoft Developers](https://developer.microsoft.com/blog/spec-driven-development-spec-kit)
- [Spec-driven development with AI - The GitHub Blog](https://github.blog/ai-and-ml/generative-ai/spec-driven-development-with-ai-get-started-with-a-new-open-source-toolkit/)
- [Understanding Spec-Driven-Development: Kiro, spec-kit, and Tessl - Martin Fowler](https://martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html)
- [Spec-Driven Development: The Complete Guide (2025) - SoftwareSeni](https://www.softwareseni.com/spec-driven-development-in-2025-the-complete-guide-to-using-ai-to-write-production-code/)
- [Build an Efficient Workflow with OpenSpec + Claude Code - Vibe Sparking AI](https://www.vibesparking.com/en/blog/ai/openspec/2025-10-17-openspec-claude-code-dev-process/)
- [Spec driven development 101 with openspec - GitHub Gist](https://gist.github.com/thomashartm/3ac8af0d39cc8651f7105d6dd308205e)

---

**Report Generated**: 2025-12-28
**Analysis Depth**: Comprehensive (5-dimensional evaluation)
**Confidence**: High (multiple sources, active project, clear patterns)
**Recommendation**: Adopt OpenSpec patterns incrementally in Ultra Builder Pro 4.2+
