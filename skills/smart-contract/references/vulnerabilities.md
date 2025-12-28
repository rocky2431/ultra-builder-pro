# Smart Contract Vulnerability Patterns

## Critical Severity

### 1. Reentrancy

**Pattern**: External call before state update allows recursive calls.

```solidity
// VULNERABLE
function withdraw(uint256 amount) external {
    require(balances[msg.sender] >= amount);
    (bool success,) = msg.sender.call{value: amount}("");  // External call
    require(success);
    balances[msg.sender] -= amount;  // State update AFTER call
}

// SECURE
function withdraw(uint256 amount) external nonReentrant {
    require(balances[msg.sender] >= amount);
    balances[msg.sender] -= amount;  // State update BEFORE call
    (bool success,) = msg.sender.call{value: amount}("");
    require(success);
}
```

**Detection**: Look for external calls (`call`, `transfer`, `send`, external contract calls) before state updates.

**Variants**:
- Cross-function reentrancy
- Cross-contract reentrancy
- Read-only reentrancy (view functions reading stale state)

---

### 2. Access Control Missing/Broken

**Pattern**: Critical functions lack proper access restrictions.

```solidity
// VULNERABLE
function mint(address to, uint256 amount) external {
    _mint(to, amount);  // Anyone can mint
}

// SECURE
function mint(address to, uint256 amount) external onlyOwner {
    _mint(to, amount);
}
```

**Detection**: Check all state-changing functions for access modifiers.

**Common Issues**:
- Missing `onlyOwner` / role checks
- `tx.origin` instead of `msg.sender`
- Uninitialized ownership
- Single point of failure (no multisig)

---

### 3. Flash Loan Attacks

**Pattern**: Price/state manipulation within single transaction.

```solidity
// VULNERABLE - Uses spot price
function getPrice() public view returns (uint256) {
    return tokenA.balanceOf(pool) / tokenB.balanceOf(pool);
}

// SECURE - Uses TWAP
function getPrice() public view returns (uint256) {
    return oracle.consult(address(tokenA), 1e18);  // Time-weighted
}
```

**Detection**: Look for on-chain price calculations, governance voting without time locks.

---

## High Severity

### 4. Integer Overflow/Underflow

**Pattern**: Arithmetic exceeds type bounds (pre-Solidity 0.8.0).

```solidity
// VULNERABLE (Solidity < 0.8.0)
uint8 balance = 255;
balance += 1;  // Overflows to 0

// SECURE
uint8 balance = 255;
balance = balance + 1;  // Reverts in 0.8.0+
// Or use SafeMath for older versions
```

**Detection**: Check Solidity version, look for `unchecked` blocks.

---

### 5. Improper Input Validation

**Pattern**: Missing checks on user-supplied data.

```solidity
// VULNERABLE
function transfer(address to, uint256 amount) external {
    balances[msg.sender] -= amount;
    balances[to] += amount;
}

// SECURE
function transfer(address to, uint256 amount) external {
    require(to != address(0), "Invalid recipient");
    require(amount > 0, "Invalid amount");
    require(balances[msg.sender] >= amount, "Insufficient balance");
    balances[msg.sender] -= amount;
    balances[to] += amount;
}
```

---

### 6. Signature Replay

**Pattern**: Signatures can be reused across transactions/chains.

```solidity
// VULNERABLE
function executeWithSig(bytes calldata sig, address to, uint256 amount) external {
    bytes32 hash = keccak256(abi.encodePacked(to, amount));
    address signer = ECDSA.recover(hash, sig);
    require(signer == owner);
    _transfer(to, amount);
}

// SECURE
function executeWithSig(bytes calldata sig, address to, uint256 amount, uint256 nonce) external {
    require(nonces[owner] == nonce, "Invalid nonce");
    bytes32 hash = keccak256(abi.encodePacked(
        "\x19\x01",
        DOMAIN_SEPARATOR,
        keccak256(abi.encode(to, amount, nonce))
    ));
    address signer = ECDSA.recover(hash, sig);
    require(signer == owner);
    nonces[owner]++;
    _transfer(to, amount);
}
```

**Detection**: Check for nonce, deadline, and domain separator in signed messages.

---

## Medium Severity

### 7. Front-running / MEV

**Pattern**: Transactions can be observed and exploited before confirmation.

```solidity
// VULNERABLE - Sandwich attackable
function swap(uint256 amountIn, uint256 minOut) external {
    uint256 amountOut = getAmountOut(amountIn);
    require(amountOut >= minOut);
    // ...
}

// MITIGATION
function swap(uint256 amountIn, uint256 minOut, uint256 deadline) external {
    require(block.timestamp <= deadline, "Expired");
    // Use commit-reveal or private mempool
}
```

---

### 8. Denial of Service

**Pattern**: Contract can be made unusable.

```solidity
// VULNERABLE - Unbounded loop
function distributeRewards(address[] calldata users) external {
    for (uint i = 0; i < users.length; i++) {  // May exceed gas limit
        _sendReward(users[i]);
    }
}

// SECURE - Bounded + pull pattern
function claimReward() external {
    uint256 reward = pendingRewards[msg.sender];
    pendingRewards[msg.sender] = 0;
    _sendReward(msg.sender, reward);
}
```

**Variants**:
- Block gas limit (unbounded loops)
- External call failures blocking execution
- Self-destruct griefing

---

### 9. Centralization Risks

**Pattern**: Single admin can drain/pause/destroy protocol.

**Checklist**:
- [ ] Owner can pause withdrawals indefinitely?
- [ ] Owner can change critical parameters without timelock?
- [ ] Owner can upgrade to malicious implementation?
- [ ] Owner keys stored in hot wallet?

**Mitigations**:
- Multisig ownership
- Timelocks on critical functions
- Governance for parameter changes
- Immutable core logic

---

## Low Severity

### 10. Floating Pragma

```solidity
// AVOID
pragma solidity ^0.8.0;

// PREFER
pragma solidity 0.8.20;
```

### 11. Missing Events

State changes should emit events for off-chain tracking.

### 12. Unused Variables/Functions

Dead code increases attack surface and gas costs.

### 13. Incorrect Visibility

Functions should use most restrictive visibility possible.

---

## Informational

### Gas Optimizations

See `gas-optimization.md` for detailed patterns.

### Code Quality

- Consistent naming conventions
- NatSpec documentation
- Test coverage > 80%
- Formal verification for critical logic

---

## Audit Checklist

```
[ ] Reentrancy (all external calls)
[ ] Access control (all state-changing functions)
[ ] Integer handling (unchecked blocks, type casts)
[ ] Input validation (all external/public functions)
[ ] Flash loan resistance (price oracles, governance)
[ ] Signature security (nonce, deadline, domain)
[ ] Front-running mitigation (commit-reveal, slippage)
[ ] DoS resistance (bounded loops, pull pattern)
[ ] Centralization assessment (owner powers)
[ ] Upgrade safety (storage layout, initialization)
```
