我将开始对指定的 `ultra-*` 指令及相关技能文件进行审计，重点检查 “Workflow Tracking (MANDATORY)” 模式的实现情况。

首先，我将读取这些文件以分析其内容和任务追踪逻辑。
经过对 `ultra-*` 指令及相关技能文件的审计，以下是关于 **Workflow Tracking (MANDATORY)** 模式实现情况的详细报告：

### 1. 多任务模式（Multi-task Pattern）实现情况
所有审核的文件均已实现多任务模式，且基本遵循“指令开始时 `TaskCreate` -> 步骤前 `TaskUpdate(in_progress)` -> 步骤后 `TaskUpdate(completed)`”的生命周期。

*   **`ultra-dev.md` (Gold Standard)**: 实现了最复杂的 13 个步骤（含 1.5, 3.1, 5.5 等细分步骤）。它将持久化状态更新（Step 1.5 和 5）也作为独立任务，确保了极高的可追踪性。
*   **`ultra-verify/SKILL.md`**: 实现了 4 个核心步骤，涵盖了从设置到合成的全过程。
*   **`ultra-review/SKILL.md`**: 实现了 5 个步骤，特别加强了对后台子代理（Background Execution）的生命周期管理。
*   **`ultra-think.md`**: 实现了 5 个步骤，与其分析协议（Scope -> Evidence -> Analysis -> Stress-Test -> Synthesis）完全匹配。

### 2. 提示词质量、重复与不一致性分析

#### **重大重复问题：`ultra-verify`**
*   **发现**：`ultra-verify/SKILL.md` 与 `references/orchestration-flow.md` 之间存在 **100% 的 Workflow Tracking 表格重复**。
*   **风险**：这种冗余会导致维护成本增加（即“同步漂移”）。如果未来修改了步骤，必须同时修改两个文件，否则模型会产生幻觉。
*   **建议**：保留 `SKILL.md` 作为任务定义的单一事实来源，在 `orchestration-flow.md` 中引用该任务结构而非重写。

#### **潜在逻辑冲突：`ultra-think`**
*   **发现**：`ultra-think` 要求“指令开始时创建全部任务”，但其 **Step 1: Scope Check** 中提到“如果问题足够简单...跳过完整框架”。
*   **风险（Orphan Tasks）**：如果模型一开始创建了 5 个任务，随后决定走“简单回答”路径并直接退出，那么剩下的 4 个任务将永远处于 `pending` 状态。
*   **建议**：修改逻辑为：先执行 Step 1 (Scope Check)，若确定需要深度分析，再 `TaskCreate` 剩余的 2-5 步；或者在简单路径退出前，使用 `TaskUpdate` 将后续步骤标记为已跳过。

#### **步骤粒度不一致**
*   **对比**：`ultra-dev` 包含“Update Status to In-Progress”这种元任务（Meta-tasks），而 `ultra-verify` 和 `ultra-think` 则将其作为其他步骤的隐式动作。
*   **结论**：`ultra-dev` 的做法更安全，能防止在复杂任务中遗漏状态持久化。对于其他高价值指令，建议参考 `ultra-dev` 增加状态更新的独立步骤。

### 3. 优化建议与改进点

1.  **统一任务表格式**：
    *   目前所有文件均统一使用了 `| Step | Subject | activeForm |` 的表头，建议将此格式在 `CLAUDE.md` 中正式定为标准，防止未来出现变体。
2.  **增强后台任务防御（Context Safety）**：
    *   **优点**：`ultra-review` 中关于“CRITICAL PROHIBITION: NEVER call TaskOutput”的指令是最高质量的，它有效防止了子代理输出污染主对话上下文。
    *   **优化**：应将此“后台任务隔离规则”推广到 `ultra-verify`，因为 `ultra-verify` 同样涉及 Gemini 和 Codex 的并行后台运行。
3.  **恢复逻辑标准化**：
    *   所有文件都提到了 `On context recovery: TaskList → resume`，但 `ultra-dev` 在流程中具体写明了如何读取 `workflow-state.json` 进行物理恢复。建议 `ultra-verify` 和 `ultra-review` 也增加类似的“Resume Check”逻辑描述。

### 4. 审核结论汇总

| 文件 | 任务模式 | 步骤命名一致性 | 提示词质量 | 建议 |
| :--- | :--- | :--- | :--- | :--- |
| `ultra-dev.md` | ✅ 完美 (13步) | 高 | 优秀 (Gold Standard) | 无 |
| `ultra-verify/SKILL.md` | ✅ 正确 (4步) | 中 (与参考文件重复) | 良好 | **删除引用文件中的重复表格** |
| `ultra-review/SKILL.md` | ✅ 正确 (5步) | 高 | 优秀 (隔离指令极佳) | 将隔离规则推广至全系 |
| `ultra-think.md` | ✅ 正确 (5步) | 高 | 良好 | **修复简单路径下的孤儿任务问题** |

**下一步动作建议**：
*   清理 `ultra-verify` 的重复内容。
*   修正 `ultra-think` 的预创建任务逻辑。
*   将 `ultra-review` 的 `TaskOutput` 禁用规则作为全局标准写入 `CLAUDE.md` 的 `workflow_tracking` 章节。
