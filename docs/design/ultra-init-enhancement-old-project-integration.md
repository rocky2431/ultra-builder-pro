# Ultra-Init 老项目集成增强设计

**版本**: 4.2
**日期**: 2025-11-18
**状态**: 设计阶段

---

## 1. 问题陈述

### 当前限制

1. **老项目缺乏互动性**
   - 检测到 `.ultra/` 存在时，直接提示重新初始化
   - 没有确认步骤，用户无法审查检测结果
   - 无法修改或调整检测到的配置

2. **AskUserQuestion 使用不足**
   - 仅在无法自动检测时才使用（fallback 模式）
   - 没有显示检测到的上下文信息
   - 不支持多选（虽然工具支持 `multiSelect: true`）

3. **新老项目体验不一致**
   - 新项目：自动检测 → 直接生成（快速但不透明）
   - 老项目：检测到 `.ultra/` → 直接覆盖提示（没有确认）
   - **期望**：统一为互动式流程

### 用户期望

> "最好的情况是 重复新项目的流程 但是在启动askquestiontool工具的时候 老项目的技术栈情况啥的列举在选项中加上（原项目）的提示"

**核心需求**：
- ✅ 老项目和新项目使用相同的互动流程
- ✅ 显示检测到的配置，标注为"（原项目）"
- ✅ 支持多选（混合项目类型，如 Web + API）
- ✅ 用户可以确认、修改或覆盖检测结果

---

## 2. 设计方案

### 2.1 核心理念

**从"自动生成"到"智能建议 + 用户确认"**

```
旧流程：
检测配置 → 直接生成 .ultra/ → 完成（无确认）

新流程：
检测配置 → 展示建议（标注来源）→ 用户确认/修改 → 生成 .ultra/ → 完成
```

### 2.2 增强后的工作流

#### Phase 0: 项目状态检测

```javascript
// 检测项目状态
const projectState = {
  isExistingProject: false,  // 是否已有代码
  hasUltraDir: false,        // 是否已初始化过
  detectedType: null,        // 检测到的项目类型
  detectedStack: null,       // 检测到的技术栈
  detectedMultiType: []      // 检测到的多种类型（如 web + api）
}

// 1. 检查 .ultra/ 是否存在
if (exists('.ultra/config.json')) {
  projectState.hasUltraDir = true
  // 读取现有配置
  const existingConfig = JSON.parse(read('.ultra/config.json'))
  projectState.existingConfig = existingConfig
}

// 2. 检查是否有代码文件
if (exists('package.json') || exists('requirements.txt') || exists('go.mod')) {
  projectState.isExistingProject = true

  // 3. 智能检测项目类型和技术栈
  projectState.detectedType = detectProjectType()      // e.g., "web"
  projectState.detectedStack = detectTechStack()       // e.g., "react-ts"
  projectState.detectedMultiType = detectMultiType()   // e.g., ["web", "api"]
}
```

#### Phase 1: 互动式确认（新增）

**适用场景**：
- ✅ 老项目（`isExistingProject = true`）
- ✅ 已初始化项目重新初始化（`hasUltraDir = true`）
- ⚠️  可选：新项目也可启用（通过参数控制）

**互动内容**：

##### 问题 1: 项目类型确认

```typescript
AskUserQuestion({
  questions: [{
    header: "项目类型",
    question: "请选择项目类型（可多选）：",
    multiSelect: true,  // ✅ 支持多选
    options: [
      {
        label: "Web 应用 (原项目)",  // ✅ 标注"（原项目）"
        description: `检测到 React + TypeScript (${detectedStack})`
      },
      {
        label: "API 服务",
        description: "后端 API 开发"
      },
      {
        label: "CLI 工具",
        description: "命令行工具"
      },
      {
        label: "全栈应用",
        description: "前后端一体化"
      }
    ]
  }]
})
```

**关键特性**：
- ✅ **multiSelect: true** - 支持选择 "Web 应用" + "API 服务"（混合项目）
- ✅ **"（原项目）"标注** - 检测到的选项显示来源
- ✅ **检测信息展示** - 在 description 中显示检测细节（如 "React + TypeScript"）

##### 问题 2: 技术栈确认

```typescript
AskUserQuestion({
  questions: [{
    header: "技术栈",
    question: "请选择主要技术栈：",
    multiSelect: false,  // 单选
    options: [
      {
        label: "React + TypeScript (原项目)",  // ✅ 检测到的栈
        description: "检测到 dependencies: react ^18.2.0, typescript ^5.0.0"
      },
      {
        label: "Vue + TypeScript",
        description: "Vue 3 + Composition API"
      },
      {
        label: "Next.js",
        description: "React 框架，内置 SSR"
      },
      {
        label: "自定义",
        description: "手动输入技术栈"
      }
    ]
  }]
})
```

##### 问题 3: 重新初始化确认（仅老项目）

```typescript
// 仅在 hasUltraDir = true 时显示
if (projectState.hasUltraDir) {
  AskUserQuestion({
    questions: [{
      header: "重新初始化",
      question: "检测到已存在 .ultra/ 目录，是否覆盖？",
      multiSelect: false,
      options: [
        {
          label: "覆盖现有配置",
          description: "将创建新的 config.json，旧配置将备份到 .ultra/backup/"
        },
        {
          label: "保留现有配置",
          description: "仅更新缺失的文件和目录"
        },
        {
          label: "取消初始化",
          description: "退出 /ultra-init 命令"
        }
      ]
    }]
  })
}
```

#### Phase 2: 生成配置

基于用户确认的选择生成 `.ultra/` 结构：

```javascript
// 1. 备份现有配置（如果覆盖）
if (userChoice === "覆盖现有配置" && hasUltraDir) {
  bash(`mkdir -p .ultra/backup/`)
  bash(`cp -r .ultra/config.json .ultra/backup/config.json.$(date +%Y%m%d-%H%M%S)`)
}

// 2. 复制模板文件
bash(`cp -r ~/.claude/.ultra-template/ .ultra/`)

// 3. 更新 config.json
const config = {
  project: {
    name: userChoice.projectName || currentDirName,
    type: userChoice.projectType,  // 可能是数组（多选）
    stack: userChoice.techStack,
    created: new Date().toISOString()
  },
  // ... 其他配置
}

write('.ultra/config.json', JSON.stringify(config, null, 2))
```

### 2.3 检测逻辑增强

#### 多类型检测（新增）

```javascript
function detectMultiType() {
  const types = []

  // 检测前端
  if (hasDependency(['react', 'vue', 'svelte', 'angular'])) {
    types.push('web')
  }

  // 检测后端
  if (hasDependency(['express', 'fastapi', 'koa', 'flask', 'django'])) {
    types.push('api')
  }

  // 检测 CLI
  if (packageJson.bin || hasDependency(['commander', 'yargs', 'inquirer'])) {
    types.push('cli')
  }

  // 检测全栈
  if (types.includes('web') && types.includes('api')) {
    types.push('fullstack')
  }

  return types
}
```

#### 上下文丰富化

```javascript
function enrichDetectionContext() {
  return {
    projectType: detectedType,
    techStack: detectedStack,
    frameworks: {
      frontend: detectFrontend(),    // ["react@18.2.0", "typescript@5.0.0"]
      backend: detectBackend(),      // ["express@4.18.0"]
      testing: detectTesting(),      // ["jest@29.0.0", "playwright@1.40.0"]
      buildTools: detectBuild()      // ["vite@5.0.0"]
    },
    packageManager: detectPM(),      // "npm" | "yarn" | "pnpm"
    hasTests: exists('tests/') || exists('__tests__/'),
    hasCI: exists('.github/workflows/') || exists('.gitlab-ci.yml')
  }
}
```

### 2.4 选项生成算法

```javascript
function generateProjectTypeOptions(detectionContext) {
  const options = []

  // 1. 添加检测到的类型（标注"（原项目）"）
  if (detectionContext.projectType) {
    options.push({
      label: `${getTypeLabel(detectionContext.projectType)} (原项目)`,
      description: `检测到 ${detectionContext.techStack}`,
      value: detectionContext.projectType,
      isDetected: true  // 标记为检测项
    })
  }

  // 2. 添加其他候选类型
  const allTypes = ['web', 'api', 'cli', 'fullstack', 'other']
  for (const type of allTypes) {
    if (type !== detectionContext.projectType) {
      options.push({
        label: getTypeLabel(type),
        description: getTypeDescription(type),
        value: type,
        isDetected: false
      })
    }
  }

  return options
}

function getTypeLabel(type) {
  const labels = {
    web: "Web 应用",
    api: "API 服务",
    cli: "CLI 工具",
    fullstack: "全栈应用",
    other: "其他"
  }
  return labels[type] || type
}
```

---

## 3. 实现计划

### 3.1 修改文件清单

| 文件 | 修改内容 | 优先级 |
|------|----------|--------|
| `commands/ultra-init.md` | 添加互动式确认流程（Phase 1） | P0 |
| `commands/ultra-init.md` | 增强检测逻辑（多类型、上下文） | P0 |
| `commands/ultra-init.md` | 添加选项生成算法 | P0 |
| `.ultra-template/config.json` | 支持多类型（type 字段改为数组） | P1 |
| `skills/guiding-workflow/SKILL.md` | 识别多类型项目 | P2 |

### 3.2 向后兼容性

**配置文件兼容**：
```json
// 旧格式（单类型）
{
  "project": {
    "type": "web"
  }
}

// 新格式（多类型）
{
  "project": {
    "type": ["web", "api"]  // 数组格式
  }
}

// 读取逻辑兼容
const projectType = Array.isArray(config.project.type)
  ? config.project.type
  : [config.project.type]
```

**命令参数兼容**：
```bash
# 旧用法（仍支持）
/ultra-init MyProject web react-ts

# 新用法（交互式）
/ultra-init MyProject --interactive

# 新用法（多类型）
/ultra-init MyProject "web,api" react-ts
```

### 3.3 用户体验优化

#### 进度指示

```
🏗️ Ultra Builder Pro 初始化

📊 项目检测完成
  ✅ 检测到 React + TypeScript
  ✅ 检测到 Express 后端
  💡 建议项目类型: Web 应用 + API 服务

❓ 正在等待用户确认...

[AskUserQuestion 工具启动]
```

#### 确认摘要

```
✅ 配置确认

项目名称: MyProject
项目类型: Web 应用, API 服务 (多类型)
技术栈: React + TypeScript (原项目检测)
Git 初始化: 是

⚙️  正在生成 .ultra/ 目录...
```

---

## 4. 示例场景

### 场景 1: 新项目首次初始化

**上下文**：空目录，无任何代码

**流程**：
1. 检测：无代码 → `isExistingProject = false`
2. **跳过互动式确认**（无检测信息）
3. 使用传统 AskUserQuestion（无"（原项目）"标注）
4. 生成 .ultra/ 目录

### 场景 2: 老项目首次初始化

**上下文**：已有 package.json（React + TS），无 .ultra/

**流程**：
1. 检测：
   - `isExistingProject = true`
   - `detectedType = "web"`
   - `detectedStack = "react-ts"`
   - `detectedMultiType = ["web"]`

2. 互动式确认：
   ```
   问题 1: 项目类型（可多选）
   [ ] Web 应用 (原项目)  ← 检测到 React + TypeScript
   [ ] API 服务
   [ ] CLI 工具
   [ ] 全栈应用
   ```

3. 用户选择：`["Web 应用 (原项目)"]`

4. 互动式确认：
   ```
   问题 2: 技术栈
   ( ) React + TypeScript (原项目)  ← 检测到 react ^18.2.0
   ( ) Vue + TypeScript
   ( ) Next.js
   ( ) 自定义
   ```

5. 用户选择：`"React + TypeScript (原项目)"`

6. 生成配置：
   ```json
   {
     "project": {
       "type": ["web"],
       "stack": "react-ts"
     }
   }
   ```

### 场景 3: 全栈项目（多类型）

**上下文**：package.json 包含 React + Express

**流程**：
1. 检测：
   - `detectedType = "fullstack"`
   - `detectedMultiType = ["web", "api", "fullstack"]`

2. 互动式确认：
   ```
   问题 1: 项目类型（可多选）
   [x] Web 应用 (原项目)  ← 检测到 React
   [x] API 服务 (原项目)  ← 检测到 Express
   [ ] CLI 工具
   [x] 全栈应用 (原项目)  ← 检测到混合
   ```

3. 用户选择：`["Web 应用", "API 服务"]`（取消勾选"全栈应用"）

4. 生成配置：
   ```json
   {
     "project": {
       "type": ["web", "api"]  // 多类型数组
     }
   }
   ```

### 场景 4: 重新初始化（已有 .ultra/）

**上下文**：已初始化项目，需重新配置

**流程**：
1. 检测：
   - `hasUltraDir = true`
   - `existingConfig = { type: "web", stack: "react-ts" }`

2. 互动式确认：
   ```
   问题 1: 重新初始化
   ( ) 覆盖现有配置  ← 备份到 .ultra/backup/
   ( ) 保留现有配置  ← 仅更新缺失文件
   ( ) 取消初始化
   ```

3. 用户选择：`"覆盖现有配置"`

4. 备份：
   ```bash
   mkdir -p .ultra/backup/
   cp .ultra/config.json .ultra/backup/config.json.20251118-143022
   ```

5. 继续后续互动式确认流程...

---

## 5. 技术考量

### 5.1 AskUserQuestion 限制

**官方限制**（from CLAUDE.md）：
- ✅ 1-4 questions per call
- ✅ 2-4 options per question
- ✅ multiSelect: true supported
- ✅ header max 12 chars

**应对策略**：
- 分批提问（不超过 4 个问题）
- 每个问题 2-4 选项（"其他"选项作为 fallback）
- header 精简为"项目类型""技术栈""Git配置"

### 5.2 多选结果处理

```typescript
// AskUserQuestion 返回格式
{
  answers: {
    "项目类型": ["Web 应用 (原项目)", "API 服务"]
  }
}

// 解析为配置
function parseUserSelection(answers) {
  const typeLabels = answers["项目类型"]
  const types = []

  for (const label of typeLabels) {
    if (label.includes("Web 应用")) types.push("web")
    if (label.includes("API 服务")) types.push("api")
    if (label.includes("CLI 工具")) types.push("cli")
    if (label.includes("全栈应用")) types.push("fullstack")
  }

  return { type: types }
}
```

### 5.3 性能影响

**额外开销**：
- 检测逻辑：+50ms（读取 package.json 等）
- AskUserQuestion：用户决策时间（无额外 token 消耗）
- 配置生成：+10ms（JSON 序列化）

**总计**：~60ms 机器时间 + 用户决策时间

---

## 6. 成功指标

### 6.1 功能指标

- ✅ 老项目初始化成功率：100%（无报错）
- ✅ 检测准确率：≥90%（检测到的类型/栈正确）
- ✅ 用户确认率：≥80%（用户接受检测建议）
- ✅ 多选使用率：≥30%（混合项目场景）

### 6.2 用户体验指标

- ✅ 互动流程完成率：≥95%（用户不中途退出）
- ✅ 重新初始化覆盖率：100%（无数据丢失）
- ✅ 新老项目流程一致性：100%（相同步骤）

### 6.3 向后兼容性

- ✅ 旧命令格式兼容：100%（`/ultra-init web react-ts` 仍可用）
- ✅ 旧配置文件兼容：100%（单类型 config.json 可读取）

---

## 7. 风险与缓解

### 风险 1: AskUserQuestion 工具限制

**风险**：选项过多导致体验不佳
**缓解**：
- 限制每个问题 4 个选项
- 使用"自定义"选项作为 escape hatch
- 分批提问（项目类型 → 技术栈 → Git）

### 风险 2: 检测错误导致误导

**风险**：检测到错误的技术栈，标注"（原项目）"误导用户
**缓解**：
- 在 description 中显示检测依据（如 "检测到 react ^18.2.0"）
- 允许用户选择其他选项
- 提供"自定义"选项

### 风险 3: 多类型配置兼容性

**风险**：旧命令/Skills 无法处理 `type: ["web", "api"]` 格式
**缓解**：
- 兼容读取逻辑：`Array.isArray(type) ? type : [type]`
- 渐进式迁移：先支持单类型，后支持多类型
- 文档明确说明新格式

---

## 8. 下一步行动

### 阶段 1: 设计评审（当前）
- [ ] 获取用户反馈
- [ ] 确认技术可行性
- [ ] 调整设计细节

### 阶段 2: 实现 (P0)
- [ ] 修改 `commands/ultra-init.md` - 添加互动式确认流程
- [ ] 增强检测逻辑（多类型、上下文）
- [ ] 实现选项生成算法

### 阶段 3: 测试 (P0)
- [ ] 单元测试：检测逻辑准确性
- [ ] 集成测试：新项目、老项目、重新初始化场景
- [ ] 兼容性测试：旧命令格式、旧配置文件

### 阶段 4: 文档更新 (P1)
- [ ] 更新 ULTRA_BUILDER_PRO_4.1_QUICK_START.md
- [ ] 更新 workflows/ultra-development-workflow.md
- [ ] 添加示例场景到文档

---

## 9. 附录

### 附录 A: AskUserQuestion 示例完整代码

```typescript
// 完整的 AskUserQuestion 调用示例
const questions = [
  {
    header: "项目类型",
    question: "请选择项目类型（可多选，适用于混合项目）：",
    multiSelect: true,
    options: [
      {
        label: "Web 应用 (原项目)",
        description: "检测到 React + TypeScript (react ^18.2.0, typescript ^5.0.0)"
      },
      {
        label: "API 服务",
        description: "后端 API 开发（RESTful 或 GraphQL）"
      },
      {
        label: "CLI 工具",
        description: "命令行工具或脚本"
      },
      {
        label: "其他",
        description: "手动指定项目类型"
      }
    ]
  },
  {
    header: "技术栈",
    question: "请选择主要技术栈：",
    multiSelect: false,
    options: [
      {
        label: "React + TypeScript (原项目)",
        description: "检测到 react ^18.2.0, typescript ^5.0.0"
      },
      {
        label: "Vue + TypeScript",
        description: "Vue 3 + Composition API"
      },
      {
        label: "Next.js",
        description: "React 框架，内置 SSR/SSG"
      },
      {
        label: "自定义",
        description: "手动输入技术栈名称"
      }
    ]
  }
]

// Claude 调用
AskUserQuestion({ questions })
```

### 附录 B: 配置文件对比

**旧格式**（Ultra Builder Pro 4.0-4.1）：
```json
{
  "version": "4.1",
  "project": {
    "name": "MyProject",
    "type": "web",
    "stack": "react-ts"
  }
}
```

**新格式**（Ultra Builder Pro 4.2+）：
```json
{
  "version": "4.2",
  "project": {
    "name": "MyProject",
    "type": ["web", "api"],  // ← 支持多类型
    "stack": "react-ts",
    "detectionContext": {    // ← 新增：检测上下文
      "frameworks": {
        "frontend": ["react@18.2.0"],
        "backend": ["express@4.18.0"]
      },
      "packageManager": "npm",
      "hasTests": true
    }
  }
}
```

---

**设计完成日期**: 2025-11-18
**待评审**: 等待用户反馈
