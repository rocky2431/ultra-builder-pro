<div align="center">

# Ultra Builder Pro

[English](README.md) · **简体中文**

**为 Claude Code 打造的动态项目知识库 —— 让需求偏移不再是技术债的源头。**

**解决"PRD 写的是什么" vs "代码实际在做什么"之间的断层 —— 哪怕 50 轮需求变更之后。**

[![Version](https://img.shields.io/badge/version-7.1.0-blue?style=for-the-badge)](CHANGELOG.md)
[![Tests](https://img.shields.io/badge/tests-179_passing-brightgreen?style=for-the-badge)](hooks/tests/)
[![Hooks](https://img.shields.io/badge/hooks-15-yellow?style=for-the-badge)](docs/architecture.md#hooks-system)
[![Agents](https://img.shields.io/badge/agents-12-red?style=for-the-badge)](docs/architecture.md#agent-system)
[![Skills](https://img.shields.io/badge/skills-17-orange?style=for-the-badge)](skills/)
[![License](https://img.shields.io/badge/license-MIT-blue?style=for-the-badge)](LICENSE)

```bash
git clone https://github.com/rocky2431/ultra-builder-pro.git ~/.claude
```

**Claude Code 跑得了的地方就跑得了。** macOS · Linux · Windows.

[为什么做这个](#为什么做这个) · [怎么用](#怎么用) · [动态项目知识库](#动态项目知识库) · [架构细节](docs/architecture.md) · [更新日志](CHANGELOG.md)

</div>

---

## 为什么做这个

我是 DeFi 工程师。大部分时候我不写代码 —— Claude Code 写。

但发版越多，我越发现同一个问题：**需求一直在偏移，没人盯**。

真实工程的现实是：PRD 永远不是"终稿"，只是"今天这版"。需求多一个子功能、约束改一个、实施过程中冒出新边界 —— 静态文档跟不上。它会过期。技术债就在 *规约说什么* 和 *代码做什么* 的缝隙里悄悄长。

BMAD、Speckit、Taskmaster 这些工具在 *规划阶段* 都做得不错。但你做到第 3 个 phase 的时候，PRD 还说"VIP 用户免运费"，代码已经悄悄改成"5 折优惠" —— 没有任何测试能抓到，因为测试是按新代码写的，不是按原始规约。

**结构性 lint（types、schema、调用图）看不到这种偏移。只有把 PRD 文本和 diff 一起读的 LLM 能看到。**

Ultra Builder Pro 就是这个想法的工程实现。它是一套**动态项目知识库** —— 一个会跟着代码改动**自我更新**的层，能同时浮现 *工程断点*（schema/类型/调用）和 *功能断点*（语义/意图），并把对的上下文喂给 Claude Code 的每一次编辑。

不需要 50 人公司的企业流程。不需要 sprint 仪式。只是 6 个命令 + 一套 sensor-driven 的 harness，让 Claude 在项目持续偏移的过程中保持清醒。

— **rocky2431**

---

## 适合谁

用 Claude Code 真正在做产品，并且希望系统能：

- **记住**：每个文件什么意思、属于哪个任务、上次改了什么
- **浮现偏移**：在 "免运费" 悄悄变成 "5 折" 的瞬间发现，不是部署后才发现
- **不挡路**：6 个命令，不是 30 个；不要 sprint 计划、不要故事点
- **真测试**：179 个 hook 测试通过，核心路径不 mock

如果你想要重型企业流程，用 [BMAD](https://github.com/bmad-code-org/BMAD-METHOD)。想要纯规划工具，用 [Speckit](https://github.com/specifyx/speckit)。想要不动 git 的工作流，这个不适合 —— Ultra Builder 每个任务都 atomic commit。

---

## 最新版本 — v7.1.0（动态项目知识库）

让知识库活着、跟得上需求偏移。五个增量，全是 sensor 模式（不阻断），全部复用 v7.0 substrate：

- **反向 trace**（`post_edit_guard.py`）—— 编辑文件时 stderr 注入"该文件属于哪个任务 + 前几条 AC"；不属于任何任务的文件回退到 git 上下文（branch + 最近 commit）
- **AC 偏移检测**（`review-ac-drift` agent）—— `/ultra-review` 的第 7 个专家；同时读 AC 文本和 diff；抓到结构性 lint 看不到的语义漂移（"免运费 → 5 折"那种）
- **wiki 视图**（`wiki_generator.py`）—— 从项目状态自动派生 `.ultra/wiki/{index,log}.md`，含 Recent Activity 表
- **会话 trail**（`session_trail.py`）—— Stop hook 把会话事实 fold 进当前任务的 `## Session Trail` 段
- **孤儿会话处理** —— 没有 active task 的会话也不丢：写到 `.ultra/sessions/orphan-trail.md` + Recent Activity 合并

→ 完整版本历史见 [CHANGELOG.md](CHANGELOG.md)。架构细节见 [docs/architecture.md](docs/architecture.md)。

---

## 快速开始

```bash
git clone https://github.com/rocky2431/ultra-builder-pro.git ~/.claude
cd ~/.claude && python3 -m pytest hooks/tests/ --ignore=hooks/tests/test_pre_stop_check.py
# 应该输出：179 passed
```

然后到任意项目下：

```bash
cd ~/your-project && claude
```

在 Claude Code 里跑 `/ultra-init` 初始化新项目（或 `/ultra-status` 验证安装）。

### 推荐：跳过权限确认模式

```bash
claude --dangerously-skip-permissions
```

整个系统是为顺畅自动化设计的。一边跑一边停下来批 `date` 和 `git commit` 50 次，背离了初衷。如果你不想全开，可以在 `.claude/settings.json` 的 `permissions.allow` 里白名单具体命令。

---

## 怎么用

六个命令。每个只做一件事；复杂度藏在系统里面。

### 1. 初始化

```
/ultra-init
```

自动检测项目类型，从 `.ultra-template/` 复制模板，建好 `.ultra/` 目录结构。**产出：** `.ultra/{specs,tasks,docs}/`、`PHILOSOPHY.md`、`north-star.md`。

### 2. Research（可选但建议）

```
/ultra-research
```

17 个 step-file（BMAD 风格架构，每个 ~200 行）。每步都有：强制 web search + 预写好的查询、结构化输出模板带字段级 spec、写完就走的纪律。

- Steps 00–05：产品 Discovery（TAM/SAM/SOM、Strategy Canvas、验证计划）
- Steps 10–11：Personas & Scenarios
- Steps 20–22：功能定义带 Given/When/Then AC
- Steps 30–32：架构（每个技术选型都要带来源）
- Steps 40–41：质量 & 部署
- Step 99：综合 → `research-distillate.md`

**产出：** `.ultra/specs/{discovery,product,architecture}.md`。

### 3. 规划

```
/ultra-plan
```

读规约，生成原子任务拆解。模式选择：EXPAND / SELECTIVE（默认）/ HOLD / REDUCE。每个任务带 Given/When/Then AC、Definition of Drift（防范围蔓延）、目标文件、`trace_to` 指向规约段。Walking skeleton 永远是 Task #1。每 3-4 个任务插一个 Integration Checkpoint。

**产出：** `.ultra/tasks/{tasks.json, contexts/task-N.md}`。

### 4. 开发

```
/ultra-dev
```

TDD 流程：RED → GREEN → REFACTOR。**Goal-Always-Present** 机制（`mid_workflow_recall.py`）每次 Edit/Write 都把当前任务 AC 注入 stderr —— Claude 永远知道"完成"长什么样。`progress.json` 持续追踪 6 维 `evidence_score`。Step 4.5 在 commit 前自动跑 `/ultra-review all`。

**产出：** 实现 + 测试 + 每个任务一个 atomic commit。

### 5. 评审

```
/ultra-review              # 智能跳过（按 diff 内容）
/ultra-review all          # 强制 7 个 agent（合并前的 gate）
```

7 个专家 agent 平行跑，各自在新鲜上下文里，把 findings 写到 `.ultra/reviews/<session>/`。Coordinator 聚合 → SUMMARY。第 7 个 agent（`review-ac-drift`，v7.1）同时读 spec 和 diff，做语义对齐。

### 6. 交付

```
/ultra-deliver
```

CHANGELOG、版本号、build、tag、push。Pre-flight：完整测试套件 + ultra-review verdict 必须是 APPROVE。

---

## 动态项目知识库

和 BMAD/Speckit/Taskmaster 不一样的核心：**这个 KB 是活的**。每次 Edit/Write/Stop 都自动更新，你什么都不用做。

### 三层架构

```
┌─────────────────────────────────────────────────────────────┐
│  Layer 3 — Schema 层（哲学，不变）                           │
│    .ultra/PHILOSOPHY.md, CLAUDE.md, harness 规则            │
│                                                              │
│  Layer 2 — Wiki 层（解读；人 + LLM 都读）                    │
│    .ultra/wiki/index.md            按状态分组的任务         │
│    .ultra/wiki/log.md              时间序进度               │
│    task-*.md ## Session Trail      fold 进来的会话事实      │
│    .ultra/sessions/orphan-trail.md 无任务会话               │
│                                                              │
│  Layer 1 — Facts 层（机器维护）                              │
│    .ultra/relations.json           task ↔ spec ↔ code       │
│    .ultra/tasks/progress/          每任务 evidence_score    │
│    git history                     真理来源                 │
└─────────────────────────────────────────────────────────────┘
```

Wiki 节点**不存事实**，只存解读。事实由机器维护新鲜度。**不会有悄悄过期** —— 事实变了，wiki 重新生成。

### 实际行为（你可以试）

| 触发 | 你看到什么 |
|------|-----------|
| 编辑某个属于任务的文件 | stderr 出现 `[Trace] task-3 (in_progress): VIP shipping; AC-1: VIP 用户运费 = 0` |
| 在 Ultra 项目里编辑无主文件 | `[Trace] (no task) shipping.ts on branch main; last: abc123 fix...` |
| 在非 Ultra 项目里编辑文件 | 完全静默（不打扰） |
| 有 active task 时 Stop + 改了文件 | 一行 fold 进任务的 `## Session Trail` 段 |
| 无 active task 时 Stop + 改了文件 | 一行 fold 进 `.ultra/sessions/orphan-trail.md` |
| 改 spec 或 task 定义 | `relations.json` 重建 + wiki 刷新 |
| 跑 `/ultra-review all` | 7 个 agent 平行评审；review-ac-drift 同时读 spec + diff 做语义对齐 |

---

## 它为什么管用

### Sensor-Not-Blocker 哲学（v7.0）

v7 之前：hook 对每个可恢复问题都阻断（mock、scope 字眼、silent catch）。结果：agent 改测试/规约去 *绕开* 阻断 —— 比没 hook 更糟。

v7 反过来：阻断只留给**真不可逆**的动作（硬编码 secret、SQL 注入、force-push 到 main、DB 迁移 commit）。其他全是 advisory。Agent 读到、判断、继续。

### 双向可追溯

大部分工具只维护 `spec → task`。Ultra Builder 维护三向：

- `task → spec section`（`trace_to`）
- `spec section → tasks`（`referenced_by`）
- `code path → tasks`（`files` 反向索引，v7.1）

编辑 `src/checkout/shipping.ts`，系统知道：这是 task-3，trace 到 `specs/product.md#vip-shipping`，有 2 条 AC。编辑的瞬间全部出现在 stderr。

### 平行多 Agent 评审

串行评审会随 finding 累积丢失上下文。Ultra Review 把 7 个专家 fan-out 平行跑 —— 每个在新鲜的 200k 上下文里 —— 各自把 findings 写到 JSON 文件，coordinator 去重 + 排序。主会话上下文用量保持在 30-40%。

### 跨会话记忆

`session_journal.py` 把结构化摘要写到 SQLite FTS5 + Chroma 向量。下次会话，`mid_workflow_recall.py` 在你编辑文件时注入相关历史失败 + 当前 AC。混合搜索（FTS5 + RRF）由 `/recall` 提供。这是从 claude-mem 失败模式（一次 ~25k token 的批量注入）里学到的：我们 SessionStart 注入 ~50 token，按需搜索。

---

## 命令 & 技能

| 类别 | 例子 | 说明 |
|------|------|------|
| **工作流** | `/ultra-init` `/ultra-research` `/ultra-plan` `/ultra-dev` `/ultra-test` `/ultra-deliver` | 分步 pipeline |
| **质量** | `/ultra-review` `/ultra-verify`（三方 AI 验证）`/ultra-status` | 独立 gate |
| **记忆** | `/recall` `/learn` | 跨会话搜索 + 模式提取 |
| **思考** | `/ultra-think` | 对抗性推理框架 |

**17 个 skill** 在 `skills/` 下 —— research step-files、review pipeline、三方 verify（Claude + Gemini + Codex）、recall、vercel 最佳实践、Web 设计指南、以及只供 agent 用的清单（security/testing/integration）。

**12 个 agent** 在 `agents/` 下 —— 5 个交互式（智能合约专家 + 审计、code-reviewer、tdd-runner、debugger）+ 7 个评审 pipeline。所有 agent 都用 `memory: project`，按项目积累模式。

→ 完整参考：[docs/architecture.md](docs/architecture.md)。

---

## 配置

项目级配置在 `.ultra/`（按项目走，大部分 gitignore）。全局配置在 `~/.claude/settings.json`。

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

---

## 许可证

MIT。详见 [LICENSE](LICENSE)。

---

<div align="center">

**Claude Code 很强。Ultra Builder Pro 让它在项目持续偏移时保持清醒。**

</div>
