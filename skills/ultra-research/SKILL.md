---
name: ultra-research
description: "Think-Driven Interactive Discovery - Deep research with step-file architecture for high-density output"
user-invocable: true
---

# Ultra Research v2 — Step-File Architecture

## Overview

Transform vague ideas into complete, high-confidence specifications through progressive interactive discovery. Each research step is a self-contained instruction file loaded just-in-time for maximum LLM attention density.

**Philosophy**: Research is collaborative. Each decision validated with user before proceeding. All findings must have 90%+ confidence. Every claim needs a source.

## WORKFLOW ARCHITECTURE

### Core Principles

- **Step-File Design**: Each step is a self-contained .md file with full execution instructions
- **Just-In-Time Loading**: Only the current step file is in context — never load future steps
- **Sequential Enforcement**: Steps must be completed in order, no skipping
- **Write-Immediately**: Every step writes its output to the spec file BEFORE presenting to user
- **User Gate**: User must explicitly confirm [C] Continue before proceeding to next step
- **State Tracking**: Track progress via TaskCreate/TaskUpdate system
- **Web-First**: Every analysis step REQUIRES web search with citations. No search = no proceed.

### Step Processing Rules

1. **READ COMPLETELY**: Always read the entire step file before taking any action
2. **FOLLOW SEQUENCE**: Execute all numbered sections in order
3. **SEARCH FIRST**: Execute web searches BEFORE generating analysis
4. **WRITE IMMEDIATELY**: Append content to spec file as soon as analysis is complete
5. **WAIT FOR INPUT**: Present [C] Continue — halt and wait for user selection
6. **LOAD NEXT**: When user confirms, Read the next step file and follow it

### Critical Rules (NO EXCEPTIONS)

- NEVER load multiple step files simultaneously
- ALWAYS read entire step file before execution
- NEVER skip steps or optimize the sequence
- ALWAYS write output to spec file before presenting to user
- ALWAYS halt at [C] Continue and wait for user input
- NEVER proceed without user confirmation
- NEVER rely solely on training data — web search is mandatory for factual claims

## STEP SEQUENCE

### Round 0: Product Discovery & Strategy

| Step | File | Focus | Output |
|------|------|-------|--------|
| 00 | `step-00-problem-validation.md` | Validate the problem is real and worth solving | discovery.md §0 |
| 01 | `step-01-opportunity-discovery.md` | Opportunity Solution Tree (Teresa Torres) | discovery.md §1 |
| 02 | `step-02-market-assessment.md` | TAM/SAM/SOM with dual approach | discovery.md §2 |
| 03 | `step-03-competitive-landscape.md` | Competitors + Porter's Five Forces | discovery.md §3 |
| 04 | `step-04-product-strategy.md` | Vision, segments, value prop, trade-offs | discovery.md §4 |
| 05 | `step-05-assumptions-validation.md` | Risk assumptions + experiment design | discovery.md §5 |

### Round 1: User & Scenario Discovery

| Step | File | Focus | Output |
|------|------|-------|--------|
| 10 | `step-10-user-personas.md` | 2-3 personas with goals, pain points, context | product.md §1-2 |
| 11 | `step-11-user-scenarios.md` | 3-5 user scenarios with trigger/flow/outcome | product.md §3 |

### Round 2: Feature Definition

| Step | File | Focus | Output |
|------|------|-------|--------|
| 20 | `step-20-user-stories.md` | User stories with acceptance criteria | product.md §4 |
| 21 | `step-21-features-scope.md` | Feature prioritization + explicit exclusions | product.md §5 |
| 22 | `step-22-success-metrics.md` | Business + user metrics with targets | product.md §6 |

### Round 3: Architecture Design

| Step | File | Focus | Output |
|------|------|-------|--------|
| 30 | `step-30-architecture-context.md` | Quality goals, constraints, system context | architecture.md §1-3 |
| 31 | `step-31-solution-strategy.md` | Tech stack selection with rationale | architecture.md §4 |
| 32 | `step-32-building-blocks.md` | Module decomposition + runtime scenarios | architecture.md §5-6 |

### Round 4: Quality & Deployment

| Step | File | Focus | Output |
|------|------|-------|--------|
| 40 | `step-40-deployment.md` | Infrastructure, environments, CI/CD | architecture.md §7-9 |
| 41 | `step-41-quality-risks.md` | Quality scenarios, risks, tech debt | architecture.md §10-12 |

### Synthesis

| Step | File | Focus | Output |
|------|------|-------|--------|
| 99 | `step-99-synthesis.md` | Distillate + validation + quality summary | research-distillate.md |

## ACTIVATION

When invoked, follow this sequence:

### 1. Pre-Research Check

- If `.ultra/specs/product.md` has [NEEDS CLARIFICATION] → proceed with research
- If `.ultra/specs/` doesn't exist → suggest `/ultra-init` first
- If specs 100% complete → suggest skip to `/ultra-plan`

### 2. Project Type Detection

Ask user to determine research scope:

| Type | Steps | Focus |
|------|-------|-------|
| Full Project | 00-99 | All rounds |
| Product Only | 00-22 | Discovery + product |
| Feature Only | 10-22 | User scenarios + features (skip discovery) |
| Architecture Change | 30-41 | Architecture + deployment |
| Custom | User selects | Specific steps |

**Round 0 skip conditions**: Skip if user provides existing market research, validated strategy docs, or explicitly states "I already know the market".

### 3. Begin Step Execution

Read the first applicable step file:
```
Read: skills/ultra-research/steps/step-{NN}-{name}.md
```

Follow every instruction in that file. When the step is complete and user confirms [C], read the next step file.

### 4. Output Files

| File | Content |
|------|---------|
| `.ultra/specs/discovery.md` | §0-5: Problem, Opportunities, Market, Competition, Strategy, Assumptions |
| `.ultra/specs/product.md` | §1-6: Problem, Personas, Scenarios, Stories, Scope, Metrics |
| `.ultra/specs/architecture.md` | §1-12: arc42 structure |
| `.ultra/specs/research-distillate.md` | Token-efficient summary for /ultra-plan consumption |
| `.ultra/docs/research/*.md` | Per-round research reports |

## QUALITY STANDARDS

| Element | Requirement |
|---------|-------------|
| Sources | Every factual claim has URL citation |
| Confidence | 90%+ for recommendations |
| Code | Production-ready (no TODO/demo) |
| Trade-offs | Quantified pros/cons |
| Next steps | Specific, actionable items |

## COMPLETION

Research is complete when:
- All selected steps have [C] confirmed by user
- All spec files have no [NEEDS CLARIFICATION] markers
- Research distillate generated
- All recommendations have 90%+ confidence

**Next**: Run `/ultra-plan` to generate task breakdown from complete specs.
