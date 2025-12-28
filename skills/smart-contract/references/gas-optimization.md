# Gas Optimization Guide

## Priority Order

Apply optimizations in this order (highest impact first):

1. **Architecture** - Storage design, data structures
2. **Storage** - Packing, access patterns
3. **Calldata** - Parameter optimization
4. **Computation** - Algorithm efficiency
5. **Assembly** - Last resort for critical paths

---

## Storage Optimization

### Variable Packing

```solidity
// INEFFICIENT: 3 storage slots (96 bytes used, 96 bytes allocated)
contract Inefficient {
    uint256 a;      // Slot 0 (32 bytes)
    uint8 b;        // Slot 1 (1 byte, 31 wasted)
    uint256 c;      // Slot 2 (32 bytes)
    uint8 d;        // Slot 3 (1 byte, 31 wasted)
}

// OPTIMIZED: 2 storage slots (66 bytes used, 64 bytes allocated)
contract Optimized {
    uint256 a;      // Slot 0 (32 bytes)
    uint256 c;      // Slot 1 (32 bytes)
    uint8 b;        // Slot 2 (1 byte)
    uint8 d;        // Slot 2 (1 byte, packed)
}
```

**Packing Rules**:
- Variables < 32 bytes can share a slot
- Order variables by size (largest first, then small together)
- Structs follow same packing rules

### Struct Packing

```solidity
// INEFFICIENT: 3 slots
struct UserBad {
    uint8 age;          // Slot 0
    uint256 balance;    // Slot 1
    uint8 level;        // Slot 2
    address wallet;     // Slot 3
}

// OPTIMIZED: 2 slots
struct UserGood {
    uint256 balance;    // Slot 0 (32 bytes)
    address wallet;     // Slot 1 (20 bytes)
    uint8 age;          // Slot 1 (1 byte, packed)
    uint8 level;        // Slot 1 (1 byte, packed)
}
```

### Cold vs Warm Storage

```solidity
// First access (cold): 2100 gas
// Subsequent access (warm): 100 gas

function inefficient(uint256 amount) external {
    require(balances[msg.sender] >= amount);  // Cold read: 2100
    balances[msg.sender] -= amount;           // Cold write + warm read
    require(balances[msg.sender] >= 0);       // Warm read: 100
}

function optimized(uint256 amount) external {
    uint256 balance = balances[msg.sender];   // Cold read: 2100
    require(balance >= amount);               // Memory: 3
    balances[msg.sender] = balance - amount;  // Write only
}
```

### Use Constants and Immutables

```solidity
// STORAGE: 2100 gas per read
uint256 public maxSupply = 1000000e18;

// CONSTANT: Inlined at compile time (0 gas)
uint256 public constant MAX_SUPPLY = 1000000e18;

// IMMUTABLE: Set once in constructor, no storage read
uint256 public immutable DEPLOY_TIME;

constructor() {
    DEPLOY_TIME = block.timestamp;
}
```

---

## Calldata vs Memory

```solidity
// EXPENSIVE: Copies array to memory
function sumMemory(uint256[] memory data) external pure returns (uint256) {
    uint256 total;
    for (uint i = 0; i < data.length; i++) {
        total += data[i];
    }
    return total;
}

// CHEAP: Reads directly from calldata
function sumCalldata(uint256[] calldata data) external pure returns (uint256) {
    uint256 total;
    for (uint i = 0; i < data.length; i++) {
        total += data[i];
    }
    return total;
}
```

**Rules**:
- Use `calldata` for external function parameters (read-only)
- Use `memory` only when modification needed
- Never use `storage` for temporary variables

---

## Loop Optimization

### Cache Array Length

```solidity
// INEFFICIENT: Length read every iteration
for (uint i = 0; i < array.length; i++) { ... }

// OPTIMIZED: Length cached
uint256 length = array.length;
for (uint i = 0; i < length; i++) { ... }
```

### Unchecked Increment

```solidity
// INEFFICIENT: Overflow check on every increment
for (uint i = 0; i < length; i++) { ... }

// OPTIMIZED: Skip overflow check (safe because length is bounded)
for (uint i = 0; i < length;) {
    // ...
    unchecked { ++i; }
}
```

### Pre-increment vs Post-increment

```solidity
// Slightly cheaper
++i;  // Returns new value

// Slightly more expensive
i++;  // Returns old value (requires temp storage)
```

---

## Function Optimization

### Custom Errors vs Require Strings

```solidity
// EXPENSIVE: String stored in bytecode
require(balance >= amount, "Insufficient balance");

// CHEAP: 4-byte selector only
error InsufficientBalance();
if (balance < amount) revert InsufficientBalance();
```

**Savings**: ~50 gas per revert + deployment size reduction

### Short-Circuit Evaluation

```solidity
// Evaluates left-to-right, stops on first false
require(amount > 0 && balances[msg.sender] >= amount);
// If amount == 0, skips storage read
```

### Function Visibility

```solidity
// External: Uses calldata (cheaper for arrays)
function processExternal(uint256[] calldata data) external { ... }

// Public: Copies to memory (more expensive)
function processPublic(uint256[] memory data) public { ... }
```

**Rule**: Use `external` when function won't be called internally.

---

## Bit Manipulation

### Packing Multiple Values

```solidity
// Store 4 uint64 values in one uint256
function pack(uint64 a, uint64 b, uint64 c, uint64 d) pure returns (uint256) {
    return uint256(a) | (uint256(b) << 64) | (uint256(c) << 128) | (uint256(d) << 192);
}

function unpack(uint256 packed) pure returns (uint64 a, uint64 b, uint64 c, uint64 d) {
    a = uint64(packed);
    b = uint64(packed >> 64);
    c = uint64(packed >> 128);
    d = uint64(packed >> 192);
}
```

### Boolean Flags

```solidity
// EXPENSIVE: Each bool is 1 storage slot
bool public isActive;
bool public isPaused;
bool public isLocked;

// CHEAP: Pack into single uint8
uint8 public flags;
uint8 constant FLAG_ACTIVE = 1;  // 0001
uint8 constant FLAG_PAUSED = 2;  // 0010
uint8 constant FLAG_LOCKED = 4;  // 0100

function isActive() view returns (bool) {
    return flags & FLAG_ACTIVE != 0;
}
```

---

## Assembly (Use Sparingly)

### Efficient Transfers

```solidity
// Standard: ~2300 gas overhead
payable(to).transfer(amount);

// Assembly: More efficient
assembly {
    let success := call(gas(), to, amount, 0, 0, 0, 0)
    if iszero(success) { revert(0, 0) }
}
```

### Memory Operations

```solidity
// Get free memory pointer
assembly {
    let ptr := mload(0x40)
}

// Efficient keccak256
function efficientHash(uint256 a, uint256 b) pure returns (bytes32 result) {
    assembly {
        mstore(0x00, a)
        mstore(0x20, b)
        result := keccak256(0x00, 0x40)
    }
}
```

---

## Gas Cost Reference

| Operation | Gas Cost |
|-----------|----------|
| SSTORE (zero → non-zero) | 20,000 |
| SSTORE (non-zero → non-zero) | 5,000 |
| SSTORE (non-zero → zero) | Refund 15,000 |
| SLOAD (cold) | 2,100 |
| SLOAD (warm) | 100 |
| CALL | 100 + memory expansion |
| CALL with value | +9,000 |
| CREATE | 32,000 |
| CREATE2 | 32,000 |
| KECCAK256 | 30 + 6 per word |
| LOG0-4 | 375 + 375 per topic + 8 per byte |

---

## Optimization Checklist

```
[ ] Storage variables packed efficiently
[ ] Constants/immutables used where possible
[ ] Calldata used for external function parameters
[ ] Array lengths cached in loops
[ ] Unchecked blocks for safe arithmetic
[ ] Custom errors instead of require strings
[ ] External visibility where applicable
[ ] Boolean flags packed into single variable
[ ] Minimal storage reads (cache to memory)
[ ] Short-circuit evaluation leveraged
```
