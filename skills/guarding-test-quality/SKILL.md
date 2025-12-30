---
name: guarding-test-quality
description: "Validates test authenticity using TAS (Test Authenticity Score). This skill activates during /ultra-test, test file edits (*.test.ts, *.spec.ts), or task completion with tests."
---

# Test Quality Guardian

Ensures tests verify real behavior, not just achieve coverage numbers.

## Activation Context

This skill activates during:
- `/ultra-test` execution
- Test file modifications (*.test.ts, *.spec.ts, *.test.js, *.spec.js)
- Task completion that includes tests

## Resources

| Resource | Purpose |
|----------|---------|
| `scripts/tas_analyzer.py` | Calculate TAS scores |
| `REFERENCE.md` | Detailed test patterns and examples |

## TAS Analysis

Run the analyzer to evaluate test quality:

```bash
python scripts/tas_analyzer.py <test-file>
python scripts/tas_analyzer.py src/  # All tests
python scripts/tas_analyzer.py --summary  # Summary only
```

## TAS Score Components

| Component | Weight | High Score | Low Score |
|-----------|--------|------------|-----------|
| Mock Ratio | 25% | <30% internal mocks | >50% internal mocks |
| Assertion Quality | 35% | Behavioral assertions | Mock-only assertions |
| Real Execution | 25% | >60% real code paths | <30% real code |
| Pattern Quality | 15% | Clean test structure | Anti-patterns present |

## Grade Thresholds

| Grade | Score | Status |
|-------|-------|--------|
| A | 85-100% | Excellent - production ready |
| B | 70-84% | Good - minor improvements |
| C | 50-69% | Needs improvement |
| D/F | <50% | Significant issues |

## Good Test Characteristics

### Behavioral Assertions

Tests verify outcomes, not implementation:

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

### Appropriate Mocking

Mock external boundaries only:

| External (mock) | Internal (use real) |
|-----------------|---------------------|
| HTTP clients | Your services |
| Databases | Your utilities |
| Third-party SDKs | Business logic |
| File system | Custom hooks |

## Anti-Patterns to Detect

### 1. Tautology Tests

```typescript
// Always passes
expect(true).toBe(true);
```

**Fix:** Assert on actual function outputs

### 2. Empty Test Bodies

```typescript
it('should process payment', () => {
  // empty
});
```

**Fix:** Add behavioral assertions

### 3. Mock-Only Assertions

```typescript
// Only verifies call, not outcome
expect(mockService.process).toHaveBeenCalled();
```

**Fix:** Add outcome assertions

### 4. Over-Mocking

```typescript
// Mocking internal modules
jest.mock('../services/UserService');
jest.mock('../utils/validator');
```

**Fix:** Use real implementations

### 5. Testing Implementation Details

```typescript
// BAD: Tests internal state, not behavior
it('should set isLoading to true when fetching', () => {
  const component = mount(<UserList />)
  component.instance().fetchUsers()
  expect(component.state('isLoading')).toBe(true)
})
```

**Fix:** Test what user sees, not internal state

### 6. Snapshot Overuse

```typescript
// BAD: 500+ line snapshots never reviewed
it('should render correctly', () => {
  const { container } = render(<ComplexDashboard data={mockData} />)
  expect(container).toMatchSnapshot()
})
```

**Fix:** Use specific behavioral assertions instead

### 7. Testing Private Methods

```typescript
// BAD: Accessing private implementation
it('should hash password internally', () => {
  // @ts-ignore - accessing private method
  const hash = service._hashPassword('password123')
})
```

**Fix:** Test through public interface only

### 8. Coupling to CSS Selectors

```typescript
// BAD: Breaks on CSS changes
await userEvent.click(document.querySelector('.btn-primary.submit-form'))
expect(document.querySelector('.error-container > .error-text')).toHaveTextContent('Required')
```

**Fix:** Use accessible queries (getByRole, getByLabelText)

### 9. Test Interdependence

```typescript
// BAD: Tests depend on shared mutable state
let userId: string
it('should create user', async () => { userId = (await createUser()).id })
it('should update user', async () => { await updateUser(userId, {...}) })
```

**Fix:** Each test self-contained with own setup

### 10. Hardcoded Waits

```typescript
// BAD: Magic number, slow, flaky
await new Promise(resolve => setTimeout(resolve, 2000))
expect(screen.getByText('Success')).toBeInTheDocument()
```

**Fix:** Use `findBy*` queries that wait dynamically

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

{发现的问题和改进建议}

========================
```

**Tone:** Constructive, educational, improvement-focused
