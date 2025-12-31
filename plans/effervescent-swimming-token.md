# Ultra Builder Pro 4.x 系统重构计划

## 概述

**目标**：解决系统中的 mock/降级/静态编码问题，使 ultra-research 和 ultra-init 建立的体系能够真正发挥作用。

**核心问题**：
1. ultra-dev 允许 mock/降级/静态编码绕过质量门禁
2. 测试规范可被任意修改以通过测试
3. ultra-test/ultra-deliver/ultra-session-reset 基本无用
4. Agent 完全闲置
5. Skills 触发不精准
6. CLAUDE.md 过载，违反官方 <600 tokens 建议

**参考案例**：OpenSpec、spec-kit、Agent-Skills-for-Context-Engineering、Claude Code 官方文档

---

## Phase 1: 核心阻断机制（最高优先级）

### 1.1 ultra-dev 硬性阻断

**文件**: `~/.claude/commands/ultra-dev.md`

**修改内容**：
- 添加 3 个硬性阻断检查（规范未确认、分支未创建、测试未先行）
- 阻断时输出清晰的中文错误消息
- 无法绕过，必须修复后才能继续

**新增阻断逻辑**：
```
阻断条件 1: 规范未确认
- 检查 .ultra/changes/feat-xxx/proposal.md 是否存在
- 不存在则阻断: "规范未确认，请先运行 /ultra-research"

阻断条件 2: 分支未创建
- 检查当前是否在 main/master 分支
- 是则阻断: "禁止在主分支开发，请先创建 feat/task-xxx 分支"

阻断条件 3: 测试未先行
- 监控代码生成顺序
- 实现代码先于测试则警告
```

### 1.2 TAS 强化阻断

**文件**: `~/.claude/skills/guarding-test-quality/SKILL.md`

**修改内容**：
- 硬性阻断 TAS <70%
- 检测到 tautology 测试自动 F 级
- 空测试体自动 F 级
- Mock 比率 >50% 强制审查
- 输出详细的问题诊断和修复建议

### 1.3 规范-测试绑定

**文件**: `~/.claude/skills/guarding-test-quality/SKILL.md`

**新增内容**：
- 验收测试必须 @trace_to 对应规范
- 测试修改时检查对应规范是否变更
- assertions 减少 >30% 时阻断

---

## Phase 2: 架构重构

### 2.1 引入 specs/changes 分离

**新增目录结构**：
```
.ultra/
├── specs/              # 当前真相（已实现）
├── changes/            # 变更提案（新增）
│   └── feat-xxx/
│       ├── proposal.md
│       ├── delta.md    # ADDED/MODIFIED/REMOVED
│       └── tasks.md
└── archive/            # 已归档变更（新增）
```

**修改文件**：
- `~/.claude/commands/ultra-research.md` - 输出到 changes/
- `~/.claude/commands/ultra-plan.md` - 读取 changes/
- `~/.claude/commands/ultra-deliver.md` - 合并到 specs/
- `~/.claude/.ultra-template/` - 添加 changes/ 模板

### 2.2 CLAUDE.md 瘦身

**文件**: `~/.claude/CLAUDE.md`

**目标**: 从 ~500行 减少到 <100行 (~200 tokens)

**保留内容**：
- 语言协议（中文输出）
- 核心工作流命令
- 质量门禁摘要
- 配置文件位置

**移除内容**：
- Skills 详细指南 → 移入 Skills 自身
- MCP 详细指南 → 移入按需文档
- Git 工作流详情 → 移入 Skill reference
- 质量标准详情 → 移入 Skill reference
- 测试哲学详情 → 移入 Skill reference

### 2.3 ultra-dev/test 职责分离

**文件**: `~/.claude/commands/ultra-dev.md`

**修改**：
- 只负责 TDD 开发周期
- 不负责覆盖率验证
- 完成后提示运行 /ultra-test

**文件**: `~/.claude/commands/ultra-test.md`

**修改**：
- 独立的质量验证阶段
- 运行完整测试套件
- 计算 TAS 分数
- 验证 6 维覆盖
- 阻断不合格任务

---

## Phase 3: Skills 优化

### 3.1 精简 Skill Descriptions

**所有 Skills** 的 description 字段：

**格式规范**：
```yaml
description: "[做什么，<30词]. TRIGGERS: [具体触发条件]. DO NOT trigger: [排除条件]."
```

**修改文件**：
- `~/.claude/skills/guarding-quality/SKILL.md`
- `~/.claude/skills/guarding-test-quality/SKILL.md`
- `~/.claude/skills/guarding-git-workflow/SKILL.md`
- `~/.claude/skills/compressing-context/SKILL.md`
- `~/.claude/skills/syncing-docs/SKILL.md`
- `~/.claude/skills/syncing-status/SKILL.md`
- `~/.claude/skills/guiding-workflow/SKILL.md`
- `~/.claude/skills/automating-e2e-tests/SKILL.md`

### 3.2 添加评估用例

**新增目录**：
```
~/.claude/skills/[skill-name]/evals/
└── eval-xxx.json
```

**评估用例格式**：
```json
{
  "query": "实际任务描述",
  "expected_behavior": ["预期行为1", "预期行为2"],
  "failure_indicators": ["失败标志1", "失败标志2"]
}
```

### 3.3 拆分 guarding-quality

**当前**: 1 个 Skill 负责代码质量+测试覆盖+UI设计

**拆分为**:
- `guarding-code-quality/` - SOLID/DRY/KISS
- `guarding-test-coverage/` - 覆盖率检查
- `guarding-ui-design/` - 前端设计约束

---

## Phase 4: Agent 激活

### 4.1 定义精确触发条件

**文件**: `~/.claude/agents/ultra-research-agent.md`
- 触发: /ultra-research Mode 2、"深度研究"关键词、复杂度>7的技术选型

**文件**: `~/.claude/agents/ultra-architect-agent.md`
- 触发: 任务类型为 architecture、多组件系统设计

**文件**: `~/.claude/agents/ultra-qa-agent.md`
- 触发: /ultra-test 发现复杂问题、TAS<50%

**文件**: `~/.claude/agents/ultra-performance-agent.md`
- 触发: Core Web Vitals 不达标、性能优化任务

### 4.2 简化 ultra-deliver

**文件**: `~/.claude/commands/ultra-deliver.md`

**精简为 3 个功能**：
1. 运行 /ultra-test（未通过则阻断）
2. 更新 CHANGELOG
3. 合并 changes/ 到 specs/

---

## Phase 5: 上下文优化

### 5.1 实现 Progressive Disclosure

**所有 Skills**：
- SKILL.md 保持 <500 行
- 详细内容移入 REFERENCE.md
- 启动时只加载 name+description (~100 tokens/Skill)

### 5.2 创建 Rules 目录

**新增**：
```
~/.claude/rules/
├── typescript.md
├── python.md
├── frontend.md
└── backend.md
```

**作用**: 按项目类型加载特定规则

---

## 关键文件清单

### 需要修改的文件

| 文件 | Phase | 修改类型 |
|------|-------|----------|
| `~/.claude/CLAUDE.md` | 2.2 | 大幅精简 |
| `~/.claude/commands/ultra-dev.md` | 1.1, 2.3 | 添加阻断+职责分离 |
| `~/.claude/commands/ultra-test.md` | 2.3 | 增强独立性 |
| `~/.claude/commands/ultra-deliver.md` | 4.2 | 简化 |
| `~/.claude/commands/ultra-research.md` | 2.1 | 输出到 changes/ |
| `~/.claude/commands/ultra-plan.md` | 2.1 | 读取 changes/ |
| `~/.claude/skills/guarding-test-quality/SKILL.md` | 1.2, 1.3 | 强化阻断+绑定 |
| `~/.claude/skills/guarding-quality/SKILL.md` | 3.1, 3.3 | 精简+拆分 |
| `~/.claude/skills/*/SKILL.md` (全部 8 个) | 3.1 | 精简 description |
| `~/.claude/agents/*.md` (全部 4 个) | 4.1 | 添加触发条件 |

### 需要新增的文件/目录

| 文件/目录 | Phase | 用途 |
|-----------|-------|------|
| `~/.claude/.ultra-template/changes/` | 2.1 | 变更提案模板 |
| `~/.claude/.ultra-template/archive/` | 2.1 | 归档目录模板 |
| `~/.claude/rules/` | 5.2 | 按类型规则目录 |
| `~/.claude/skills/*/evals/` | 3.2 | 评估用例 |
| `~/.claude/skills/guarding-code-quality/` | 3.3 | 拆分后的新 Skill |
| `~/.claude/skills/guarding-test-coverage/` | 3.3 | 拆分后的新 Skill |
| `~/.claude/skills/guarding-ui-design/` | 3.3 | 拆分后的新 Skill |

---

## 实施顺序

```
Phase 1 (核心阻断) → Phase 2 (架构重构) → Phase 3 (Skills优化) → Phase 4 (Agent激活) → Phase 5 (上下文优化)
```

**预计总工作量**: ~8-10 小时（因选择完整方案）

---

## 详细实施步骤

### Step 1: Phase 1 - 核心阻断 (2小时)

1.1 修改 `ultra-dev.md` 添加 3 个阻断检查
1.2 修改 `guarding-test-quality/SKILL.md` 强化 TAS 阻断
1.3 添加规范-测试绑定逻辑

### Step 2: Phase 2 - 架构重构 (3小时)

2.1 创建 `.ultra-template/changes/` 目录和模板
2.2 创建 `.ultra-template/archive/` 目录
2.3 修改 `ultra-research.md` 输出到 changes/
2.4 修改 `ultra-plan.md` 读取 changes/
2.5 修改 `ultra-deliver.md` 合并到 specs/
2.6 精简 `CLAUDE.md` 到 <100 行

### Step 3: Phase 3 - Skills 优化 (2.5小时)

3.1 拆分 guarding-quality 为 3 个独立 Skills:
    - guarding-code-quality/SKILL.md
    - guarding-code-quality/REFERENCE.md (迁移 solid-principles.md)
    - guarding-test-coverage/SKILL.md
    - guarding-test-coverage/REFERENCE.md
    - guarding-ui-design/SKILL.md
    - guarding-ui-design/REFERENCE.md (迁移 quality-standards.md 前端部分)

3.2 迁移 guidelines/ 到对应 Skills:
    - testing-philosophy.md → guarding-test-quality/REFERENCE.md
    - git-workflow.md → guarding-git-workflow/REFERENCE.md
    - quality-standards.md → 拆分到各 Skills

3.3 精简所有 8 个 Skills 的 description

3.4 为每个 Skill 添加 evals/ 目录和评估用例

### Step 4: Phase 4 - Agent 激活 (1.5小时)

4.1 更新 ultra-research-agent.md 添加精确触发条件
4.2 更新 ultra-architect-agent.md 添加精确触发条件
4.3 更新 ultra-qa-agent.md 添加精确触发条件
4.4 更新 ultra-performance-agent.md 添加精确触发条件
4.5 简化 ultra-deliver.md 为 3 个核心功能

### Step 5: Phase 5 - 上下文优化 (1小时)

5.1 创建 ~/.claude/rules/ 目录
5.2 创建 typescript.md, python.md, frontend.md, backend.md
5.3 删除 guidelines/ 和 config/ 中的冗余文件
5.4 更新 @import 引用

### Step 6: 验证与测试

6.1 测试 Phase 1 阻断机制
6.2 测试 Phase 2 specs/changes 流程
6.3 测试 Phase 3 Skill 触发
6.4 测试 Phase 4 Agent 委托
6.5 测量上下文消耗

**预期效果**:
- ✅ 消除 mock/降级/静态编码问题
- ✅ ultra-test/deliver/session-reset 变得有用
- ✅ Agent 开始发挥作用
- ✅ Skills 触发更精准
- ✅ 上下文消耗降低 60%+
- ✅ 通过 init/research 建立的体系能够持续发挥作用

---

## 用户确认的选择

1. **Skill 拆分**: 拆分为 3 个独立 Skills（guarding-code-quality + guarding-test-coverage + guarding-ui-design）
2. **架构模式**: 完整 OpenSpec 模式（specs/ + changes/ + archive/ + Delta 格式）
3. **配置迁移**: 全部迁移到 Skills 的 REFERENCE.md（按 Progressive Disclosure 原则）

---

## 验证标准

每个 Phase 完成后验证：

**Phase 1**：
- [ ] 在 main 分支运行 /ultra-dev 被阻断
- [ ] 提交包含 expect(true).toBe(true) 的测试被阻断
- [ ] TAS<70% 无法完成任务

**Phase 2**：
- [ ] /ultra-research 输出到 changes/
- [ ] /ultra-deliver 合并到 specs/
- [ ] CLAUDE.md <100 行

**Phase 3**：
- [ ] 所有 Skill description <200 词
- [ ] 每个 Skill 有至少 1 个评估用例

**Phase 4**：
- [ ] 复杂技术选型自动委托给 ultra-research-agent
- [ ] TAS<50% 自动委托给 ultra-qa-agent

**Phase 5**：
- [ ] 启动时 token 消耗 <1000
- [ ] 触发 Skill 时才加载完整内容
