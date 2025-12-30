# 6-Step Interactive Cycle Template

Every research round follows this exact 6-step cycle. Do not skip steps.

---

## Step 1: Requirement Clarification

**Action**: Use AskUserQuestion tool to collect inputs.

**Structure**:
- Part A: Load core questions for this round (see round-questions.md)
- Part B: Generate 1-2 context-specific extension questions based on:
  - User's project description
  - Previous round answers
  - Domain keywords detected

**Extension Question Guidelines**:
- Format: 2-4 options, header ≤12 chars
- Validate: header.length ≤12, options have label + description
- If validation fails: retry max 2 times, then use core questions only

**Gate**: Do not proceed until ALL questions answered.

---

## Step 2: Deep Analysis

**Action**: Invoke `/ultra-think` with collected context.

**Prompt Template**:
```
/ultra-think "[Round-specific analysis task] for [project_name]:
- Context from Step 1: [user_answers]
- Previous rounds context: [if applicable]

Perform 6D analysis (Technical, Business, Team, Ecosystem, Strategic, Meta)"
```

**Gate**: Do not proceed until /ultra-think completes with structured output.

---

## Step 3: Analysis Validation

**Action**: Present summary to user and validate.

**Process**:
1. Show 2-3 key findings from Step 2 (NOT full 6D output)
2. Use AskUserQuestion:
   - Question: "Does this analysis align with your understanding?"
   - Options: Satisfied / Needs Adjustment / Critical Miss

**Gate**: Do not proceed until user validation collected.

---

## Step 4: Iteration Decision

**Action**: Route based on Step 3 response.

| Response | Action |
|----------|--------|
| Satisfied | Proceed to Step 5 |
| Needs Adjustment | Collect feedback → Back to Step 2 (max 2 iterations) |
| Critical Miss | Back to Step 1 |

**Gate**: Do not proceed without proper iteration handling.

---

## Step 5: Generate Spec Content

**Action**: Write to spec files using Edit tool.

**Files**:
- Round 1-2: Update `specs/product.md`
- Round 3: Create `specs/architecture.md`
- Round 4: Append risk sections to both

**Rules**:
- Use Edit tool with specific old_string/new_string
- Do not overwrite previous round content
- Save research report to `.ultra/docs/research/[report-name]-{date}.md`

**Gate**: Do not proceed until files written and verified.

---

## Step 6: Round Satisfaction Rating

**Action**: Collect quality metrics.

**Process**:
1. Use AskUserQuestion: "Rate your satisfaction with this round (1-5 stars)"
2. If rating < 4: Collect improvement suggestions
3. Record to `.ultra/docs/research/metadata.json`

**Gate**: Do not proceed to next round until rating collected.

---

## Quality Thresholds

| Metric | Threshold | Action if Failed |
|--------|-----------|------------------|
| Round rating | ≥3 stars | Offer to restart round |
| Iterations per round | ≤2 | Force proceed with warning |
| Overall rating | ≥4 stars | Collect detailed feedback |
