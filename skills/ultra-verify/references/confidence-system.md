# Confidence System

Confidence scoring based on AI consensus for cross-verify results.

## Levels

### Consensus (3/3 Agree)
- **Confidence**: Highest
- **Action**: Strongly recommended — proceed with high confidence
- **Display**: `[CONSENSUS 3/3]`

### Majority (2/3 Agree)
- **Confidence**: High
- **Action**: Recommended — investigate the dissenting view for edge cases or alternative perspectives
- **Display**: `[MAJORITY 2/3]` + note which AI dissented and why

### No Consensus (All Differ)
- **Confidence**: Low
- **Action**: Decompose the problem into smaller questions, gather more data, or accept that the answer is genuinely ambiguous
- **Display**: `[NO CONSENSUS]` + summary of each position

## Application by Mode

| Mode | Consensus | Majority | No Consensus |
|------|-----------|----------|--------------|
| decision | Strong recommendation | Recommended + dissent analysis | Present all options, suggest decomposition |
| diagnose | Investigate first | Investigate second | Check all, may need more data |
| audit | Critical — fix now | High — likely real | Investigate — may be false positive |
| estimate | Use average, high confidence | Investigate outlier | Decompose task further |

## Degraded Confidence

When only 2 AIs respond (one failed):

- **2/2 Agree**: Equivalent to Majority (not Consensus — missing perspective)
- **2/2 Differ**: Low confidence — note missing third opinion

When only 1 AI responds: Claude-only analysis — explicitly mark as single-source, no consensus scoring.
