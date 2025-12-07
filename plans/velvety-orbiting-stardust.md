# Trading-System-V2 前后端对齐计划 (Phase 2)

## 一、现状分析

### 1.1 已完成 (Phase 1 - 数据库统一)
- ✅ 数据库统一为 TimescaleDB（删除了 db.py）
- ✅ RD-Agent 因子入库（FactorRecord 含 source_task_id/evolution_generation/code_hash）
- ✅ 数据管道持久化（PipelineState 写入 DB）
- ✅ 因子同步服务（sync_factors_to_qlib）

### 1.2 待对齐缺口

| 模块 | 问题 | 优先级 |
|------|------|--------|
| **Factor Lab** | 只区分 Template/AI，不展示 RD-Agent 来源和血缘 | 🔴 高 |
| **Evolution 页面** | 仍是 DEMO 数据，RD-Agent 接口未被调用 | 🔴 高 |
| **Qlib Provider** | 无 TimescaleDB-backed Provider | 🟡 中 |
| **Settings 页面** | 不展示 Data Pipeline / Factor Sync 状态 | 🟡 中 |

---

## 二、推荐实施方案

### Phase 7: Factor Lab 与 RD-Agent 因子对齐

**目标**：前端 Factor Lab 能区分并展示 RD-Agent 因子及其血缘信息

**7.1 后端 API 增强**

文件：`/src/trading_system/api/routers/factors.py`

```python
# 扩展 list_factors 接口参数
@router.get("/library")
async def list_factors(
    category: str | None = None,
    ai_only: bool = False,
    templates_only: bool = False,
    source: str | None = None,  # 新增：template/llm/rdagent/manual
    has_lineage: bool | None = None,  # 新增：只返回有血缘的因子
):
    # 映射 source='rdagent' 到 category='ai_evolved'
```

**7.2 前端类型定义更新**

文件：`/frontend/src/services/api.ts`

```typescript
interface Factor {
  // 现有字段...

  // 新增血缘字段
  source_task_id?: string;
  evolution_generation?: number;
  parent_factor_id?: string;
  version?: string;
  code_hash?: string;
}

// 新增来源类型
type FactorSource = 'template' | 'llm' | 'rdagent' | 'manual';
```

**7.3 Factor Lab UI 增强**

文件：`/frontend/src/pages/FactorLabPage.tsx`

- 添加"来源"过滤标签（All / Template / LLM / RD-Agent）
- 因子列表增加来源徽章（📋 Template / 🤖 LLM / 🔬 RD-Agent）
- 详情面板增加"血缘信息"部分：
  - Source Task ID（链接到 Evolution 页面）
  - Evolution Generation
  - Parent Factor（链接到父因子）
  - Version / Code Hash

**工作量**：6-8 小时

---

### Phase 8: Evolution ↔ RD-Agent 任务对齐

**目标**：Evolution 页面展示真实 RD-Agent 任务数据，替换 DEMO 数据

**8.1 前端 API 扩展**

文件：`/frontend/src/services/api.ts`

```typescript
export const evolutionApi = {
  // 现有接口...

  // 新增 RD-Agent 接口
  getRDAgentStatus: () => fetchApi('/evolution/rdagent/status'),
  listRDAgentTasks: (status?: string) =>
    fetchApi(`/evolution/rdagent/tasks${status ? `?status=${status}` : ''}`),
  getRDAgentTask: (taskId: string) =>
    fetchApi(`/evolution/rdagent/tasks/${taskId}`),
  startFactorLoop: (config: RDAgentLoopConfig) =>
    fetchApi('/evolution/rdagent/factor-loop', { method: 'POST', body: JSON.stringify(config) }),
};
```

**8.2 Evolution 页面重构**

文件：`/frontend/src/pages/EvolutionPage.tsx`

- 添加 Tab 切换：`策略演化 (Demo)` | `RD-Agent 任务`
- RD-Agent 任务列表：
  - 显示 task_id、类型（factor/model/quant）、状态、开始时间
  - 点击展开详情：persisted_factor_ids 列表、回测结果
- 启动循环按钮：Factor Loop / Model Loop / Quant Loop
- 任务状态实时轮询（或 WebSocket）

**8.3 任务详情与因子联动**

- persisted_factor_ids 可点击跳转到 Factor Lab
- 从 Evolution 页面可直接验证 RD-Agent 生成的因子

**工作量**：8-10 小时

---

### Phase 9: Qlib 与 Timescale 数据源统一 (可选)

**目标**：创建 TimescaleDB-backed Qlib Provider

**9.1 新建 Provider**

文件：`/src/trading_system/qlib_adapter/timescale_provider.py`

```python
class TimescaleDataHandler:
    """从 TimescaleDB 直接获取 OHLCV 数据的 Qlib Handler"""

    def __init__(self, db: TimescaleDB, symbols: list[str]):
        self._db = db
        self._symbols = symbols

    def fetch(self, start_time: str, end_time: str) -> pd.DataFrame:
        """获取多标的 OHLCV 数据，返回 MultiIndex DataFrame"""
        # 从 TimescaleDB 读取数据
        # 转换为 Qlib 格式 (datetime, symbol) MultiIndex
```

**9.2 更新 DataPipelineManager**

文件：`/src/trading_system/data_pipeline/manager.py`

```python
def initialize_qlib(self, use_timescale: bool = False) -> bool:
    if use_timescale:
        # 使用 TimescaleDB Provider
        from trading_system.qlib_adapter.timescale_provider import TimescaleDataHandler
        # 初始化...
    else:
        # 现有逻辑：使用本地 bin 文件
```

**工作量**：6 小时

**注意**：此 Phase 可作为后续迭代，当前阶段保持 bin 文件方式作为稳定方案。

---

### Phase 10: Settings 页面状态增强

**目标**：展示 Data Pipeline 和 Factor Sync 状态

**10.1 后端接口（已实现）**

- `/data-pipeline/status` - 管道状态
- `/data-pipeline/factor-sync-status` - 因子同步状态（需新增）

**10.2 前端 Settings 页面更新**

文件：`/frontend/src/pages/SettingsPage.tsx`

```tsx
// 新增状态卡片
<Card title="Data Pipeline">
  <StatusItem label="Source Dir" value={pipelineStatus.source_dir_exists} />
  <StatusItem label="Qlib Dir" value={pipelineStatus.qlib_dir_exists} />
  <StatusItem label="Last Download" value={pipelineStatus.last_download} />
  <StatusItem label="Last Conversion" value={pipelineStatus.last_conversion} />
  <StatusItem label="Symbols Count" value={pipelineStatus.instruments_count} />
</Card>

<Card title="Factor Sync">
  <StatusItem label="Total Factors" value={syncStatus.total_factors_in_db} />
  <StatusItem label="Valid Factors" value={syncStatus.valid_factors} />
  <StatusItem label="AI Generated" value={syncStatus.ai_generated_factors} />
  <StatusItem label="Synced to Qlib" value={syncStatus.synced_factors} />
  <Button onClick={syncFactors}>Sync Now</Button>
</Card>
```

**工作量**：4 小时

---

## 三、关键文件清单

| 文件 | 操作 | Phase |
|------|------|-------|
| `api/routers/factors.py` | 扩展 list_factors 参数 | 7 |
| `frontend/src/services/api.ts` | 添加类型定义和 RD-Agent 接口 | 7, 8 |
| `frontend/src/pages/FactorLabPage.tsx` | 添加来源过滤和血缘展示 | 7 |
| `frontend/src/pages/EvolutionPage.tsx` | 添加 RD-Agent 任务 Tab | 8 |
| `qlib_adapter/timescale_provider.py` | 新建 (可选) | 9 |
| `data_pipeline/manager.py` | 添加 factor-sync-status 接口 | 10 |
| `frontend/src/pages/SettingsPage.tsx` | 添加状态卡片 | 10 |

---

## 四、工作量估计

| Phase | 描述 | 工时 | 优先级 |
|-------|------|------|--------|
| 7 | Factor Lab 与 RD-Agent 对齐 | 6-8h | 🔴 高 |
| 8 | Evolution ↔ RD-Agent 对齐 | 8-10h | 🔴 高 |
| 9 | Timescale Qlib Provider (可选) | 6h | 🟡 中 |
| 10 | Settings 状态增强 | 4h | 🟡 中 |

**总计**：18-24 小时（核心）/ 24-30 小时（含可选）

---

## 五、决策确认 ✅

1. **Phase 9 (Timescale Provider)**: ✅ 本轮实施，完成数据源统一

2. **Evolution 页面 DEMO 数据**: ✅ 完全替换为 RD-Agent 真实数据

3. **因子来源分类**: ✅ 四分类 (Template / LLM / RD-Agent / Manual)

---

## 六、实施顺序（已确认）

```
Phase 7: Factor Lab 与 RD-Agent 对齐 (6-8h)
    └─ 后端 API 扩展（source 过滤）
    └─ 前端类型定义（四分类：Template/LLM/RD-Agent/Manual）
    └─ UI 增强（来源徽章 + 血缘面板）

Phase 8: Evolution ↔ RD-Agent 对齐 (8-10h)
    └─ 前端 API 扩展（调用 /evolution/rdagent/* 接口）
    └─ Evolution 页面重构（完全替换 DEMO 数据）
    └─ 因子联动（persisted_factor_ids 跳转）

Phase 9: Timescale Qlib Provider (6h) ✅ 确认实施
    └─ 新建 TimescaleDataHandler
    └─ 集成到 DataPipelineManager
    └─ 统一数据源

Phase 10: Settings 状态增强 (4h)
    └─ 后端接口（factor-sync-status）
    └─ 前端卡片（Data Pipeline + Factor Sync）
```

**预计总工时**：24-30 小时
