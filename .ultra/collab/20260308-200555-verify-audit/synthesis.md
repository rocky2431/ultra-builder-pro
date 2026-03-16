# Ultra Verify Synthesis: ultra-verify Skill Audit

**Mode**: audit | **Scope**: verify_wait.py, SKILL.md, orchestration-flow.md, reference files | **AIs**: 2/3 (Codex degraded — no uncommitted changes to review) | **Degraded**: yes

---

## Per-AI Summary

### Claude
**12 findings total**: 8 OK, 2 P2, 2 P3

核心逻辑（error log handling、stability check、TOCTOU safety）全部正确。主要关注点：
1. [P2] Bash tool 超时 (10min) < 脚本超时 (20min)，脚本会被提前杀死
2. [P2] codex-raw.txt 稳定性检查对非 audit 模式依赖 `_file_size()` 返回 -1 的实现细节
3. [P3] collab-protocol.md 中 5 分钟超时引用过期
4. SKILL.md ↔ orchestration-flow.md 内容一致性：通过

### Gemini
**7 findings total**: 4 OK, 1 P1, 1 P2, 1 P3

与 Claude 高度一致，核心逻辑评价相同。额外发现：
1. [P1] 超时不匹配（同 Claude P2，Gemini 评为更高优先级）
2. [P2] `sys.exit(1)` 在全部超时时可能导致 Claude 不解析 JSON
3. [P3] docstring 声明 exit 0 = "All AIs completed" 与代码 `any_done` 逻辑不一致

### Codex
**Status**: 无有效输出。`codex review --uncommitted` 因目标文件刚提交（eb5983b），没有 uncommitted tracked changes，只扫描了不相关的 untracked 文件。

---

## Consensus Analysis

### [MAJORITY 2/2] Bash Tool 超时 < 脚本超时 — 存在死区

| AI | Severity | Description |
|----|----------|-------------|
| Claude | P2 | Bash 600000ms (10min) < script 1200s (20min)，脚本被提前杀死 |
| Gemini | P1 | 相同发现，评为更高优先级 |

**共识**：两方一致认为这是当前最大的设计缺陷。Bash tool 硬限制为 600000ms (10 分钟)，脚本的 20 分钟超时永远无法触达。如果 AI 输出需要 >10 分钟，脚本被杀，不产生 JSON，Step 3→4 流程断裂。

**实际影响**：低。实测中 Gemini ~1min，Codex ~3min，本次 57s。10 分钟对绝大多数场景足够。但文档声称 "up to 20 minutes" 是误导性的。

**建议**：
- 将 SKILL.md 和 orchestration-flow.md 中的描述改为 "up to 10 minutes (Bash tool limit)"
- 脚本 `--timeout 1200` 改为 `--timeout 580`（留 20s 余量写 JSON）
- 或者接受当前状态，在文档中说明 Bash tool 限制是有效超时上限

### [MAJORITY 2/2] 核心逻辑全部正确

| Component | Claude | Gemini |
|-----------|--------|--------|
| Error log handling (only at timeout) | OK | OK |
| Stability check (size unchanged between polls) | OK | OK ("设计精良") |
| TOCTOU safety (_file_size try/except) | OK | OK |
| Codex audit mode (codex-raw.txt + tee) | OK | OK |
| CRITICAL PROHIBITION rules | OK | (implicitly OK) |

**置信度**：高 — 两方独立审计完全一致，核心修复有效。

### Gemini 独有发现

**[P2] sys.exit(1) 可能阻断降级逻辑**

当两个 AI 全部超时，脚本输出 JSON 后执行 `sys.exit(1)`。Claude 的 Bash tool 可能将此标记为 "命令失败"，导致跳过 JSON 解析，无法触发降级路径。

**分析**：有道理。虽然 Bash tool 在 exit 1 时仍然返回 stdout 内容，但 Claude 可能因为看到错误标记而不去解析。建议改为始终 `sys.exit(0)`，用 JSON `status` 字段表达结果。

**[P3] Docstring 与代码不一致**

docstring 声称 exit 0 = "All AIs completed"，但代码是 `any_done`（至少一个完成就 exit 0）。低风险但影响可读性。

### Claude 独有发现

**[P2] codex-raw.txt 稳定性耦合**

非 audit 模式下，`codex_stable` 检查同时要求 `codex-output.md` 和 `codex-raw.txt` 稳定。后者不存在时返回 -1 == -1 = True，不阻塞。逻辑正确但依赖隐式行为。

**[P3] collab-protocol.md 过期超时引用**

L112 写 ">5min"，实际已改为 20 分钟。低影响（通用协议文件）。

---

## Pipeline 运行验证

本次审计同时验证了 ultra-verify 管道本身的运行：

| 检查项 | 结果 |
|--------|------|
| Session 目录创建 | OK |
| Claude 先写分析（防污染） | OK |
| Gemini + Codex 并行启动 | OK |
| verify_wait.py 阻塞等待 | OK (57s) |
| Stability check 工作 | OK (gemini/codex 都经历 stabilizing → complete) |
| 错误日志未误报 | OK (Codex MCP 日志未触发 false positive) |
| JSON 输出结构正确 | OK |
| 三方输出文件可读 | OK |

**结论**：管道运行通畅，上次修复有效。

---

## Action Items（按优先级）

1. **[MAJORITY P1/P2] 超时文档修正** — 要么降低 `--timeout` 到 580s，要么在文档中明确 10 分钟是有效上限
2. **[Gemini P2] sys.exit(1) → sys.exit(0)** — 全部超时时也返回 0，用 JSON status 表达结果
3. **[Gemini P3] 修正 docstring** — exit 0 = "at least one completed or known failure"
4. **[Claude P3] collab-protocol.md** — 更新 ">5min" 超时引用

**置信度**: Majority (2/2 degraded) — Codex 因 scope 不匹配未产出有效审计

---

## Overall Assessment

**ultra-verify 的核心修复（error log false positive + stability check + TOCTOU safety）经两方独立审计确认正确。** 管道运行通畅，57 秒完成。

唯一值得修复的是超时层设计的文档误导和 `sys.exit(1)` 的潜在问题。这些都是 P2/P3 级别，不影响当前功能。
