---
description: Analyze decisions with structured trade-off comparison
argument-hint: [decision question]
---

# /ultra-think

Deep analysis for complex decisions.

## Instructions

Think through this problem thoroughly and in great detail:

$ARGUMENTS

Consider multiple approaches and show your complete reasoning. Try different methods if your first approach doesn't work. Challenge your own assumptions.

## Output Format (Chinese)

Use `<thinking>` for internal reasoning, then provide:

```
## 问题
[1-2 句: 核心决策 + 约束]

## 分析
[Claude 自主选择相关维度分析]

## 方案对比
| 维度 | 方案A | 方案B |
|------|-------|-------|

## 推荐
- **选择**: [方案]
- **置信度**: High/Medium/Low
- **理由**: [1-2 句]
- **风险**: [主要风险 + 缓解]

## 下一步
[具体行动]
```

## Evidence Requirement

Per CLAUDE.md `<evidence_first>`: External claims require verification (Context7/Exa MCP). Label assertions as Fact/Inference/Speculation.

## When NOT to Use

- Simple questions → direct answer
- Implementation → `/ultra-dev`
- Research → `/ultra-research`
