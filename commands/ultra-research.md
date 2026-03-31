---
description: Think-Driven Interactive Discovery - Deep research with step-file architecture
argument-hint: [topic]
allowed-tools: Task, Read, Write, WebSearch, WebFetch, Grep, Glob, AskUserQuestion
model: opus
---

# Ultra Research v2

**Step-file architecture**: Each research step is a self-contained instruction file loaded just-in-time for maximum LLM attention density.

## How This Works

1. Read the main skill file: `skills/ultra-research/SKILL.md`
2. Follow the activation sequence (pre-checks → project type detection → step routing)
3. For each step: Read `skills/ultra-research/steps/step-{NN}-{name}.md` and follow ALL instructions
4. Each step writes output immediately to spec files, then presents [C] Continue gate
5. Only proceed to next step after user confirms [C]

## Step Sequence

| Step | File | Focus |
|------|------|-------|
| **R0: Product Discovery** | | |
| 00 | `step-00-problem-validation.md` | Validate the problem is real |
| 01 | `step-01-opportunity-discovery.md` | Map opportunity space (OST) |
| 02 | `step-02-market-assessment.md` | TAM/SAM/SOM sizing |
| 03 | `step-03-competitive-landscape.md` | Competitor analysis |
| 04 | `step-04-product-strategy.md` | Vision, segments, trade-offs |
| 05 | `step-05-assumptions-validation.md` | Risk assumptions + experiments |
| **R1: User & Scenario** | | |
| 10 | `step-10-user-personas.md` | 2-3 personas |
| 11 | `step-11-user-scenarios.md` | 3-5 user scenarios |
| **R2: Feature Definition** | | |
| 20 | `step-20-user-stories.md` | Stories + acceptance criteria |
| 21 | `step-21-features-scope.md` | MVP scope + exclusions |
| 22 | `step-22-success-metrics.md` | KPIs + targets |
| **R3: Architecture** | | |
| 30 | `step-30-architecture-context.md` | Quality goals, constraints |
| 31 | `step-31-solution-strategy.md` | Tech stack decisions |
| 32 | `step-32-building-blocks.md` | Modules + runtime scenarios |
| **R4: Quality & Deploy** | | |
| 40 | `step-40-deployment.md` | Infrastructure + CI/CD |
| 41 | `step-41-quality-risks.md` | Quality scenarios + risks |
| **Synthesis** | | |
| 99 | `step-99-synthesis.md` | Distillate + validation |

## Critical Rules

- **Read SKILL.md first** — it has activation logic and project type detection
- **One step at a time** — never load multiple step files simultaneously
- **Write immediately** — every step writes to spec file before presenting to user
- **Web search mandatory** — factual claims need sources, no exceptions
- **User gate** — halt at [C] Continue, do not auto-proceed

## Begin

Read `skills/ultra-research/SKILL.md` now and follow the activation sequence.
