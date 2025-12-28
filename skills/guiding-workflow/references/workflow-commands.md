# Ultra Builder Workflow Commands Reference

## Command Overview

| Phase | Command | Purpose |
|-------|---------|---------|
| Initialize | `/ultra-init` | Set up project structure |
| Research | `/ultra-research` | Technical investigation |
| Plan | `/ultra-plan` | Task breakdown |
| Develop | `/ultra-dev` | TDD implementation |
| Test | `/ultra-test` | Quality validation |
| Deliver | `/ultra-deliver` | Deployment prep |
| Status | `/ultra-status` | Progress report |
| Analyze | `/max-think` | Deep 6D analysis |

## Workflow Sequence

```
/ultra-init → /ultra-research → /ultra-plan → /ultra-dev → /ultra-test → /ultra-deliver
                    ↑                              ↓
                    └──────── iterate ─────────────┘
```

## Phase Details

### 1. /ultra-init

**When to use:** Starting a new project

**Creates:**
```
.ultra/
├── tasks/tasks.json
├── specs/
│   ├── product.md
│   └── architecture.md
└── docs/
    ├── research/
    └── decisions/
```

**Next step:** `/ultra-research`

---

### 2. /ultra-research

**When to use:**
- New technology evaluation
- Architecture decisions
- Risk assessment

**Output:**
- Research reports in `.ultra/docs/research/`
- Updated specs with findings
- ADRs for major decisions

**Next step:** `/ultra-plan`

---

### 3. /ultra-plan

**When to use:** After specs are complete

**Creates:**
- `tasks.json` with prioritized tasks
- Dependency graph
- Effort estimates

**Next step:** `/ultra-dev`

---

### 4. /ultra-dev

**When to use:** Implementing features

**Process:**
1. RED: Write failing test
2. GREEN: Implement minimum code
3. REFACTOR: Clean up

**Creates:**
- Feature code
- Test files
- Git commits per task

**Next step:** `/ultra-test` or next `/ultra-dev`

---

### 5. /ultra-test

**When to use:**
- Task completion
- Before merge
- Quality gate

**Validates:**
- Test coverage ≥80%
- TAS score ≥70%
- Core Web Vitals targets
- SOLID compliance

**Next step:** `/ultra-deliver` or fix issues

---

### 6. /ultra-deliver

**When to use:** Preparing for deployment

**Performs:**
- Final quality checks
- Documentation sync
- Build optimization
- Security scan

**Output:**
- Deployment-ready code
- Updated documentation
- Release notes

---

### 7. /ultra-status

**When to use:** Anytime

**Shows:**
- Task progress
- Test results
- Blocking issues
- Risk assessment

---

### 8. /max-think

**When to use:**
- Complex decisions
- Technology selection
- Architecture design

**6D Analysis:**
1. Technical dimension
2. Business dimension
3. Team dimension
4. Ecosystem dimension
5. Strategic dimension
6. Meta dimension
