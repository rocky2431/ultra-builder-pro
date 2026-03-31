# Step 99: Research Synthesis & Distillate

## MANDATORY EXECUTION RULES

- VERIFY all spec files are complete — no [NEEDS CLARIFICATION] markers
- GENERATE distillate — token-efficient summary for /ultra-plan consumption
- VALIDATE field-level completeness — not just "file exists"
- THIS IS THE FINAL STEP — quality gate before handoff to /ultra-plan
- WRITE all outputs BEFORE presenting to user
- ALL output in English (spec files); conversation in Chinese

## PREREQUISITES

- All selected steps completed with [C]
- Spec files written: discovery.md, product.md, architecture.md

## CONTEXT BOUNDARIES

- Focus: Verify completeness, generate distillate, produce quality summary
- This step does NOT add new research — it synthesizes existing output
- Distillate is the primary artifact consumed by /ultra-plan

## EXECUTION SEQUENCE

### 1. Spec Completeness Validation

Read each spec file and validate field-level completeness:

**discovery.md Checklist**:
- [ ] §0 Problem Validation — has demand signal + confidence
- [ ] §1 Opportunity Space — has scored opportunity map
- [ ] §2 Market Assessment — has TAM/SAM/SOM with sources
- [ ] §3 Competitive Landscape — has comparison matrix + Porter's
- [ ] §4 Product Strategy — has vision + trade-offs + defensibility
- [ ] §5 Assumptions — has prioritized assumptions + experiments

**product.md Checklist**:
- [ ] §1 Problem Statement — has core problem + impact
- [ ] §2 Personas — has 2-3 personas with goals + pain points
- [ ] §3 Scenarios — has 3-5 scenarios with flows
- [ ] §4 User Stories — has stories with acceptance criteria
- [ ] §5 Feature Scope — has MVP features + exclusions
- [ ] §6 Success Metrics — has North Star + business + user metrics

**architecture.md Checklist**:
- [ ] §1-3 Context — has quality goals + constraints + system context
- [ ] §4 Solution Strategy — has tech stack with rationale
- [ ] §5-6 Building Blocks — has modules + runtime scenarios
- [ ] §7-9 Deployment — has environments + CI/CD + costs
- [ ] §10-12 Quality — has scenarios + risks + ADRs

**If ANY item fails**: List specific gaps and ask user whether to:
- [F] Fix — Go back to the relevant step to fill the gap
- [S] Skip — Accept the gap and proceed (note it in distillate)

### 2. Generate Research Distillate

Create `.ultra/specs/research-distillate.md` — a token-efficient summary optimized for LLM consumption by /ultra-plan:

```markdown
# Research Distillate

> Generated: [date]
> Source: /ultra-research steps [list of completed steps]
> Token budget: <2000 tokens

## Product Core
- **Problem**: [One sentence — what pain we solve]
- **For whom**: [Primary persona — one sentence]
- **Unique angle**: [What makes our approach different — one sentence]
- **North Star**: [Metric name: target by timeline]

## Scope (MVP)
### Must-Build
- [Feature 1]: [One-line description] — traces to [US-XX]
- [Feature 2]: [One-line description] — traces to [US-XX]
- [Feature 3]: [One-line description] — traces to [US-XX]

### Explicitly Out
- [Feature X]: [Why excluded]
- [Feature Y]: [Why excluded]

## Architecture Decisions
- **Stack**: [Language] + [Framework] + [Database] + [Hosting]
- **Pattern**: Functional Core / Imperative Shell
- **Key trade-off 1**: [Chose X over Y because Z]
- **Key trade-off 2**: [Chose X over Y because Z]

## Constraints
- [Technical constraint 1]
- [Organizational constraint 1]
- [Regulatory constraint 1]

## Top Risks
1. [Risk 1]: [Probability] × [Impact] — Mitigation: [Action]
2. [Risk 2]: [Probability] × [Impact] — Mitigation: [Action]
3. [Risk 3]: [Probability] × [Impact] — Mitigation: [Action]

## Unresolved Questions
- [Question 1 — what we still don't know]
- [Question 2 — what we still don't know]

## Rejected Alternatives
- [Alternative 1]: [Why rejected — prevents re-proposals]
- [Alternative 2]: [Why rejected]

## Quality Targets
| Attribute | Target | Priority |
|-----------|--------|----------|
| [Performance] | [p95 < Xms] | 1 |
| [Availability] | [99.X%] | 2 |
| [Security] | [Compliance level] | 3 |
```

### 3. Generate Quality Summary

Display to user:

```
Research Quality Summary
========================
Step 00 (Problem Validation):    ✅ [confidence]%
Step 01 (Opportunity Discovery): ✅ [confidence]%
Step 02 (Market Assessment):     ✅ [confidence]%
Step 03 (Competitive Landscape): ✅ [confidence]%
Step 04 (Product Strategy):      ✅ [confidence]%
Step 05 (Assumptions):           ✅ [confidence]%
Step 10 (User Personas):         ✅ [confidence]%
Step 11 (User Scenarios):        ✅ [confidence]%
Step 20 (User Stories):          ✅ [confidence]%
Step 21 (Features & Scope):      ✅ [confidence]%
Step 22 (Success Metrics):       ✅ [confidence]%
Step 30 (Architecture Context):  ✅ [confidence]%
Step 31 (Solution Strategy):     ✅ [confidence]%
Step 32 (Building Blocks):       ✅ [confidence]%
Step 40 (Deployment):            ✅ [confidence]%
Step 41 (Quality & Risks):       ✅ [confidence]%

Overall: [avg]% confidence
Spec completeness: [X]/[total] fields validated
Distillate: .ultra/specs/research-distillate.md

Output files:
  .ultra/specs/discovery.md
  .ultra/specs/product.md
  .ultra/specs/architecture.md
  .ultra/specs/research-distillate.md
  .ultra/docs/research/*.md (per-round reports)

Next: /ultra-plan
```

### 4. Present to User

```
[D] Done — Research complete, ready for /ultra-plan
[F] Fix — Go back to fix specific gaps
[E] Export — Generate additional summary format
```

**HALT — wait for user response before proceeding.**

### 5. Handle Response

- **[D]**: Research workflow complete. Suggest running `/ultra-plan`.
- **[F]**: Identify which step to revisit, load that step file
- **[E]**: Generate requested format

## SUCCESS METRICS

- All spec files validated at field level
- Research distillate generated (<2000 tokens)
- Quality summary displayed with per-step confidence
- No [NEEDS CLARIFICATION] markers remain (or explicitly accepted)
- All output files verified to exist

## FAILURE MODES

- Skipping validation ("files exist, good enough")
- Distillate is too verbose (>2000 tokens)
- Distillate missing rejected alternatives (will cause re-proposals)
- Not checking for [NEEDS CLARIFICATION] markers
- Inflating confidence scores

## WORKFLOW COMPLETE

This is the terminal step. After [D], the research workflow is done.
Next command: `/ultra-plan`
