---
name: guarding-quality
description: "Validates code quality across SOLID principles, test coverage, and UI design. Activates when editing code files (*.ts, *.js, *.py, *.go), UI files (*.css, *.scss), or discussing refactoring and quality."
allowed-tools: Read, Grep
---

# Quality Guardian

Ensures production-grade code quality across three dimensions.

## Activation Context

This skill activates when:
- Editing code files (*.ts, *.js, *.tsx, *.jsx, *.py, *.go, *.vue)
- Editing UI files (*.css, *.scss, *.styled.ts)
- Discussing quality, refactoring, or testing
- Running /ultra-test or completing tasks

## Code Quality Standards

### Function Design

Well-designed functions are:
- **Focused**: ≤50 lines, single responsibility
- **Shallow**: ≤3 levels of nesting
- **Simple**: ≤10 cyclomatic complexity
- **Unique**: ≤3 duplicate lines

**Example of good structure:**

```typescript
// Focused: does one thing well
async function processOrder(order: Order): Promise<OrderResult> {
  const validated = validateOrder(order);
  const payment = await chargePayment(validated);
  return createConfirmation(validated, payment);
}

// Each sub-function also focused
function validateOrder(order: Order): ValidatedOrder {
  if (!order.items.length) throw new ValidationError('Empty order');
  if (!order.customer) throw new ValidationError('Missing customer');
  return { ...order, validatedAt: new Date() };
}
```

### SOLID Principles in Practice

| Principle | What It Looks Like |
|-----------|-------------------|
| Single Responsibility | One reason to change per class/function |
| Open-Closed | Extend via abstraction, stable core code |
| Liskov Substitution | Subtypes work wherever parent works |
| Interface Segregation | Small, focused interfaces |
| Dependency Inversion | Depend on abstractions, inject dependencies |

### Configuration Values

Use named constants and environment variables:

```typescript
// Good: Configurable, self-documenting
const MAX_RETRY_ATTEMPTS = 3;
const API_TIMEOUT_MS = parseInt(process.env.API_TIMEOUT || '5000');

// Instead of magic numbers in code
```

## Test Coverage Standards

| Scope | Target |
|-------|--------|
| Overall | ≥80% |
| Critical paths | 100% |
| Branch coverage | ≥75% |

**Six testing dimensions:**
1. Functional - Does it work correctly?
2. Boundary - Edge cases handled?
3. Exception - Errors handled gracefully?
4. Performance - Meets speed requirements?
5. Security - Protected against attacks?
6. Compatibility - Works across environments?

## UI Design Quality

### Component Libraries

Recommended for distinctive design:
- shadcn/ui, Galaxy UI, React Bits

### Design Tokens

Use tokens for consistent theming:

```typescript
// Good: Uses design system
const Card = styled.div`
  background: var(--color-surface);
  border-radius: var(--radius-md);
  padding: var(--space-4);
`;
```

### Visual Distinctiveness

Consider:
- Bold typography with clear hierarchy
- Intentional color palette
- Consistent spacing system
- Purposeful motion/animation

## Output Format

Provide guidance in Chinese at runtime:

```
代码质量检查
========================

检查结果：
- {具体发现}
- {改进建议}

参考：REFERENCE.md {section}
========================
```

**Tone:** Constructive, specific, actionable
