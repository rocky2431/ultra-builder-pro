这是一份针对当前 Python + SQLite 记忆系统的优化方案。参考了 `claude-mem` 的设计，我们的核心目标是**实用、轻量、高信噪比**，坚决避免过度工程化。

以下是优先级明确、可落地的系统演进建议：

### 1. claude-mem 特性取舍 (Adoption vs. Over-engineering)

**绝对值得采纳的特性：**
* **Structured Summaries (结构化总结)**：采用 `request/learned/completed/next_steps` 的严格划分。这是解决“总结质量极其不稳定”的银弹。
* **Content Hash Deduplication (内容哈希去重)**：使用 SHA-256 判断内容是否实质性改变，取代脆弱的时间窗口机制。
* **PostToolUse 拦截 (轻量级观察)**：捕获细粒度操作，为 AI 总结提供高密度的精确上下文。

**属于过度工程化（建议放弃）的特性：**
* **9 张表和 20+ 索引**：对于单用户的 CLI 记忆系统，维持 2-3 张表（会话表、事件表、FTS5表）即可满足 99% 的查询需求，过度范式化只会增加读写延迟和维护成本。
* **Token Budgeting (发现型 Token ROI 追踪)**：计算复杂度高，且对实际编码过程的上下文注入帮助有限。
* **三层搜索架构**：当前的 `FTS5 (关键字) + Chroma (语义)` 已经是目前最成熟且简单的混合检索方案，再增加中间层纯属画蛇添足。

---

### 2. 如何解决总结质量与一致性问题？

当前的根本问题是：**用最贵的模型 (Opus) 处理了最脏的数据 (15K 截断的 Transcript)。**

* **模型降级换速**：**立即停止使用 Opus**。总结任务应该交给 **Claude 3.5 Haiku** 或 Sonnet。Haiku 速度极快、成本极低，且对于结构化数据的提取能力非常出色。
* **强制结构化输出**：在系统提示词中，要求模型严格返回 JSON 格式：
  ```json
  {
    "request": "用户的原始意图",
    "learned": "发现的代码架构、坑点或重要上下文",
    "completed": "实际修改了什么",
    "next_steps": "未完成的部分或遗留的 bug"
  }
  ```
  如果某些会话极短，允许字段留空，但必须遵循此结构。

---

### 3. 是否添加 Observation Capture？如何做到轻量化？

**必须添加，但要做到“极简”。** 15K 字符的 Transcript 截断会丢失大量关键行为，导致总结时只能回退到 Git Commit 信息。

* **如何轻量化**：在 `PostToolUse` Hook 中，**不要捕获长篇的命令行输出或文件内容**。只捕获三个维度的元数据：
  1. `tool_name` (如：`grep_search`, `run_shell_command`)
  2. `action_summary` (如：`grep: "AuthenticationError"`, `shell: "pytest tests/auth.py"`)
  3. `outcome` (如：`Success`, `Failed with exit code 1`)
* **优化总结流**：当触发 `Stop` hook 进行总结时，将这些轻量级的 Observation 序列传给模型，而不是原始文本。这不仅将 Token 消耗降低了一个数量级，还能让模型清晰地看到你的“思考和试错路径”。

---

### 4. 如何解决 Merge Window 与去重问题 (修复 stop_count 异常)

30分钟的基于时间的合并机制在面对长会话（或频繁停止的会话）时必然崩溃，导致 `stop_count` 飙升至 4306 这种异常值。

* **引入显式 Session ID**：在 `SessionStart` Hook 触发时，生成一个全局唯一的 UUID，并将其写入一个临时文件（如 `.claude/.current_session_id`）。后续的所有 Hook 都读取这个 ID。
* **数据库 UPSERT**：不再用时间窗口去猜“这是不是同一个会话”，而是使用确定的 `session_id` 进行操作：
  ```sql
  INSERT INTO sessions (session_id, ...) VALUES (...) 
  ON CONFLICT(session_id) DO UPDATE SET ...
  ```
* **SHA-256 脏检查**：在触发更新前，对新生成的结构化总结计算 SHA-256。如果哈希值与当前数据库里的 `content_hash` 一致，直接丢弃该次写入，从而消除无意义的近义重复记录。

---

### 5. 理想的 Schema 演进方向

建议从目前的 1 张大表，拆解为 **2 张实体表 + 1 张检索表**，完美支撑上述优化：

```sql
-- 1. 核心会话表：彻底告别基于时间的合并
CREATE TABLE sessions (
    session_id TEXT PRIMARY KEY,
    started_at DATETIME,
    last_active DATETIME,
    branch TEXT,
    cwd TEXT,
    files_modified TEXT, -- JSON Array
    request TEXT,        -- [结构化总结字段]
    learned TEXT,        -- [结构化总结字段]
    completed TEXT,      -- [结构化总结字段]
    next_steps TEXT,     -- [结构化总结字段]
    stop_count INTEGER DEFAULT 0,
    content_hash TEXT    -- 核心：用于阻断重复写入
);

-- 2. 极简操作记录表 (由 PostToolUse 异步追加)
CREATE TABLE observations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT,
    timestamp DATETIME,
    tool_name TEXT,
    action_summary TEXT, 
    FOREIGN KEY(session_id) REFERENCES sessions(session_id) ON DELETE CASCADE
);

-- 3. FTS5 全文检索虚拟表 (仅索引高价值文本)
CREATE VIRTUAL TABLE sessions_fts USING fts5(
    session_id UNINDEXED,
    request,
    learned,
    completed,
    next_steps,
    content=sessions,
    content_rowid=rowid
);
```

### 务实的执行计划 (Prioritized Action Plan)

1. **[高优 - 见效最快] 修复状态管理**：引入 `.current_session_id` 机制，配合 SQL 的 `UPSERT` 和 `SHA-256` 拦截，解决 `stop_count` 异常和海量重复记录。
2. **[高优 - 降本提质] 改造总结流**：将模型从 Opus 切到 Haiku / Sonnet，使用系统提示词强制输出 JSON 结构化数据，并按 schema 分列存储。
3. **[中优 - 丰富上下文] 实现轻量观察**：编写 `PostToolUse` hook，异步记录极简操作日志到 `observations` 表，并在总结时将其作为核心输入。
4. **[暂缓] 基础设施替换**：继续使用 `double-fork` daemon 和 Chroma。虽然 Bun worker 理论上性能更好，但只要把重构重心放在数据流清洗上，当前的 Python 基础设施完全够用，重构 daemon 的 ROI 不高。
