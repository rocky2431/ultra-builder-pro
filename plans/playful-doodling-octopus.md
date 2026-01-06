# P0 + P1 Implementation Plan: Trading System Enhancement

## Overview

基于对比分析，实现以下优先级任务：
- **P0-1**: 集成 Optuna 超参数优化到 UnifiedBacktestRunner
- **P0-2**: 添加 Lookahead-bias 检测工具
- **P1-1**: 完善 WebUI 回测结果展示
- **P1-2**: 添加策略模板库

---

## P0-1: Optuna 超参数优化集成

### 发现
- 系统已有 Optuna 基础设施：
  - `src/iqfmp/evaluation/hyperopt_optimizer.py` - BayesianOptimizer 使用 Optuna
  - `src/iqfmp/ml/optimizer.py` - StrategyOptimizer, OptimizationConfig
- 缺少：将 Optuna 与 `UnifiedBacktestRunner` 连接的桥接层

### 实施步骤

#### Step 1: 创建 BacktestOptimizer 类
**文件**: `src/iqfmp/evaluation/backtest_optimizer.py` (新建)

```python
class BacktestOptimizer:
    """Optuna-based backtest parameter optimization."""

    def __init__(
        self,
        runner: UnifiedBacktestRunner,
        signals: pd.DataFrame,
        price_data: pd.DataFrame,
        config: OptimizationConfig,
    )

    def define_search_space(self, trial: optuna.Trial) -> UnifiedBacktestParams
    def objective(self, trial: optuna.Trial) -> float
    def optimize(self) -> OptimizationResult
```

关键功能:
- 支持 TPE/CMAES/Random 采样器
- 支持 Median/Hyperband 剪枝
- Redis 进度回调
- PostgreSQL 持久化存储

#### Step 2: 扩展 UnifiedBacktestParams
**文件**: `src/iqfmp/core/unified_backtest.py`

添加字段:
```python
trial_id: Optional[int] = None
optimization_run_id: Optional[str] = None
```

#### Step 3: 添加 API 端点
**文件**: `src/iqfmp/api/backtest/router.py`

```python
@router.post("/optimizations")
async def create_optimization(
    strategy_id: str,
    config: OptimizationRequest,
) -> OptimizationResponse

@router.get("/optimizations/{id}")
async def get_optimization_result(id: str) -> OptimizationDetailResponse
```

#### Step 4: 测试
**文件**: `tests/unit/evaluation/test_backtest_optimizer.py` (新建)

---

## P0-2: Lookahead-bias 检测工具

### 发现
- 系统在 `factor_engine.py:390-394` 使用 `shift(-N)` 计算前向收益 - 风险点
- 无 Qlib 表达式验证 (`Ref($x, -N)` 可通过)
- 无 IC 衰减分析检测

### 实施步骤

#### Step 1: 创建 LookaheadBiasDetector
**文件**: `src/iqfmp/evaluation/lookahead_detector.py` (新建)

```python
class LookaheadBiasDetector:
    """Detect lookahead bias in factors and expressions."""

    def check_qlib_expression(self, expr: str) -> DetectionResult
    def check_python_code(self, code: str) -> DetectionResult
    def audit_temporal_alignment(
        self, factor_df: pd.DataFrame, target_df: pd.DataFrame
    ) -> AuditReport
    def ic_decay_analysis(
        self, factor: pd.Series, price_data: pd.DataFrame
    ) -> DecayAnalysis
```

#### Step 2: 集成到因子评估流程
**文件**: `src/iqfmp/evaluation/factor_evaluator.py`

在评估前添加检测:
```python
def evaluate(self, factor_df, ...):
    # NEW: Lookahead check
    detection = self.detector.audit_temporal_alignment(factor_df, returns)
    if detection.has_bias:
        raise LookaheadBiasError(detection.details)
```

#### Step 3: 添加 CLI 命令
**文件**: `src/iqfmp/cli/commands/validate.py` (新建)

```bash
iqfmp validate --check-lookahead --factor=my_factor
```

#### Step 4: 测试
**文件**: `tests/unit/evaluation/test_lookahead_detector.py` (新建)

---

## P1-1: WebUI 回测结果展示增强

### 发现
- `BacktestCenterPage.tsx` 已有基础结构
- 缺少: 权益曲线图表、回撤可视化、滚动指标

### 实施步骤

#### Step 1: 添加图表组件
**文件**: `dashboard/src/components/backtest/EquityCurveChart.tsx` (新建)

使用 Recharts:
- 双轴: 权益曲线 + 回撤
- 交互式 tooltip
- 对比基准线

#### Step 2: 添加月度收益热力图
**文件**: `dashboard/src/components/backtest/MonthlyReturnsHeatmap.tsx` (新建)

12x年数 网格，颜色编码收益

#### Step 3: 扩展 BacktestDetailView
**文件**: `dashboard/src/pages/BacktestCenterPage.tsx`

添加 Tabs:
- Overview (现有指标)
- Equity Curve (新图表)
- Monthly Returns (热力图)
- Trade Analysis (交易分布)

#### Step 4: 后端 API 增强
**文件**: `src/iqfmp/api/backtest/schemas.py`

添加:
```python
class BacktestAnalysisResponse:
    rolling_sharpe: List[RollingMetric]
    drawdown_periods: List[DrawdownPeriod]
    trade_distribution: TradeDistribution
```

---

## P1-2: 策略模板库

### 发现
- `StrategyWorkshopPage.tsx` 支持策略创建
- 缺少: 预设模板、一键应用

### 实施步骤

#### Step 1: 定义模板数据
**文件**: `dashboard/src/data/strategyTemplates.ts` (新建)

```typescript
export const STRATEGY_TEMPLATES: StrategyTemplate[] = [
  {
    id: "momentum_basic",
    name: "Basic Momentum",
    description: "Simple price momentum strategy",
    factors: ["momentum_20d", "momentum_60d"],
    weightingMethod: "equal",
    rebalanceFrequency: "weekly",
    maxPositions: 20,
    longOnly: true,
  },
  // ... 更多模板
]
```

预设模板:
1. Basic Momentum - 动量因子
2. Value Investing - 价值因子组合
3. Low Volatility - 低波动策略
4. Multi-Factor - 多因子平衡
5. Crypto Trend - 加密货币趋势

#### Step 2: 添加模板选择 UI
**文件**: `dashboard/src/pages/StrategyWorkshopPage.tsx`

添加 "From Template" tab，显示模板卡片网格

#### Step 3: 后端支持
**文件**: `src/iqfmp/api/strategies/router.py`

```python
@router.get("/templates")
async def list_templates() -> List[StrategyTemplate]

@router.post("/from-template/{template_id}")
async def create_from_template(template_id: str) -> StrategyResponse
```

---

## 文件修改清单

### 新建文件

| 文件 | 用途 | 优先级 |
|------|------|--------|
| `src/iqfmp/evaluation/backtest_optimizer.py` | Optuna 优化器 | P0 |
| `src/iqfmp/evaluation/lookahead_detector.py` | 前瞻偏差检测 | P0 |
| `tests/unit/evaluation/test_backtest_optimizer.py` | 优化器测试 | P0 |
| `tests/unit/evaluation/test_lookahead_detector.py` | 检测器测试 | P0 |
| `dashboard/src/components/backtest/EquityCurveChart.tsx` | 权益曲线图 | P1 |
| `dashboard/src/components/backtest/MonthlyReturnsHeatmap.tsx` | 月度热力图 | P1 |
| `dashboard/src/data/strategyTemplates.ts` | 策略模板数据 | P1 |

### 修改文件

| 文件 | 修改内容 | 优先级 |
|------|----------|--------|
| `src/iqfmp/core/unified_backtest.py` | 添加 trial_id 字段 | P0 |
| `src/iqfmp/api/backtest/router.py` | 添加优化端点 | P0 |
| `src/iqfmp/api/backtest/schemas.py` | 添加优化请求/响应 | P0 |
| `src/iqfmp/evaluation/factor_evaluator.py` | 集成前瞻检测 | P0 |
| `dashboard/src/pages/BacktestCenterPage.tsx` | 增强结果展示 | P1 |
| `dashboard/src/pages/StrategyWorkshopPage.tsx` | 添加模板选择 | P1 |
| `dashboard/src/api/backtest.ts` | 添加优化 API | P1 |

---

## 实施顺序

```
Week 1: P0-1 Optuna Integration
  Day 1-2: BacktestOptimizer 核心类
  Day 3: API 端点
  Day 4-5: 测试 + 集成

Week 2: P0-2 Lookahead Detection
  Day 1-2: LookaheadBiasDetector 核心
  Day 3: IC 衰减分析
  Day 4-5: 集成到评估流程 + 测试

Week 3: P1-1 WebUI Enhancement
  Day 1-2: EquityCurveChart 组件
  Day 3: MonthlyReturnsHeatmap
  Day 4-5: BacktestDetailView 集成

Week 4: P1-2 Strategy Templates
  Day 1-2: 模板数据 + 后端 API
  Day 3-5: 前端 UI + 集成测试
```

---

## 技术决策

1. **Optuna 采样器**: 默认 TPE，高维空间用 CMAES
2. **优化指标**: 可配置多指标 (Sharpe/Calmar/Return/IC)，API 参数选择
3. **前瞻检测模式**: 用户可配置 (strict=抛异常, lenient=警告继续)
4. **存储**: PostgreSQL (与现有 research_ledger 一致)
5. **图表库**: Recharts (已在项目中使用)
6. **模板存储**: 硬编码 + 数据库混合 (核心模板硬编码，用户自定义存数据库)
7. **策略模板类型**: Momentum, Mean Reversion, Multi-Factor, Crypto-Specific

---

## 依赖

```
optuna>=3.0.0 (已安装)
recharts (前端已有)
```

## 风险

1. **Optuna 并行**: n_jobs > 1 需要 PostgreSQL 存储锁定
2. **前瞻检测**: 可能误报合法的滞后因子
3. **图表性能**: 大量数据点需要下采样
