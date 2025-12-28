# Foundry Testing Patterns

## Project Structure

```
project/
├── src/
│   └── Token.sol
├── test/
│   ├── Token.t.sol           # Unit tests
│   ├── Token.invariant.t.sol # Invariant tests
│   └── mocks/
│       └── MockOracle.sol
├── script/
│   └── DeployToken.s.sol
└── foundry.toml
```

## Basic Test Structure

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {Test, console2} from "forge-std/Test.sol";
import {Token} from "../src/Token.sol";

contract TokenTest is Test {
    Token public token;
    address public owner;
    address public user1;
    address public user2;

    // Events to test
    event Transfer(address indexed from, address indexed to, uint256 value);

    function setUp() public {
        owner = makeAddr("owner");
        user1 = makeAddr("user1");
        user2 = makeAddr("user2");

        vm.startPrank(owner);
        token = new Token("Test", "TST", 1000000e18);
        vm.stopPrank();
    }

    function test_InitialState() public view {
        assertEq(token.name(), "Test");
        assertEq(token.symbol(), "TST");
        assertEq(token.totalSupply(), 1000000e18);
        assertEq(token.balanceOf(owner), 1000000e18);
    }
}
```

---

## Test Naming Convention

```solidity
// Pattern: test_FunctionName_Condition_ExpectedBehavior

function test_Transfer_ValidAmount_UpdatesBalances() public { ... }
function test_Transfer_ZeroAmount_Reverts() public { ... }
function test_Transfer_InsufficientBalance_Reverts() public { ... }

// Fuzz test prefix
function testFuzz_Transfer_AnyValidAmount(uint256 amount) public { ... }

// Invariant test prefix
function invariant_TotalSupplyConstant() public { ... }
```

---

## Cheatcodes Reference

### Account Management

```solidity
// Create labeled address
address alice = makeAddr("alice");

// Fund account with ETH
vm.deal(alice, 100 ether);

// Set msg.sender for next call
vm.prank(alice);
token.transfer(bob, 100);

// Set msg.sender for multiple calls
vm.startPrank(alice);
token.approve(spender, 1000);
token.transfer(bob, 100);
vm.stopPrank();
```

### Time Manipulation

```solidity
// Set block.timestamp
vm.warp(1700000000);

// Skip forward
skip(1 days);

// Set block.number
vm.roll(1000);
```

### Expect Revert

```solidity
// Expect any revert
vm.expectRevert();
token.transfer(address(0), 100);

// Expect specific error
vm.expectRevert(Token.InsufficientBalance.selector);
token.transfer(bob, type(uint256).max);

// Expect error with parameters
vm.expectRevert(
    abi.encodeWithSelector(Token.InsufficientBalance.selector, 0, 100)
);
token.transfer(bob, 100);

// Expect require string
vm.expectRevert("Insufficient balance");
token.transfer(bob, 100);
```

### Expect Events

```solidity
// Expect event emission
vm.expectEmit(true, true, false, true);
emit Transfer(alice, bob, 100);
token.transfer(bob, 100);

// Parameters: check topic1, topic2, topic3, check data
```

### Storage Manipulation

```solidity
// Read storage slot
bytes32 slot = vm.load(address(token), bytes32(uint256(0)));

// Write storage slot
vm.store(address(token), bytes32(uint256(0)), bytes32(uint256(1000)));
```

---

## Fuzz Testing

### Basic Fuzz Test

```solidity
function testFuzz_Transfer(uint256 amount) public {
    // Bound input to valid range
    amount = bound(amount, 0, token.balanceOf(owner));

    vm.prank(owner);
    token.transfer(user1, amount);

    assertEq(token.balanceOf(user1), amount);
}
```

### Multiple Parameters

```solidity
function testFuzz_TransferMultiple(
    uint256 amount1,
    uint256 amount2,
    address recipient
) public {
    // Exclude invalid addresses
    vm.assume(recipient != address(0));
    vm.assume(recipient != address(token));

    // Bound amounts
    uint256 total = token.balanceOf(owner);
    amount1 = bound(amount1, 0, total / 2);
    amount2 = bound(amount2, 0, total / 2);

    vm.startPrank(owner);
    token.transfer(recipient, amount1);
    token.transfer(recipient, amount2);
    vm.stopPrank();

    assertEq(token.balanceOf(recipient), amount1 + amount2);
}
```

### Foundry.toml Fuzz Config

```toml
[fuzz]
runs = 256
max_test_rejects = 65536
seed = "0x1234"
```

---

## Invariant Testing

### Handler Contract

```solidity
contract TokenHandler is Test {
    Token public token;
    address[] public actors;

    constructor(Token _token) {
        token = _token;
        actors.push(makeAddr("actor1"));
        actors.push(makeAddr("actor2"));
    }

    function transfer(uint256 actorSeed, uint256 amount) public {
        address from = actors[actorSeed % actors.length];
        address to = actors[(actorSeed + 1) % actors.length];

        amount = bound(amount, 0, token.balanceOf(from));

        vm.prank(from);
        token.transfer(to, amount);
    }
}
```

### Invariant Test

```solidity
contract TokenInvariantTest is Test {
    Token public token;
    TokenHandler public handler;

    function setUp() public {
        token = new Token("Test", "TST", 1000000e18);
        handler = new TokenHandler(token);

        // Fund actors
        token.transfer(handler.actors(0), 500000e18);
        token.transfer(handler.actors(1), 500000e18);

        // Target only the handler
        targetContract(address(handler));
    }

    function invariant_TotalSupplyConstant() public view {
        assertEq(token.totalSupply(), 1000000e18);
    }

    function invariant_SumOfBalancesEqualsTotalSupply() public view {
        uint256 sum = token.balanceOf(address(this));
        sum += token.balanceOf(handler.actors(0));
        sum += token.balanceOf(handler.actors(1));
        assertEq(sum, token.totalSupply());
    }
}
```

---

## Fork Testing

```solidity
contract ForkTest is Test {
    uint256 mainnetFork;

    function setUp() public {
        mainnetFork = vm.createFork(vm.envString("ETH_RPC_URL"));
        vm.selectFork(mainnetFork);
    }

    function test_ForkBlockNumber() public view {
        assertGt(block.number, 18000000);
    }

    function test_InteractWithMainnet() public {
        IERC20 usdc = IERC20(0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48);
        address whale = 0x47ac0Fb4F2D84898e4D9E7b4DaB3C24507a6D503;

        vm.prank(whale);
        usdc.transfer(address(this), 1000e6);

        assertEq(usdc.balanceOf(address(this)), 1000e6);
    }
}
```

---

## Gas Reporting

### Enable in foundry.toml

```toml
[profile.default]
gas_reports = ["Token", "Vault"]
```

### Gas Snapshot

```bash
# Create snapshot
forge snapshot

# Compare with previous
forge snapshot --diff
```

### Inline Gas Measurement

```solidity
function test_GasMeasurement() public {
    uint256 gasBefore = gasleft();

    token.transfer(user1, 100);

    uint256 gasUsed = gasBefore - gasleft();
    console2.log("Gas used:", gasUsed);

    assertLt(gasUsed, 50000);
}
```

---

## Deployment Scripts

```solidity
// script/DeployToken.s.sol
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {Script, console2} from "forge-std/Script.sol";
import {Token} from "../src/Token.sol";

contract DeployToken is Script {
    function run() public returns (Token) {
        uint256 deployerPrivateKey = vm.envUint("PRIVATE_KEY");

        vm.startBroadcast(deployerPrivateKey);

        Token token = new Token("MyToken", "MTK", 1000000e18);
        console2.log("Token deployed at:", address(token));

        vm.stopBroadcast();

        return token;
    }
}
```

### Run Deployment

```bash
# Dry run
forge script script/DeployToken.s.sol

# Deploy to network
forge script script/DeployToken.s.sol --rpc-url $RPC_URL --broadcast --verify
```

---

## Common Test Patterns

### Reentrancy Test

```solidity
contract ReentrancyAttacker {
    Vault public target;
    uint256 public attackCount;

    constructor(Vault _target) {
        target = _target;
    }

    function attack() external payable {
        target.deposit{value: msg.value}();
        target.withdraw(msg.value);
    }

    receive() external payable {
        if (attackCount < 5 && address(target).balance >= 1 ether) {
            attackCount++;
            target.withdraw(1 ether);
        }
    }
}

function test_ReentrancyProtection() public {
    ReentrancyAttacker attacker = new ReentrancyAttacker(vault);
    vm.deal(address(attacker), 1 ether);

    vm.expectRevert();
    attacker.attack();
}
```

### Access Control Test

```solidity
function test_OnlyOwnerCanMint() public {
    // Non-owner should fail
    vm.prank(user1);
    vm.expectRevert("Ownable: caller is not the owner");
    token.mint(user1, 1000);

    // Owner should succeed
    vm.prank(owner);
    token.mint(user1, 1000);
    assertEq(token.balanceOf(user1), 1000);
}
```

### Time-Based Test

```solidity
function test_VestingCliff() public {
    // Before cliff
    vm.expectRevert("Cliff not reached");
    vesting.claim();

    // After cliff
    skip(365 days);
    vesting.claim();
    assertGt(token.balanceOf(address(this)), 0);
}
```
