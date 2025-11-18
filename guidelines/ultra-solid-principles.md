# SOLID Principles - Essential Guide

**Ultra Builder Pro 4.0** - Core principles enforced in every code change.

---

## Overview

SOLID principles are **mandatory**. Every code change must demonstrate adherence. Enforced by guarding-quality skill.

---

## S - Single Responsibility Principle

**Definition**: Each function/class does exactly one thing and has only one reason to change.

### Rules
- ✅ Split immediately when a function exceeds 50 lines
- ✅ One class = one reason to change
- ✅ Extract helper functions aggressively

### Example

**Bad** ❌:
```typescript
class User {
  saveToDatabase() { /* ... */ }
  sendWelcomeEmail() { /* ... */ }
  generateReport() { /* ... */ }
}
// Multiple responsibilities: persistence, email, reporting
```

**Good** ✅:
```typescript
class User { /* Only user data */ }
class UserRepository { save(user: User) { /* ... */ } }
class EmailService { sendWelcome(user: User) { /* ... */ } }
class ReportGenerator { generateUserReport(user: User) { /* ... */ } }
```

### Detection Signals
- Function/class exceeds 50 lines
- Multiple unrelated methods in one class
- Class changes for multiple unrelated reasons

---

## O - Open/Closed Principle

**Definition**: Software entities should be open for extension, but closed for modification.

### Rules
- ✅ Use interfaces/protocols for extensibility
- ✅ Strategy pattern over if-else chains
- ✅ Add new features without changing existing code

### Example

**Bad** ❌:
```typescript
class PaymentProcessor {
  process(type: string, amount: number) {
    if (type === 'credit') { /* ... */ }
    else if (type === 'paypal') { /* ... */ }
    else if (type === 'bitcoin') { /* ... */ } // ← Modified existing code
  }
}
```

**Good** ✅:
```typescript
interface PaymentMethod {
  process(amount: number): Promise<void>;
}

class CreditCardPayment implements PaymentMethod {
  async process(amount: number) { /* ... */ }
}

class PayPalPayment implements PaymentMethod {
  async process(amount: number) { /* ... */ }
}

class BitcoinPayment implements PaymentMethod { // ← Extended without modifying
  async process(amount: number) { /* ... */ }
}

class PaymentProcessor {
  constructor(private method: PaymentMethod) {}
  async process(amount: number) {
    await this.method.process(amount);
  }
}
```

### Detection Signals
- Frequent modifications to stable classes
- Long if-else or switch statements
- Fear of breaking existing functionality

---

## L - Liskov Substitution Principle

**Definition**: Subtypes must be substitutable for their base types without altering program correctness.

### Rules
- ✅ Child classes must honor parent contracts
- ✅ No strengthening preconditions in overrides
- ✅ Preserve invariants of the parent class

### Example

**Bad** ❌:
```typescript
class Rectangle {
  setWidth(w: number) { this.width = w; }
  setHeight(h: number) { this.height = h; }
  getArea(): number { return this.width * this.height; }
}

class Square extends Rectangle {
  setWidth(w: number) {
    this.width = w;
    this.height = w; // ← Violates LSP: unexpected side effect
  }
}

// This will fail:
function testRectangle(r: Rectangle) {
  r.setWidth(5);
  r.setHeight(10);
  console.assert(r.getArea() === 50); // ✅ Rectangle, ❌ Square (returns 100)
}
```

**Good** ✅:
```typescript
interface Shape {
  getArea(): number;
}

class Rectangle implements Shape {
  constructor(private width: number, private height: number) {}
  setWidth(w: number) { this.width = w; }
  setHeight(h: number) { this.height = h; }
  getArea(): number { return this.width * this.height; }
}

class Square implements Shape { // ← Not extending Rectangle
  constructor(private size: number) {}
  setSize(s: number) { this.size = s; }
  getArea(): number { return this.size * this.size; }
}
```

### Detection Signals
- Subclass throws exceptions parent doesn't
- Need to check instance type before using

---

## I - Interface Segregation Principle

**Definition**: Keep interfaces focused and minimal. Clients should not depend on methods they don't use.

### Rules
- ✅ No "fat interfaces" with 10+ methods
- ✅ Client-specific interfaces over general-purpose ones
- ✅ Multiple small interfaces over one large interface

### Example

**Bad** ❌:
```typescript
interface Worker {
  work(): void;
  eat(): void;
  sleep(): void;
  getPaid(): void;
  writeCode(): void;
  designUI(): void;
  testSoftware(): void;
}

class Developer implements Worker {
  work() { /* ... */ }
  writeCode() { /* ... */ }
  designUI() { throw new Error('Not applicable'); } // ← Forced to implement
}
```

**Good** ✅:
```typescript
interface Workable { work(): void; }
interface Programmer { writeCode(): void; }
interface Designer { designUI(): void; }

class Developer implements Workable, Programmer {
  work() { /* ... */ }
  writeCode() { /* ... */ }
}

class UIDesigner implements Workable, Designer {
  work() { /* ... */ }
  designUI() { /* ... */ }
}
```

### Detection Signals
- Implementing empty or throwing methods
- Interface has many methods (>5)
- Different clients use different subsets

---

## D - Dependency Inversion Principle

**Definition**: Depend on abstractions, not concrete implementations.

### Rules
- ✅ Inject dependencies through constructors
- ✅ Use interfaces for all external dependencies
- ✅ Configuration over hardcoded values

### Example

**Bad** ❌:
```typescript
class UserService {
  private emailSender = new EmailSender(); // ← Hardcoded dependency

  registerUser(user: User) {
    // ...
    this.emailSender.send('Welcome!'); // ← Depends on concrete class
  }
}
```

**Good** ✅:
```typescript
interface MessageSender {
  send(message: string): Promise<void>;
}

class EmailSender implements MessageSender {
  async send(message: string) { /* ... */ }
}

class UserService {
  constructor(private messageSender: MessageSender) {} // ← Injected abstraction

  async registerUser(user: User) {
    // ...
    await this.messageSender.send('Welcome!'); // ← Depends on interface
  }
}

// Usage
const emailSender = new EmailSender();
const userService = new UserService(emailSender); // ← Easy to swap
```

### Detection Signals
- Direct instantiation with `new` inside classes
- Hardcoded configuration values
- Difficulty testing (can't mock dependencies)

---

## Additional Core Principles

### DRY - Don't Repeat Yourself
- No code duplication >3 lines
- Abstract repeated patterns immediately

### KISS - Keep It Simple
- Cyclomatic complexity <10 per function
- Maximum 3 levels of nesting

### YAGNI - You Aren't Gonna Need It
- Only implement current requirements
- Delete unused code immediately

---

## Philosophy Priority

```
User Value > Technical Showoff
Code Quality > Development Speed
Systems Thinking > Fragmented Execution
Proactive Communication > Silent Work
Test-First > Ship-Then-Test
```

---

## Enforcement

- **guarding-quality** skill: Automatic detection
- **Test coverage**: ≥80% (enforced)
- **Refactoring**: Mandatory when violations found

**Remember**: SOLID is not optional. It's constitutional.
