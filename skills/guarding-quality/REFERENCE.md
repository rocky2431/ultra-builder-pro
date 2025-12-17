# Quality Guardian - Complete Reference

**Ultra Builder Pro 4.1** - Comprehensive quality enforcement reference for code quality, testing, and UI design.

---

## Part 1: SOLID Principles

### Overview

SOLID principles are **mandatory**. Every code change must demonstrate adherence. Enforced by quality-guardian skill.

---

### S - Single Responsibility Principle

**Definition**: Each function/class does exactly one thing and has only one reason to change.

#### Rules
- ✅ Split immediately when a function exceeds 50 lines
- ✅ One class = one reason to change
- ✅ Extract helper functions aggressively

#### Example

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

#### Detection Signals
- Function/class exceeds 50 lines
- Multiple unrelated methods in one class
- Class changes for multiple unrelated reasons

---

### O - Open/Closed Principle

**Definition**: Software entities should be open for extension, but closed for modification.

#### Rules
- ✅ Use interfaces/protocols for extensibility
- ✅ Strategy pattern over if-else chains
- ✅ Add new features without changing existing code

#### Example

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

#### Detection Signals
- Frequent modifications to stable classes
- Long if-else or switch statements
- Fear of breaking existing functionality

---

### L - Liskov Substitution Principle

**Definition**: Subtypes must be substitutable for their base types without altering program correctness.

#### Rules
- ✅ Child classes must honor parent contracts
- ✅ No strengthening preconditions in overrides
- ✅ Preserve invariants of the parent class

#### Example

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

#### Detection Signals
- Subclass throws exceptions parent doesn't
- Need to check instance type before using

---

### I - Interface Segregation Principle

**Definition**: Keep interfaces focused and minimal. Clients should not depend on methods they don't use.

#### Rules
- ✅ No "fat interfaces" with 10+ methods
- ✅ Client-specific interfaces over general-purpose ones
- ✅ Multiple small interfaces over one large interface

#### Example

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

#### Detection Signals
- Implementing empty or throwing methods
- Interface has many methods (>5)
- Different clients use different subsets

---

### D - Dependency Inversion Principle

**Definition**: Depend on abstractions, not concrete implementations.

#### Rules
- ✅ Inject dependencies through constructors
- ✅ Use interfaces for all external dependencies
- ✅ Configuration over hardcoded values

#### Example

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

#### Detection Signals
- Direct instantiation with `new` inside classes
- Hardcoded configuration values
- Difficulty testing (can't mock dependencies)

---

### Additional Core Principles

#### DRY - Don't Repeat Yourself
- No code duplication >3 lines
- Abstract repeated patterns immediately

#### KISS - Keep It Simple
- Cyclomatic complexity <10 per function
- Maximum 3 levels of nesting

#### YAGNI - You Aren't Gonna Need It
- Only implement current requirements
- Delete unused code immediately

---

### Philosophy Priority

```
User Value > Technical Showoff
Code Quality > Development Speed
Systems Thinking > Fragmented Execution
Proactive Communication > Silent Work
Test-First > Ship-Then-Test
```

---

## Part 2: Quality Standards

### Code Quality Baseline

#### Core Requirements

- ✅ **Follow SOLID/DRY/KISS/YAGNI** - See Part 1 above
- ✅ **All public functions must have clear comments** - JSDoc format with @param, @returns, @example
- ✅ **Unit test coverage ≥80%** - Enforced by quality-guardian skill

#### Code Smells Detection

Immediately fix when detected:
- ❌ Functions >50 lines → Split
- ❌ Nesting depth >3 levels → Refactor
- ❌ Magic numbers → Extract to named constants
- ❌ Commented-out code → Delete (use git history)
- ❌ Duplicate code >3 lines → Extract to shared function
- ❌ God classes (>500 lines) → Split by responsibility
- ❌ Long parameter lists (>5 params) → Use object parameters
- ❌ Cryptic variable names → Use descriptive names

#### Code Documentation Example

```typescript
/**
 * Brief description of what function does.
 * @param paramName - Description
 * @returns Description of return value
 * @example
 * functionName(arg)  // Brief usage example
 */
```

---

### Frontend Quality Baseline

**Mandatory for frontend projects only** (React, Vue, Angular, etc.)

#### Recommended Component Libraries

**Primary (use first)**:
- **shadcn/ui** - Beautiful, accessible, copy-paste components
- **Galaxy UI** - Modern, animated component collection
- **React Bits** - Unique, creative UI components

**Alternatives**:
- Magic UI, Aceternity UI (advanced animations)
- Radix UI (headless, accessible primitives)
- Framer Motion (complex animations)

**Avoid**: Generic Bootstrap, default Material UI without customization

#### UI Design Anti-Patterns (Enforced)

- ❌ **Prohibited**: Default fonts (Inter, Roboto, Open Sans, Lato, Arial, system-ui)
- ❌ **Prohibited**: Purple gradients on white backgrounds
- ❌ **Prohibited**: Hard-coded colors (use design tokens/CSS variables)
- ❌ **Prohibited**: Inconsistent spacing (use theme spacing multiples)
- ❌ **Prohibited**: Cookie-cutter layouts without context-specific character
- ❌ **Prohibited**: Converging on common font choices (Space Grotesk) across projects

**Rationale**: Prevents distributional convergence ("AI slop" appearance)

#### Design Thinking (Before Coding)

Commit to a **BOLD aesthetic direction**:
- **Purpose**: What problem does this interface solve? Who uses it?
- **Tone**: Pick an extreme - brutally minimal, maximalist chaos, retro-futuristic, organic/natural, luxury/refined, playful/toy-like, editorial/magazine, brutalist/raw, art deco/geometric, soft/pastel, industrial/utilitarian
- **Differentiation**: What makes this UNFORGETTABLE?

**CRITICAL**: Bold maximalism and refined minimalism both work - the key is **intentionality**, not intensity.

#### Design Best Practices (Suggested)

- ✅ **Typography**: Distinctive font choices (avoid generic), 3x+ size jumps, pair display font with refined body font
- ✅ **Color**: CSS variables, dominant colors with sharp accents (not timid even palettes)
- ✅ **Motion**: CSS-only first, orchestrated page load with staggered reveals, scroll-triggering, surprising hover states
- ✅ **Spatial Composition**: Unexpected layouts, asymmetry, overlap, diagonal flow, grid-breaking elements
- ✅ **Backgrounds**: Atmosphere and depth (gradient meshes, noise textures, geometric patterns, layered transparencies, dramatic shadows, grain overlays)

#### Internationalization

- ✅ Implement bilingual support: Chinese (simplified) + English
- ✅ Use react-i18next (React) or vue-i18n (Vue)
- ✅ All UI strings translatable, date/time/number formatting localized

#### Core Web Vitals

**Measured with Lighthouse CLI** (industry standard):
- ✅ **LCP** < 2.5s - Optimize images, reduce server response time
- ✅ **INP** < 200ms - Break up long tasks, use web workers
- ✅ **CLS** < 0.1 - Include size attributes, reserve space for dynamic content

---

### Testing Quality Baseline

#### Test Authenticity Score (TAS) - NEW

**Delegated to**: `guarding-test-quality` skill

This skill detects fake/useless tests through static analysis. Key metrics:

| Component | Weight | Pass Threshold |
|-----------|--------|----------------|
| Mock Ratio | 25% | ≤50% internal mocks |
| Assertion Quality | 35% | >50% behavioral assertions |
| Real Execution | 25% | >50% real code paths |
| Pattern Compliance | 15% | 0 critical anti-patterns |

**Grade Thresholds**:
- A (85-100): ✅ High quality tests
- B (70-84): ✅ Pass with minor issues
- C (50-69): ❌ **BLOCKED** - Needs improvement
- D/F (<50): ❌ **BLOCKED** - Fake tests detected

**Reference**: `guidelines/ultra-testing-philosophy.md` for anti-pattern examples and fixes

---

#### Realistic Test Execution

- ✅ Execute tests 100% realistically
- ❌ Minimal mocking: Only mock external services (APIs, databases, SDKs)
- ✅ Use real implementations for internal dependencies
- ✅ Test environment approximates production

**Why**: Over-mocked tests give false confidence.

#### Six-Dimensional Test Coverage

**All six dimensions mandatory** - Enforced by quality-guardian skill.

| Dimension | Focus |
|-----------|-------|
| **1. Functional** | Core business logic, happy paths, component integration |
| **2. Boundary** | Edge cases (empty/max/min), null/undefined, zero/negative, large inputs |
| **3. Exception** | Error handling (network/timeout), invalid input, error messages, graceful degradation |
| **4. Performance** | Load tests, response time, memory leaks, N+1 query detection |
| **5. Security** | Input validation (SQL/XSS), auth/authz, sensitive data, rate limiting |
| **6. Compatibility** | Cross-browser/platform/mobile, responsive design |

#### Test Coverage Requirements

- ✅ **Overall coverage ≥80%**
- ✅ **Critical paths: 100%** (authentication, payment, data integrity)
- ✅ **Branch coverage ≥75%** (all if/else branches tested)
- ✅ **Function coverage ≥85%** (most functions tested)

**Measurement**:
- JavaScript/TypeScript: `npm test -- --coverage`
- Python: `pytest --cov=src --cov-report=html`
- Go: `go test -coverprofile=coverage.out ./...`

---

### Quality Enforcement

#### Automated Enforcement

- **quality-guardian** - SOLID/DRY/KISS/YAGNI violations, six-dimensional test coverage, UI anti-patterns
- **CI/CD pipeline** - Tests must pass, coverage must meet threshold
- **Production monitoring** - Core Web Vitals tracked in real-time

#### Violation Consequences

- ❌ Code quality violations → Task cannot be marked complete
- ❌ Test coverage <80% → PR blocked
- ❌ Core Web Vitals failing → Deployment blocked
- ❌ Security issues → Immediate rollback and fix

---

### Quality Metrics Dashboard

| Metric | Target | Current | Trend |
|--------|--------|---------|-------|
| Test Coverage | ≥80% | _Track_ | _Monitor_ |
| Code Smells | 0 | _Track_ | _Monitor_ |
| LCP | <2.5s | _Measure_ | _Monitor_ |
| INP | <200ms | _Measure_ | _Monitor_ |
| CLS | <0.1 | _Measure_ | _Monitor_ |
| Build Time | <5min | _Track_ | _Monitor_ |
| Deployment Frequency | Daily | _Track_ | _Monitor_ |

---

**Remember**: Quality is not negotiable. It's the foundation of sustainable software development.
