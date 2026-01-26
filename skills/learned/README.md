# Learned Patterns

This directory stores patterns extracted via the `/learn` command.

## File Naming Convention

- `pattern-name_unverified.md` - Freshly extracted, confidence is Speculation
- `pattern-name.md` - Verified, confidence is Inference or Fact

## Confidence Levels

| Level | File Suffix | Description |
|-------|-------------|-------------|
| Speculation | `_unverified` | Freshly extracted, unverified |
| Inference | No suffix | Human review passed |
| Fact | No suffix + marked in file | Multiple successful uses verified |

## Verification Process

1. Run `/learn` to extract patterns
2. Pattern saved as `*_unverified.md`
3. Human review, if valid remove `_unverified` suffix
4. After multiple successful uses, update confidence to Fact in file

## Loading Priority

When patterns conflict: Fact > Inference > Speculation
