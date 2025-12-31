# IQFMP 优化实施计划

## 用户约束（必须严格遵守）

- **禁止 mock** - 所有测试使用真实依赖
- **禁止降级/fallback** - 不允许备选实现
- **禁止自主实现** - 不允许 Pandas 替代 Qlib
- **禁止简化测试** - 测试必须完整严格
- **必须使用真实数据** - 数据库中的真实数据
- **必须使用真实 Qlib 回测引擎**

---

## Phase 1: P0-1 Qlib 版本冲突修复 (0.5h)

### 问题
`qlib 0.0.2.dev20` 阻塞 `vendor/qlib 0.9.6.99`

### 操作步骤

```bash
# 1. 卸载系统 qlib
pip uninstall qlib -y

# 2. 验证 vendor/qlib 正确加载
python -c "import qlib; print(qlib.__version__, qlib.__file__)"
# 期望: 0.9.6.99 /Users/rocky243/trading-system-v3/vendor/qlib/qlib/__init__.py
```

### 文件变更
- **修改**: `/pyproject.toml` - 确保 pythonpath 顺序正确

---

## Phase 2: P0-2 删除 Pandas Fallback (1h)

### 问题
- `qlib_crypto.py:45-384` 有完整的 Pandas 操作符实现
- `factor_engine.py:701-908` 有 `_evaluate_expression()` 本地实现

### 操作步骤

**Step 2.1: 删除 `qlib_crypto.py` 的 Pandas 实现**

文件: `src/iqfmp/core/qlib_crypto.py`

删除以下代码块：
- 行 45-384: `_build_qlib_ops_pandas()` 函数及所有操作符定义
- 删除: `QLIB_PANDAS_OPS = _build_qlib_ops_pandas()` 调用

**Step 2.2: 删除 `factor_engine.py` 的本地实现**

文件: `src/iqfmp/core/factor_engine.py`

删除行 701-908 的以下方法：
- `_evaluate_expression()`
- `_find_main_operator()`
- `_op_ref()`, `_op_mean()`, `_op_std()`, `_op_sum()`, `_op_max()`, `_op_min()`
- `_op_delta()`, `_op_rank()`, `_op_abs()`, `_op_log()`, `_op_sign()`
- `_op_corr()`, `_op_cov()`, `_op_wma()`, `_op_ema()`, `_op_rsi()`, `_op_macd()`
- `_add()`, `_sub()`, `_mul()`, `_div()`, `_gt()`, `_lt()`

替换为强制 Qlib 的实现：
```python
def _compute_qlib_expression(self, expression: str) -> pd.Series:
    """Compute expression - Qlib only, no fallback."""
    if not self._expression_engine:
        raise QlibUnavailableError("Qlib expression engine not initialized")
    return self._expression_engine.compute_expression(
        expression=expression,
        df=self._qlib_data,
        result_name="factor",
    )
```

### 文件变更
- **修改**: `src/iqfmp/core/qlib_crypto.py` (删除 ~340 行)
- **修改**: `src/iqfmp/core/factor_engine.py` (删除 ~210 行, 新增 ~10 行)

### 验证
```bash
grep -r "QLIB_PANDAS_OPS" src/
# 应返回空

grep -r "_evaluate_expression" src/iqfmp/core/factor_engine.py
# 应返回空或仅有 Qlib 调用
```

---

## Phase 3: P0-3 测试覆盖率提升 38.77% → 80% (4h)

### 问题
- 核心模块（BacktestEngine, DataProvider, FactorEngine）无单元测试
- 测试使用 SQLite 内存数据库绕过 PostgreSQL
- 18 个文件使用 Mock

### 操作步骤

**Step 3.1: 扩展覆盖率范围**

修改 `pyproject.toml`：
```toml
[tool.coverage.run]
source = [
    "src/iqfmp/api",
    "src/iqfmp/models",
    "src/iqfmp/agents",
    "src/iqfmp/evaluation",
    "src/iqfmp/core",      # 新增
    "src/iqfmp/exchange",  # 新增
    "src/iqfmp/strategy",  # 新增
]
```

**Step 3.2: 创建真实数据测试 Fixtures**

新建: `tests/fixtures/real_data_fixtures.py`

```python
"""Real data fixtures - NO MOCKS."""
import pytest
import pandas as pd
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

@pytest.fixture
async def real_db_session():
    """Create real database session."""
    engine = create_async_engine(
        "postgresql+asyncpg://iqfmp:iqfmp@localhost:5433/iqfmp_test"
    )
    async with AsyncSession(engine) as session:
        yield session

@pytest.fixture
def real_ohlcv_data():
    """Load real OHLCV from database/CSV."""
    # 使用真实数据
    ...

@pytest.fixture
def real_qlib_engine(real_ohlcv_data):
    """Create real Qlib-backed factor engine."""
    from iqfmp.core.factor_engine import QlibFactorEngine
    return QlibFactorEngine(df=real_ohlcv_data, require_qlib=True)
```

**Step 3.3: 为核心模块添加测试**

新建测试文件：
- `tests/unit/core/test_backtest_engine_real.py` (~200 行)
- `tests/unit/core/test_data_provider_real.py` (~150 行)
- `tests/unit/core/test_factor_engine_real.py` (~200 行)
- `tests/unit/exchange/test_margin_real.py` (~150 行)

**Step 3.4: 重构使用 Mock 的测试**

修改以下文件，用真实实现替换 Mock：
- `tests/unit/exchange/test_risk_controller.py`
- `tests/unit/agents/test_*.py` (移除不必要的 AsyncMock)

### 文件变更
- **修改**: `pyproject.toml`
- **新建**: `tests/fixtures/real_data_fixtures.py`
- **新建**: `tests/unit/core/test_backtest_engine_real.py`
- **新建**: `tests/unit/core/test_data_provider_real.py`
- **新建**: `tests/unit/core/test_factor_engine_real.py`
- **修改**: 多个测试文件

### 验证
```bash
pytest tests/ --cov=src/iqfmp --cov-report=term-missing --cov-fail-under=80
```

---

## Phase 4: P1-1 实现 Purged K-Fold CV (2h)

### 问题
当前只有简单 gap，无 Embargo Period，可能有数据泄漏

### 操作步骤

**Step 4.1: 实现 PurgedKFoldCV**

新建: `src/iqfmp/evaluation/purged_cv.py` (~200 行)

```python
"""Purged K-Fold CV with Embargo Period.
Reference: Lopez de Prado, AFML Chapter 7
"""

@dataclass
class PurgedCVConfig:
    n_splits: int = 5
    purge_gap: int = 5
    embargo_pct: float = 0.01

class PurgedKFoldCV:
    def split(self, X, t) -> Iterator[PurgedSplit]:
        # 实现 purging 和 embargo 逻辑
        ...
```

**Step 4.2: 集成到 WalkForwardValidator**

修改: `src/iqfmp/evaluation/walk_forward_validator.py`

```python
from iqfmp.evaluation.purged_cv import PurgedKFoldCV

class WalkForwardValidator:
    def __init__(self, ..., use_purged_cv: bool = True):
        if use_purged_cv:
            self.purged_cv = PurgedKFoldCV(...)
```

### 文件变更
- **新建**: `src/iqfmp/evaluation/purged_cv.py`
- **修改**: `src/iqfmp/evaluation/walk_forward_validator.py`
- **新建**: `tests/unit/evaluation/test_purged_cv.py`

### 验证
```bash
pytest tests/unit/evaluation/test_purged_cv.py -v
```

---

## Phase 5: P1-2 完整保证金计算引擎 (2h)

### 问题
仅有杠杆检查，无维持保证金计算

### 操作步骤

**Step 5.1: 实现 MarginCalculator**

新建: `src/iqfmp/exchange/margin.py` (~250 行)

```python
"""Margin calculation engine for perpetual futures."""

class MarginCalculator:
    def calculate_initial_margin(self, position_size, entry_price) -> Decimal
    def calculate_maintenance_margin(self, position_size, mark_price) -> Decimal
    def calculate_margin_ratio(self, margin_balance, maintenance_margin) -> Decimal
    def calculate_liquidation_price_long(self, ...) -> Decimal
    def calculate_liquidation_price_short(self, ...) -> Decimal
    def get_margin_status(self, ...) -> MarginStatus
```

**Step 5.2: 集成到 RiskController**

修改: `src/iqfmp/exchange/risk.py`

```python
from iqfmp.exchange.margin import MarginCalculator

class RiskController:
    MARGIN_WARNING_RATIO = Decimal("0.5")
    MARGIN_DANGER_RATIO = Decimal("0.7")

    def check_margin_status(self, position, mark_price, margin_balance):
        return self._margin_calculator.get_margin_status(...)
```

### 文件变更
- **新建**: `src/iqfmp/exchange/margin.py`
- **修改**: `src/iqfmp/exchange/risk.py`
- **新建**: `tests/unit/exchange/test_margin.py`

### 验证
```bash
pytest tests/unit/exchange/test_margin.py -v
```

---

## 关键文件清单

| 优先级 | 文件 | 操作 | 预估行数 |
|--------|------|------|----------|
| P0 | `src/iqfmp/core/qlib_crypto.py` | 删除 Pandas ops | -340 |
| P0 | `src/iqfmp/core/factor_engine.py` | 删除本地实现 | -210 |
| P0 | `pyproject.toml` | 更新覆盖率配置 | +10 |
| P0 | `tests/fixtures/real_data_fixtures.py` | 新建 | +100 |
| P0 | `tests/unit/core/test_*.py` | 新建 | +550 |
| P1 | `src/iqfmp/evaluation/purged_cv.py` | 新建 | +200 |
| P1 | `src/iqfmp/evaluation/walk_forward_validator.py` | 修改 | +30 |
| P1 | `src/iqfmp/exchange/margin.py` | 新建 | +250 |
| P1 | `src/iqfmp/exchange/risk.py` | 修改 | +50 |

---

## 验证清单

### P0 验证

```bash
# 1. Qlib 版本正确
python -c "import qlib; print(qlib.__file__)"
# → vendor/qlib 路径

# 2. 无 Pandas fallback
grep -r "QLIB_PANDAS_OPS" src/
grep -r "_evaluate_expression" src/iqfmp/core/factor_engine.py
# → 应返回空

# 3. 测试覆盖率达标
pytest tests/ --cov=src/iqfmp --cov-fail-under=80
```

### P1 验证

```bash
# 4. Purged CV 工作
pytest tests/unit/evaluation/test_purged_cv.py -v

# 5. 保证金计算工作
pytest tests/unit/exchange/test_margin.py -v
```

---

## 时间线

| Phase | 任务 | 时间 | 依赖 |
|-------|------|------|------|
| 1 | Qlib 版本修复 | 0.5h | 无 |
| 2 | 删除 Pandas Fallback | 1h | Phase 1 |
| 3 | 测试覆盖率提升 | 4h | Phase 1, 2 |
| 4 | Purged CV | 2h | Phase 1 |
| 5 | 保证金引擎 | 2h | 无 |

**总计**: ~9.5 小时
