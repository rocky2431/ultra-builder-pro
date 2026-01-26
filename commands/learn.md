---
description: Extract reusable patterns from current session and save to skills/learned/
argument-hint: [pattern-name]
allowed-tools: Read, Write, Grep, Glob, AskUserQuestion
model: opus
---

# /learn - Extract Reusable Patterns

Analyze current session and extract patterns worth saving as skills.

## Trigger Conditions

After solving a non-trivial problem, run `/learn` to extract patterns.

## What to Extract

Look for these types of patterns:

### 1. Error Resolution Patterns
- What error occurred?
- What was the root cause?
- How was it fixed?
- Can it be used for similar errors?

### 2. Debugging Techniques
- Non-obvious debugging steps
- Effective tool combinations
- Diagnostic patterns

### 3. Workarounds
- Library quirks
- API limitations
- Version-specific fixes

### 4. Project-Specific Patterns
- Discovered codebase conventions
- Architectural decisions made
- Integration patterns

## Output Format

Create skill file to `~/.claude/skills/learned/[pattern-name]_unverified.md`:

```markdown
# [Descriptive Pattern Name]

**Extracted:** YYYY-MM-DD
**Confidence:** Speculation (unverified)
**Context:** [Brief description of when this applies]

## Problem
[What problem does this pattern solve - be specific]

## Solution
[Pattern/technique/workaround]

## Example
[Code example if applicable]

## Trigger Conditions
[What situations should activate this skill]

## Verification Status
- [ ] Human review passed
- [ ] Multiple successful uses
```

## Process

1. Review session for extractable patterns
2. Identify most valuable/reusable insights
3. Draft skill file
4. **Ask user confirmation** before saving
5. Save to `~/.claude/skills/learned/` with `_unverified` suffix

## Verification Upgrade Path

1. **Speculation**: Freshly extracted, unverified
2. **Inference**: Human review passed, remove `_unverified` suffix
3. **Fact**: Multiple successful uses verified

## What NOT to Extract

- Simple typo fixes
- One-time issues (specific API outages, etc.)
- Patterns too specific to reuse

## Example

```
User: /learn

Claude: I identified the following extractable pattern from this session:

**Pattern: Supabase RLS Policy Debugging**

When Supabase queries return empty results but data exists:
1. Check if RLS policies are enabled
2. Verify auth.uid() matches
3. Test bypassing RLS with service role key

Save this pattern to ~/.claude/skills/learned/supabase-rls-debug_unverified.md?
```

**Remember**: Only extract patterns that will save time in future sessions. Keep skills focused - one pattern per skill.
