# Claude Code 完整能力继承计划

## 概述

为 Auto Claude 实现对 Claude Code 所有原生能力的完整继承，包括：CLAUDE.md 动态加载、MCP 管理、Hook 管理、Command 管理、Skill 管理、@import 文档语法。

---

## 当前状态 vs 目标状态

| 能力 | 当前 | 目标 |
|------|------|------|
| CLAUDE.md | 静态文档，未加载到 agent | 动态注入到系统提示词 |
| MCP 管理 | 代码硬编码，无 UI | mcp.json 兼容 + 配置 UI |
| Hook 管理 | 仅安全 hook | 用户自定义 PreToolUse/PostToolUse |
| Command 管理 | 无 | .claude/commands/ 支持 + UI |
| Skill 管理 | 无 | .claude/skills/ 支持 + UI |
| @import 语法 | 无 | 递归导入 + 变量替换 |

---

## 实现优先级

```
P0 (立即): CLAUDE.md 动态加载
P1 (高):   MCP 管理 + Hook 管理
P2 (中):   Command 管理 + Skill 管理
P3 (低):   @import 文档语法
```

---

## Phase 1: CLAUDE.md 动态加载 (P0)

### 目标
将项目/用户/Spec 级别的 CLAUDE.md 自动注入到 agent 系统提示词。

### 层级优先级（从低到高）
1. `~/.claude/CLAUDE.md` (用户全局)
2. `{project}/.claude/CLAUDE.md` 或 `{project}/CLAUDE.md` (项目级)
3. `{spec_dir}/CLAUDE.md` (Spec 级别覆盖)

### 新建文件

**`apps/backend/prompts_pkg/claude_md_loader.py`**
```python
def find_claude_md(project_dir, spec_dir) -> list[Path]
def load_claude_md(project_dir, spec_dir) -> str
```

### 修改文件

| 文件 | 修改内容 |
|------|----------|
| `apps/backend/core/client.py:345-354` | system_prompt 前添加 CLAUDE.md 内容 |
| `apps/backend/prompts_pkg/prompts.py` | 所有 `get_*_prompt()` 函数注入 CLAUDE.md |

### 测试
- `tests/test_claude_md_loader.py` - 层级解析、合并逻辑

---

## Phase 2: MCP 管理 (P1)

### 目标
支持 Claude Code 的 `mcp.json` 格式，提供 UI 管理 MCP 服务器。

### 存储格式
```json
// .claude/mcp.json (Claude Code 兼容)
{
  "mcpServers": {
    "my-server": {
      "command": "npx",
      "args": ["-y", "my-mcp-server"],
      "env": {"API_KEY": "${env:MY_KEY}"},
      "disabled": false
    }
  }
}
```

### 新建文件

**Backend:**
- `apps/backend/mcp/config_loader.py` - MCP 配置加载/保存
- `apps/backend/mcp/__init__.py`

**Frontend:**
- `apps/frontend/src/renderer/components/settings/MCPSettings.tsx` - MCP 管理 UI
- `apps/frontend/src/main/ipc-handlers/mcp-handlers.ts` - IPC 处理

### 修改文件

| 文件 | 修改内容 |
|------|----------|
| `apps/backend/core/client.py:297-340` | 合并用户 MCP 配置到 mcp_servers |
| `apps/frontend/src/shared/constants/ipc.ts` | 添加 MCP_* IPC 通道 |
| `apps/frontend/src/renderer/components/settings/AppSettings.tsx` | 添加 MCP 导航项 |

---

## Phase 3: Hook 管理 (P1)

### 目标
支持用户自定义 PreToolUse/PostToolUse hooks。

### 存储格式
```json
// .claude/hooks.json
{
  "PreToolUse": [
    {
      "name": "validate-paths",
      "matcher": "Write",
      "type": "script",
      "script": ".claude/scripts/validate.sh",
      "timeout": 5
    }
  ],
  "PostToolUse": [
    {
      "name": "format-code",
      "matcher": "Write",
      "type": "command",
      "command": "prettier --write $FILE_PATH"
    }
  ]
}
```

### 新建文件

**Backend:**
- `apps/backend/hooks/user_hooks.py` - 用户 hook 加载/执行
- `apps/backend/hooks/__init__.py`

**Frontend:**
- `apps/frontend/src/renderer/components/settings/HookSettings.tsx` - Hook 管理 UI
- `apps/frontend/src/main/ipc-handlers/hook-handlers.ts` - IPC 处理

### 修改文件

| 文件 | 修改内容 |
|------|----------|
| `apps/backend/core/client.py:357-361` | 使用 `build_hooks_dict()` 合并用户 hooks |
| `apps/frontend/src/shared/constants/ipc.ts` | 添加 HOOKS_* IPC 通道 |

### 关键设计
- 系统安全 hook (`bash_security_hook`) 始终优先执行
- 用户 hooks 追加在系统 hooks 之后
- Hook 执行日志写入 `{spec_dir}/hooks.log`

---

## Phase 4: Command 管理 (P2)

### 目标
支持 `.claude/commands/*.md` 格式的命令发现和管理。

### 新建文件

**Backend:**
- `apps/backend/commands/registry.py` - 命令发现/注册

**Frontend:**
- `apps/frontend/src/renderer/components/settings/CommandsSettings.tsx` - 命令 UI

### 内置命令注册
Auto Claude 内置命令将自动注册到 `.claude/commands/`:
- `/build` - 启动自主构建
- `/plan` - 创建实现计划
- `/qa` - 运行 QA 审查
- `/status` - 显示构建状态

---

## Phase 5: Skill 管理 (P2)

### 目标
支持 `.claude/skills/*.md` 格式的技能发现、激活/停用。

### 存储格式
```
.claude/skills/
├── testing.md       # 技能定义
├── security.md
└── skills.json      # 激活状态 {"active": {"testing": true}}
```

### 新建文件

**Backend:**
- `apps/backend/skills/loader.py` - 技能发现/加载

**Frontend:**
- `apps/frontend/src/renderer/components/settings/SkillsSettings.tsx` - 技能 UI

### 集成点
- 激活的技能内容注入到 agent 提示词（在 CLAUDE.md 之后）

---

## Phase 6: @import 文档语法 (P3)

### 目标
支持在提示词文件中使用 `@import` 指令。

### 语法
```markdown
@import "./common/header.md"
@import "${project}/.claude/skills/testing.md"
```

### 新建文件
- `apps/backend/prompts_pkg/import_processor.py` - 导入处理器

### 特性
- 递归导入解析
- 循环引用检测
- 变量替换 (`${project}`, `${spec}`)

---

## 关键文件路径

### 核心集成点
```
apps/backend/core/client.py          # ClaudeSDKClient 创建，所有功能集成
apps/backend/prompts_pkg/prompts.py  # 提示词加载，CLAUDE.md/Skills 注入
apps/backend/security/hooks.py       # Hook 模式参考
```

### 前端模式参考
```
apps/frontend/src/renderer/components/settings/IntegrationSettings.tsx  # UI 模式
apps/frontend/src/main/ipc-handlers/settings-handlers.ts               # IPC 模式
apps/frontend/src/shared/constants/ipc.ts                               # IPC 通道
```

---

## 实现顺序

```
Week 1-2: Phase 1 (CLAUDE.md) + Phase 2 Backend (MCP loader)
Week 3-4: Phase 2 Frontend (MCP UI) + Phase 3 (Hooks)
Week 5-6: Phase 4 (Commands) + Phase 5 (Skills)
Week 7:   Phase 6 (@import) + 集成测试
```

---

## 兼容性保证

1. **向后兼容**: 所有功能为可选项，无配置时行为不变
2. **渐进采用**: 用户可逐步启用各功能
3. **Claude Code 兼容**: mcp.json、commands、skills 格式与 Claude Code 一致

---

## 已确认决策

| 问题 | 决策 |
|------|------|
| MCP 环境变量引用 | ✅ 支持 `${env:VAR_NAME}` 语法 |
| Hook UI 范围 | ✅ 完整 UI（可视化编辑器 + 日志查看器 + 测试运行） |
| 实现范围 | ✅ 一次性全部实现所有 6 个功能 |
| Hook 超时默认值 | 5 秒 |

---

## 完整实现任务清单

### Phase 1: CLAUDE.md 动态加载

- [ ] 创建 `apps/backend/prompts_pkg/claude_md_loader.py`
  - [ ] `find_claude_md()` - 查找所有层级的 CLAUDE.md
  - [ ] `load_claude_md()` - 加载并合并内容
- [ ] 修改 `apps/backend/core/client.py`
  - [ ] 在 system_prompt 前注入 CLAUDE.md 内容
- [ ] 修改 `apps/backend/prompts_pkg/prompts.py`
  - [ ] `get_planner_prompt()` 注入 CLAUDE.md
  - [ ] `get_coding_prompt()` 注入 CLAUDE.md
  - [ ] `get_qa_reviewer_prompt()` 注入 CLAUDE.md
  - [ ] `get_qa_fixer_prompt()` 注入 CLAUDE.md
- [ ] 创建 `tests/test_claude_md_loader.py`

### Phase 2: MCP 管理

**Backend:**
- [ ] 创建 `apps/backend/mcp/__init__.py`
- [ ] 创建 `apps/backend/mcp/config_loader.py`
  - [ ] `load_mcp_config()` - 加载 mcp.json
  - [ ] `save_mcp_config()` - 保存配置
  - [ ] `resolve_env_vars()` - 解析 ${env:VAR_NAME}
- [ ] 修改 `apps/backend/core/client.py`
  - [ ] 合并用户 MCP 配置

**Frontend:**
- [ ] 创建 `apps/frontend/src/renderer/components/settings/MCPSettings.tsx`
  - [ ] MCP 服务器列表
  - [ ] 添加/编辑/删除服务器
  - [ ] 启用/禁用开关
  - [ ] 环境变量引用 UI
- [ ] 创建 `apps/frontend/src/main/ipc-handlers/mcp-handlers.ts`
- [ ] 修改 `apps/frontend/src/shared/constants/ipc.ts` - 添加 MCP_* 通道
- [ ] 修改 `apps/frontend/src/renderer/components/settings/AppSettings.tsx` - 添加 MCP 导航

### Phase 3: Hook 管理

**Backend:**
- [ ] 创建 `apps/backend/hooks/__init__.py`
- [ ] 创建 `apps/backend/hooks/user_hooks.py`
  - [ ] `load_hooks_config()` - 加载 hooks.json
  - [ ] `create_hook_from_config()` - 创建 hook 函数
  - [ ] `build_hooks_dict()` - 合并系统和用户 hooks
  - [ ] `log_hook_execution()` - 记录 hook 执行日志
- [ ] 修改 `apps/backend/core/client.py`
  - [ ] 使用 `build_hooks_dict()` 替换静态 hooks

**Frontend:**
- [ ] 创建 `apps/frontend/src/renderer/components/settings/HookSettings.tsx`
  - [ ] Hook 列表（PreToolUse / PostToolUse）
  - [ ] 可视化编辑器
  - [ ] Hook 执行日志查看器
  - [ ] 测试运行按钮
- [ ] 创建 `apps/frontend/src/main/ipc-handlers/hook-handlers.ts`
- [ ] 修改 `apps/frontend/src/shared/constants/ipc.ts` - 添加 HOOKS_* 通道

### Phase 4: Command 管理

**Backend:**
- [ ] 创建 `apps/backend/commands/__init__.py`
- [ ] 创建 `apps/backend/commands/registry.py`
  - [ ] `discover_commands()` - 发现命令
  - [ ] `get_command()` - 获取单个命令
  - [ ] `register_auto_claude_commands()` - 注册内置命令

**Frontend:**
- [ ] 创建 `apps/frontend/src/renderer/components/settings/CommandsSettings.tsx`
  - [ ] 命令列表
  - [ ] 命令内容预览
  - [ ] 创建/编辑命令
  - [ ] 执行命令按钮
- [ ] 创建 `apps/frontend/src/main/ipc-handlers/command-handlers.ts`

### Phase 5: Skill 管理

**Backend:**
- [ ] 创建 `apps/backend/skills/__init__.py`
- [ ] 创建 `apps/backend/skills/loader.py`
  - [ ] `discover_skills()` - 发现技能
  - [ ] `load_active_skills()` - 加载激活的技能
  - [ ] `set_skill_active()` - 设置激活状态
- [ ] 修改 `apps/backend/prompts_pkg/prompts.py`
  - [ ] 注入激活的技能内容

**Frontend:**
- [ ] 创建 `apps/frontend/src/renderer/components/settings/SkillsSettings.tsx`
  - [ ] 技能列表
  - [ ] 激活/停用开关
  - [ ] 技能内容预览
  - [ ] 创建新技能
- [ ] 创建 `apps/frontend/src/main/ipc-handlers/skill-handlers.ts`

### Phase 6: @import 文档语法

**Backend:**
- [ ] 创建 `apps/backend/prompts_pkg/import_processor.py`
  - [ ] `process_imports()` - 处理 @import 指令
  - [ ] 递归导入解析
  - [ ] 循环引用检测
  - [ ] 变量替换 (${project}, ${spec})
- [ ] 修改 `apps/backend/prompts_pkg/prompts.py`
  - [ ] 在所有 prompt 加载函数中调用 import 处理

### 集成与测试

- [ ] 创建 `tests/test_mcp_config.py`
- [ ] 创建 `tests/test_user_hooks.py`
- [ ] 创建 `tests/test_commands.py`
- [ ] 创建 `tests/test_skills.py`
- [ ] 创建 `tests/test_import_processor.py`
- [ ] 集成测试：完整 agent 会话测试
