# Ultra Builder Pro 组件审计计划

基于 Claude Code 官方文档规范的全面对比分析。

---

## 📊 审计总览

| 组件类型 | 数量 | 严重问题 | 中等问题 | 轻微问题 |
|----------|------|----------|----------|----------|
| CLAUDE.md | 1 | 0 | 1 | 1 |
| Commands | 9 | 1 | 3 | 2 |
| Agents | 4 | **4** | 0 | 0 |
| Skills | 8 | 0 | 0 | 0 |

**总结**: Agents 有严重格式问题，1个 Command 过大，其余基本符合规范。

---

## 1️⃣ CLAUDE.md 审计

### 官方规范

```markdown
# 无需 frontmatter
# 使用 @import 引用外部文件
# 保持简洁，复杂内容放入 @references
```

### 当前状态

```markdown
# Ultra Builder Pro 4.2

**Always respond in Chinese-simplified**

## Commands
| Command | Purpose |
...
(79 行)
```

### 问题分析

| 问题 | 等级 | 详情 |
|------|------|------|
| ⚠️ 缺少 @import | 中等 | 未使用官方支持的 `@path/file` 语法引用详细文档 |
| 💡 可以更简洁 | 轻微 | Skills/Agents 列表可以用 @import 引用 |

### ✅ 符合规范

- 无 frontmatter（正确）
- 使用表格组织（良好）
- 保持简洁 79 行（良好）

### 建议修改

```markdown
# Ultra Builder Pro 4.2

**Always respond in Chinese-simplified**

## Quick Reference
@config/ultra-skills-guide.md
@guidelines/ultra-quality-standards.md

## Commands
[保持现有表格]

## Quality Gates
[保持现有内容]
```

**优先级**: 低 - 当前已经很简洁

---

## 2️⃣ Commands 审计 (9个)

### 官方规范

```yaml
---
description: Brief description (显示在帮助中)
allowed-tools: Tool1, Tool2
argument-hint: [arg1] [arg2]  # 可选但推荐
model: claude-opus            # 可选
---

# 命令内容
简洁的指令，复杂内容使用 @import
```

### 各命令审计

| 命令 | 大小 | description | allowed-tools | argument-hint | 问题 |
|------|------|-------------|---------------|---------------|------|
| ultra-think.md | 10KB | ✅ | ✅ | ✅ | ⚠️ 略大 |
| ultra-deliver.md | 3KB | ✅ | ✅ | ❌ 缺失 | ⚠️ 需添加 |
| ultra-dev.md | 6KB | ✅ | ✅ | ✅ | ✅ 良好 |
| ultra-init.md | 12KB | ✅ | ✅ | ✅ | ⚠️ 略大 |
| ultra-plan.md | 8KB | ✅ | ✅ | ❌ 缺失 | ⚠️ 需添加 |
| **ultra-research.md** | **25KB** | ✅ | ✅ | ❌ 缺失 | **❌ 过大！** |
| ultra-session-reset.md | 3KB | ✅ | ✅ | ❌ 缺失 | ⚠️ 内容引用错误命令名 |
| ultra-status.md | 5KB | ✅ | ✅ | ❌ 缺失 | ⚠️ 需添加 |
| ultra-test.md | 10KB | ✅ | ✅ | ❌ 缺失 | ⚠️ 略大 |

### 🔴 严重问题

**ultra-research.md (25KB)** - 严重超大

官方建议命令应简洁。25KB 的命令文件会：
- 每次调用消耗大量 token
- 降低响应速度
- 超出最佳实践

**建议**: 拆分为：
- `ultra-research.md` (3-5KB) - 核心工作流
- `RESEARCH-REFERENCE.md` (20KB) - 详细指南，用 @import 引用

### ⚠️ 中等问题

**缺少 argument-hint 的命令**:
- ultra-deliver.md
- ultra-plan.md
- ultra-research.md
- ultra-session-reset.md
- ultra-status.md
- ultra-test.md

**建议**: 添加 `argument-hint` 字段

```yaml
# ultra-deliver.md
argument-hint: [version-type]

# ultra-plan.md
argument-hint: [scope]

# ultra-research.md
argument-hint: [topic]

# ultra-session-reset.md
argument-hint: (无参数)

# ultra-status.md
argument-hint: [task-id]

# ultra-test.md
argument-hint: [scope]
```

### 💡 轻微问题

**ultra-session-reset.md 内容引用错误**:
```markdown
# /session-reset  ← 应该是 /ultra-session-reset
```

---

## 3️⃣ Agents 审计 (4个) - 🔴 严重问题

### 官方规范

```yaml
---
name: agent-name
description: "Expert code reviewer. Use proactively after code changes."
tools: Read, Write, Bash
model: sonnet
permissionMode: acceptEdits
skills: skill1, skill2
---

You are an expert...
```

**官方 description 格式**:
- 描述代理的专业领域
- 说明何时应该委托给此代理
- **不使用 "TRIGGERS:" 格式** - 那是 Skills 的格式

### 当前状态 (错误格式)

```yaml
# ultra-architect-agent.md
description: "System architecture design expert. TRIGGERS: Architecture design, SOLID compliance analysis..."

# ultra-performance-agent.md
description: "Performance optimization expert. TRIGGERS: Core Web Vitals optimization..."

# ultra-qa-agent.md
description: "Test strategy and quality assurance expert. TRIGGERS: Test planning..."

# ultra-research-agent.md
description: "Technical research specialist for /ultra-research Mode 2 and on-demand deep analysis. TRIGGERS: Technology comparisons..."
```

### 🔴 问题分析

**所有 4 个 Agents 都使用了错误的 description 格式！**

Agents 和 Skills 的 description 有不同用途：

| 组件 | Description 用途 | 正确格式 |
|------|------------------|----------|
| **Skills** | 让 Claude 自动判断何时触发 | `TRIGGERS when: ..., DO NOT trigger for: ...` |
| **Agents** | 让 Claude 判断何时委托任务 | `Expert in X. Use when Y.` |

### ✅ 修正方案

```yaml
# ultra-architect-agent.md
description: "Expert software architect for system design decisions. Use when designing new systems, evaluating architecture patterns, or analyzing SOLID compliance for complex components."

# ultra-performance-agent.md
description: "Performance optimization specialist. Use when analyzing bottlenecks, optimizing Core Web Vitals, or improving load times for frontend applications."

# ultra-qa-agent.md
description: "Test strategy and quality assurance expert. Use when designing test suites, improving coverage strategy, or diagnosing low TAS scores."

# ultra-research-agent.md
description: "Technical research specialist for evidence-based analysis. Use for technology comparisons, best-practice extraction, or risk assessment requiring web research."
```

---

## 4️⃣ Skills 审计 (8个) - ✅ 符合规范

### 官方规范

```yaml
---
name: skill-name          # 必需：小写+连字符
description: "..."        # 必需：<1024字符
allowed-tools: Tool1      # 可选
---
```

### 各 Skill 审计

| Skill | name | description 格式 | allowed-tools | 状态 |
|-------|------|------------------|---------------|------|
| automating-e2e-tests | ✅ | ✅ TRIGGERS+DO NOT | ✅ | ✅ 符合 |
| compressing-context | ✅ | ✅ TRIGGERS+DO NOT | ✅ | ✅ 符合 |
| guarding-git-workflow | ✅ | ✅ TRIGGERS+DO NOT | ✅ | ✅ 符合 |
| guarding-quality | ✅ | ✅ TRIGGERS+DO NOT | ✅ | ✅ 符合 |
| guarding-test-quality | ✅ | ✅ TRIGGERS+DO NOT | ✅ | ✅ 符合 |
| guiding-workflow | ✅ | ✅ TRIGGERS+DO NOT | ✅ | ✅ 符合 |
| syncing-docs | ✅ | ✅ TRIGGERS+DO NOT | ✅ | ✅ 符合 |
| syncing-status | ✅ | ✅ TRIGGERS+DO NOT | ✅ | ✅ 符合 |

**所有 8 个 Skills 都符合官方规范！**

---

## 📋 修复优先级

### P0 - 必须立即修复

| 问题 | 影响 | 修复方案 |
|------|------|----------|
| Agents description 格式错误 | Claude 无法正确判断何时委托 | 重写 4 个 Agent descriptions |

### P1 - 应该修复

| 问题 | 影响 | 修复方案 |
|------|------|----------|
| ultra-research.md 25KB | 每次调用消耗大量 token | 拆分为核心+引用 |
| Commands 缺少 argument-hint | 用户体验下降 | 添加 6 个 argument-hint |

### P2 - 可以修复

| 问题 | 影响 | 修复方案 |
|------|------|----------|
| ultra-session-reset 命令名错误 | 轻微混淆 | 修正标题 |
| CLAUDE.md 缺少 @import | 组织性 | 添加引用 |

---

## 📝 执行计划

### Phase 1: 修复 Agents (P0)

1. 重写 ultra-architect-agent.md description
2. 重写 ultra-performance-agent.md description
3. 重写 ultra-qa-agent.md description
4. 重写 ultra-research-agent.md description

**预计**: 15 分钟

### Phase 2: 优化 Commands (P1)

1. 拆分 ultra-research.md (25KB → 5KB + 引用)
2. 添加 6 个 argument-hint
3. 修正 ultra-session-reset 标题

**预计**: 30 分钟

### Phase 3: 优化 CLAUDE.md (P2)

1. 添加 @import 引用（如果需要）

**预计**: 10 分钟

---

## 验证标准

完成后验证：

- [ ] 所有 Agents description 不包含 "TRIGGERS:"
- [ ] ultra-research.md < 10KB
- [ ] 所有 Commands 有 argument-hint
- [ ] ultra-session-reset 标题正确
- [ ] 所有组件通过 `claude mcp list` 验证

---

**计划生成时间**: 2024-12-28
**基于**: Claude Code 官方文档 (2025-11-06)
