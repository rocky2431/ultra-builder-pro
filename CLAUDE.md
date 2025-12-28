# Ultra Builder Pro 4.2

**Always respond in Chinese-simplified**

---

## Production-First Engineering

> "There is no demo. Every line of code is production code."

All code must be deployable today. When implementing any feature, write it as if it ships to production immediately after merge.

### Core Principle: Real Implementation

Write actual business logic with proper architecture. Every function should handle real-world scenarios including edge cases, errors, and varying inputs.

**What this looks like in practice:**

```typescript
// Production-ready: handles real scenarios
async function processPayment(order: Order): Promise<PaymentResult> {
  validateOrder(order);  // Input validation at boundary

  const result = await paymentGateway.charge({
    amount: order.total,
    currency: order.currency,
    idempotencyKey: order.id,  // Handles retries safely
  });

  if (!result.success) {
    logger.error('Payment failed', { orderId: order.id, error: result.error });
    throw new PaymentError(result.error, { recoverable: result.canRetry });
  }

  return result;
}
```

**Key characteristics:**
- Configuration via environment variables (12-Factor)
- Error handling with context for debugging
- Input validation at system boundaries
- Dependency injection for testability
- Structured logging for observability

### Core Principle: Meaningful Tests

Tests verify behavior, not implementation. Mock only external boundaries (APIs, databases, filesystem), use real implementations for internal code.

**What this looks like in practice:**

```typescript
// Tests actual behavior with minimal mocking
describe('PaymentService', () => {
  it('processes valid payment and returns confirmation', async () => {
    const mockGateway = createMockPaymentGateway({ willSucceed: true });
    const service = new PaymentService(mockGateway);  // Only external dep mocked

    const result = await service.process(validOrder);

    expect(result.status).toBe('confirmed');
    expect(result.transactionId).toBeDefined();
    expect(mockGateway.charge).toHaveBeenCalledWith(
      expect.objectContaining({ amount: validOrder.total })
    );
  });

  it('handles gateway timeout with retry info', async () => {
    const mockGateway = createMockPaymentGateway({ willTimeout: true });
    const service = new PaymentService(mockGateway);

    await expect(service.process(validOrder)).rejects.toThrow(PaymentError);
    // Verify error contains recovery information
  });
});
```

**Key characteristics:**
- Assertions verify outcomes, not code paths
- Mock external boundaries only (payment gateway = external)
- Test error scenarios with expected recovery behavior
- TAS ≥70: real logic, minimal mocking, meaningful assertions

### Core Principle: Complete Delivery

Every merged feature works end-to-end. Partial implementations stay in feature branches until complete.

**Completeness checklist:**
- Runs in dev, staging, and prod without code changes
- Error handling covers failure scenarios
- Logging provides debugging context
- Tests verify actual behavior

---

## Quality Standards

### Coverage Targets
| Scope | Target |
|-------|--------|
| Overall | ≥80% |
| Critical paths | 100% |
| Branch | ≥75% |

### Code Limits
| Metric | Limit |
|--------|-------|
| Function lines | ≤50 |
| Nesting depth | ≤3 |
| Complexity | ≤10 |

### Frontend (Core Web Vitals)
| Metric | Target |
|--------|--------|
| LCP | <2.5s |
| INP | <200ms |
| CLS | <0.1 |

---

## Development Workflow

**TDD Cycle**: RED → GREEN → REFACTOR

### Commands

| Command | Purpose |
|---------|---------|
| `/ultra-init` | Initialize project |
| `/ultra-research` | Technical investigation |
| `/ultra-plan` | Task planning |
| `/ultra-dev` | TDD development |
| `/ultra-test` | Quality validation |
| `/ultra-deliver` | Deployment prep |
| `/ultra-status` | Progress report |
| `/max-think` | Deep analysis (6D) |

**Workflow**: init → research → plan → dev → test → deliver

---

## Git Workflow

### Branch Strategy
```
feat/task-{id}-{slug}     # New feature
fix/bug-{id}-{slug}       # Bug fix
refactor/{slug}           # Refactoring
```

### Commit Convention
- Style: Conventional Commits
- Co-author: `Claude <noreply@anthropic.com>`
- Strategy: task → branch → merge → delete

---

## Project Structure

```
.ultra/
├── tasks/tasks.json
├── specs/
│   ├── product.md
│   └── architecture.md
└── docs/
    ├── research/
    └── decisions/
```

**OpenSpec Pattern**: specs/ (truth) → changes/ (proposals) → archive/

---

## Skills (6 auto-loaded)

| Type | Skills |
|------|--------|
| Guards | guarding-quality, guarding-test-quality, guarding-git-workflow |
| Sync | syncing-docs, syncing-status |
| Utils | guiding-workflow |

---

## Agents (auto-delegated)

| Agent | Use Case |
|-------|----------|
| ultra-research-agent | Tech comparisons, risk assessment |
| ultra-architect-agent | System design, SOLID analysis |
| ultra-qa-agent | Test strategy, coverage planning |
| ultra-performance-agent | Core Web Vitals optimization |

---

## Tools Priority

1. Built-in first (Read/Write/Edit/Grep/Glob)
2. Official docs → Context7 MCP
3. Code search → Exa MCP

---

## Language Protocol

- **Output**: Chinese (simplified)
- **Technical terms**: English
- **Code/paths**: English
