# Paimon Backend 计划符合度优化方案

> 基于: PROJECT-AUDIT-REPORT.md (2024-12-17)
> 版本: 2.0.0
> 置信度: 95%+

## 执行摘要

**问题**: 后端代码与 `docs/backend/` 计划文档存在显著差距，核心业务逻辑 (链上交互) 严重缺失
**目标**: 使代码实现完全符合 v2.0.0 计划文档要求
**核心差距**: 链上写入能力为零，无法执行审批/调仓等关键操作

### 符合度现状

| 模块 | 符合度 | 状态 |
|------|--------|------|
| 事件监听框架 | 70% | 🟡 缺少 15+ 事件 |
| 调仓引擎 | 60% | 🟡 缺少执行器 |
| 风控系统 | 50% | 🟡 未对接链上配额 |
| **审批工作流** | **30%** | 🔴 无链上执行 |
| **区块链交互** | **40%** | 🔴 无写入能力 |
| 数据模型 | 75% | 🟡 缺少字段 |

---

## 一、P0 阻断性问题 (必须立即修复)

### 1.1 链上交易能力实现

**问题**: 后端无法执行任何链上写入操作，审批/调仓/结算全部无法执行

**需要修改的文件**:

| 文件 | 修改内容 | 工作量 |
|------|----------|--------|
| `config.py` | 添加 `vip_approver_private_key` 配置 | 0.5h |
| `contracts.py` | 添加 `send_transaction()` 方法 | 2h |
| **新建** `transaction.py` | 交易签名和发送服务 | 3h |

**实现代码**:

```python
# src/app/infrastructure/blockchain/transaction.py (NEW)
from eth_account import Account
from web3 import Web3

class TransactionService:
    """链上交易发送服务"""

    def __init__(self, client: ChainClient, private_key: str):
        self.client = client
        self.account = Account.from_key(private_key)
        self.w3 = Web3()

    async def send_transaction(
        self,
        contract_address: str,
        abi: list[dict],
        function_name: str,
        args: list,
        gas_limit: int = 500000,
    ) -> str:
        """发送链上交易

        Returns:
            交易哈希
        """
        # 1. 编码函数调用
        contract = self.w3.eth.contract(
            address=Web3.to_checksum_address(contract_address),
            abi=abi
        )
        func = contract.get_function_by_name(function_name)
        data = func(*args)._encode_transaction_data()

        # 2. 获取 nonce
        nonce = await self.client.get_transaction_count(self.account.address)

        # 3. 获取 gas price
        gas_price = await self.client.get_gas_price()

        # 4. 构建交易
        tx = {
            'to': Web3.to_checksum_address(contract_address),
            'data': data,
            'gas': gas_limit,
            'gasPrice': gas_price,
            'nonce': nonce,
            'chainId': self.client.chain_id,
        }

        # 5. 签名
        signed = self.account.sign_transaction(tx)

        # 6. 发送
        tx_hash = await self.client.send_raw_transaction(signed.rawTransaction)

        return tx_hash

    async def wait_for_receipt(self, tx_hash: str, timeout: int = 120):
        """等待交易确认"""
        return await self.client.wait_for_transaction_receipt(tx_hash, timeout)
```

---

### 1.2 VIP_APPROVER 配置添加

**修改文件**: `src/app/core/config.py`

```python
# 添加以下配置
vip_approver_private_key: str = Field(
    default="",
    description="Private key for VIP_APPROVER_ROLE (链上审批执行)"
)

# 添加 computed property
@computed_field
@property
def active_approver_key(self) -> str:
    """获取当前网络的审批私钥"""
    if self.blockchain_network == "testnet":
        return self.testnet_hot_wallet_pk
    return self.vip_approver_private_key
```

---

### 1.3 审批执行器实现

**新建文件**: `src/app/services/approval/executor.py`

```python
class ApprovalExecutor:
    """审批决策链上执行器 - 对应 04-approval-workflow.md"""

    def __init__(self, tx_service: TransactionService):
        self.tx_service = tx_service
        self.abi_loader = get_abi_loader()

    async def execute_approval(
        self,
        request_id: int,
        approved: bool,
        custom_settlement_time: int = 0,
        rejection_reason: str = "",
    ) -> str:
        """执行链上审批

        对应计划文档 04-approval-workflow.md:624-672

        Args:
            request_id: 赎回请求ID
            approved: True=批准, False=拒绝
            custom_settlement_time: 自定义结算时间 (秒, 0=使用默认)
            rejection_reason: 拒绝原因

        Returns:
            交易哈希
        """
        abi = self.abi_loader.redemption_manager_abi
        address = settings.active_redemption_manager

        if approved:
            if custom_settlement_time > 0:
                func_name = "approveRedemptionWithDate"
                args = [request_id, custom_settlement_time]
            else:
                func_name = "approveRedemption"
                args = [request_id]
        else:
            func_name = "rejectRedemption"
            args = [request_id, rejection_reason]

        tx_hash = await self.tx_service.send_transaction(
            contract_address=address,
            abi=abi,
            function_name=func_name,
            args=args,
        )

        return tx_hash
```

---

### 1.4 事件类型补全

**修改文件**: `src/app/infrastructure/blockchain/events.py`

**添加缺失的 15+ 事件**:

```python
class EventType(str, Enum):
    # === 现有事件 ===
    DEPOSIT = "Deposit"
    WITHDRAW = "Withdraw"
    REDEMPTION_REQUESTED = "RedemptionRequested"
    REDEMPTION_APPROVED = "RedemptionApproved"
    REDEMPTION_REJECTED = "RedemptionRejected"
    REDEMPTION_SETTLED = "RedemptionSettled"
    REDEMPTION_CANCELLED = "RedemptionCancelled"  # 已禁用
    EMERGENCY_MODE_CHANGED = "EmergencyModeChanged"
    ASSET_ADDED = "AssetAdded"
    ASSET_REMOVED = "AssetRemoved"
    REBALANCE_EXECUTED = "RebalanceExecuted"

    # === PPT.sol 新增事件 (v2.0.0) ===
    SHARES_LOCKED = "SharesLocked"
    SHARES_UNLOCKED = "SharesUnlocked"
    SHARES_BURNED = "SharesBurned"
    REDEMPTION_FEE_ADDED = "RedemptionFeeAdded"
    REDEMPTION_FEE_REDUCED = "RedemptionFeeReduced"
    NAV_UPDATED = "NavUpdated"
    EMERGENCY_QUOTA_REFRESHED = "EmergencyQuotaRefreshed"
    EMERGENCY_QUOTA_RESTORED = "EmergencyQuotaRestored"
    LOCKED_MINT_ASSETS_RESET = "LockedMintAssetsReset"
    STANDARD_QUOTA_RATIO_UPDATED = "StandardQuotaRatioUpdated"
    PENDING_APPROVAL_SHARES_ADDED = "PendingApprovalSharesAdded"
    PENDING_APPROVAL_SHARES_REMOVED = "PendingApprovalSharesRemoved"
    PENDING_APPROVAL_SHARES_CONVERTED = "PendingApprovalSharesConverted"
    ASSET_CONTROLLER_UPDATED = "AssetControllerUpdated"
    REDEMPTION_MANAGER_UPDATED = "RedemptionManagerUpdated"

    # === RedemptionManager.sol 新增事件 (v2.0.0) ===
    VOUCHER_MINTED = "VoucherMinted"
    DAILY_LIABILITY_ADDED = "DailyLiabilityAdded"
    LIABILITY_REMOVED = "LiabilityRemoved"
    SETTLEMENT_WATERFALL_TRIGGERED = "SettlementWaterfallTriggered"
    BASE_REDEMPTION_FEE_UPDATED = "BaseRedemptionFeeUpdated"
    EMERGENCY_PENALTY_FEE_UPDATED = "EmergencyPenaltyFeeUpdated"
    VOUCHER_THRESHOLD_UPDATED = "VoucherThresholdUpdated"
```

---

### 1.5 事件签名修复

**修改文件**: `src/app/infrastructure/blockchain/events.py`

```python
EVENT_SIGNATURES = {
    # 修正 RedemptionRequested 签名 (与合约匹配)
    EventType.REDEMPTION_REQUESTED: (
        "RedemptionRequested(uint256,address,address,uint256,uint256,"
        "uint256,uint8,bool,uint256,uint256)"
    ),

    # 新增签名
    EventType.VOUCHER_MINTED: "VoucherMinted(uint256,uint256,address)",
    EventType.PENDING_APPROVAL_SHARES_ADDED: "PendingApprovalSharesAdded(address,uint256)",
    EventType.PENDING_APPROVAL_SHARES_REMOVED: "PendingApprovalSharesRemoved(address,uint256)",
    EventType.PENDING_APPROVAL_SHARES_CONVERTED: "PendingApprovalSharesConverted(address,uint256)",
    EventType.SETTLEMENT_WATERFALL_TRIGGERED: "SettlementWaterfallTriggered(uint256,uint256,uint256)",
    EventType.DAILY_LIABILITY_ADDED: "DailyLiabilityAdded(uint256,uint256)",
    EventType.NAV_UPDATED: "NavUpdated(uint256,uint256,uint256)",
    # ... 其他签名
}
```

---

## 二、P1 高优先级修复

### 2.1 数据库模型补充字段

**修改文件**: `src/app/models/redemption.py`

```python
class RedemptionRequest(Base, TimestampMixin):
    # ... 现有字段 ...

    # === v2.0.0 新增字段 ===
    voucher_token_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="NFT Voucher Token ID"
    )
    has_voucher: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False, comment="是否已铸造 NFT"
    )
    pending_approval_shares: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(78, 0), nullable=True, comment="待审批份额快照"
    )
    waterfall_triggered: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False, comment="是否触发瀑布清算"
    )
    waterfall_amount: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(78, 0), nullable=True, comment="瀑布清算金额"
    )
```

**新建迁移**: `alembic/versions/xxx_add_redemption_v2_fields.py`

---

### 2.2 NFT Voucher 事件处理器

**新建文件**: `src/app/services/event_handlers/voucher.py`

```python
class VoucherEventHandler(EventHandlerBase):
    """NFT Voucher 事件处理器 - 对应 04-approval-workflow.md 第10章"""

    def __init__(self):
        super().__init__(EventType.VOUCHER_MINTED)

    async def handle(self, event: ParsedEvent) -> None:
        """处理 VoucherMinted 事件"""
        request_id = event.args["requestId"]
        token_id = event.args["tokenId"]
        owner = event.args["owner"]

        async with AsyncSessionLocal() as session:
            repo = RedemptionRepository(session)
            await repo.update_voucher_info(
                request_id=request_id,
                voucher_token_id=token_id,
                has_voucher=True,
            )
            await session.commit()

        logger.info(f"VoucherMinted: request={request_id}, token={token_id}")
```

---

### 2.3 负债处理定时任务

**修改文件**: `src/app/tasks/monitoring_tasks.py`

```python
@celery_app.task(bind=True, base=BaseTask)
async def process_overdue_liability(self):
    """处理逾期负债 - 对应 03-risk-control.md:93-101

    每日 00:05 执行，调用链上 processOverdueLiabilityBatch(30)
    """
    tx_service = get_transaction_service()
    abi = get_abi_loader().redemption_manager_abi

    tx_hash = await tx_service.send_transaction(
        contract_address=settings.active_redemption_manager,
        abi=abi,
        function_name="processOverdueLiabilityBatch",
        args=[30],  # 处理过去30天的逾期
    )

    logger.info(f"processOverdueLiabilityBatch executed: {tx_hash}")
    return tx_hash

# Celery Beat 配置
celerybeat_schedule = {
    'process-overdue-liability': {
        'task': 'app.tasks.monitoring_tasks.process_overdue_liability',
        'schedule': crontab(hour=0, minute=5),
    },
}
```

---

### 2.4 调仓执行器实现

**修改文件**: `src/app/services/rebalance/executor.py`

添加真实链上执行逻辑 (替换 mock):

```python
class RebalanceExecutor:
    """调仓执行器 - 对应 02-rebalance-engine.md"""

    async def execute(self, plan: RebalancePlan) -> RebalanceResult:
        """执行调仓计划 (链上)"""
        results = []

        for step in plan.steps:
            if step.action == RebalanceAction.SWAP:
                tx_hash = await self._execute_swap(step)
            elif step.action == RebalanceAction.LIQUIDATE:
                tx_hash = await self._execute_liquidate(step)

            results.append({
                "step_id": step.step_id,
                "tx_hash": tx_hash,
                "status": "executed",
            })

        return RebalanceResult(
            plan_id=plan.plan_id,
            status=RebalanceStatus.COMPLETED,
            step_results=results,
        )

    async def _execute_swap(self, step: RebalancePlanStep) -> str:
        """执行 swap 操作"""
        # 调用 AssetController.rebalance()
        pass

    async def _execute_liquidate(self, step: RebalancePlanStep) -> str:
        """执行清算操作"""
        # 调用 AssetController.executeWaterfallLiquidation()
        pass
```

---

## 三、P2 中优先级优化

### 3.1 Layer 配置默认值调整

**修改文件**: `src/app/services/rebalance/strategy.py`

```python
DEFAULT_TIER_CONFIGS: dict[LiquidityTier, TierConfig] = {
    LiquidityTier.L1: TierConfig(
        tier=LiquidityTier.L1,
        target_ratio=Decimal("0.10"),   # 10% (原 11.5%)
        min_ratio=Decimal("0.05"),       # 5%
        max_ratio=Decimal("0.20"),       # 20%
        rebalance_threshold=Decimal("0.02"),
    ),
    LiquidityTier.L2: TierConfig(
        tier=LiquidityTier.L2,
        target_ratio=Decimal("0.30"),   # 30% (不变)
        min_ratio=Decimal("0.20"),       # 20%
        max_ratio=Decimal("0.40"),       # 40%
        rebalance_threshold=Decimal("0.03"),
    ),
    LiquidityTier.L3: TierConfig(
        tier=LiquidityTier.L3,
        target_ratio=Decimal("0.60"),   # 60% (原 58.5%)
        min_ratio=Decimal("0.50"),       # 50%
        max_ratio=Decimal("0.70"),       # 70%
        rebalance_threshold=Decimal("0.03"),
    ),
}
```

---

### 3.2 风控对接链上配额

**修改文件**: `src/app/services/risk/monitor.py`

```python
async def calculate_liquidity_risk(self) -> LiquidityRisk:
    """计算流动性风险 - 对接链上实时数据"""
    cm = ContractManager(get_bsc_client())

    # 获取链上配额
    breakdown = await cm.get_liquidity_breakdown(settings.active_vault_address)

    standard_quota = breakdown.get("standard_channel_quota", 0)
    l1_ratio = breakdown["layer1_total"] / total_assets if total_assets > 0 else 0

    return LiquidityRisk(
        l1_ratio=Decimal(str(l1_ratio)),
        standard_channel_quota=Decimal(str(standard_quota)),
        # ...
    )
```

---

### 3.3 审批阈值配置化

**修改文件**: `src/app/core/config.py`

```python
# 审批阈值 (与合约 PPTTypes.sol 保持同步)
standard_approval_amount: int = Field(
    default=50_000 * 10**18,  # 50K USDT
    description="标准通道审批阈值"
)
emergency_approval_amount: int = Field(
    default=30_000 * 10**18,  # 30K USDT
    description="紧急通道审批阈值"
)
approval_quota_ratio: int = Field(
    default=2000,  # 20% = 2000 basis points
    description="配额比例阈值 (basis points)"
)
```

---

## 四、新建文件清单

| 文件路径 | 用途 | 优先级 |
|----------|------|--------|
| `infrastructure/blockchain/transaction.py` | 交易发送服务 | P0 |
| `services/approval/executor.py` | 链上审批执行 | P0 |
| `services/event_handlers/redemption.py` | 赎回事件处理器 | P1 |
| `services/event_handlers/voucher.py` | NFT 事件处理器 | P1 |
| `services/event_handlers/quota.py` | 配额事件处理器 | P1 |
| `tasks/liability_tasks.py` | 负债处理任务 | P1 |
| `alembic/versions/xxx_add_v2_fields.py` | 数据库迁移 | P1 |

---

## 五、修改文件清单

| 文件路径 | 修改内容 | 优先级 |
|----------|----------|--------|
| `core/config.py` | 添加 VIP_APPROVER 配置、审批阈值 | P0 |
| `infrastructure/blockchain/events.py` | 补充事件类型、修复签名 | P0 |
| `infrastructure/blockchain/client.py` | 添加写操作方法 | P0 |
| `models/redemption.py` | 添加 voucher 字段 | P1 |
| `services/rebalance/executor.py` | 实现链上执行 | P1 |
| `services/rebalance/strategy.py` | 调整默认配置 | P2 |
| `services/risk/monitor.py` | 对接链上配额 | P2 |
| `tasks/monitoring_tasks.py` | 添加负债处理任务 | P1 |

---

## 六、实施时间线

```
Phase 1: P0 修复 (1-2 天)
├─ Day 1 AM: 添加 VIP_APPROVER 配置
├─ Day 1 PM: 实现 TransactionService
├─ Day 2 AM: 创建 ApprovalExecutor
└─ Day 2 PM: 补充事件类型和签名

Phase 2: P1 修复 (2-3 天)
├─ Day 3: 数据库迁移 + 模型更新
├─ Day 4: NFT 事件处理器
├─ Day 5 AM: 负债处理任务
└─ Day 5 PM: 调仓执行器

Phase 3: P2 优化 (1-2 天)
├─ Day 6: Layer 配置调整
├─ Day 6: 风控对接链上配额
└─ Day 7: 审批阈值配置化 + 测试
```

**总计: 5-7 天**

---

## 七、验收标准

### P0 验收
- [ ] `TransactionService.send_transaction()` 可成功发送测试网交易
- [ ] `ApprovalExecutor.execute_approval()` 可执行链上审批
- [ ] `EventType` 包含所有 v2.0.0 新增事件
- [ ] 事件签名与合约匹配

### P1 验收
- [ ] `RedemptionRequest` 模型包含 voucher 字段
- [ ] NFT 事件正确更新数据库
- [ ] 负债处理任务按计划执行
- [ ] 调仓执行器可调用链上合约

### P2 验收
- [ ] Layer 默认配置符合计划文档
- [ ] 风控使用链上实时配额
- [ ] 审批阈值可通过配置调整

---

## 八、风险与缓解

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|----------|
| 私钥泄露 | 低 | 极高 | 环境变量 + 密钥轮换 |
| 交易失败 | 中 | 中 | 重试机制 + Gas 估算 |
| 事件遗漏 | 中 | 高 | 检查点 + 增量同步 |
| 签名不匹配 | 中 | 高 | 自动化测试验证 |
