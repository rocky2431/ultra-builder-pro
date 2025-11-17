---
description: Intelligent code refactoring with semantic analysis (Serena MCP)
argument-hint: <operation> <target>
allowed-tools: Read, Write, Edit, TodoWrite
---

# /ultra-refactor

## Purpose

Perform intelligent, safe code refactoring using semantic analysis.

**Role clarification**: This command **executes** refactorings suggested by `guarding-code-quality` skill (which **detects** violations).

**Required**: This command uses Serena MCP for semantic code intelligence. Ensure Serena MCP is configured.

## Arguments

- `$1`: Operation (rename/extract/inline/move)
- `$2`: Target symbol or file path
- `$ARGUMENTS`: Additional context (new name, destination, etc.)

## Workflow

### 1. Analyze Current Code

**Use Serena to understand code structure:**
- `mcp__serena__get_symbols_overview(file_path)` - Get file structure
- `mcp__serena__find_symbol(symbol_name)` - Locate target symbol
- `mcp__serena__find_referencing_symbols(symbol, file)` - Check all usages

### 2. Assess Refactoring Impact

**Before any changes:**
- Count references across codebase
- Identify dependent modules
- Check for potential breaking changes
- Display impact report to user for confirmation

### 3. Execute Refactoring

**Rename Symbol**: `mcp__serena__rename_symbol(old_name, new_name, file_path)` - Safe rename across entire codebase

**Extract Method**:
1. Identify code block to extract
2. `mcp__serena__insert_after_symbol(name_path, file_path, new_function_body)`
3. Replace original code with call

**Inline Function**:
1. Get function body
2. `mcp__serena__find_referencing_symbols(function_name, file_path)` - Find all call sites
3. Replace calls with inline code

**Move Symbol**:
1. Read symbol from source
2. Insert into destination
3. Update all imports/references

### 4. Validate Changes

- Run tests automatically
- Check no references broken
- Verify code still compiles
- Git diff review

### 5. Project Memory Update

```typescript
mcp__serena__write_memory("refactoring-log", {
  date, operation, from, to, filesAffected, testsPass
})
```

## Usage Examples

```bash
/ultra-refactor rename getUserById fetchUserById
/ultra-refactor extract src/utils/auth.ts:validateToken
/ultra-refactor inline src/helpers/format.ts:formatDate
/ultra-refactor move User src/models/User.ts
```

## Refactoring Catalog

### Basic Refactorings

**Rename** (Most Common): Variables, functions, classes, parameters - Updates all references automatically

**Extract**: Extract method from long function, extract class from large file, extract constant from magic numbers

**Inline**: Remove unnecessary indirection, simplify code structure

**Move**: Reorganize file structure, better module organization

---

### SOLID-Driven Refactorings

#### Single Responsibility Violations → Split Class/Function

**Detection**:
- Function >50 lines
- Class with multiple unrelated methods
- Class changes for multiple reasons

**Refactoring**:
```typescript
// Example: UserService with mixed responsibilities
// Before:
class UserService {
  saveToDatabase() { /* ... */ }
  sendEmail() { /* ... */ }
  generateReport() { /* ... */ }
}

// After: Extract classes by responsibility
class UserRepository { saveToDatabase() { /* ... */ } }
class EmailService { sendEmail() { /* ... */ } }
class ReportGenerator { generateReport() { /* ... */ } }
```

**Serena Workflow**:
1. `find_symbol("UserService", depth=1)` - See all methods
2. `insert_after_symbol("UserService", new_class_body)` - Add UserRepository
3. `rename_symbol("UserService/saveToDatabase")` → Move to UserRepository
4. Repeat for EmailService, ReportGenerator

---

#### Open/Closed Violations → Extract Interface/Strategy

**Detection**:
- Long if-else or switch statements
- Frequent modifications to stable classes
- Type checking before operations

**Refactoring**:
```typescript
// Before: Violates Open/Closed
class PaymentProcessor {
  process(type: string) {
    if (type === 'credit') { /* ... */ }
    else if (type === 'paypal') { /* ... */ }
  }
}

// After: Strategy pattern
interface PaymentMethod { process(): void }
class CreditCardPayment implements PaymentMethod { /* ... */ }
class PayPalPayment implements PaymentMethod { /* ... */ }
class PaymentProcessor {
  constructor(private method: PaymentMethod) {}
  process() { this.method.process() }
}
```

**Serena Workflow**:
1. `insert_before_symbol("PaymentProcessor", interface_definition)`
2. `insert_after_symbol("PaymentProcessor", new_implementation_classes)`
3. `replace_symbol_body("PaymentProcessor", new_constructor_body)`

---

#### Dependency Inversion Violations → Inject Dependencies

**Detection**:
- Direct instantiation with `new` inside classes
- Hardcoded configuration values
- Difficult to test (can't mock dependencies)

**Refactoring**:
```typescript
// Before: Hardcoded dependency
class UserService {
  private emailSender = new EmailSender(); // ← Violation
  registerUser(user: User) {
    this.emailSender.send('Welcome!');
  }
}

// After: Injected abstraction
interface MessageSender { send(msg: string): Promise<void> }
class UserService {
  constructor(private messageSender: MessageSender) {} // ← Injected
  registerUser(user: User) {
    this.messageSender.send('Welcome!');
  }
}
```

**Serena Workflow**:
1. `find_symbol("UserService/constructor")` - Check current constructor
2. `insert_before_symbol("UserService", interface_definition)`
3. `replace_symbol_body("UserService/constructor", new_constructor)`
4. `find_referencing_symbols("UserService")` - Update all instantiation sites

---

### Code Smell Refactorings

#### Long Parameter List → Parameter Object

**Detection**: Function with >5 parameters

**Refactoring**:
```typescript
// Before:
function createUser(name: string, email: string, age: number, address: string, phone: string) { /* ... */ }

// After:
interface UserParams { name: string; email: string; age: number; address: string; phone: string }
function createUser(params: UserParams) { /* ... */ }
```

**Serena Workflow**:
1. `find_symbol("createUser", include_body=true)` - Get full signature
2. `insert_before_symbol("createUser", interface_definition)`
3. `replace_symbol_body("createUser", new_function_body)`
4. `find_referencing_symbols("createUser")` - Update all call sites

---

#### Duplicate Code → Extract Shared Function

**Detection**: Code duplication >3 lines

**Refactoring**:
```typescript
// Before: Duplication in multiple places
function handleUserLogin() {
  const user = await db.query('SELECT * FROM users WHERE id = ?', [userId]);
  if (!user) throw new Error('User not found');
  return user;
}
function handleUserUpdate() {
  const user = await db.query('SELECT * FROM users WHERE id = ?', [userId]);
  if (!user) throw new Error('User not found');
  return user;
}

// After: Extract common logic
function getUserById(userId: string) {
  const user = await db.query('SELECT * FROM users WHERE id = ?', [userId]);
  if (!user) throw new Error('User not found');
  return user;
}
function handleUserLogin() { return getUserById(userId); }
function handleUserUpdate() { return getUserById(userId); }
```

**Serena Workflow**:
1. `search_for_pattern("db.query.*users.*id")` - Find all duplicates
2. `insert_before_symbol("handleUserLogin", new_shared_function)`
3. `replace_symbol_body("handleUserLogin", simplified_body)`
4. Repeat for other duplicates

---

#### Magic Numbers → Named Constants

**Detection**: Hardcoded numbers without context

**Refactoring**:
```typescript
// Before:
if (user.age > 18) { /* ... */ }
if (order.total > 1000) { /* ... */ }

// After:
const MINIMUM_AGE = 18;
const FREE_SHIPPING_THRESHOLD = 1000;
if (user.age > MINIMUM_AGE) { /* ... */ }
if (order.total > FREE_SHIPPING_THRESHOLD) { /* ... */ }
```

**Serena Workflow**:
1. `search_for_pattern("\\d{2,}")` - Find all magic numbers
2. `insert_before_symbol(first_function, constants_block)`
3. `replace_symbol_body` for each function using magic numbers

---

### Auto-Detection Integration

**Code Quality Guardian Integration**: When guarding-code-quality detects violations, it can suggest specific refactorings from this catalog.

**Example Flow**:
```
guarding-code-quality detects: "Function exceeds 50 lines, violates SRP"
                         ↓
Suggests: "/ultra-refactor extract UserService/processPayment"
                         ↓
User runs: /ultra-refactor extract UserService/processPayment
                         ↓
ultra-refactor executes: Extract Method pattern from catalog
```

## Safety Checks

Before executing refactoring:
- ✅ All tests passing
- ✅ No uncommitted changes (or ask user)
- ✅ Impact analysis completed
- ✅ User confirmation for large changes (>10 files)
- ✅ Backup created automatically

## Integration

- **Skills**: Code Quality Guardian (validates quality after refactoring)
- **Tools**: Serena MCP (required for semantic operations)
- **Next**: Run `/ultra-test` to verify changes

## Success Criteria

- ✅ All references updated correctly
- ✅ Tests still pass
- ✅ Code quality maintained or improved
- ✅ No breaking changes introduced
- ✅ Refactoring logged to project memory

## Output Format

**Standard output structure**: See `@config/ultra-command-output-template.md` for the complete 6-section format.

**Command icon**: ♻️

**Example output**: See template for ultra-refactor specific example.
