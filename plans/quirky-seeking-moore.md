# 前后端对接完整性审查报告

## 审查目标
以后端实现为基准，检查前端是否完整对接所有功能，找出 mock 数据和未打通链路。

---

## 一、总体结论

| 维度 | 状态 | 说明 |
|------|------|------|
| API 覆盖率 | ✅ 95%+ | 前端已调用后端绝大部分 API |
| Mock 数据 | ⚠️ 存在 | 实盘交易 100% 模拟，向量库有 fallback |
| 未打通链路 | ❌ 1 处严重 | Live Trading 完全未连接后端 |
| 后端未实现 | ⚠️ 5 处 | 部分数据类型/功能标记 TODO |

---

## 二、严重问题 (P0)

### 🔴 1. 实盘交易 - 前端完全模拟，后端无 API

**文件**: `dashboard/src/hooks/useLiveTrading.ts`

**问题**:
- 前端有完整的实盘交易 UI（持仓、挂单、平仓）
- 但 **100% 使用硬编码模拟数据**
- 后端 **无 `/api/v1/trading` 端点**

**模拟内容**:
```typescript
// 硬编码持仓
const initialPositions: Position[] = [
  { symbol: 'BTC-USDT', side: 'long', size: 0.5, entryPrice: 42150, ... },
  { symbol: 'ETH-USDT', side: 'short', size: 2.0, entryPrice: 2280, ... },
]

// 价格模拟更新 (每2秒随机变动)
setInterval(() => {
  const change = (Math.random() - 0.5) * 100
  position.markPrice += change
}, 2000)
```

**影响**: 用户看到的实盘数据全是假的

**修复方案**:
1. 后端实现 Trading API（连接交易所 WebSocket）
2. 前端调用真实 API 替换模拟数据
3. 或暂时隐藏实盘交易功能

---

## 三、中等问题 (P1)

### 🟡 2. MockQdrantClient - 向量数据库 Fallback

**文件**: `src/iqfmp/vector/client.py:245-294`

**问题**: 当 Qdrant 服务不可用时，使用内存 mock
- 数据不持久化
- 搜索返回空结果
- 生产环境可能静默降级

**触发条件**:
```python
allow_mock=not self.config.vector_strict_mode  # 非严格模式时允许
```

**建议**: 生产环境强制 `vector_strict_mode=True`

---

### 🟡 3. LLM 占位符因子

**文件**: `src/iqfmp/celery_app/tasks.py:1050-1060`

**问题**: LLM API 未配置时返回硬编码因子
```python
"code": f"def calculate(data):\n    return data['close'].pct_change()"
```

**影响**: 看似正常运行但因子无意义

---

### 🟡 4. 后端未实现的数据类型

**文件**: `src/iqfmp/api/data/service.py:62-94`

| 数据类型 | 状态 | 说明 |
|----------|------|------|
| Aggregated Trades | TODO | 按价格聚合的交易 |
| Tick Trades | TODO | 逐笔交易数据 |
| Order Book Snapshot | TODO | 订单簿快照 |

**前端影响**: DataPage 显示这些选项但选择后无数据

---

### 🟡 5. WebSocket 实时监控 - Stub

**文件**: `src/iqfmp/exchange/monitoring.py:583-587`

```python
async def start(self) -> None:
    self._running = True
    # In production, this would start the WebSocket connection
```

**问题**: `RealtimeUpdater.start()` 只是占位，无实际 WebSocket 连接

---

## 四、已禁用功能 (Feature Flags)

| 功能 | 配置 | 默认值 | 影响 |
|------|------|--------|------|
| ML 信号生成 | `ml_signal_enabled` | False | SignalConverter 不用 ML |
| 工具上下文 | `tool_context_enabled` | False | Agent 无工具调用 |
| LLM 缓存 | `cache_enabled` | False | 每次重新调用 LLM |
| TimescaleDB 超表 | `hypertables_enabled` | False | 无时序优化 |
| 实盘交易 | `is_live_trading_enabled` | False | 后端禁用 |
| 检查点恢复 | `checkpoint_enabled` | False | Pipeline 无断点续传 |

---

## 五、前后端 API 对接详情

### ✅ 完全对接 (9/10)

| 模块 | 后端端点 | 前端调用 | 状态 |
|------|----------|----------|------|
| Auth | `/auth/*` | `authApi.*` | ✅ |
| Factors | `/factors/*` | `factorsApi.*` | ✅ |
| Research | `/research/*` | `researchApi.*` | ✅ |
| Pipeline | `/pipeline/*` | `pipelineApi.*` + WebSocket | ✅ |
| Strategies | `/strategies/*` | `strategiesApi.*` | ✅ |
| Backtest | `/backtest/*` | `backtestApi.*` | ✅ |
| System | `/system/*` | `systemApi.*` + WebSocket | ✅ |
| Config | `/config/*` | `configApi.*` | ✅ |
| Data | `/data/*` | `dataApi.*` | ✅ |

### ❌ 未对接 (1/10)

| 模块 | 问题 |
|------|------|
| Trading | 前端模拟，后端无 API |

---

## 六、测试覆盖问题

**标记 xfail 的测试**:
- `test_pipeline_smoke_*` - 使用 Stub LLM
- `test_crypto_agent_flow` - Series 比较 bug
- `test_backtest_engine` - 索引对齐问题
- 数据库测试 - 需要真实连接

---

## 七、建议优先级

### P0 - 必须修复
1. **实盘交易**: 要么实现后端 API，要么前端移除/隐藏该功能

### P1 - 应该修复
2. **向量库严格模式**: 生产环境禁用 MockQdrantClient
3. **LLM 配置校验**: 启动时检查，无配置则阻止因子生成
4. **数据类型实现**: 完成 Aggregated/Tick Trades

### P2 - 可以优化
5. **WebSocket 监控**: 实现 RealtimeUpdater
6. **Feature Flags**: 评估是否启用 ML 信号等功能
7. **测试修复**: 解决 xfail 测试的根本问题

---

## 八、修复工作量估算

| 任务 | 复杂度 | 预计文件数 |
|------|--------|-----------|
| Trading API 后端实现 | 高 | 5-8 |
| Trading 前端对接 | 中 | 2-3 |
| 向量库严格模式 | 低 | 1 |
| LLM 配置校验 | 低 | 2 |
| 数据类型实现 | 中 | 3-4 |

---

## 九、关键文件清单

### 需要修改
- `dashboard/src/hooks/useLiveTrading.ts` - 替换模拟数据
- `src/iqfmp/api/` - 新增 Trading Router
- `src/iqfmp/vector/client.py` - 严格模式配置
- `src/iqfmp/api/data/service.py` - 实现 TODO 数据类型

### 需要新增
- `src/iqfmp/api/trading/router.py` - Trading API
- `src/iqfmp/api/trading/service.py` - Trading Service
- `src/iqfmp/api/trading/schemas.py` - Trading Schemas
- `dashboard/src/api/trading.ts` - 前端 Trading API 模块
