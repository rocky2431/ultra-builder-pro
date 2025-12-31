# 统一多CLI协作框架 v2.1

> **置信度**: 95%（核心功能98%，Gemini/Codex适配90%）
> **更新日期**: 2025-12-29（基于官方文档深度研究）

## 概述

**目标**: 构建"乐高积木"式的多CLI协作系统，实现：
1. 统一工作流：`init → research → plan → dev → test → deliver`
2. 外挂技能库：基于 OpenSkills 的跨CLI统一技能系统
3. Hook驱动激活：三CLI都有原生/扩展Hook支持
4. OpenSpec分支隔离：每个任务分支有独立的文档和上下文
5. 可配置Agent技能：用户定义哪些CLI使用哪些技能
6. **Research阶段深度优化**：文档驱动开发的核心，生成落地文档

**核心理念**:
- MCP协议为统一能力桥梁（100%兼容）
- OpenSkills为统一技能格式（SKILL.md）
- Hook系统为统一触发机制（Claude/Gemini原生，Codex notify+MCP）

---

## 研究发现总结（2025-12-29 官方文档）

### 三CLI能力矩阵（修正版）

| 能力 | Claude Code | Gemini CLI | Codex CLI | 统一方案 |
|------|-------------|------------|-----------|----------|
| **Commands** | ✅ 原生 | ✅ 原生 (`/`,`@`,`!`) | ✅ 原生 | 统一 `/` 前缀 |
| **Skills** | ✅ 原生 SKILL.md | ✅ gemini-cli-skillz | ✅ 原生 6级作用域 | OpenSkills |
| **MCP** | ✅ 原生 | ✅ 原生 (240+扩展) | ✅ 原生 (STDIO/HTTP) | 100%兼容 |
| **Hooks** | ✅ 3种核心 | ✅ 11种生命周期 | ⚠️ notify出站 | Hook映射层 |
| **项目配置** | .claude/ | .gemini/ | .codex/ | ConfigTranspiler |
| **指令文件** | CLAUDE.md | GEMINI.md | AGENTS.md | 统一生成 |

### Hook系统详细对比

| Hook类型 | Claude Code | Gemini CLI | Codex CLI |
|----------|-------------|------------|-----------|
| **用户输入前** | UserPromptSubmit | BeforeAgent | ❌ |
| **工具使用前** | PreToolUse | BeforeTool | ❌ |
| **工具使用后** | PostToolUse | AfterTool | notify(agent-turn-complete) |
| **模型调用前** | ❌ | BeforeModel | ❌ |
| **模型调用后** | ❌ | AfterModel | ❌ |
| **会话开始** | ❌ | SessionStart | ❌ |
| **会话结束** | ❌ | SessionEnd | notify(session-end) |
| **审批请求** | ❌ | ❌ | notify(approval-requested) |

### 关键借鉴点

1. **ultra-builder-pro**: Spec-driven development, Orchestrator-Agent分离, Graphiti记忆
2. **infrastructure-showcase**: 双层匹配激活(Hook+规则引擎), 500行模块化Skill
3. **OpenSkills**: 通用技能加载器，渐进式披露（3层加载），纯LLM推理匹配
4. **gemini-cli-skillz**: Gemini CLI扩展，`ln -s ~/.claude/skills ~/.skillz` 共享技能
5. **Codex 6级作用域**: REPO/USER/ADMIN/SYSTEM，显式`$skill-name`调用

---

## Research阶段深度优化（文档驱动开发核心）

> **核心理念**: 生成的文档越落地，OpenSpec分离出来的文档就越确定

### Research阶段的战略地位

```
init → [RESEARCH] → plan → dev → test → deliver
              ↑
         文档驱动开发的核心
         决定整个项目的质量上限
```

**为什么Research是核心**：
1. **PRD质量决定开发方向** - 模糊的PRD导致无效迭代
2. **技术文档决定实现路径** - 缺失的技术调研导致返工
3. **规范文档决定一致性** - 无规范导致风格混乱
4. **OpenSpec隔离依赖Research输出** - 垃圾进垃圾出

### Research阶段产出物（6大文档）

```
.openspec/
├── master/                          # Research阶段输出
│   ├── PRD.md                       # 产品需求文档（落地版）
│   ├── TECH_SPEC.md                 # 技术规格文档
│   ├── ARCHITECTURE.md              # 架构设计文档
│   ├── API_SPEC.md                  # API规格（OpenAPI/GraphQL）
│   ├── CONVENTIONS.md               # 编码规范和约定
│   └── TASK_BREAKDOWN.md            # 任务分解（带依赖图）
└── feature/{branch}/                # 分支隔离上下文
    ├── BRANCH_SPEC.md               # 分支特定规格（继承master）
    ├── CHANGES.md                   # 变更记录
    └── tasks.json                   # 分支任务状态
```

### Research阶段流程（3轮迭代）

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        Research阶段流程（3轮迭代）                           │
└─────────────────────────────────────────────────────────────────────────────┘

Round 1: 需求发现（Discovery）
┌─────────────────────────────────────────────────────────────────────────────┐
│  输入: 用户需求描述（可能模糊）                                               │
│         │                                                                   │
│         ▼                                                                   │
│  ┌─────────────────┐                                                        │
│  │  需求澄清Agent   │ ← 使用 AskUserQuestion 进行多轮对话                    │
│  └─────────────────┘                                                        │
│         │                                                                   │
│         ▼                                                                   │
│  输出: PRD初稿 + 功能列表 + 验收标准                                         │
└─────────────────────────────────────────────────────────────────────────────┘

Round 2: 技术调研（Technical Research）
┌─────────────────────────────────────────────────────────────────────────────┐
│  输入: PRD初稿 + 现有代码库                                                  │
│         │                                                                   │
│         ▼                                                                   │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐             │
│  │  代码分析Agent   │  │  技术选型Agent   │  │  风险评估Agent   │             │
│  │  (Gemini 1M)    │  │  (Claude)       │  │  (Claude)       │             │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘             │
│         │                    │                    │                         │
│         └────────────────────┼────────────────────┘                         │
│                              ▼                                              │
│  输出: TECH_SPEC.md + ARCHITECTURE.md + 风险清单                            │
└─────────────────────────────────────────────────────────────────────────────┘

Round 3: 文档精炼（Refinement）
┌─────────────────────────────────────────────────────────────────────────────┐
│  输入: 所有初稿文档                                                          │
│         │                                                                   │
│         ▼                                                                   │
│  ┌─────────────────┐                                                        │
│  │  文档审查Agent   │ ← 6维度检查（完整性/一致性/可执行性/可测试/无歧义/合规） │
│  └─────────────────┘                                                        │
│         │                                                                   │
│         ▼                                                                   │
│  ┌─────────────────┐                                                        │
│  │  任务分解Agent   │ ← 生成 TASK_BREAKDOWN.md + DAG依赖图                   │
│  └─────────────────┘                                                        │
│         │                                                                   │
│         ▼                                                                   │
│  输出: 最终版6大文档 + 可视化任务图                                          │
└─────────────────────────────────────────────────────────────────────────────┘
```

### CLI分工优化（Research阶段）

| 角色 | 推荐CLI | 原因 |
|------|---------|------|
| **需求澄清** | Claude Code | 复杂推理、多轮对话 |
| **代码分析** | Gemini CLI | 1M上下文、快速分析大代码库 |
| **技术选型** | Claude Code | 深度推理、权衡利弊 |
| **文档生成** | Gemini CLI | 速度快、长文档生成 |
| **文档审查** | Claude Code | 严谨、发现逻辑漏洞 |
| **任务分解** | Claude Code | 复杂依赖推理 |

### Research质量门禁（Gate Check）

```python
class ResearchQualityGate:
    """Research阶段质量检查"""

    def check_prd(self, prd: str) -> QualityReport:
        """PRD质量检查"""
        return {
            'completeness': self._check_sections(['背景', '目标', '功能列表', '验收标准']),
            'measurability': self._check_smart_goals(prd),  # SMART原则
            'testability': self._check_acceptance_criteria(prd),
            'no_ambiguity': self._check_vague_words(prd),  # 检测"等"、"可能"、"大概"
        }

    def check_tech_spec(self, spec: str) -> QualityReport:
        """技术规格质量检查"""
        return {
            'api_defined': self._has_api_contracts(spec),
            'data_models': self._has_data_schemas(spec),
            'error_handling': self._has_error_scenarios(spec),
            'dependencies': self._has_dependency_list(spec),
        }

    def check_task_breakdown(self, tasks: List[Task]) -> QualityReport:
        """任务分解质量检查"""
        return {
            'dag_valid': self._validate_dag(tasks),  # 无环检查
            'estimations': self._all_have_estimates(tasks),
            'assignable': self._all_have_clear_scope(tasks),
            'testable': self._all_have_done_criteria(tasks),
        }
```

### 落地文档模板

#### PRD.md 模板
```markdown
# {Feature Name} - 产品需求文档

## 1. 背景和目标
### 1.1 问题陈述
[具体描述当前痛点，用数据支撑]

### 1.2 目标
- 主要目标: [SMART格式]
- 次要目标: [SMART格式]
- 非目标: [明确排除的范围]

## 2. 功能需求
### 2.1 用户故事
| ID | 作为... | 我想要... | 以便于... | 优先级 |
|----|---------|----------|----------|--------|
| US-001 | 开发者 | 一键初始化项目 | 快速开始开发 | P0 |

### 2.2 功能列表
| 功能 | 描述 | 验收标准 | 优先级 |
|------|------|---------|--------|

## 3. 非功能需求
- 性能: [具体指标]
- 安全: [合规要求]
- 可用性: [SLA目标]

## 4. 验收标准（AC）
### AC-001: {功能名称}
**Given** [前置条件]
**When** [用户操作]
**Then** [期望结果]
```

#### TASK_BREAKDOWN.md 模板
```markdown
# 任务分解

## 依赖图（Mermaid）
\`\`\`mermaid
graph TD
    T1[任务1: 数据模型] --> T2[任务2: API层]
    T1 --> T3[任务3: 前端组件]
    T2 --> T4[任务4: 集成测试]
    T3 --> T4
\`\`\`

## 任务列表
| ID | 任务 | 依赖 | 估算 | 推荐CLI | 状态 |
|----|------|------|------|---------|------|
| T1 | 数据模型定义 | - | 2h | Claude | pending |
| T2 | API层实现 | T1 | 4h | Codex | pending |
| T3 | 前端组件 | T1 | 3h | Gemini | pending |
| T4 | 集成测试 | T2,T3 | 2h | Claude | pending |
```

---

## 系统架构设计

### 整体架构图

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        Unified CLI Collaboration Framework                   │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
         ┌────────────────────────────┼────────────────────────────┐
         ▼                            ▼                            ▼
┌─────────────────┐        ┌─────────────────┐        ┌─────────────────┐
│   Claude Code    │        │   Gemini CLI     │        │   Codex CLI      │
│   Adapter        │        │   Adapter        │        │   Adapter        │
├─────────────────┤        ├─────────────────┤        ├─────────────────┤
│ hooks.json       │        │ settings.json    │        │ config.toml      │
│ mcp.json         │        │ mcp (JSON)       │        │ mcp (TOML)       │
│ skills/*.md      │        │ skills/*.md      │        │ rules/*.rules    │
└────────┬────────┘        └────────┬────────┘        └────────┬────────┘
         │                          │                          │
         └──────────────────────────┼──────────────────────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    ▼                               ▼
         ┌─────────────────────┐        ┌─────────────────────┐
         │  Skill Activation   │        │  MCP Protocol       │
         │  Engine (双层匹配)   │        │  (95% 跨CLI兼容)    │
         ├─────────────────────┤        ├─────────────────────┤
         │ 1. Hook Trigger     │        │ - context7           │
         │ 2. Rule Matching    │        │ - graphiti-memory    │
         │ 3. Skill Injection  │        │ - custom MCP tools   │
         └─────────┬───────────┘        └───────────────────────┘
                   │
                   ▼
    ┌──────────────────────────────────────────────────────────┐
    │                    OpenSpec Workflow                      │
    │            (Branch-Isolated Documentation)                │
    ├──────────────────────────────────────────────────────────┤
    │  .openspec/                                               │
    │  ├── master/specs/     # 主分支规格（真相源）              │
    │  ├── feature/xxx/      # 功能分支独立上下文               │
    │  │   ├── specs/        # 分支规格                        │
    │  │   ├── changes/      # 变更提议                        │
    │  │   └── tasks.json    # 分支任务                        │
    │  └── project.md        # 全局约定                        │
    └──────────────────────────────────────────────────────────┘
                   │
                   ▼
    ┌──────────────────────────────────────────────────────────┐
    │               Unified Workflow Engine                     │
    │       /ultra-init → research → plan → dev → test → deliver│
    └──────────────────────────────────────────────────────────┘
```

### 技能激活双层机制（核心创新）

```
Layer 1: Hook Trigger (UserPromptSubmit / PreToolUse)
┌─────────────────────────────────────────────────────────────┐
│  user_prompt / tool_input                                    │
│         │                                                    │
│         ▼                                                    │
│  Hook: skill-activation → skill-rules.json                   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
Layer 2: Rule Engine (四层匹配)
┌─────────────────────────────────────────────────────────────┐
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │  Keywords   │  │   Intent    │  │    Path     │          │
│  │ React,API.. │  │ commit,test │  │ **/*.ts     │          │
│  └─────────────┘  └─────────────┘  └─────────────┘          │
│         │                │                │                  │
│         └────────────────┼────────────────┘                  │
│                          ▼                                   │
│              加权评分 → 优先级排序 → 激活                      │
└─────────────────────────────────────────────────────────────┘
```

---

## 已完成模块（Phase 1-6）

> ✅ 以下模块已在之前的迭代中完成，代码已提交到 `develop` 分支

| Phase | 模块 | 状态 | 代码行数 |
|-------|------|------|----------|
| 1 | 任务管理系统 (`apps/backend/tasks/`) | ✅ 完成 | ~800行 |
| 2 | CLI执行层 (`apps/backend/cli_executors/`) | ✅ 完成 | ~600行 |
| 3 | OpenSpec上下文 (`apps/backend/context/`) | ✅ 完成 | ~500行 |
| 4 | Kanban看板UI (`apps/frontend/.../kanban/`) | ✅ 完成 | ~1200行 |
| 5 | 协作协议 (`apps/backend/collaboration/`) | ✅ 完成 | ~2500行 |
| 6 | Graphiti增强 (`apps/backend/integrations/graphiti/`) | ✅ 完成 | ~900行 |

---

## 新实现计划：统一技能框架

> 基于 ultra-builder-pro 和 infrastructure-showcase 的研究，实现跨CLI统一技能系统

### Phase 7: 基础配置层 (1周)

**目标**: 建立统一配置格式和配置转换器

#### 7.1 统一配置格式 (unified-config.yaml)

**文件**: `apps/backend/unified_skills/config/unified_config_schema.py`

```yaml
# ~/.auto-claude/unified-config.yaml (用户配置示例)
version: "2.0"
project:
  name: "my-project"
  root: "./project"

# CLI 适配器配置
cli_adapters:
  claude:
    enabled: true
    config_path: ".claude/"
    hooks_enabled: true
    skills:
      - "ultra-workflow"
      - "code-quality"
      - "git-workflow"
  gemini:
    enabled: true
    config_path: ".gemini/"
    mcp_bridge: true  # 通过 MCP 桥接技能
    skills:
      - "documentation"
      - "code-review"
  codex:
    enabled: false
    config_path: ".codex/"

# 统一工作流
workflow:
  phases:
    - init
    - research
    - plan
    - dev
    - test
    - deliver

# 技能库配置
skill_library:
  root: "~/.skill-library/"
  enabled_skills:
    - "ultra-workflow"
    - "code-quality"
    - "git-workflow"
    - "documentation"
```

#### 7.2 配置转换器 (ConfigTranspiler)

**文件**: `apps/backend/unified_skills/config/transpiler.py`

```python
class ConfigTranspiler:
    """将统一配置转换为各CLI特定格式"""

    def transpile_to_claude(self, config: UnifiedConfig) -> ClaudeConfig:
        """生成 .claude/settings.json + hooks.json"""

    def transpile_to_gemini(self, config: UnifiedConfig) -> GeminiConfig:
        """生成 .gemini/settings.json + MCP桥接配置"""

    def transpile_to_codex(self, config: UnifiedConfig) -> CodexConfig:
        """生成 .codex/config.toml"""

    def sync_all(self, config: UnifiedConfig) -> None:
        """同步到所有启用的CLI"""
```

#### 7.3 CLI适配器基类

**文件**: `apps/backend/unified_skills/adapters/base.py`

```python
class CLIAdapter(ABC):
    """CLI 适配器抽象基类"""

    name: str
    config_format: str  # json/yaml/toml
    hooks_supported: bool
    mcp_supported: bool

    @abstractmethod
    def load_config(self, path: Path) -> CLIConfig: ...

    @abstractmethod
    def save_config(self, config: CLIConfig, path: Path) -> None: ...

    @abstractmethod
    def inject_skill(self, skill: Skill) -> None: ...

    @abstractmethod
    def get_active_skills(self) -> List[str]: ...
```

**关键文件清单**:
- `apps/backend/unified_skills/__init__.py`
- `apps/backend/unified_skills/config/unified_config_schema.py`
- `apps/backend/unified_skills/config/transpiler.py`
- `apps/backend/unified_skills/config/validator.py`
- `apps/backend/unified_skills/adapters/__init__.py`
- `apps/backend/unified_skills/adapters/base.py`
- `apps/backend/unified_skills/adapters/claude_adapter.py`

---

### Phase 8: 技能激活引擎 (1周)

**目标**: 实现双层匹配激活机制（参考 infrastructure-showcase）

#### 8.1 技能规则定义 (skill-rules.json)

**文件**: `apps/backend/unified_skills/activation/rules_schema.py`

```json
{
  "version": "1.0",
  "rules": [
    {
      "skill": "ultra-workflow",
      "triggers": {
        "keywords": ["init", "research", "plan", "dev", "test", "deliver"],
        "intentPatterns": ["^/ultra-", "start project", "new feature"],
        "pathPatterns": [".ultra/**", "specs/**"],
        "contentPatterns": ["TODO:", "FIXME:"]
      },
      "weight": {
        "keywords": 0.4,
        "intent": 0.3,
        "path": 0.2,
        "content": 0.1
      },
      "threshold": 0.5,
      "priority": 100
    },
    {
      "skill": "code-quality",
      "triggers": {
        "keywords": ["refactor", "lint", "quality", "SOLID"],
        "intentPatterns": ["review code", "check quality"],
        "pathPatterns": ["**/*.ts", "**/*.py"],
        "contentPatterns": ["complexity", "coverage"]
      },
      "weight": { "keywords": 0.5, "intent": 0.3, "path": 0.15, "content": 0.05 },
      "threshold": 0.4,
      "priority": 80
    }
  ]
}
```

#### 8.2 双层激活引擎

**文件**: `apps/backend/unified_skills/activation/engine.py`

```python
class SkillActivationEngine:
    """双层技能激活引擎"""

    def __init__(self, rules_path: Path):
        self.rules = self._load_rules(rules_path)

    # Layer 1: Hook Trigger
    def on_user_prompt(self, prompt: str, context: dict) -> List[SkillMatch]:
        """UserPromptSubmit Hook 触发"""

    def on_pre_tool_use(self, tool: str, input: dict) -> List[SkillMatch]:
        """PreToolUse Hook 触发"""

    # Layer 2: Rule Engine (四层匹配)
    def _match_keywords(self, text: str, rule: Rule) -> float: ...
    def _match_intent(self, text: str, rule: Rule) -> float: ...
    def _match_path(self, paths: List[str], rule: Rule) -> float: ...
    def _match_content(self, content: str, rule: Rule) -> float: ...

    def calculate_score(self, context: ActivationContext, rule: Rule) -> float:
        """计算加权匹配分数"""
        return (
            rule.weight.keywords * self._match_keywords(context.text, rule) +
            rule.weight.intent * self._match_intent(context.text, rule) +
            rule.weight.path * self._match_path(context.paths, rule) +
            rule.weight.content * self._match_content(context.content, rule)
        )

    def activate(self, context: ActivationContext) -> List[ActivatedSkill]:
        """激活匹配的技能，按优先级排序"""
```

#### 8.3 Hook 集成

**文件**: `apps/backend/unified_skills/hooks/skill_activation_hook.py`

```python
# 注册到 ~/.claude/hooks.json
{
    "hooks": [
        {
            "matcher": {
                "event": "user_prompt_submit"
            },
            "hooks": [{
                "type": "command",
                "command": "python -m unified_skills.hooks.skill_activation_hook"
            }]
        }
    ]
}
```

**关键文件清单**:
- `apps/backend/unified_skills/activation/__init__.py`
- `apps/backend/unified_skills/activation/rules_schema.py`
- `apps/backend/unified_skills/activation/engine.py`
- `apps/backend/unified_skills/activation/matcher.py`
- `apps/backend/unified_skills/hooks/__init__.py`
- `apps/backend/unified_skills/hooks/skill_activation_hook.py`
- `apps/backend/unified_skills/hooks/pre_tool_hook.py`

---

### Phase 9: 基于OpenSkills的统一技能库 (1周)

**目标**: 基于 OpenSkills 标准创建跨CLI统一技能系统

> **关键决策**: 使用 OpenSkills 而非自研技能系统
> - 100% 兼容 Anthropic SKILL.md 格式
> - 已有社区生态和官方技能库 (anthropics/skills)
> - 渐进式披露机制成熟（3层加载）

#### 9.1 OpenSkills 集成架构

```
统一技能架构
┌─────────────────────────────────────────────────────────────────────────────┐
│                              OpenSkills CLI                                  │
│                         (npm i -g openskills)                               │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
         ┌───────────────────────────┼───────────────────────────┐
         ▼                           ▼                           ▼
┌─────────────────┐        ┌─────────────────┐        ┌─────────────────┐
│   Claude Code    │        │   Gemini CLI     │        │   Codex CLI      │
│   原生 SKILL.md  │        │gemini-cli-skillz │        │ 原生 6级作用域   │
├─────────────────┤        ├─────────────────┤        ├─────────────────┤
│ ~/.claude/skills │ ←────→│   ~/.skillz      │←──────→│ ~/.codex/skills  │
│ (软链接共享)     │        │ (软链接共享)     │        │ (OpenSkills sync)│
└─────────────────┘        └─────────────────┘        └─────────────────┘
```

#### 9.2 技能目录结构（兼容 Anthropic 标准）

```
~/.claude/skills/                    # 主技能目录（三CLI共享）
├── ultra-workflow/
│   ├── SKILL.md                     # 技能核心 (<500行)
│   └── references/                  # 渐进式加载资源
│       ├── init-workflow.md
│       ├── research-workflow.md
│       ├── plan-workflow.md
│       ├── dev-workflow.md
│       ├── test-workflow.md
│       └── deliver-workflow.md
├── code-quality/
│   ├── SKILL.md
│   └── references/
│       ├── solid-principles.md
│       ├── complexity-rules.md
│       └── test-patterns.md
├── git-workflow/
│   └── SKILL.md
└── research-deep/                   # 新增：深度研究技能
    ├── SKILL.md
    └── references/
        ├── prd-template.md
        ├── tech-spec-template.md
        ├── quality-gate-rules.md
        └── task-breakdown-template.md

# 软链接共享
~/.skillz -> ~/.claude/skills        # Gemini CLI 共享
~/.codex/skills -> ~/.claude/skills  # Codex CLI 共享（需 openskills sync）
```

#### 9.3 SKILL.md 格式（Anthropic 标准）

```markdown
---
name: ultra-workflow
description: Ultra Builder Pro 完整工作流 - init/research/plan/dev/test/deliver
---

# Ultra Workflow 技能

当用户请求项目初始化、研究、规划、开发、测试或交付时，执行此技能。

## 触发条件
- 用户输入包含: /ultra-init, /ultra-research, /ultra-plan, /ultra-dev, /ultra-test, /ultra-deliver
- 或描述: "开始项目", "做技术调研", "写规格文档", "任务分解"

## 工作流阶段
1. **init**: 初始化项目结构和配置
2. **research**: 深度技术调研和文档生成（见 references/research-workflow.md）
3. **plan**: 任务分解和依赖图生成
4. **dev**: TDD 驱动开发
5. **test**: 质量验证
6. **deliver**: 部署和发布

## 引用
详细流程见 {baseDir}/references/ 目录下的各阶段文档。
```

#### 9.4 OpenSkills 集成代码

**文件**: `apps/backend/unified_skills/openskills_integration.py`

```python
class OpenSkillsIntegration:
    """OpenSkills 集成管理"""

    def __init__(self):
        self.skills_root = Path.home() / ".claude" / "skills"

    def install_official_skills(self) -> None:
        """安装官方技能库"""
        subprocess.run(["openskills", "install", "anthropics/skills"])

    def install_custom_skill(self, skill_path: str) -> None:
        """安装自定义技能"""
        subprocess.run(["openskills", "install", skill_path])

    def sync_to_agents_md(self, project_dir: Path) -> None:
        """同步技能列表到 AGENTS.md（Codex 兼容）"""
        subprocess.run(["openskills", "sync"], cwd=project_dir)

    def setup_gemini_symlink(self) -> None:
        """设置 Gemini CLI 软链接"""
        skillz_path = Path.home() / ".skillz"
        if not skillz_path.exists():
            skillz_path.symlink_to(self.skills_root)

    def setup_codex_symlink(self) -> None:
        """设置 Codex CLI 软链接"""
        codex_skills = Path.home() / ".codex" / "skills"
        codex_skills.parent.mkdir(parents=True, exist_ok=True)
        if not codex_skills.exists():
            codex_skills.symlink_to(self.skills_root)

    def list_skills(self) -> List[SkillInfo]:
        """列出所有已安装技能"""
        result = subprocess.run(
            ["openskills", "list", "--json"],
            capture_output=True, text=True
        )
        return json.loads(result.stdout)

    def read_skill(self, name: str) -> str:
        """读取技能内容（AI 调用）"""
        result = subprocess.run(
            ["openskills", "read", name],
            capture_output=True, text=True
        )
        return result.stdout
```

#### 9.5 渐进式披露机制（3层加载）

```
Layer 1: 技能索引（启动时预加载）
┌─────────────────────────────────────────────────────────────────────────────┐
│  <available_skills>                                                          │
│    ultra-workflow: Ultra Builder Pro 完整工作流                              │
│    code-quality: 代码质量检查和 SOLID 原则                                   │
│    git-workflow: Git 分支策略和提交规范                                       │
│    research-deep: 深度技术调研和文档生成                                      │
│  </available_skills>                                                         │
│                                                                              │
│  Token 消耗: ~100-200 tokens                                                 │
└─────────────────────────────────────────────────────────────────────────────┘

Layer 2: 技能核心（AI 判断相关时加载）
┌─────────────────────────────────────────────────────────────────────────────┐
│  AI: "用户想做技术调研，我需要 research-deep 技能"                            │
│       │                                                                     │
│       ▼                                                                     │
│  执行: openskills read research-deep                                        │
│       │                                                                     │
│       ▼                                                                     │
│  加载: SKILL.md 完整内容 (~500行, ~1500 tokens)                              │
└─────────────────────────────────────────────────────────────────────────────┘

Layer 3: 引用资源（按需加载）
┌─────────────────────────────────────────────────────────────────────────────┐
│  AI: "需要 PRD 模板来生成文档"                                               │
│       │                                                                     │
│       ▼                                                                     │
│  读取: {baseDir}/references/prd-template.md                                 │
│       │                                                                     │
│       ▼                                                                     │
│  加载: 特定资源 (~500-2000 tokens)                                          │
└─────────────────────────────────────────────────────────────────────────────┘
```

**关键文件清单**:
- `apps/backend/unified_skills/openskills_integration.py`
- `apps/backend/unified_skills/skill_sync.py`
- `~/.claude/skills/ultra-workflow/SKILL.md`
- `~/.claude/skills/research-deep/SKILL.md` (新增)
- `~/.claude/skills/research-deep/references/*.md` (6大文档模板)

---

### Phase 10: Gemini/Codex 适配器 (1周)

**目标**: 实现 Gemini CLI 和 Codex CLI 的适配器

#### 10.1 Gemini CLI 适配器

**文件**: `apps/backend/unified_skills/adapters/gemini_adapter.py`

```python
class GeminiAdapter(CLIAdapter):
    """Gemini CLI 适配器 - 通过 MCP 桥接技能"""

    name = "gemini"
    config_format = "json"
    hooks_supported = False  # Gemini 无原生 Hook
    mcp_supported = True

    def inject_skill(self, skill: Skill) -> None:
        """通过 MCP 工具注入技能"""
        # Gemini 不支持原生 Skill，通过 MCP server 暴露技能能力
        self._register_mcp_skill_tool(skill)

    def _register_mcp_skill_tool(self, skill: Skill) -> None:
        """将技能注册为 MCP 工具"""
        # 1. 创建 MCP tool definition
        # 2. 注册到 gemini 的 mcp 配置
        # 3. 提供 skill 内容作为 tool 输出
```

#### 10.2 Codex CLI 适配器

**文件**: `apps/backend/unified_skills/adapters/codex_adapter.py`

```python
class CodexAdapter(CLIAdapter):
    """Codex CLI 适配器 - 使用 Rules 系统"""

    name = "codex"
    config_format = "toml"
    hooks_supported = True  # Codex 有 notify 事件
    mcp_supported = True

    def inject_skill(self, skill: Skill) -> None:
        """转换技能为 Codex Rules 格式"""
        rule_content = self._skill_to_rule(skill)
        self._write_rule_file(skill.name, rule_content)

    def _skill_to_rule(self, skill: Skill) -> str:
        """将 Skill 转换为 .rules 文件格式"""
```

#### 10.3 MCP 技能桥接器

**文件**: `apps/backend/unified_skills/mcp/skill_bridge_server.py`

```python
class SkillBridgeMCPServer:
    """MCP Server - 为不支持原生技能的 CLI 提供技能桥接"""

    def __init__(self, skill_loader: SkillLoader):
        self.skill_loader = skill_loader

    @mcp_tool("get_skill_content")
    def get_skill_content(self, skill_name: str, resource: str = None) -> str:
        """MCP 工具: 获取技能内容"""

    @mcp_tool("list_available_skills")
    def list_available_skills(self) -> List[SkillInfo]:
        """MCP 工具: 列出可用技能"""

    @mcp_tool("activate_skill")
    def activate_skill(self, skill_name: str, context: dict) -> ActivationResult:
        """MCP 工具: 激活技能并返回相关指令"""
```

**关键文件清单**:
- `apps/backend/unified_skills/adapters/gemini_adapter.py`
- `apps/backend/unified_skills/adapters/codex_adapter.py`
- `apps/backend/unified_skills/mcp/__init__.py`
- `apps/backend/unified_skills/mcp/skill_bridge_server.py`
- `apps/backend/unified_skills/mcp/mcp_config_generator.py`

---

### Phase 11: OpenSpec 分支隔离增强 (1周)

**目标**: 实现每个任务分支的独立文档和上下文

#### 11.1 分支感知的 OpenSpec

**文件**: `apps/backend/unified_skills/openspec/branch_manager.py`

```python
class BranchAwareOpenSpec:
    """分支感知的 OpenSpec 管理"""

    def __init__(self, project_root: Path):
        self.project_root = project_root

    def get_branch_spec_dir(self, branch: str) -> Path:
        """获取分支特定的 spec 目录"""
        # .openspec/feature/{branch}/specs/

    def create_branch_context(self, branch: str, parent: str = "main") -> None:
        """为新分支创建上下文（继承父分支）"""

    def sync_to_main(self, branch: str) -> None:
        """将分支 spec 同步到主分支"""

    def get_branch_tasks(self, branch: str) -> List[Task]:
        """获取分支特定的任务列表"""
```

#### 11.2 Git 集成

**文件**: `apps/backend/unified_skills/openspec/git_sync.py`

```python
class OpenSpecGitSync:
    """OpenSpec 与 Git 分支同步"""

    def on_branch_create(self, branch: str) -> None:
        """创建分支时自动初始化 OpenSpec"""

    def on_branch_switch(self, branch: str) -> None:
        """切换分支时加载对应的 OpenSpec"""

    def on_branch_merge(self, source: str, target: str) -> None:
        """合并分支时同步 OpenSpec"""

    def setup_git_hooks(self) -> None:
        """安装 Git hooks (post-checkout, post-merge)"""
```

**关键文件清单**:
- `apps/backend/unified_skills/openspec/__init__.py`
- `apps/backend/unified_skills/openspec/branch_manager.py`
- `apps/backend/unified_skills/openspec/git_sync.py`
- `apps/backend/unified_skills/openspec/merge_handler.py`

---

### Phase 12: 集成测试与文档 (1周)

**目标**: 端到端测试和完善文档

#### 12.1 集成测试

**文件**: `tests/unified_skills/`

```python
# test_config_transpiler.py
# test_skill_activation.py
# test_cli_adapters.py
# test_mcp_bridge.py
# test_openspec_branch.py
# test_e2e_workflow.py
```

#### 12.2 用户文档

**文件**: `guides/unified-skills/`

```
guides/unified-skills/
├── README.md                 # 快速入门
├── configuration.md          # 配置指南
├── creating-skills.md        # 技能开发指南
├── cli-adapters.md           # CLI 适配器说明
├── troubleshooting.md        # 常见问题
└── api-reference.md          # API 参考
```

**关键文件清单**:
- `tests/unified_skills/test_config_transpiler.py`
- `tests/unified_skills/test_skill_activation.py`
- `tests/unified_skills/test_cli_adapters.py`
- `tests/unified_skills/test_e2e_workflow.py`
- `guides/unified-skills/README.md`
- `guides/unified-skills/configuration.md`
- `guides/unified-skills/creating-skills.md`

---

## 数据流

### 统一技能激活流程

```
1. 用户输入命令/提示
       │
       ▼
2. Hook 触发 (Layer 1)
   ┌─────────────────────────────────────────┐
   │  UserPromptSubmit / PreToolUse Hook     │
   │         │                               │
   │         ▼                               │
   │  skill-activation-hook.py               │
   └─────────────────────────────────────────┘
       │
       ▼
3. 规则引擎匹配 (Layer 2)
   ┌─────────────────────────────────────────┐
   │  skill-rules.json                       │
   │  ├── Keywords 匹配 (40%)                │
   │  ├── Intent 匹配 (30%)                  │
   │  ├── Path 匹配 (20%)                    │
   │  └── Content 匹配 (10%)                 │
   │         │                               │
   │         ▼                               │
   │  加权评分 → 阈值过滤 → 优先级排序        │
   └─────────────────────────────────────────┘
       │
       ▼
4. 技能加载
   ┌─────────────────────────────────────────┐
   │  SkillLoader                            │
   │  ├── 加载 SKILL.md (<500行核心)         │
   │  └── 按需加载 resources/ (渐进式)       │
   └─────────────────────────────────────────┘
       │
       ▼
5. CLI 适配器注入
   ┌─────────────┬─────────────┬─────────────┐
   │   Claude    │   Gemini    │   Codex     │
   │  Adapter    │  Adapter    │  Adapter    │
   ├─────────────┼─────────────┼─────────────┤
   │ 原生注入     │ MCP桥接     │ Rules转换   │
   │ hooks.json  │ MCP Server  │ .rules文件  │
   └─────────────┴─────────────┴─────────────┘
       │
       ▼
6. Agent 执行（带技能上下文）
   ┌─────────────────────────────────────────┐
   │  统一工作流执行                          │
   │  init → research → plan → dev → test    │
   │         │                               │
   │         ▼                               │
   │  OpenSpec 分支隔离上下文                 │
   └─────────────────────────────────────────┘
       │
       ▼
7. 结果同步到 Graphiti
```

### 配置同步流程

```
unified-config.yaml
       │
       ▼
ConfigTranspiler
       │
       ├──────────────────┬──────────────────┐
       ▼                  ▼                  ▼
.claude/              .gemini/           .codex/
├── settings.json     ├── settings.json  ├── config.toml
├── hooks.json        └── mcp.json       └── rules/
└── mcp.json                                └── *.rules
```

---

## 实现优先级

| 优先级 | Phase | 模块 | 预计工时 | 依赖 |
|--------|-------|------|----------|------|
| P0 | 7 | 统一配置格式 + ConfigTranspiler | 3天 | 无 |
| P0 | 7 | CLI适配器基类 + Claude适配器 | 2天 | 无 |
| P1 | 8 | skill-rules.json 规则定义 | 2天 | P0 |
| P1 | 8 | 双层激活引擎 | 3天 | P0 |
| P1 | 8 | Hook 集成 (skill-activation-hook) | 2天 | P1 |
| P2 | 9 | 技能库目录结构 | 1天 | P1 |
| P2 | 9 | skill.yaml 元数据格式 | 2天 | P2 |
| P2 | 9 | SkillLoader 渐进式加载 | 3天 | P2 |
| P2 | 9 | 核心技能迁移 (ultra-workflow) | 2天 | P2 |
| P3 | 10 | Gemini 适配器 + MCP桥接 | 3天 | P2 |
| P3 | 10 | Codex 适配器 + Rules转换 | 3天 | P2 |
| P3 | 11 | OpenSpec 分支隔离增强 | 4天 | P2 |
| P3 | 11 | Git 分支同步 | 2天 | P3 |
| P4 | 12 | 集成测试 | 3天 | 全部 |
| P4 | 12 | 用户文档 | 2天 | 全部 |

**总预计工时**: 约 5.5 周 (Phase 7-12)

---

## 验收标准

### 功能验收

1. **统一配置系统**
   - [ ] `unified-config.yaml` 可以定义跨CLI配置
   - [ ] ConfigTranspiler 正确生成各CLI配置文件
   - [ ] 配置变更自动同步到所有启用的CLI

2. **技能激活引擎**
   - [ ] Hook 正确触发技能匹配
   - [ ] 四层规则匹配准确率 ≥85%
   - [ ] 技能按优先级正确排序和激活

3. **统一技能库**
   - [ ] 技能可以跨CLI复用
   - [ ] 渐进式加载控制 token 使用
   - [ ] skill.yaml 元数据正确解析

4. **CLI 适配器**
   - [ ] Claude 原生注入正常工作
   - [ ] Gemini MCP桥接正常工作
   - [ ] Codex Rules转换正常工作

5. **OpenSpec 分支隔离**
   - [ ] 每个分支有独立的 spec 目录
   - [ ] Git 分支操作自动同步 OpenSpec
   - [ ] 分支合并正确处理 spec 冲突

### 性能指标

| 指标 | 目标 |
|------|------|
| 技能激活延迟 | <200ms |
| 配置转换延迟 | <500ms |
| 技能加载延迟 (core) | <100ms |
| 技能加载延迟 (full) | <500ms |
| MCP 桥接响应 | <300ms |

---

## 风险评估（2025-12-29 更新）

### 低风险 ✅
- **Gemini CLI 技能系统** (置信度: 95%)
  - **发现**: gemini-cli-skillz 扩展完全支持 Anthropic SKILL.md 格式
  - **方案**: `ln -s ~/.claude/skills ~/.skillz` 软链接共享
  - **验证**: 官方扩展，社区活跃

- **Hook 跨CLI兼容性** (置信度: 90%)
  - **发现**: Gemini CLI 有 11 种原生 Hook，比 Claude Code 更丰富
  - **Codex**: notify 出站事件 + MCP 调用可实现类似效果
  - **映射**: BeforeAgent↔UserPromptSubmit, BeforeTool↔PreToolUse

- **MCP 协议兼容性** (置信度: 100%)
  - **发现**: 三CLI都完全支持 MCP
  - **Gemini**: 240+ 扩展生态，原生支持
  - **Codex**: STDIO/HTTP 双模式

### 中风险 ⚠️
- **Codex 入站 Hook 缺失** (置信度: 75%)
  - **问题**: Codex 无入站 Hook，无法从外部事件自动恢复会话
  - **缓解**: `codex resume` + notify 脚本组合
  - **影响**: 技能激活需主动调用而非自动触发

- **配置同步复杂度**
  - **问题**: 三种配置格式（JSON/JSON/TOML）+ 三种指令文件（CLAUDE.md/GEMINI.md/AGENTS.md）
  - **缓解**: ConfigTranspiler + 模板生成
  - **工时**: 比预期多 2-3 天

### 低风险 ✅（已验证）
- **技能库 token 膨胀**
  - **发现**: OpenSkills 渐进式披露机制成熟
  - **Layer 1**: ~100-200 tokens（技能列表）
  - **Layer 2**: ~1500 tokens（技能核心）
  - **Layer 3**: 按需加载
  - **预算**: 每次对话节省 ~3000 tokens

---

## 置信度分析（更新版）

| 模块 | 置信度 | 原因 | 验证来源 |
|------|--------|------|----------|
| 统一配置系统 | 98% | 三CLI都支持项目级配置 | 官方文档 |
| 双层激活引擎 | 98% | Claude/Gemini 原生 Hook | 官方文档 |
| Claude 适配器 | 100% | 原生支持，无需适配 | 官方文档 |
| Gemini 适配器 | 95% | gemini-cli-skillz + 11种Hook | GitHub扩展 |
| Codex 适配器 | 85% | 原生 Skills，但缺入站 Hook | 官方文档 |
| OpenSkills 集成 | 98% | 已有成熟方案 | NPM包+GitHub |
| OpenSpec 分支隔离 | 90% | Git Hook 集成成熟 | 实践验证 |
| Research 阶段优化 | 95% | 流程清晰，模板完善 | 最佳实践 |

**总体置信度**: 95% (核心功能 98%，Gemini/Codex 适配 90%)

---

## 下一步

### Week 1: 基础设施 + Research 阶段核心

**Day 1-2: 项目结构**
- [ ] 创建 `apps/backend/unified_skills/` 目录结构
- [ ] 实现 `unified_config_schema.py` 统一配置格式
- [ ] 实现 `ConfigTranspiler` 配置转换器

**Day 3-4: Research 阶段核心**
- [ ] 创建 `research-deep` 技能 SKILL.md
- [ ] 编写 6 大文档模板（PRD/TECH_SPEC/ARCHITECTURE/API_SPEC/CONVENTIONS/TASK_BREAKDOWN）
- [ ] 实现 `ResearchQualityGate` 质量门禁

**Day 5: OpenSkills 集成**
- [ ] 安装 OpenSkills CLI
- [ ] 实现 `OpenSkillsIntegration` 集成类
- [ ] 设置三CLI软链接共享

### Week 2: 技能激活引擎

**Day 1-2: 双层激活**
- [ ] 实现 `skill-rules.json` 规则定义
- [ ] 实现 `SkillActivationEngine` 双层匹配
- [ ] Claude Code Hook 集成

**Day 3-4: Gemini/Codex 适配**
- [ ] 安装 gemini-cli-skillz 扩展
- [ ] 实现 `GeminiAdapter` Hook 映射
- [ ] 实现 `CodexAdapter` notify 事件处理

**Day 5: 集成测试**
- [ ] 端到端测试：统一技能在三CLI上的激活
- [ ] Research 阶段完整流程测试

### Week 3: OpenSpec 增强 + 文档

**Day 1-3: 分支隔离**
- [ ] 实现 `BranchAwareOpenSpec` 分支感知
- [ ] 实现 `OpenSpecGitSync` Git 集成
- [ ] Git Hook 安装脚本

**Day 4-5: 文档和发布**
- [ ] 用户文档编写
- [ ] 示例项目创建
- [ ] 发布 v2.1 版本

---

## 研究报告参考

完整研究报告已保存至：
- `/.ultra/docs/research/gemini-cli-capabilities-2025-12-29.md`
- `/.ultra/docs/research/openai-codex-cli-2025-12-29.md`
- `/.ultra/docs/research/openskill-agent-skills-2025-12-29.md`

---

## 关键命令速查

```bash
# OpenSkills 安装和使用
npm i -g openskills
openskills install anthropics/skills
openskills sync
openskills read <skill-name>

# Gemini CLI 技能扩展
gemini extensions install https://github.com/intellectronica/gemini-cli-skillz
ln -s ~/.claude/skills ~/.skillz

# Codex CLI 技能目录
ln -s ~/.claude/skills ~/.codex/skills

# 三CLI共享技能目录
~/.claude/skills/  # 主目录
~/.skillz -> ~/.claude/skills  # Gemini 软链接
~/.codex/skills -> ~/.claude/skills  # Codex 软链接
```
