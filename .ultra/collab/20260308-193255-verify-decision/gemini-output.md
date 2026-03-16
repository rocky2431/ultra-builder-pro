现在我有了完整的上下文。以下是我的独立分析：

---

## Ultra-Verify 架构重构方案评估

### 1. Agent 替代 Bash CLI 调用 — **方向正确，但成本偏高**

**优势：**
- 消除 shell redirect 竞态条件（空文件问题在实际 session `20260308-193255` 中已确认出现）
- CLI 参数错误由 agent 自行修复（retry with skill reference），而非 Bash 直接 exit 1
- Agent 天然支持错误处理分支（成功→Write，失败→Write error log）

**设计缺陷：**
- **成本放大严重**：每次 verify 需要 2 个 Sonnet agent（10 turns each），仅为执行 1 条 CLI 命令 + 1 次文件写入。相比 Bash `run_in_background` 的零 token 开销，这是从 O(0) 到 O(数千 tokens) 的跃迁
- **Bash 工具捕获 stdout 有大小限制**：Gemini/Codex 输出可能 10-50KB，agent 需要先用 Bash 捕获整个 stdout 到内存，再用 Write 写出。如果 stdout 被 Bash tool 截断，Write 写入的就是不完整数据
- **Agent 不可靠性替代了 shell 不可靠性**：agent 可能消耗所有 turns 却没完成、可能理解错 prompt、可能在 Write 前被 timeout 终止
- **Skill injection 开销**：每个 agent 加载 `gemini-collab` / `codex-collab` skill 只为读一个 CLI reference 文件——过度间接

**改进建议：**
- 不用 Agent，用 **Bash + 直接 Write tool** 的组合：在 SKILL.md 中指导主 agent 先用 `Bash(run_in_background)` 跑 CLI 不带 redirect（纯 stdout 捕获），等 background 完成后用 Write 写文件。这保留了原子写入优势而消除了 agent 开销
- 如果坚持用 Agent，将 `maxTurns` 从 10 降到 **3**（run bash → check output → write file），减少浪费

### 2. Write Tool 原子写入替代 shell redirect — **核心洞察正确**

**优势：**
- Write tool 语义确实是原子的：文件要么完整存在、要么不存在。消除了 `> file` 在 Bash 启动时创建空文件的竞态
- 这是整个重构最有价值的改变点

**边界情况：**
- **Write tool 不是 OS 层面的原子操作**：它是 Claude Code 的 SDK 调用，底层实现可能仍然是 open→write→close。如果 agent 进程在写入中途被 kill（如 OOM），文件可能仍然是部分写入的。不要假设它有事务语义
- **`run_in_background` 的 agent 完成通知时序**：如果 agent 写完文件后 Claude Code 还没发出 TaskOutput 通知，verify_wait.py 可能先于通知检测到文件，这在简化版中没问题（文件已完整），但在原版中的 "pending" 状态判断会更复杂
- **Codex `-o` flag 的矛盾**：agent 指令说"不用 `-o` flag"，但当前 SKILL.md 的 Bash 方案用了 `-o`。如果 Codex 的 `-o` 本身就是原子写入（由 Codex 内部实现），那用 agent 做同样的事是多此一举

### 3. 简化 verify_wait.py 去掉 stability check — **正确但引入了新风险**

**优势：**
- 消除了 `at_timeout` 参数的复杂双路逻辑
- 代码从 89 行降到 55 行核心逻辑，更容易理解和维护
- `_file_size()` 的 try/except 修复了 exists() + stat() 之间的 TOCTOU 竞态——这是一个纯增量改进

**设计缺陷：**
- **丢失了 "empty" 状态**：简化后只有 `complete`/`failed`/`pending`，没有 `empty`。如果 agent 成功执行了 CLI 但 CLI 返回了空输出（合法场景：Codex 可能对某些 prompt 返回空），agent 会把空字符串 Write 到文件，verify_wait 看到 size=0 报 `pending`，永远等不到完成
- **超时后状态不准确**：原版在超时后有 `empty` vs `pending` 的区分（文件存在但空 vs 文件不存在）。简化版在超时后全部返回 `pending`，丢失了诊断信息
- **Agent 可能只写 error log 不写 output**：简化版的逻辑 `if _file_size(error) > 0: return failed` 是正确的，但如果 agent 既没写 output 也没写 error（被 maxTurns 用完或崩溃），两者都返回 pending——这和 Bash 方案行为一致，没有退化

**改进建议：**
- 在原子写入模型下，保留 timeout 时的最终检查：如果文件存在且 size==0，报 `"empty"`（因为 Write tool 不会写空文件，所以这只可能来自非原子路径的遗留文件或手动创建）
- 添加 `_file_size(output) == 0` 的特殊处理而不是忽略它

### 4. CRITICAL PROHIBITION 防止主 agent 跳过等待 — **必要但不够**

**优势：**
- 正确识别了核心风险：Claude 主 agent 收到 background agent 完成通知后可能直接读文件跳过 verify_wait
- "IMMEDIATELY in the next message" 的措辞比原版更强硬

**设计缺陷：**
- **指令型约束的脆弱性**：这是一个 prompt-level 约束，没有机械强制力。在 context 压缩后，这些 CRITICAL PROHIBITION 可能被截断或稀释。如果 Claude 的上下文中同时有 "agent completed: wrote 15KB to gemini-output.md" 通知和 "NEVER read output files directly" 指令，行为不可预测
- **"ignore ALL agent completion notifications"** 和 Agent tool 的设计冲突：`run_in_background: true` 的设计意图就是让主 agent 收到通知后继续处理。让主 agent 忽略这些通知违反了工具的使用模式
- **缺乏 hook 强制**：应该有一个 hook（类似 `post_edit_guard.py`）检测主 agent 是否在 verify_wait 返回前尝试读取 session 目录下的 output 文件

**改进建议：**
- 将 "不得跳过 wait" 的约束从 prompt 层提升到 **hook 层**：创建一个 `verify_read_guard` hook，在 Read tool 调用时检查路径是否匹配 `.ultra/collab/*/gemini-output.md` 或 `codex-output.md`，如果当前没有 verify_wait.py 进程在运行，则阻止读取
- 或者更简单：在 verify_wait.py 完成前用一个 lockfile（`.ultra/collab/<session>/WAIT_LOCK`），Wait 结束后删除。主 agent 的 SKILL.md 规则是"检查 WAIT_LOCK 是否存在"

### 5. 被忽略的更根本的设计问题

**问题 A：为什么需要 verify_wait.py？**

`run_in_background` 的 Agent/Bash 完成后，Claude Code 会主动通知主 agent。理论上主 agent 可以等两个通知都到了再继续，无需轮询文件系统。verify_wait.py 存在的原因是主 agent **不可靠地等待**——它可能在收到第一个通知后就继续。

真正的修复不是"更好的文件轮询"，而是让主 agent 的控制流更可靠。但在当前 Claude Code 架构下，prompt-level 控制流确实不可靠，所以 verify_wait.py 作为 **机械门控** 是合理的退而求其次的方案。

**问题 B：Bash stdout 截断**

无论用 Agent 还是直接 Bash，核心问题是：如果 Gemini/Codex 输出超过 Bash tool 的 stdout 缓冲区限制，输出会被截断。当前的 shell redirect 方案（`> file`）绕过了这个问题——output 直接写入文件，不经过 Bash tool 的 stdout 通道。Agent 方案反而引入了这个问题，因为 agent 要先通过 Bash 捕获 stdout 再 Write。

**这是 Agent 方案最严重的设计缺陷**——它用一个新问题（stdout 截断）替代了旧问题（空文件竞态）。

**问题 C：Codex `-o` flag 已经是原子的**

Codex CLI 的 `-o` flag 由 Codex 内部实现文件写入，可能已经是原子的（写入临时文件然后 rename）。如果是这样，只有 Gemini 的 shell redirect 需要修复，而不需要整个 Agent 架构。

### 总结评估

| 改动 | 判定 | 理由 |
|------|------|------|
| Agent 替代 Bash CLI | **反对** | 成本过高、引入 stdout 截断风险、过度工程 |
| Write tool 原子写入 | **赞成核心思路** | 但应通过更轻量的方式实现 |
| 简化 verify_wait.py | **部分赞成** | `_file_size()` TOCTOU 修复好，但不应丢失 `empty` 状态 |
| CRITICAL PROHIBITION | **赞成但不够** | 需要 hook 层强制，不能仅靠 prompt |

### 推荐方案

**不引入 Agent，用 Bash + temp file + rename 模式：**

```bash
# Gemini: 写入临时文件，成功后 rename（OS 级原子操作）
gemini -p "<prompt>" --yolo > "${SESSION_PATH}/.gemini-output.tmp" 2>"${SESSION_PATH}/gemini-error.log" && mv "${SESSION_PATH}/.gemini-output.tmp" "${SESSION_PATH}/gemini-output.md"
```

这是 UNIX 世界最经典的原子写入模式：
- 写入 `.tmp` 文件（verify_wait.py 不检测它）
- `mv` 是 POSIX 标准的原子操作（同一文件系统上）
- 如果 CLI 失败，`.tmp` 要么不存在要么残留（可以用 `|| rm -f .tmp` 清理）
- 零 token 开销，零 agent 开销
- verify_wait.py 的 stability check 可以安全移除（因为文件出现即完整）

保留 verify_wait.py 的 `_file_size()` TOCTOU 修复和 timeout 时的 `empty` 状态区分，仅移除 `at_timeout` 的双路逻辑。
