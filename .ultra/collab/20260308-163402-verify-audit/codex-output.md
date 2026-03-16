1. `Warning`  
位置：[SKILL.md](/Users/rocky243/.claude/skills/gemini-collab/SKILL.md#L39) [SKILL.md](/Users/rocky243/.claude/skills/gemini-collab/SKILL.md#L50) [gemini-cli-reference.md](/Users/rocky243/.claude/skills/gemini-collab/references/gemini-cli-reference.md#L15) [gemini-prompts.md](/Users/rocky243/.claude/skills/gemini-collab/references/gemini-prompts.md#L10) [SKILL.md](/Users/rocky243/.claude/skills/codex-collab/SKILL.md#L48) [codex-cli-reference.md](/Users/rocky243/.claude/skills/codex-collab/references/codex-cli-reference.md#L51) [codex-prompts.md](/Users/rocky243/.claude/skills/codex-collab/references/codex-prompts.md#L28)  
说明：`2>/dev/null` 仍大量残留，说明“stderr 改写到 error.log”只在 `ultra-verify` 编排文档里落地了，没有全量修复到 `gemini-collab` / `codex-collab` 主文档和 prompts/reference。这样会吞掉认证失败、CLI 参数错误、超时前告警，直接导致空 `output.md`，排障信息丢失。你提到的 Round 2 修复目前只算“部分应用”，不是“全部正确应用”。

2. `Warning`  
位置：[gemini-cli-reference.md](/Users/rocky243/.claude/skills/gemini-collab/references/gemini-cli-reference.md#L65) [gemini-prompts.md](/Users/rocky243/.claude/skills/gemini-collab/references/gemini-prompts.md#L10)  
说明：`git diff HEAD~1 | gemini ...` 作为“review current changes”示例有范围错误。`git diff HEAD~1` 会把“上一提交以来的全部差异”都送进去，不仅包含未提交改动，还会把 `HEAD` 相对 `HEAD~1` 的已提交改动也混进来；同时在首个提交或浅克隆场景下可能直接失败。对“当前改动审查”来说，这会产生错误审查范围。

3. `Info`  
位置：[codex-cli-reference.md](/Users/rocky243/.claude/skills/codex-collab/references/codex-cli-reference.md#L18) [codex-prompts.md](/Users/rocky243/.claude/skills/codex-collab/references/codex-prompts.md#L7) [orchestration-flow.md](/Users/rocky243/.claude/skills/ultra-verify/references/orchestration-flow.md#L27)  
说明：其余 3 个上一轮问题我没有看到残留：`--commit-title` 已改为 `--title`，`$(cat FILE)` 已改为 stdin pipe，`--full-auto` 与 `-s read-only` 的冲突也已修正；`ultra-verify` 的编排文档确实改成了 `error.log`。当前主要问题是这些修复没有在所有协作文档里同步完成。