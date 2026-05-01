<div align="center">

# Ultra Builder Pro

[English](README.md) · **简体中文**

**为 Claude Code 打造的 production-grade 工程化 harness。**

**6 命令工作流 · sensor-driven 钩子链 · 多 agent 平行评审 · 跨会话记忆 · 活的项目知识库 · 三方 AI 交叉验证。**

[![Version](https://img.shields.io/badge/version-7.1.0-blue?style=for-the-badge)](CHANGELOG.md)
[![Tests](https://img.shields.io/badge/tests-179_passing-brightgreen?style=for-the-badge)](hooks/tests/)
[![Hooks](https://img.shields.io/badge/hooks-15-yellow?style=for-the-badge)](docs/architecture.md#hooks-system)
[![Agents](https://img.shields.io/badge/agents-9-red?style=for-the-badge)](docs/architecture.md#agent-system)
[![Skills](https://img.shields.io/badge/skills-22-orange?style=for-the-badge)](skills/)
[![License](https://img.shields.io/badge/license-MIT-blue?style=for-the-badge)](LICENSE)

```bash
git clone https://github.com/rocky2431/ultra-builder-pro.git ~/.claude
```

**Claude Code 跑得了的地方就跑得了。** macOS · Linux · Windows.

[为什么做这个](#为什么做这个) · [里面有什么](#里面有什么) · [怎么用](#怎么用) · [它为什么管用](#它为什么管用) · [架构](docs/architecture.md) · [更新日志](CHANGELOG.md)

</div>

---

## 为什么做这个

我是 Web3 + AI-native 工程师。我不写代码，Claude Code 写。

但用 Claude Code 把代码 *写出来*，和把代码 *推到 production*，是两回事。当你需要：

- 真的 code review，不是"看起来没问题"
- 真的测试通过，不是 mock 装出来的绿
- 经得起 50 轮需求偏移的规约，不是悄悄漂移
- 跨会话不丢上下文，不是昨天决策今天蒸发
- 多 AI 互相校验，不是一家之言

—— 单靠对话不够。LLM 会忘、会偷懒、会 silently scope-reduce、会假装通过。会说"VIP 用户免运费"然后实现成"5 折"。

Ultra Builder Pro 是建立在 Claude Code 之上的 **工程化 harness**，让它达到 production-grade。不是单一工具——是六层集成的 substrate：

1. **Spec-driven 6 命令工作流**：从想法到发布
2. **Sensor-driven 15 钩子链**：v7.0 哲学，提示而不阻挠
3. **7 agent 平行评审 pipeline**：含语义偏移检测
4. **跨会话 SQLite + 向量记忆**：结构化 AI 摘要
5. **活的双向 task ↔ code ↔ spec 知识库** (v7.1)
6. **三方 AI 验证**：Claude + Gemini + Codex 共识打分

它不替你思考。它**替你盯住 Claude**——让 LLM 在干活时始终知道目标、看到上下文、跑过测试、过了评审、留下足迹。

别的系统给你其中一部分。BMAD 有工作流，claude-mem 试过记忆然后炸了，GSD 把 spec-driven 做得很到位。Ultra Builder Pro 是集成版本——每一层都和别的层咬合。

— **rocky2431**

---

## 适合谁

用 Claude Code 做真产品、想要：

- **默认就有 production 纪律**——TDD 强制、平行评审、每任务原子 commit
- **会记事的系统**——跨文件、跨任务、跨会话、跨 AI provider
- **早抓 drift**——"免运费"刚变成"5 折"就抓到，不是部署后才发现
- **不要表演式流程**——9 个命令而不是 30 个；不要 sprint 计划、故事点、Jira

如果你想要重型企业流程，用 [BMAD](https://github.com/bmad-code-org/BMAD-METHOD)。要纯规划工具，用 [Speckit](https://github.com/specifyx/speckit)。要轻量 context 工程，用 [GSD](https://github.com/gsd-build/get-shit-done)。Ultra Builder Pro 是 *最大化* 选项——你想要每层都集成的时候选这个。

---

## 里面有什么

建立在 Claude Code 之上。加六层 production engineering 纪律。

### 1. Spec-Driven 6 命令工作流

```
/ultra-init  →  /ultra-research  →  /ultra-plan  →  /ultra-dev  →  /ultra-test  →  /ultra-deliver
```

每个命令只做一件事；复杂度藏在系统里。背后是：TDD 红绿重构强制、自动 git 流程（每任务一个原子 commit）、walking skeleton 优先、每 3-4 个任务插一个 integration checkpoint。

`/ultra-research` 本身是 17 个 step-file 的架构（BMAD 启发）——每步密集指令、预写好的 web 搜索查询、结构化输出模板、写完就走的纪律。产出：`discovery.md`、`product.md`、`architecture.md`，以及供 `/ultra-plan` 消费的 token 紧凑版 `research-distillate.md`。

→ 见 `commands/ultra-*.md` 和 [docs/architecture.md](docs/architecture.md)。

### 2. Sensor-Driven 钩子链 (15 hooks)

**v7.0 哲学：阻断只留给 *真不可逆* 的动作。** 硬编码 secret、SQL 注入、force-push 到 main、DB 迁移 commit。其他全部——mock、scope reduction、silent catch、TODO/FIXME、默认关闭的 feature flag——都是 *advisory*。Agent 读到、判断、继续。

这反转了 v7 之前的 over-correction 死循环：被阻断的 agent 会偷偷改测试和规约去绕开（比没钩子更糟）。Sensor 模式只给信号，不扭曲。钩子还在决策时刻 **注入目标上下文**：你开始编辑文件时，`mid_workflow_recall.py` 把当前任务 AC + memory.db 里相关的历史失败注入 stderr。

→ 钩子表：[docs/architecture.md#hooks-system](docs/architecture.md#hooks-system)。

### 3. 多 agent 平行评审 pipeline (7 专家)

串行评审会随 finding 累积丢失上下文。`/ultra-review` 把 7 个专家平行 fan-out——每个在新鲜的 200k 上下文里——coordinator 去重 + 排序。**主会话上下文用量保持在 30-40%**，哪怕跑完整套深度评审。

专家们：
- `review-code`——security、SOLID、forbidden patterns、scope drift
- `review-tests`——mock 违规、覆盖率缺口、边界测试
- `review-errors`——silent failure、吞掉的错误、空 catch
- `review-design`——类型设计、封装、复杂度
- `review-comments`——过期、误导、低价值的注释
- `review-ac-drift` (v7.1)——**语义对齐**：同时读 spec 文本和 diff，抓"VIP 免运费 → 5 折"这种结构 lint 看不到的偏移
- `review-coordinator`——聚合、去重、生成 SUMMARY

verdict 逻辑：P0 > 0 → REQUEST_CHANGES；P1 > 3 → REQUEST_CHANGES；P1 > 0 → COMMENT；否则 APPROVE。Branch-scoped session 索引，支持多次 recheck 形成迭代链。

→ 见 `skills/ultra-review/SKILL.md`。

### 4. 跨会话记忆 + AI 摘要

SQLite FTS5 + Chroma 向量库 + 结构化 Haiku 摘要。**会话结束时** 一个非阻塞 daemon 解析 transcript，生成结构化 JSON 摘要（`request`、`completed`、`learned`、`next_steps`），同时写入 SQLite FTS5 行和 Chroma 向量。**会话开始时** 注入一行（~50 token）讲上次会话——不批量倾倒。

按需用 `/recall` 搜索。混合模式（默认）：FTS5 关键词 + Chroma 语义，通过 RRF (k=60) 融合。还有纯语义 / 纯关键词模式。skill 在 forked context 里跑，搜索结果不污染主对话。

设计成 **claude-mem** 失败之后的安全替代——claude-mem 一次注入 ~25k token 把上下文炸了。

→ 见 `skills/recall/SKILL.md`。

### 5. 活的项目知识库 (v7.1)

`.ultra/relations.json` 维护 task ↔ code ↔ spec 的双向索引。`.ultra/wiki/{index,log}.md` 自动派生 wiki 视图。会话事实 fold 进任务 context md 的 `## Session Trail` 段。没有 active task 的会话也不丢——residue 进 `.ultra/sessions/orphan-trail.md`。

三层架构：

```
Layer 3 — Schema 层（不变）：    PHILOSOPHY.md, CLAUDE.md, harness 规则
Layer 2 — Wiki 层（解读）：      wiki/{index,log}.md, ## Session Trail, orphan-trail
Layer 1 — Facts 层（机器维护）： relations.json, progress/*.json, git history
```

Wiki 节点**不存事实**，只存解读。**不会有悄悄过期**——事实变了，wiki 重生。编辑某个属于任务的文件 → stderr 显示任务 + AC。编辑无主文件 → git 上下文回退（branch + 最近 commit）。在非 Ultra 项目里编辑 → 完全静默。

→ 见 [CHANGELOG v7.1](CHANGELOG.md#v710-2026-05-01--dynamic-project-knowledge-base)。

### 6. 三方 AI 交叉验证

`/ultra-verify` 把 Claude + Gemini + Codex *独立* 起 background 任务。Claude 在读其他人之前 *先把自己的答案写到文件*——防止污染。然后 Claude 读三份输出做综合，按共识打分：

| 结果 | 信心 |
|------|------|
| 3/3 一致 | **共识** |
| 2/3 一致 | **多数** |
| 全分歧 | **无共识** |

四个模式：`decision`（架构选择）、`diagnose`（bug 假设）、`audit`（代码审计）、`estimate`（工作量估算）。降级优雅——一个 AI 失败 → 两方比对（信心封顶 Majority）；两个失败 → Claude 单干并显式警告。

底层共享 `ai-collab-base` skill 同步 collab protocol 文件。消除 gemini-collab 和 codex-collab 之间 ~90% 的结构性重复。

→ 见 `skills/ultra-verify/SKILL.md`。

---

## 最新版本 — v7.1.0

**动态项目知识库** —— 在 v7.0 sensor-first 基础上的五个增量：

- 文件 → 任务反向 trace + git 上下文回退（`post_edit_guard.py`）
- 第 7 个评审专家 `review-ac-drift` 做语义对齐
- 自动派生 wiki + Recent Activity 表
- 会话 trail fold 进任务 context
- 孤儿会话处理（覆盖跨任务 / 无规划 / hotfix）

→ 完整版本历史：[CHANGELOG.md](CHANGELOG.md)。

---

## 快速开始

```bash
git clone https://github.com/rocky2431/ultra-builder-pro.git ~/.claude
cd ~/.claude && python3 -m pytest hooks/tests/ --ignore=hooks/tests/test_pre_stop_check.py
# 应该输出：179 passed
```

到任意项目下：

```bash
cd ~/your-project && claude
```

在 Claude Code 里跑 `/ultra-init` 初始化（或 `/ultra-status` 验证安装）。

### 推荐：跳过权限确认模式

```bash
claude --dangerously-skip-permissions
```

整个 harness 是为顺畅自动化设计的。一边跑一边停下来批 `git commit` 50 次，背离了初衷。如果你不想全开，可以在 `.claude/settings.json` 的 `permissions.allow` 里白名单具体命令。

---

## 怎么用

6 命令 pipeline，端到端。每个命令的输出是下一个命令的输入。

| 步 | 命令 | 做什么 | 产出 |
|----|------|-------|------|
| 1 | `/ultra-init` | 自动检测项目类型；从 `.ultra-template/` 复制模板；建立 `.ultra/` 目录 | `.ultra/{specs,tasks,docs}/`、`PHILOSOPHY.md`、`north-star.md` |
| 2 | `/ultra-research` | 17 步研究 pipeline；每步强制 web 搜索；结构化输出模板 | `discovery.md`、`product.md`、`architecture.md`、`research-distillate.md` |
| 3 | `/ultra-plan` | 原子任务拆解；模式（EXPAND/SELECTIVE/HOLD/REDUCE）；walking skeleton 优先；integration checkpoint | `tasks.json`、`contexts/task-N.md` 每任务一份 |
| 4 | `/ultra-dev` | TDD 红绿重构；Goal-Always-Present AC 注入；每任务一个原子 commit；Step 4.5 自动跑 `/ultra-review all` | 实现、测试、commit |
| 5 | `/ultra-review` | 7 agent 平行评审；coordinator 去重；SUMMARY.json + .md | `.ultra/reviews/<session>/SUMMARY.{json,md}` |
| 6 | `/ultra-deliver` | Pre-flight 测试 + review verdict APPROVE；CHANGELOG；版本号；tag；push | 发布产物、git tag |

独立 gate（任意时候用）：`/ultra-status`、`/ultra-verify`、`/ultra-test`、`/ultra-think`。记忆：`/recall`、`/learn`。

---

## 它为什么管用

### Sensor-Not-Blocker 哲学（v7.0）

v7 之前钩子对每个可恢复问题都阻断——agent 用改测试 / 改规约绕开，比没钩子更糟。v7 反过来：阻断只留给不可逆的事，其他全是 advisory。Agent 既有信号又有自主权。PHILOSOPHY.md C3 (Sensors not Blockers) + C4 (Incremental Validation) 把这写成了规则。

### 双向可追溯

大部分工具只维护 `spec → task`。Ultra Builder 维护三向：
- `task → spec section`（`trace_to`）
- `spec section → tasks`（`referenced_by`）
- `code path → tasks`（`files` 反向索引，v7.1）

编辑 `src/checkout/shipping.ts` → 系统知道是 task-3 → trace 到 `specs/product.md#vip-shipping` → 有 2 条 AC。编辑的瞬间全部出现在 stderr。

### 平行多 Agent 评审（零上下文污染）

串行评审会丢上下文。Ultra Review 把 7 个专家 fan-out 平行跑，每个在新鲜 200k 上下文里，把 finding 写到 JSON 文件；coordinator 去重。主对话从来看不到 raw findings——只看到去重后的 SUMMARY。哪怕跑完 7 路评审，上下文用量也保持在 30-40%。

### 跨会话记忆，不批量注入

claude-mem 在 SessionStart 注入 ~25k token，炸了上下文。我们的方法：开会话时 1 行（~50 token），按需搜索。Stop 时通过异步 daemon 自动捕获（不阻塞热路径）。混合检索：FTS5 + Chroma 向量，通过 Reciprocal Rank Fusion 融合。

### 三方 AI 互相 review

单 LLM 是自己改自己作业。三个不同 family 的 LLM（Anthropic、Google、OpenAI）才是真独立。共识浮现而不是断言。

---

## 命令 & 技能

`commands/` 下 **9 个命令**：

| 类别 | 命令 |
|------|------|
| 工作流 | `ultra-init` `ultra-research` `ultra-plan` `ultra-dev` `ultra-test` `ultra-deliver` |
| 质量 | `ultra-status` `ultra-think` |
| 记忆 | `learn` |

`skills/` 下 **22 个 skill**：

| 类别 | Skills |
|------|--------|
| 工作流 | `ultra-research`（17 step-files）、`ultra-review`、`ultra-verify`、`recall` |
| AI 协作 | `ai-collab-base`、`gemini-collab`、`codex-collab` |
| Agent-only 清单 | `code-review-expert`、`integration-rules`、`security-rules`、`testing-rules` |
| 工具 | `agent-browser`、`find-skills`、`use-railway`、`market-research` |
| 设计 / 输出 | `web-design-guidelines`、`guizang-ppt-skill`、`html-ppt` |
| Vercel 最佳实践 | `vercel-react-best-practices`、`vercel-react-native-skills`、`vercel-composition-patterns` |
| 模式提取 | `learned/`（由 `/learn` 填充） |

`agents/` 下 **9 个 agent**：

| 类型 | Agents |
|------|--------|
| 交互式 | `code-reviewer`、`debugger` |
| 评审 pipeline（平行） | `review-code`、`review-tests`、`review-errors`、`review-design`、`review-comments`、`review-ac-drift`、`review-coordinator` |

所有 agent 都用 `memory: project` 按项目积累模式。

→ 完整参考：[docs/architecture.md](docs/architecture.md)。

---

## 配置

项目状态在 `.ultra/`（按项目走，大部分 gitignore）。全局配置在 `~/.claude/settings.json`。

### 推荐 `.gitignore`

```
.ultra/memory/
.ultra/reviews/
.ultra/compact-snapshot.md
.ultra/debug/
.ultra/workflow-state.json
.ultra/sessions/orphan-trail.md
```

这些**要**进版本控制：
- `.ultra/specs/`
- `.ultra/tasks/tasks.json`、`.ultra/tasks/contexts/`
- `.ultra/relations.json`
- `.ultra/wiki/{index,log}.md`（自动生成，但 code review 时有用）

### 敏感文件保护

加到 `~/.claude/settings.json`：

```json
{
  "permissions": {
    "deny": [
      "Read(./.env)", "Read(./.env.*)",
      "Read(./secrets/**)", "Read(./**/*credential*)"
    ]
  }
}
```

---

## 常见问题

| 现象 | 解决 |
|------|------|
| 装完测试不过 | 跑 `python3 hooks/system_doctor.py` 做深度审计 |
| Hook 不触发 | 检查 `~/.claude/settings.json` 有 `hooks` 段；重启 Claude Code |
| Wiki 过期 | 改一下 `.ultra/specs/` 或 `.ultra/tasks/` 任意文件触发；或手动跑 `python3 ~/.claude/hooks/wiki_generator.py /your/repo` |
| Memory.db locked | 关掉残留 Claude Code 会话（一次只能一个写入） |
| `relations.json` 有 dangling trace_to | 跑 `/ultra-status`；断链会被高亮 |
| `ultra-verify` Gemini/Codex 不可用 | 装：`npm i -g @google/gemini-cli @openai/codex`；不可用时降级到仅 Claude 并警告 |

---

## 许可证

MIT。详见 [LICENSE](LICENSE)。

---

<div align="center">

**Claude Code 很强。Ultra Builder Pro 让它达到 production-grade。**

</div>
