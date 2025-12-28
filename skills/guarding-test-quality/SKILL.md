---
name: guarding-test-quality
description: "Validates test authenticity using TAS (Test Authenticity Score). Activates during /ultra-test, test file edits (*.test.ts, *.spec.ts), or task completion with tests."
allowed-tools: Read, Grep, Glob
---

# Test Quality Guardian

Ensures tests verify real behavior, not just achieve coverage numbers.

## Activation Context

This skill activates during:
- `/ultra-test` execution
- Test file modifications (*.test.ts, *.spec.ts, *.test.js, *.spec.js)
- Task completion that includes tests

## What Good Tests Look Like

### Behavioral Assertions

Tests verify outcomes, not implementation details:

```typescript
// Good: Tests actual behavior
describe('PaymentService', () => {
  it('confirms successful payment with transaction ID', async () => {
    const gateway = createMockGateway({ willSucceed: true });
    const service = new PaymentService(gateway);

    const result = await service.process(validOrder);

    expect(result.status).toBe('confirmed');
    expect(result.transactionId).toMatch(/^txn_/);
  });
});
```

**Characteristics:**
- Asserts on return values and state changes
- Uses real internal code, mocks only external boundaries
- Each test has meaningful assertions

### Appropriate Mocking

Mock external boundaries, use real implementations for internal code:

| External (mock these) | Internal (use real) |
|-----------------------|---------------------|
| HTTP clients (axios, fetch) | Your services (`../services/`) |
| Databases | Your utilities (`../utils/`) |
| Third-party SDKs | Business logic |
| File system | Custom hooks |

### TAS Score Components

| Component | Weight | High Score | Low Score |
|-----------|--------|------------|-----------|
| Mock Ratio | 25% | <30% internal mocks | >50% internal mocks |
| Assertion Quality | 35% | Behavioral assertions | Mock-only assertions |
| Real Execution | 25% | >60% real code paths | <30% real code |
| Pattern Quality | 15% | Clean test structure | Anti-patterns present |

### Grade Thresholds

| Grade | Score | Status |
|-------|-------|--------|
| A | 85-100% | Excellent |
| B | 70-84% | Good |
| C | 50-69% | Needs improvement |
| D/F | <50% | Significant issues |

## Quality Checks

When analyzing tests, look for these patterns:

### Pattern 1: Tautology Tests

```typescript
// Issue: Always passes regardless of code behavior
expect(true).toBe(true);
expect(1).toBe(1);
```

**Better approach:** Assert on actual function outputs

### Pattern 2: Empty Test Bodies

```typescript
// Issue: No assertions
it('should process payment', () => {
  // empty
});
```

**Better approach:** Add behavioral assertions

### Pattern 3: Mock-Only Assertions

```typescript
// Issue: Only verifies mock was called, not outcome
expect(mockService.process).toHaveBeenCalled();
// Missing: expect(result).toBe(expectedValue);
```

**Better approach:** Combine call verification with outcome assertions

### Pattern 4: Over-Mocking Internal Code

```typescript
// Issue: Mocking your own modules
jest.mock('../services/UserService');
jest.mock('../utils/validator');
```

**Better approach:** Use real implementations, mock only external APIs

## Output Format

Provide analysis in Chinese at runtime:

```
📊 测试质量分析报告
========================

项目 TAS 分数：{score}% (等级：{grade})

分析摘要：
- 测试文件：{count} 个
- 平均断言数：{avg} 个/测试
- Mock 比例：{ratio}%

{发现的具体问题和改进建议}

========================
```

**Tone:** Constructive and educational, focused on improvement
