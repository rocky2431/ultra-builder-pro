# Smart Contract Best Practices

## Solidity Conventions

### Version & License

```solidity
// SPDX-License-Identifier: MIT
pragma solidity 0.8.20;
```

- Use fixed pragma version for deployments
- Include SPDX license identifier

### Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| Contract | PascalCase | `TokenVesting` |
| Interface | I + PascalCase | `ITokenVesting` |
| Library | PascalCase | `SafeMath` |
| Function | camelCase | `transferFrom` |
| Variable | camelCase | `totalSupply` |
| Constant | UPPER_SNAKE | `MAX_SUPPLY` |
| Immutable | UPPER_SNAKE | `WETH_ADDRESS` |
| Private/Internal | _prefixed | `_balances` |
| Event | PascalCase | `Transfer` |
| Error | PascalCase | `InsufficientBalance` |

### Contract Structure Order

```solidity
contract Example {
    // 1. Type declarations
    using SafeMath for uint256;

    // 2. State variables
    uint256 public constant MAX_SUPPLY = 1000000e18;
    uint256 public immutable DEPLOY_TIME;
    uint256 public totalSupply;
    mapping(address => uint256) private _balances;

    // 3. Events
    event Transfer(address indexed from, address indexed to, uint256 value);

    // 4. Errors
    error InsufficientBalance(uint256 available, uint256 required);

    // 5. Modifiers
    modifier onlyOwner() { ... }

    // 6. Constructor
    constructor() { ... }

    // 7. Receive/Fallback
    receive() external payable { ... }

    // 8. External functions
    // 9. Public functions
    // 10. Internal functions
    // 11. Private functions
    // 12. View/Pure functions (each visibility group)
}
```

### Function Visibility Order

```
external → public → internal → private
```

Within each visibility:
```
state-changing → view → pure
```

---

## Security Patterns

### Checks-Effects-Interactions (CEI)

```solidity
function withdraw(uint256 amount) external nonReentrant {
    // 1. CHECKS
    require(balances[msg.sender] >= amount, "Insufficient");

    // 2. EFFECTS
    balances[msg.sender] -= amount;

    // 3. INTERACTIONS
    (bool success,) = msg.sender.call{value: amount}("");
    require(success, "Transfer failed");
}
```

### Pull Over Push

```solidity
// AVOID: Push pattern
function distribute(address[] calldata recipients) external {
    for (uint i = 0; i < recipients.length; i++) {
        payable(recipients[i]).transfer(amount);  // Can fail
    }
}

// PREFER: Pull pattern
mapping(address => uint256) public pendingWithdrawals;

function withdraw() external {
    uint256 amount = pendingWithdrawals[msg.sender];
    pendingWithdrawals[msg.sender] = 0;
    payable(msg.sender).transfer(amount);
}
```

### Access Control

```solidity
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";

// Simple ownership
contract Token is Ownable {
    function mint(address to, uint256 amount) external onlyOwner { ... }
}

// Role-based
contract Protocol is AccessControl {
    bytes32 public constant MINTER_ROLE = keccak256("MINTER_ROLE");
    bytes32 public constant PAUSER_ROLE = keccak256("PAUSER_ROLE");

    function mint(address to, uint256 amount) external onlyRole(MINTER_ROLE) { ... }
}
```

### Reentrancy Guard

```solidity
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

contract Vault is ReentrancyGuard {
    function withdraw(uint256 amount) external nonReentrant {
        // Safe from reentrancy
    }
}
```

### Pausable

```solidity
import "@openzeppelin/contracts/security/Pausable.sol";

contract Token is Pausable {
    function transfer(address to, uint256 amount) external whenNotPaused {
        // Cannot execute when paused
    }

    function pause() external onlyOwner {
        _pause();
    }
}
```

---

## Input Validation

### Function Parameters

```solidity
function transfer(address to, uint256 amount) external {
    require(to != address(0), "Invalid recipient");
    require(amount > 0, "Amount must be positive");
    require(amount <= balances[msg.sender], "Insufficient balance");
    // ...
}
```

### Array Bounds

```solidity
function batchTransfer(address[] calldata recipients, uint256[] calldata amounts) external {
    require(recipients.length == amounts.length, "Length mismatch");
    require(recipients.length <= 100, "Batch too large");
    // ...
}
```

### Custom Errors (Gas Efficient)

```solidity
error InvalidRecipient();
error InsufficientBalance(uint256 available, uint256 required);

function transfer(address to, uint256 amount) external {
    if (to == address(0)) revert InvalidRecipient();
    if (balances[msg.sender] < amount) {
        revert InsufficientBalance(balances[msg.sender], amount);
    }
}
```

---

## Upgradeable Contracts

### Storage Layout

```solidity
// V1
contract TokenV1 {
    uint256 public totalSupply;
    mapping(address => uint256) public balances;
    // Storage slot 0: totalSupply
    // Storage slot 1: balances mapping
}

// V2 - CORRECT: Append only
contract TokenV2 {
    uint256 public totalSupply;
    mapping(address => uint256) public balances;
    uint256 public newVariable;  // Appended at slot 2
}

// V2 - WRONG: Changes existing layout
contract TokenV2Wrong {
    uint256 public newVariable;  // Overwrites totalSupply!
    uint256 public totalSupply;
    mapping(address => uint256) public balances;
}
```

### Initialization

```solidity
import "@openzeppelin/contracts-upgradeable/proxy/utils/Initializable.sol";

contract TokenUpgradeable is Initializable {
    uint256 public totalSupply;

    /// @custom:oz-upgrades-unsafe-allow constructor
    constructor() {
        _disableInitializers();  // Prevent implementation initialization
    }

    function initialize(uint256 _totalSupply) external initializer {
        totalSupply = _totalSupply;
    }
}
```

---

## Events

### Event Design

```solidity
// Include indexed parameters for filtering
event Transfer(
    address indexed from,
    address indexed to,
    uint256 value
);

// Emit for all state changes
function transfer(address to, uint256 amount) external {
    balances[msg.sender] -= amount;
    balances[to] += amount;
    emit Transfer(msg.sender, to, amount);  // Always emit
}
```

### Event Naming

- Use past tense or noun for completed actions: `Transferred`, `Deposit`
- Match function name when applicable

---

## Documentation

### NatSpec

```solidity
/// @title Token Vesting Contract
/// @author Protocol Team
/// @notice Handles token vesting schedules for team and investors
/// @dev Implements linear vesting with cliff period
contract TokenVesting {
    /// @notice Creates a new vesting schedule
    /// @dev Reverts if schedule already exists for beneficiary
    /// @param beneficiary Address that will receive vested tokens
    /// @param amount Total tokens to vest
    /// @param cliffDuration Cliff period in seconds
    /// @param vestingDuration Total vesting period in seconds
    /// @return scheduleId The ID of the created schedule
    function createSchedule(
        address beneficiary,
        uint256 amount,
        uint256 cliffDuration,
        uint256 vestingDuration
    ) external returns (uint256 scheduleId) {
        // ...
    }
}
```

---

## Testing Requirements

### Minimum Coverage

| Category | Target |
|----------|--------|
| Line coverage | ≥ 80% |
| Branch coverage | ≥ 75% |
| Critical paths | 100% |

### Required Test Cases

1. Happy path for all functions
2. Access control violations
3. Edge cases (zero values, max values)
4. Revert conditions
5. Event emissions
6. Fuzz tests for numeric inputs
7. Invariant tests for protocol properties

---

## Deployment Checklist

```
[ ] All tests passing
[ ] Coverage meets thresholds
[ ] Slither/Mythril clean
[ ] Constructor arguments verified
[ ] Ownership transferred to multisig
[ ] Timelock configured
[ ] Contract verified on explorer
[ ] Emergency pause tested
[ ] Upgrade path tested (if applicable)
```
