**判断**

我对下面这套优化顺序有超过 90% 的把握，因为当前几个核心问题在代码里是直接可见的，不是推测：

- 当前会话合并完全靠 `branch + cwd + 30 分钟窗口`，没有使用真实 `session_id`，所以长会话、重试 stop、同分支并行工作都会被错误合并或拆分，见 [memory_db.py](/Users/rocky243/.claude/hooks/memory_db.py#L128)。
- `pre_stop_check.py` 每次 block 都会增加临时 stop 计数，见 [pre_stop_check.py](/Users/rocky243/.claude/hooks/pre_stop_check.py#L350)；而 `session_journal.py` 在 `stop_hook_active=true` 的重触发场景下仍然写 DB，只是跳过 AI 摘要，见 [session_journal.py](/Users/rocky243/.claude/hooks/session_journal.py#L395)。这就是 `stop_count=4306` 这类异常的直接根因。
- 摘要输入目前只取 transcript 的 head/tail 文本采样，基本不吸收“实际做了什么”的结构化信号，见 [session_journal.py](/Users/rocky243/.claude/hooks/session_journal.py#L122) 和 [session_journal.py](/Users/rocky243/.claude/hooks/session_journal.py#L277)。
- claude-mem 值得借鉴的不是 Bun worker 本身，而是 lifecycle 切分、真实会话 ID、结构化 summary、内容哈希去重，见 [hooks.json](/Users/rocky243/claude-mem/plugin/hooks/hooks.json#L16)、[session-init.ts](/Users/rocky243/claude-mem/src/cli/handlers/session-init.ts#L25)、[observations/store.ts](/Users/rocky243/claude-mem/src/services/sqlite/observations/store.ts#L12)、[SessionStore.ts](/Users/rocky243/claude-mem/src/services/sqlite/SessionStore.ts#L76)。

**逐项结论**

1. 值得采用的 claude-mem 特性：
- `UserPromptSubmit` 建 session，用真实 `content_session_id` 作为主身份。这个必须搬。
- 结构化 summary 字段。这个必须搬。
- 短窗口内容哈希去重。这个必须搬。
- `PostToolUse` observation，但要做轻量版。这个应该搬。
- `session_summaries` 和 `observations` 分表。这个应该搬。

2. 明显过度设计的部分：
- Bun HTTP worker、端口服务、完整异步队列体系。你当前 Python hooks + SQLite 不需要为了这件事重建一套服务层。
- 9 张表、20+ 索引、完整 timeline/fetch/search API。现在的瓶颈不是查询层，而是写入质量。
- `discovery_tokens` ROI 跟踪和 UI 经济学展示。对当前问题帮助很小，后置。

3. 摘要质量和一致性的修法：
- 不要再让“fallback commit summary”和“AI summary”共用一个无状态 `summary` 字段。
- 摘要必须改成固定结构，建议 4 段：`request / completed / learned / next_steps`。`investigated` 可选，不是必须。
- 摘要输入不要只喂 transcript 采样，应该喂：
  - 初始用户请求
  - 修改文件列表
  - 最后一个 assistant message
  - 失败的测试/命令错误摘要
  - 可选的 transcript 尾部片段
- 模型换成更便宜更快的非 Opus 档即可。这里数据整理比模型档位更重要。
- 增加 summary validator。低质量摘要直接标记为 `fallback` 或 `failed`，不要冒充正式摘要。

4. observation 是否要加：
- 要加，但先做最轻版。
- 第一版只捕获高信号工具事件：
  - `Edit|Write|MultiEdit`：记录改了哪些文件
  - `Bash`：只记录测试/构建/lint 失败或修复成功
  - 可选 `WebFetch|WebSearch`：只记录明确外部事实
- 不要记录每一次 `Read/Grep/Glob`。噪音太大。
- 不需要每次都跑模型。先规则提取，Stop 时再汇总成 1 到 3 条 observation 就够了。

5. merge window / dedup 的修法：
- 主键改成真实 `content_session_id` 后，30 分钟 merge window 只保留为“缺失 session_id 时的降级策略”。
- `stop_count` 不再代表 stop 尝试次数。拆成：
  - `stop_attempts`
  - `stop_blocks`
  - `completed_at`
- `stop_hook_active=true` 时不应再 upsert session。
- 去重用 `summary_hash` 和 `observation_hash`，窗口 30 秒到 2 分钟都可以；会话去重不再靠时间窗口。

**优先级计划**

1. P0，本周先做身份修复。
把真实 `session_id` 引入存储层，新增 `content_session_id UNIQUE`，Stop 重触发时不再写 session。只做这一步，`stop_count` 异常、长会话 merge 失真、很多重复记录会立刻下降。

2. P0，同步改摘要存储契约。
新增 `summary_status`、`summary_source`、`summary_model`、`summary_hash`，并把摘要拆成结构化字段。fallback 只能填 `summary_source='fallback'`，不能阻止后续正式摘要生成。

3. P1，加 `UserPromptSubmit`。
这是摘要质量的关键输入。没有原始 request，后面的 summary 永远不稳定。你不需要像 claude-mem 那样上完整 worker，只要 hook 直接写 SQLite 即可。

4. P1，加轻量 `PostToolUse` observation。
先只存高信号 observation，限制每 session 最多注入 3 条。这样能明显提升跨会话 recall，但不会把系统变成日志仓库。

5. P1，分表 + FTS 重构。
保留 `sessions` 作为元数据表，搜索主入口改到 `session_summaries_fts` 和 `observations_fts`。当前把一切塞进 `sessions.summary`，检索粒度太粗。

6. P2，一次性清洗历史坏数据。
写一个离线脚本：
- 合并同 `content_session_id` 的记录
- 对旧数据用 `(branch,cwd,summary_hash,时间邻近)` 识别 probable duplicates
- 保留“质量最高”的 summary
- 重建 Chroma embedding

**推荐的最小 schema 演进**

```sql
CREATE TABLE sessions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  content_session_id TEXT UNIQUE NOT NULL,
  started_at TEXT NOT NULL,
  last_active TEXT NOT NULL,
  completed_at TEXT,
  branch TEXT NOT NULL DEFAULT '',
  cwd TEXT NOT NULL DEFAULT '',
  files_modified_json TEXT NOT NULL DEFAULT '[]',
  stop_attempts INTEGER NOT NULL DEFAULT 0,
  stop_blocks INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE user_prompts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  session_id INTEGER NOT NULL,
  prompt_text TEXT NOT NULL,
  created_at TEXT NOT NULL,
  FOREIGN KEY(session_id) REFERENCES sessions(id) ON DELETE CASCADE
);

CREATE TABLE session_summaries (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  session_id INTEGER NOT NULL UNIQUE,
  summary_status TEXT NOT NULL CHECK(summary_status IN ('pending','ready','fallback','failed')),
  summary_source TEXT NOT NULL CHECK(summary_source IN ('model','fallback','manual')),
  summary_model TEXT,
  request TEXT,
  completed TEXT,
  learned TEXT,
  next_steps TEXT,
  raw_text TEXT,
  summary_hash TEXT,
  quality_score INTEGER NOT NULL DEFAULT 0,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  FOREIGN KEY(session_id) REFERENCES sessions(id) ON DELETE CASCADE
);

CREATE TABLE observations (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  session_id INTEGER NOT NULL,
  kind TEXT NOT NULL CHECK(kind IN ('edit','test_failure','test_fix','decision','external_fact')),
  title TEXT NOT NULL,
  detail TEXT NOT NULL,
  tool_name TEXT,
  files_json TEXT NOT NULL DEFAULT '[]',
  content_hash TEXT,
  created_at TEXT NOT NULL,
  FOREIGN KEY(session_id) REFERENCES sessions(id) ON DELETE CASCADE
);
```

**取舍**

- 我不建议把当前系统直接“升级成 claude-mem”。那会把你从数据质量问题，带到运维复杂度问题。
- 我建议保留你现在的“少量 SessionStart 注入”策略，这点已经是对的。先把写入质量修好，再谈更复杂的搜索层。
- 如果只能做两件事，就做：
  1. `content_session_id` 主身份
  2. 结构化 summary + source/status

**验证命令**

```bash
sqlite3 "$(git rev-parse --show-toplevel)/.ultra/memory/memory.db" \
"select count(*), count(distinct content_session_id) from sessions;"
```

```bash
sqlite3 "$(git rev-parse --show-toplevel)/.ultra/memory/memory.db" \
"select summary_source, summary_status, count(*) from session_summaries group by 1,2 order by 1,2;"
```

```bash
sqlite3 "$(git rev-parse --show-toplevel)/.ultra/memory/memory.db" \
"select kind, count(*) from observations group by 1 order by 2 desc;"
```

如果你要，我下一步可以直接把这个方案收敛成一个“最小可落地改造清单”，按 `Phase 0/1/2` 拆到具体 hook、字段、迁移顺序。