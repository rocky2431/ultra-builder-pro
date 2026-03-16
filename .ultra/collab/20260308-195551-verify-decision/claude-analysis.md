# Claude Analysis: Bash+verify_wait.py vs Agent-based Architecture

## Decision Context

**Question**: ultra-verify 当前的 Bash shell redirect + verify_wait.py 轮询架构是否足够健壮？还是应该切换到 Agent-based 架构（verify-gemini/verify-codex agents with atomic Write tool）？

## Option A: Current Bash Architecture (保持现状)

### How it works
1. Bash `run_in_background: true` 启动 `gemini -p "..." > output.md`
2. Shell redirect `>` 立即创建空文件，CLI 增量写入
3. verify_wait.py 轮询文件大小，stability check（连续两次 poll 大小不变 = 完成）
4. at_timeout 区分空文件（pending vs empty）

### Pros
- **简单直接** — 无额外抽象层，Bash 命令一目了然
- **成熟** — shell redirect 是 Unix 基础设施，行为可预测
- **已修复** — stability check + TOCTOU fix + at_timeout 已解决已知竞态
- **零依赖** — 不需要额外 agent 文件或 skill 引用
- **调试容易** — 可以手动运行同样的命令验证

### Cons
- **空文件竞态** — shell redirect 创建空文件是根本性设计缺陷，需要 stability check 来补偿
- **复杂度** — verify_wait.py 因为要处理空文件、stability、at_timeout 变得复杂（~190 行）
- **脆弱** — CLI 命令硬编码在 SKILL.md 中，CLI 更新时需要同步多个文件
- **无错误隔离** — Bash 命令在主 Claude 进程中运行，stderr 混入上下文

### Risks
- CLI 参数变更需要同步 SKILL.md + orchestration-flow.md
- Codex `-o` flag 行为不一致（有时不输出到指定文件）
- Shell redirect 在某些边界条件下可能丢失数据（进程被 kill 时）

## Option B: Agent-based Architecture (切换)

### How it works
1. 两个专用 agent (verify-gemini, verify-codex) 带 `run_in_background: true`
2. Agent 通过 collab skill 获取正确 CLI 语法
3. Agent 运行 CLI，捕获 stdout，用 Write tool 原子写入文件
4. verify_wait.py 简化为：文件存在 + 非空 = 完成

### Pros
- **原子写入** — Write tool 保证文件要么完整要么不存在，从根本上消除空文件竞态
- **简化 wait 脚本** — 无需 stability check / at_timeout / get_output_sizes，~130 行
- **CLI 解耦** — agent 通过 skill 获取 CLI 语法，SKILL.md 不需要硬编码命令
- **错误隔离** — agent 在独立上下文运行，不污染主对话
- **模式一致** — 与 ultra-review 的 agent 模式一致（已验证可靠）

### Cons
- **额外复杂度** — 多了 2 个 agent 文件 + skill 依赖链
- **调试层次深** — agent 内部的 CLI 错误不直接可见，需查看 agent transcript
- **启动开销** — agent 启动比 Bash 慢（需要初始化上下文）
- **CLAUDECODE 限制** — Codex CLI 实际上在 Claude Code 环境中无法运行（CLAUDECODE 环境变量阻止嵌套）

### Risks
- Agent 的 Bash tool 仍然有 timeout 限制
- Agent 可能因 skill 加载失败而整体失败
- CLAUDECODE 环境变量问题是根本性的——Codex agent 在 Claude Code 内部无法工作

## My Recommendation

**保持 Bash 架构（Option A），继续增强。**

理由：
1. **CLAUDECODE 限制是致命的** — Codex CLI 在 Claude Code agent 内部会被 CLAUDECODE 环境变量阻止，Agent 方案在 Codex 端根本不可行
2. **已修复的竞态足够健壮** — stability check + at_timeout + TOCTOU fix 已经覆盖了已知边界条件
3. **Gemini 部分可以考虑 Agent** — 但 Codex 不行，混合架构（一个 Agent 一个 Bash）比纯 Bash 更复杂
4. **KISS 原则** — 当前方案已经工作，复杂度可控，不应为了理论上的优雅引入更多活动部件

**建议的增强**（在当前 Bash 架构上）：
1. 修复 code review 中的 P2 问题（_file_size 捕获 OSError、timeout 参数校验）
2. 考虑 temp file + rename 模式（`> .tmp && mv .tmp final`）替代直接 shell redirect，可以低成本实现原子写入
3. 保持 CRITICAL PROHIBITION 和 stability check 作为双重保障

## Confidence: Medium-High

当前方案有已知局限但已有有效补偿机制。Agent 方案有根本性的 CLAUDECODE 兼容问题。
