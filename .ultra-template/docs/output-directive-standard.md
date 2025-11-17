# OUTPUT Directive Standard

**Purpose**: Standard OUTPUT directive template for all reference documentation files.

---

## Standard Template

Use this exact text at the end of all REFERENCE.md and reference/*.md files:

```markdown
**OUTPUT: All examples show English templates. User messages output in Chinese at runtime; keep this file English-only.**
```

---

## Why This Matters

### Language Protocol Compliance

- **System files**: 100% English (SKILL.md, REFERENCE.md, guidelines, commands)
- **User-facing output**: Chinese (simplified) at runtime
- **Technical terms**: English (SOLID, JWT, LCP, INP, CLS, etc.)

### Consistency Benefits

1. **Clear expectations**: Developers know all examples are in English
2. **Runtime clarity**: User messages appear in Chinese
3. **Maintainability**: Single source of truth for OUTPUT directive

---

## Usage Guidelines

### When to Include

✅ **Always include in**:
- All `REFERENCE.md` files (skills/*/REFERENCE.md)
- All reference documentation (skills/*/reference/*.md)
- Any file with user-facing output examples

❌ **Do not include in**:
- `SKILL.md` files (use frontmatter `allowed-tools` instead)
- Pure code files
- Configuration files (config.json, etc.)

### Where to Place

**Location**: At the very end of the file, after all content, before the final line break.

**Example**:
```markdown
... [rest of documentation content] ...

---

**OUTPUT: All examples show English templates. User messages output in Chinese at runtime; keep this file English-only.**
```

---

## Validation

Use the validation script to check OUTPUT directive presence:

```bash
bash ~/.claude/.ultra-template/scripts/validate-consistency.sh
```

**CHECK 7** will report any missing OUTPUT directives.

---

## Migration Guide

If adding OUTPUT directive to existing file:

1. Open the file
2. Navigate to the end
3. Add a horizontal rule (`---`)
4. Add the standard OUTPUT directive
5. Run validation script to confirm

---

## Token Impact

**Current status**: 25 of 41 reference files have OUTPUT directives (61%)

**If all 41 files have directives**:
- Token cost: ~1200 tokens (41 files × ~29 tokens each)
- Percentage: 0.6% of 200K token budget
- Trade-off: Acceptable cost for clarity and consistency

---

## Version History

- **v1.0** (2024-11-17): Initial standard created during Scenario B optimization
