# Hook自动触发UltraBuild技能计划

## 置信度评估

| 方面 | 置信度 | 理由 |
|------|--------|------|
| 技术可行性 | 98% | deprecated目录有完整实现，只需恢复并配置 |
| 触发规则设计 | 95% | 技能描述中有明确的触发条件 |
| 兼容性 | 97% | 现有hooks基础设施完整 |
| **整体置信度** | **96%** | 恢复现有代码+创建配置文件 |

---

## 现状分析

### 已有资源

| 文件 | 状态 | 说明 |
|------|------|------|
| `hooks/deprecated/skill-activation-prompt.sh` | 可用 | 入口脚本 |
| `hooks/deprecated/skill-activation-prompt.ts` | 可用 | TypeScript完整实现 |
| `hooks/post-tool-use-tracker.sh` | 已启用 | 追踪文件修改 |
| `settings.json` hooks配置 | 空 `{}` | 需要配置 |
| `skills/skill-rules.json` | 不存在 | 需要创建 |

### 当前hooks目录结构
```
hooks/
├── deprecated/
│   ├── skill-activation-prompt.sh
│   └── skill-activation-prompt.ts
├── post-tool-use-tracker.sh  # 已存在
├── node_modules/
├── package.json
└── tsconfig.json
```

---

## UltraBuild技能触发规则设计

### 技能分类与触发条件

| 技能 | 类型 | 触发方式 | 关键词/模式 |
|------|------|----------|-------------|
| **guarding-quality** | auto | 代码编辑时 | 文件模式: `*.ts,*.js,*.py,*.go,*.vue,*.tsx` |
| **guarding-test-quality** | auto | 测试相关 | 关键词: `test`, `TAS`, `coverage` |
| **guarding-git-workflow** | auto | Git操作 | 关键词: `commit`, `push`, `merge`, `rebase` |
| **syncing-status** | auto | 状态查询 | 关键词: `status`, `progress`, `任务` |
| **syncing-docs** | auto | 文档同步 | 关键词: `doc`, `文档`, `research` |
| **guiding-workflow** | suggest | 工作流 | 关键词: `next`, `workflow`, `下一步` |
| **frontend** | suggest | 前端开发 | 关键词: `React`, `Vue`, `component`, `UI` |
| **backend** | suggest | 后端开发 | 关键词: `API`, `database`, `server`, `auth` |
| **smart-contract** | suggest | 合约开发 | 关键词: `contract`, `solidity`, `ERC`, `web3` |

---

## 实施步骤

### Step 1: 复制hook脚本文件（保留备份）

将deprecated目录中的文件复制到hooks主目录（保留原文件作为备份）：

```bash
# 复制文件（保留deprecated目录作为备份）
cp hooks/deprecated/skill-activation-prompt.sh hooks/
cp hooks/deprecated/skill-activation-prompt.ts hooks/
```

**新建文件**:
- `/Users/rocky243/.claude/hooks/skill-activation-prompt.sh`
- `/Users/rocky243/.claude/hooks/skill-activation-prompt.ts`

**备份保留**: `hooks/deprecated/` 目录保持不变

---

### Step 2: 创建skill-rules.json

**新建文件**: `/Users/rocky243/.claude/skills/skill-rules.json`

```json
{
  "version": "4.2",
  "description": "UltraBuild Pro 4.2 技能自动触发规则",
  "skills": {
    "guarding-quality": {
      "type": "guard",
      "enforcement": "auto",
      "priority": "high",
      "description": "代码质量守护 - SOLID原则、复杂度限制",
      "promptTriggers": {
        "keywords": ["refactor", "重构", "code review", "代码审查", "quality", "质量"],
        "intentPatterns": ["(fix|improve|optimize).*code", "(检查|分析|审查).*代码"]
      },
      "fileTriggers": {
        "pathPatterns": ["**/*.ts", "**/*.tsx", "**/*.js", "**/*.py", "**/*.go", "**/*.vue"],
        "pathExclusions": ["**/node_modules/**", "**/*.test.*", "**/*.spec.*"]
      }
    },
    "guarding-test-quality": {
      "type": "guard",
      "enforcement": "auto",
      "priority": "high",
      "description": "测试质量守护 - TAS评分、Mock比例",
      "promptTriggers": {
        "keywords": ["test", "测试", "TAS", "coverage", "覆盖率", "spec"],
        "intentPatterns": ["(write|add|fix).*test", "(编写|添加|修复).*测试"]
      },
      "fileTriggers": {
        "pathPatterns": ["**/*.test.ts", "**/*.spec.ts", "**/*.test.js", "**/__tests__/**"]
      }
    },
    "guarding-git-workflow": {
      "type": "guard",
      "enforcement": "auto",
      "priority": "critical",
      "description": "Git操作守护 - 安全提交、分支策略",
      "promptTriggers": {
        "keywords": ["commit", "push", "merge", "rebase", "branch", "git", "提交", "合并"],
        "intentPatterns": ["git (commit|push|merge|rebase)", "(提交|推送|合并).*代码"]
      }
    },
    "syncing-status": {
      "type": "sync",
      "enforcement": "auto",
      "priority": "medium",
      "description": "状态同步 - 任务进度、测试结果",
      "promptTriggers": {
        "keywords": ["status", "进度", "任务", "progress", "完成", "done"],
        "intentPatterns": ["(what|show|check).*status", "(查看|检查|显示).*(状态|进度)"]
      }
    },
    "syncing-docs": {
      "type": "sync",
      "enforcement": "suggest",
      "priority": "medium",
      "description": "文档同步 - ADR、研究报告",
      "promptTriggers": {
        "keywords": ["document", "文档", "ADR", "research", "研究", "architecture"],
        "intentPatterns": ["(update|write|create).*doc", "(更新|编写|创建).*文档"]
      }
    },
    "guiding-workflow": {
      "type": "utility",
      "enforcement": "suggest",
      "priority": "low",
      "description": "工作流指导 - 下一步建议",
      "promptTriggers": {
        "keywords": ["next", "下一步", "workflow", "工作流", "what should", "该做什么"],
        "intentPatterns": ["what.*next", "下一步.*做什么"]
      }
    },
    "frontend": {
      "type": "domain",
      "enforcement": "suggest",
      "priority": "high",
      "description": "前端开发 - React/Vue/Next.js模式",
      "promptTriggers": {
        "keywords": ["React", "Vue", "Next.js", "component", "组件", "UI", "CSS", "前端", "frontend"],
        "intentPatterns": ["(build|create|fix).*component", "(构建|创建|修复).*组件"]
      },
      "fileTriggers": {
        "pathPatterns": ["**/*.tsx", "**/*.vue", "**/components/**", "**/pages/**"]
      }
    },
    "backend": {
      "type": "domain",
      "enforcement": "suggest",
      "priority": "high",
      "description": "后端开发 - API/数据库/安全",
      "promptTriggers": {
        "keywords": ["API", "REST", "GraphQL", "database", "数据库", "server", "auth", "认证", "后端", "backend"],
        "intentPatterns": ["(create|build|fix).*api", "(创建|构建|修复).*接口"]
      },
      "fileTriggers": {
        "pathPatterns": ["**/api/**", "**/server/**", "**/controllers/**", "**/routes/**"]
      }
    },
    "smart-contract": {
      "type": "domain",
      "enforcement": "suggest",
      "priority": "high",
      "description": "智能合约开发 - EVM/Solana/安全审计",
      "promptTriggers": {
        "keywords": ["contract", "solidity", "ERC", "web3", "blockchain", "合约", "区块链"],
        "intentPatterns": ["(write|audit|deploy).*contract", "(编写|审计|部署).*合约"]
      },
      "fileTriggers": {
        "pathPatterns": ["**/*.sol", "**/contracts/**", "**/foundry/**"]
      }
    }
  }
}
```

---

### Step 3: 更新settings.json hooks配置

**修改文件**: `/Users/rocky243/.claude/settings.json`

将空的 `"hooks": {}` 替换为：

```json
"hooks": {
  "UserPromptSubmit": [
    {
      "command": "~/.claude/hooks/skill-activation-prompt.sh",
      "description": "UltraBuild技能自动激活",
      "timeout": 5000
    }
  ],
  "PostToolUse": [
    {
      "command": "~/.claude/hooks/post-tool-use-tracker.sh",
      "description": "追踪文件修改",
      "timeout": 3000,
      "filter": {
        "tools": ["Edit", "Write", "MultiEdit"]
      }
    }
  ]
}
```

---

### Step 4: 确保依赖可用

检查hooks目录的Node.js依赖：

```bash
cd ~/.claude/hooks && npm install
```

---

## 关键文件清单

| 操作 | 文件路径 |
|------|----------|
| 复制 | `hooks/deprecated/skill-activation-prompt.sh` → `hooks/` |
| 复制 | `hooks/deprecated/skill-activation-prompt.ts` → `hooks/` |
| 新建 | `skills/skill-rules.json` |
| 修改 | `settings.json` (hooks配置) |
| 保留 | `hooks/deprecated/` (备份目录) |

---

## 预期效果

### Hook触发流程

```
用户输入提示
     ↓
UserPromptSubmit Hook
     ↓
skill-activation-prompt.sh
     ↓
skill-activation-prompt.ts
     ↓
匹配 skill-rules.json 规则
     ↓
输出技能建议（按优先级排序）
     ↓
Claude自动考虑使用推荐的技能
```

### 输出示例

当用户输入 "帮我重构这个React组件" 时：

```
📚 SKILL SUGGESTIONS

🟡 **High Priority Skills** (建议使用):
  - **guarding-quality**: 代码质量守护 - SOLID原则、复杂度限制
  - **frontend**: 前端开发 - React/Vue/Next.js模式

💡 **使用方式**: 使用 Skill 工具调用相应的 Skill
```

---

## 风险与缓解

| 风险 | 概率 | 缓解措施 |
|------|------|----------|
| TypeScript运行依赖缺失 | 低 | 检查node_modules，必要时npm install |
| 规则匹配过于激进 | 中 | 初始使用suggest而非auto，观察调整 |
| Hook超时 | 低 | 设置5秒超时，脚本设计为快速返回 |

---

## 验证步骤

1. **测试hook脚本执行**:
   ```bash
   CLAUDE_USER_PROMPT="帮我写一个React组件" ~/.claude/hooks/skill-activation-prompt.sh
   ```

2. **验证settings.json语法**:
   ```bash
   jq . ~/.claude/settings.json
   ```

3. **测试完整流程**:
   - 启动新的Claude Code会话
   - 输入包含触发关键词的提示
   - 观察是否输出技能建议
