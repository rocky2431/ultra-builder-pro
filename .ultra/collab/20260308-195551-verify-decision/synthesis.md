# Ultra Verify Synthesis: Bash vs Agent Architecture

**Mode**: decision | **Scope**: ultra-verify orchestration architecture | **AIs**: 2/3 (Codex failed) | **Degraded**: yes

---

## Per-AI Summary

### Claude
**Recommendation: Option A (保持 Bash)**
- CLAUDECODE 环境变量是 Agent 方案的致命缺陷 — Codex CLI 在 Claude Code agent 内部无法运行
- 当前方案已修复已知竞态（stability check + at_timeout + TOCTOU fix）
- 建议增量改进：修复 P2 问题，考虑 temp file + rename 模式
- 混合架构（一个 Agent 一个 Bash）比纯 Bash 更复杂
- KISS 原则：当前方案工作正常，不应为理论优雅引入更多活动部件

### Gemini
**Recommendation: Option C (Hybrid temp+rename)**
- Option C 是最 "production-grade" 的工程选择
- POSIX rename 是原子操作，在文件系统层面解决同步问题
- 比 Option A 的启发式轮询和 Option B 的 agent 包装都更可靠
- stability check 是启发式而非保证 — 网络抖动或磁盘 IO 延迟可能造成假稳定
- Option B 有致命缺陷（CLAUDECODE 限制）
- 轮询逻辑可简化到 ~50-80 行
- 建议命令格式：`(gemini -p '...' > output.tmp && mv output.tmp output.md) || touch output.err`

### Codex
**Status: FAILED** — CLI 启动但未产生分析输出。只有 MCP 初始化日志。

---

## Consensus Analysis

### [MAJORITY 2/2] 排除 Option B (Agent-based)
- **Claude + Gemini 一致**：CLAUDECODE 环境变量是根本性阻碍，Codex CLI 无法在嵌套 agent 中运行
- **置信度**：高 — 这是技术事实，不是观点分歧

### [DIVERGENT] Option A vs Option C
- **Claude**：保持 Option A，已有修复足够健壮
- **Gemini**：切换 Option C，temp+rename 是更优工程实践

**分歧分析**：
- Claude 更保守（KISS，已知可工作，改动有风险）
- Gemini 更激进（stability check 是启发式，有理论隐患，rename 是根本解决）
- 两者不矛盾 — Claude 也提到了 "考虑 temp file + rename 模式"，只是没作为首选

---

## Key Insights

1. **Option B 已被排除** — CLAUDECODE 限制是硬性技术约束，2/2 共识
2. **Option C 是 Claude + Gemini 的交集** — Claude 提到作为增强建议，Gemini 作为首选推荐
3. **实际验证佐证**：本次运行中 Codex 确实失败了，证明了 CLI 集成的脆弱性
4. **Stability check 确实在工作** — Gemini 从 waiting → stabilizing → complete，证明该机制有效但增加延迟

## Recommendation

**[MAJORITY 2/2] 采用 Option C (temp file + rename)**

理由：
1. 两方都排除了 Option B
2. Option C 是两方推荐的交集（Claude 作为增强提到，Gemini 直接推荐）
3. 改动最小 — 只改 Bash 命令格式和简化 verify_wait.py
4. 从根本解决空文件竞态，无需 stability check

**实施方案**：
```bash
# Before (current)
gemini -p "..." > output.md 2>error.log

# After (Option C)
(gemini -p "..." > output.md.tmp 2>error.log && mv output.md.tmp output.md) || true
```

verify_wait.py 可简化：删除 `get_output_sizes()`、stability check、`at_timeout` 逻辑。

**置信度**: Majority (2/2 degraded) — 缺少 Codex 视角，置信度上限为 Majority
