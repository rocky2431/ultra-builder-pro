我只审了你列出的 6 个文件，不是全量 9 个 `ultra-*` 命令。

**结论**
整体上，`/ultra-review` 和 `/ultra-dev` 的多任务模式最接近可执行标准；`/ultra-think` 有硬性缺口；`ultra-verify` 的主文件和 reference 文件之间已经出现漂移，足以让模型在执行时犹豫或补脑。

**1. 多任务模式是否正确实现**

| 文件 | 结论 | 说明 |
|---|---|---|
| `ultra-verify/SKILL.md` | 部分正确 | 有任务表，也有 `TaskCreate`/`TaskUpdate` 生命周期，但它只跟踪 4 个大步，而 reference 文件把后续拆成 6/7 步，定义不闭合。 |
| `ultra-verify/references/orchestration-flow.md` | 不够正确 | 开头要求“一步一个 TaskCreate”，但只创建 4 个任务，后文却继续编号到 7，容易让模型误以为 5/6/7 也该单独建 task。 |
| `ultra-review/SKILL.md` | 基本正确 | 5 个 major steps 与正文 phase 基本对应，恢复规则也清楚。主要问题不是缺任务，而是把“工作流 tracking task”和“后台 review agent 的 Task 调用”混在一起写。 |
| `ultra-think.md` | 不正确 | 明写必须 `TaskCreate/TaskUpdate`，但 frontmatter 的 `allowed-tools` 没有 `Task`，工具权限与指令冲突。 |
| `ultra-dev.md` | 正确 | 目前最完整，能作为基线。虽然正文有 `Step 0 / 0.5 / 4.4` 这类非表内步骤，但整体意图仍然清晰。 |
| `CLAUDE.md` workflow_tracking | 正确 | 规则清楚，且强调 “Each major step gets its own TaskCreate; in_progress/completed lifecycle; compact 后 TaskList 恢复”。 |

关键定位：
[ultra-think.md](/Users/rocky243/.claude/commands/ultra-think.md):1  
[ultra-think.md](/Users/rocky243/.claude/commands/ultra-think.md):10  
[ultra-verify/SKILL.md](/Users/rocky243/.claude/skills/ultra-verify/SKILL.md):27  
[orchestration-flow.md](/Users/rocky243/.claude/skills/ultra-verify/references/orchestration-flow.md):5  
[orchestration-flow.md](/Users/rocky243/.claude/skills/ultra-verify/references/orchestration-flow.md):85  
[ultra-review/SKILL.md](/Users/rocky243/.claude/skills/ultra-review/SKILL.md):11  
[ultra-review/SKILL.md](/Users/rocky243/.claude/skills/ultra-review/SKILL.md):136  
[ultra-dev.md](/Users/rocky243/.claude/commands/ultra-dev.md):10  
[CLAUDE.md](/Users/rocky243/.claude/CLAUDE.md):195

**2. Prompt 质量问题、重复和不一致**

1. 最严重的是 `/ultra-think` 的工具声明冲突。  
[ultra-think.md](/Users/rocky243/.claude/commands/ultra-think.md):4 没有 `Task`，但 [ultra-think.md](/Users/rocky243/.claude/commands/ultra-think.md):10-24 又强制 `TaskCreate/TaskUpdate`。这不是风格问题，是执行层面的自相矛盾。

2. `ultra-verify` 的 task table 和正文步骤编号漂移。  
[ultra-verify/SKILL.md](/Users/rocky243/.claude/skills/ultra-verify/SKILL.md):31-40 只有 4 步，但 reference 在 [orchestration-flow.md](/Users/rocky243/.claude/skills/ultra-verify/references/orchestration-flow.md):97-145 又继续写 Step 5/6/7。模型很容易问自己：“5/6/7 要不要额外 TaskCreate？”

3. `ultra-verify` 存在高重复、低增益复制。  
`Workflow Tracking` 表在主文件和 reference 里几乎重复一份，但用词略有偏差：`On context recovery` vs `Recovery after compact`。这类双写最容易长期漂移。  
[ultra-verify/SKILL.md](/Users/rocky243/.claude/skills/ultra-verify/SKILL.md):27-40  
[orchestration-flow.md](/Users/rocky243/.claude/skills/ultra-verify/references/orchestration-flow.md):5-18

4. `ultra-review` 把两类 “Task” 混在一起写，术语不够干净。  
一边是 workflow tracking 的 `TaskCreate/TaskUpdate`，另一边是后台 review agents 的 `Task` 调用。对于模型来说，这会增加错误调用 `TaskOutput`、错误更新 workflow task 的概率。  
[ultra-review/SKILL.md](/Users/rocky243/.claude/skills/ultra-review/SKILL.md):11-25  
[ultra-review/SKILL.md](/Users/rocky243/.claude/skills/ultra-review/SKILL.md):138-174

5. `/ultra-think` 的“至少生成 3 个 distinct approaches”过硬。  
对很多问题，这会诱导模型硬凑方案，反而降低真实推理质量。  
[ultra-think.md](/Users/rocky243/.claude/commands/ultra-think.md):49-56

6. `/ultra-think` 的 fast path 没有定义 task 关闭语义。  
Step 1 允许“问题简单就直接回答”，但没有说剩余 Step 2-5 的 task 怎么处理。最少也该说明：跳过时仍需 `TaskUpdate(completed)` 并标记 skipped reason。  
[ultra-think.md](/Users/rocky243/.claude/commands/ultra-think.md):38-40

7. `ultra-dev` 虽然是 gold standard，但也提示了一个规范空白。  
它的任务表不是全文所有编号步骤的完整映射，说明真实规范其实是 “major step tracked, substeps narrative”。这个原则应该写死到所有命令里，否则别的文件会继续分裂。  
[ultra-dev.md](/Users/rocky243/.claude/commands/ultra-dev.md):14-32  
[CLAUDE.md](/Users/rocky243/.claude/CLAUDE.md):197-198

**3. 优化建议**

1. 统一成一个明确模板，只允许一种解释。建议所有文件都写成下面这个意思：
```md
Workflow tasks track only the rows in the table below.
Substeps/phases mentioned later are narrative unless explicitly added to the table.
For each row: one TaskCreate on start of command, TaskUpdate(in_progress) before execution, TaskUpdate(completed) after execution.
If a step is skipped by fast-path logic, still TaskUpdate(completed) with note="skipped".
```

2. `ultra-think` 先修 frontmatter。  
把 `Task` 加进 `allowed-tools`，否则它的 workflow tracking 是伪指令。  
文件：[ultra-think.md](/Users/rocky243/.claude/commands/ultra-think.md):4

3. `ultra-verify` 二选一，不要半套。
- 要么任务表升级为 6 步，对齐 Collect / Confidence / Write Synthesis。
- 要么正文把 Step 5/6/7 改成 `Substep`，明确它们归属 Step 4。  
我更建议后者，和 `ultra-dev` 风格一致。

4. `ultra-verify` 的 reference 去重。  
主文件保留 task table；reference 只写一句 “Use the same workflow task table defined in SKILL.md”。不要复制整张表。

5. `ultra-review` 改术语，避免 “Task” 二义性。  
建议把后台 agent 那段改成：
- `workflow tasks` = `TaskCreate/TaskUpdate`
- `review agent launches` = background `Task` calls  
并显式写一句 “Do not confuse workflow tasks with review-agent task invocations.”

6. 在 `CLAUDE.md` 补一条全局规则。  
直接补到 [CLAUDE.md](/Users/rocky243/.claude/CLAUDE.md):195 附近：
```md
If a command contains numbered substeps not present in the task table, they are not separate TaskCreate items unless explicitly stated.
```

如果你要，我下一步可以直接给你一份“统一版 Workflow Tracking 段落模板”，让 9 个 `ultra-*` 命令一次性对齐。  
可复核命令：

```bash
rg -n "## Workflow Tracking|TaskCreate|TaskUpdate|TaskList|allowed-tools|### Step " ~/.claude/commands ~/.claude/skills
```

```bash
diff -u ~/.claude/skills/ultra-verify/SKILL.md ~/.claude/skills/ultra-verify/references/orchestration-flow.md | sed -n '1,220p'
```