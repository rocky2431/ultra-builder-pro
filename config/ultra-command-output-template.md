# Ultra Command Output Template

**Purpose**: Standardized output format for all 10 ultra commands to ensure consistent user experience.

---

## Standard Output Structure

All commands should follow this 6-section template (adapt sections as needed):

```
🎯 [Command Icon] [Command Name] - [Phase Description]
========================

✅ [Section 1: Primary Action Completed]
   - [Detail 1]
   - [Detail 2]
   - [Detail 3]

✅ [Section 2: Secondary Actions Completed (if applicable)]
   - [Detail 1]
   - [Detail 2]

✅ [Section 3: Validation/Quality Checks (if applicable)]
   - [Metric 1]: ✅ / ⚠️ / ❌
   - [Metric 2]: ✅ / ⚠️ / ❌

⚠️ [Section 4: Warnings/Issues (if any)]
   - [Issue 1]: [Description]
   - [Recommended action]

========================
📊 [Section 5: Summary/Metrics]
   - [Key metric 1]: [Value]
   - [Key metric 2]: [Value]

🚀 [Section 6: Next Steps]
   - Run [suggested-command] [reason]
   - Or run [alternative-command] [reason]
```

**Note**: At runtime, output in Chinese per Language Protocol.

---

## Command-Specific Icons

| Command | Icon | Phase Description (in Chinese at runtime) |
|---------|------|-------------------------------------------|
| ultra-init | 🏗️ | Project Initialization |
| ultra-research | 🔬 | Technical Research |
| ultra-plan | 📋 | Task Planning |
| ultra-dev | 💻 | TDD Development |
| ultra-test | 🧪 | Comprehensive Testing |
| ultra-deliver | 🚀 | Deployment Preparation |
| ultra-status | 📊 | Progress Monitoring |
| ultra-think | 🤔 | Deep Thinking |

---

## Status Indicators

- ✅ : Success / Completed / Passed
- ⚠️ : Warning / Needs attention / Partial
- ❌ : Error / Failed / Blocked
- 🔄 : In progress
- ⏳ : Pending / Waiting

---

## Examples by Command

**Note**: All examples below show structure in English. At runtime, output in Chinese per Language Protocol.

### ultra-init

```
🏗️ Ultra Init - Project Initialization
========================

✅ Project Structure Created
   - .ultra/ directory created
   - specs/ subdirectory (product.md, architecture.md)
   - tasks/ subdirectory (tasks.json)
   - docs/ subdirectory (research/, decisions/)
   - CLAUDE.md created at project root

✅ Template Files Copied
   - specs/product.md → Product specification template
   - specs/architecture.md → Architecture design template
   - tasks/tasks.json → Task management
   - CLAUDE.md → Project context for Claude Code

✅ Git Repository Initialized (if selected)
   - git init completed
   - .gitignore created (excludes CLAUDE.local.md)
   - Initial commit completed

========================
📊 Project Information
   - Project name: my-app
   - Project type: web
   - Tech stack: react-ts
   - Directory: ./my-app

🚀 Next Steps
   - Run /ultra-research to complete specifications (RECOMMENDED)
   - Then run /ultra-plan to generate task breakdown
```

### ultra-research

```
🔬 Ultra Research - Technical Research
========================

✅ Research Execution Completed
   - Research topic: React vs Vue
   - Sources: Context7 (official docs) + Exa (community analysis)
   - Multi-source validation: 3 sources

✅ Research Report Saved
   - File path: .ultra/docs/research/2025-01-15-react-vs-vue.md
   - Report contains: Executive Summary, Comparative Analysis, Risk Assessment, Recommendation

✅ Architecture Documentation Auto-Updated
   - specs/architecture.md: Frontend Technology section updated
   - Decision recorded: React with TypeScript
   - Rationale linked: Research report

========================
📊 Research Results
   - Recommended solution: React with TypeScript (8.5/10)
   - Alternatives: Vue, Angular, Svelte
   - Key advantages: Better ecosystem, team familiarity, hiring advantage

🚀 Next Steps
   - Run /ultra-plan to generate tasks based on research
   - Or run /ultra-research to continue other technical investigations
```

### ultra-plan

```
📋 Ultra Plan - Task Planning
========================

✅ Requirements Analysis Completed
   - Spec file: specs/product.md (read)
   - Functional requirements: 12 items
   - Non-functional requirements: 5 items
   - Constraints: 3 items

✅ Task Generation Completed
   - Total tasks: 18 items
   - P0 (critical): 5 items
   - P1 (important): 8 items
   - P2 (secondary): 5 items

✅ Dependency Analysis Completed
   - Dependencies: 23 relationships
   - Circular dependencies: 0 items
   - Parallel opportunities: 3 groups (6 tasks can run in parallel)

✅ Traceability Verification
   - With trace_to links: 18/18 (100%)
   - Spec coverage: All sections covered
   - Orphaned requirements: 0 items

========================
📊 Project Estimation
   - Estimated total effort: 45 days
   - Simple tasks (1-3): 6 items (8 days)
   - Medium tasks (4-6): 8 items (20 days)
   - Complex tasks (7-10): 4 items (17 days)

🚀 Next Steps
   - Run /ultra-dev to start first task (task #1: Create database schema)
   - Or run /ultra-status to view detailed task list
```

### ultra-test

```
🧪 Ultra Test - Comprehensive Testing
========================

✅ Six-Dimensional Testing Completed
   - Functional: ✅ Passed (35/35 tests)
   - Boundary: ✅ Passed (12/12 tests)
   - Exception: ✅ Passed (8/8 tests)
   - Performance: ✅ Passed (API <200ms)
   - Security: ✅ Passed (no injection vulnerabilities)
   - Compatibility: ✅ Passed (4 browsers)

✅ Coverage Verification
   - Overall coverage: 87% (target ≥80%) ✅
   - Critical path coverage: 100% (target 100%) ✅
   - Branch coverage: 82% (target ≥75%) ✅

✅ Frontend Performance Verification (Core Web Vitals)
   - LCP: 2.1s (target <2.5s) ✅
   - INP: 150ms (target <200ms) ✅
   - CLS: 0.08 (target <0.1) ✅

========================
📊 Test Summary
   - Total tests: 55 items
   - Passed: 55 items
   - Failed: 0 items
   - Skipped: 0 items
   - Execution time: 2min 15sec

🚀 Next Steps
   - Run /ultra-deliver for deployment preparation
   - Or run /ultra-dev to continue next task
```

### ultra-deliver

```
🚀 Ultra Deliver - Deployment Preparation
========================

✅ Performance Optimization Completed
   - Bundle analysis: Main bundle 320KB (target <500KB) ✅
   - Code splitting: 3 lazy chunks
   - Image optimization: WebP format, avg 40% reduction
   - Critical CSS inline: First paint optimized

✅ Security Audit Completed
   - Dependency vulnerability scan: 0 high/critical ✅
   - Code review: No SQL injection, XSS vulnerabilities ✅
   - Sensitive data check: No hardcoded secrets ✅
   - Rate limiting: Configured (100 req/min)

✅ Documentation Update Completed
   - README.md: Updated
   - CHANGELOG.md: v1.0.0 entry added
   - API documentation: Synchronized
   - ADR: 2 decision records archived

✅ Deployment Checklist
   - [✅] All tests passing
   - [✅] Coverage ≥80%
   - [✅] No security vulnerabilities
   - [✅] Documentation updated
   - [✅] Environment variables configured
   - [✅] Database migrations ready
   - [✅] Rollback plan prepared

========================
📊 Deployment Readiness Status
   - Readiness: 100%
   - Blocking issues: 0 items
   - Recommended delay: None

🚀 Next Steps
   - Execute deployment: Deploy to production
   - Or run /ultra-status to view final project status
```

### ultra-status

```
📊 Ultra Status - Progress Monitoring
========================

✅ Task Progress Overview
   - Total tasks: 18 items
   - Completed: 12 items (67%)
   - In progress: 1 item
   - Pending: 5 items
   - Blocked: 0 items

✅ Current Work
   - Task #13: Implement payment gateway integration
   - Status: in_progress
   - Complexity: 7/10 (complex)
   - Estimated remaining: 2 days
   - Branch: feat/task-13-payment-gateway

✅ Quality Metrics
   - Test coverage: 85% ✅
   - SOLID checks: Passed ✅
   - Core Web Vitals: All passed ✅
   - Technical debt: 2 items (recorded)

⚠️ Risk Alerts
   - Task #15 depends on external API (unstable response time)
   - Recommendation: Add fallback strategy and caching

========================
📊 Milestone Status
   - MVP features: 100% complete ✅
   - Beta version: 75% complete
   - Production ready: 40% complete
   - Estimated completion: 2025-02-15

🚀 Next Steps
   - Run /ultra-dev to continue task #13
   - Or run /ultra-test to verify completed features
```

---

## Implementation Notes

### 1. Language Protocol
- **Output language**: Chinese (simplified) at runtime per CLAUDE.md Language Protocol
- **Section headers**: Translated to Chinese at runtime (user-friendly)
- **Technical terms**: English (SOLID, JWT, API, LCP, INP, CLS, etc.)
- **Metrics**: Numbers + units translated to Chinese at runtime

### 2. Visual Hierarchy
- Use separators: `========================`
- Group related items with indentation
- Use icons for quick scanning (✅⚠️❌🔄⏳)

### 3. Actionable Next Steps
- Always provide 2-3 next step options
- Include command with clear reasoning
- Prioritize most common workflow path

### 4. Error Handling
When errors occur, add error section (example structure, output in Chinese at runtime):
```
❌ Error Detected
   - [Error type]: [Description]
   - [Root cause if known]
   - Recommended action: [How to fix]
```

### 5. Progressive Disclosure
- Show summary first
- Detailed metrics in collapsed sections (if needed)
- Link to full reports for comprehensive data

---

**Usage**: All commands should import and adapt this template for consistent user experience. Remember to output in Chinese at runtime per Language Protocol.
