# IQFMP 系统修复计划 - 完整 Celery + Qlib 集成

> **目标**: 完成 Celery 任务持久化 + Qlib 初始化，使因子挖掘系统真正可用

---

## 一、当前状态诊断

### 1.1 已完成的修复

| # | 问题 | 状态 | 说明 |
|---|------|------|------|
| **C1** | 硬编码数据加载 | ✅ 完成 | symbol/timeframe 参数化 |
| **C3** | 服务启动无统一入口 | ✅ 完成 | scripts/start_dev.sh 已创建 |
| **H1** | 数据加载失败返回零指标 | ✅ 完成 | FactorEvaluationError 异常 |
| **H2** | 向量存储静默失败 | ✅ 完成 | health_check() 方法 |

### 1.2 未完成的关键问题

| # | 问题 | 位置 | 优先级 | 影响 |
|---|------|------|--------|------|
| **C2** | 任务队列不持久化 | `service.py:1262` | **Critical** | 服务重启丢失所有任务 |
| **M2** | Qlib 未正确初始化 | `factor_engine.py` | **Critical** | 因子评估功能降级 |
| **NEW** | API Key 未配置 | 环境变量 | **Critical** | LLM 无法调用 |

---

## 二、修复方案

### Phase 1: Celery 任务集成 (Critical)

**目标**: 将因子挖掘任务从 asyncio 迁移到 Celery

**现有 Celery 配置** (已就绪):
- 应用配置: `src/iqfmp/celery_app/app.py`
- 任务定义: `src/iqfmp/celery_app/tasks.py` (已有 `generate_factor_task`, `evaluate_factor_task`)
- 状态追踪: `src/iqfmp/celery_app/status.py`
- 优先级队列: high/default/low

**需要改造的位置**:

| 文件 | 行号 | 当前 | 改为 |
|------|------|------|------|
| `api/factors/service.py` | 1262 | `asyncio.create_task()` | `mining_task.delay()` |
| `api/backtest/service.py` | 230 | `asyncio.create_task()` | `backtest_task.delay()` |
| `api/data/service.py` | 442 | `asyncio.create_task()` | Celery 任务 |

**修改步骤**:

1. **创建因子挖掘 Celery 任务** (`celery_app/tasks.py`):
```python
@celery_app.task(bind=True, name="iqfmp.tasks.mining_task", queue="default")
def mining_task(self, task_id: str, task_config: dict):
    """因子挖掘任务 - 持久化到 Redis"""
    # 从 _run_mining_task() 提取逻辑
```

2. **修改 FactorService** (`api/factors/service.py:1262`):
```python
# 当前
asyncio.create_task(self._run_mining_task(task_id, task_data))

# 修改为
from iqfmp.celery_app.tasks import mining_task
mining_task.delay(task_id, task_data.dict())
```

3. **更新启动脚本** (`scripts/start_dev.sh`):
```bash
# 添加 Celery Worker 启动
celery -A iqfmp.celery_app.app worker -l info -Q high,default,low &
```

---

### Phase 2: Qlib 初始化确保 (Critical)

**目标**: 确保 Qlib 正确初始化，启用因子评估功能

**当前状态**:
- Qlib 包已安装 (系统 + vendor/qlib)
- 数据目录存在: `~/.qlib/qlib_data`
- 但 `qlib_available: false` (初始化未完成)

**修改步骤**:

1. **更新启动脚本环境变量** (`scripts/start_dev.sh`):
```bash
export PYTHONPATH="src:vendor/qlib:$PYTHONPATH"
export QLIB_AUTO_INIT=true
export QLIB_DATA_DIR="$HOME/.qlib/qlib_data"
```

2. **确保 Qlib 初始化在服务启动时执行** (`api/main.py`):
```python
from iqfmp.core.qlib_init import ensure_qlib_initialized

@app.on_event("startup")
async def startup_event():
    # 确保 Qlib 初始化
    if not ensure_qlib_initialized():
        logger.warning("Qlib initialization failed, factor evaluation may be limited")
```

3. **修复 factor_engine.py 导入顺序**:
- 确保 vendor/qlib 优先于系统 qlib

---

### Phase 3: API Key 配置 (Critical)

**目标**: 配置 LLM API Key 使因子生成可用

**当前状态**:
```json
{
    "api_key": null,
    "llm_configured": true  // 这是 bug - 没有 key 不应该是 true
}
```

**修改步骤**:

1. **修复 ConfigService 状态检查** (`api/config/service.py`):
```python
@property
def llm_configured(self) -> bool:
    # 必须有 API key 才算配置完成
    return bool(self.get_api_key())
```

2. **更新 .env.example 文件**:
```bash
# LLM 配置 (必须)
OPENROUTER_API_KEY=sk-or-v1-xxxxx
LLM_MODEL=anthropic/claude-3.5-sonnet
```

3. **用户需要配置 API Key**:
```bash
curl -X POST http://localhost:8000/api/v1/config/api-keys \
  -H "Content-Type: application/json" \
  -d '{"api_key": "sk-or-v1-xxxxx"}'
```

---

## 三、执行顺序

```
Step 1: Celery 集成 (1.5 hours)
   ├── 创建 mining_task 任务定义
   ├── 修改 service.py 使用 Celery
   └── 更新 start_dev.sh 启动 Worker

Step 2: Qlib 初始化 (30 min)
   ├── 更新 start_dev.sh 环境变量
   ├── 修改 api/main.py 启动事件
   └── 验证 Qlib 可用性

Step 3: API Key 配置修复 (20 min)
   ├── 修复 ConfigService.llm_configured 逻辑
   └── 用户配置 API Key

Step 4: 端到端测试 (40 min)
   ├── 启动完整服务栈
   ├── 创建挖掘任务验证 Celery
   ├── 验证 Qlib 因子评估
   └── 验证 LLM 因子生成
```

---

## 四、关键文件清单

| 文件 | 修改类型 | 优先级 |
|------|---------|--------|
| `src/iqfmp/celery_app/tasks.py` | 修改 | **Critical** |
| `src/iqfmp/api/factors/service.py` | 修改 | **Critical** |
| `scripts/start_dev.sh` | 修改 | **Critical** |
| `src/iqfmp/api/main.py` | 修改 | **Critical** |
| `src/iqfmp/api/config/service.py` | 修改 | High |
| `.env.example` | 更新 | High |

---

## 五、验收标准

1. **Celery Worker 运行**: `celery -A iqfmp.celery_app.app worker` 正常启动
2. **任务持久化**: 服务重启后，任务从 Redis 恢复
3. **Qlib 可用**: `/api/v1/config/status` 返回 `qlib_available: true`
4. **LLM 可用**: `/api/v1/config/status` 返回 `llm_configured: true` (有 API Key 时)
5. **因子评估**: `/api/v1/factors/{id}/evaluate` 使用 Qlib 返回真实指标

---

## 六、前置条件

1. **API Key**: 用户需要提供 OpenRouter API Key
2. **Redis**: 必须运行用于 Celery 任务队列
3. **Qlib 数据**: `~/.qlib/qlib_data` 目录需要有数据
