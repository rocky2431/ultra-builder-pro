# Testing Philosophy - Best Practices Guide

**Ultra Builder Pro 4.3** - Core testing principles and anti-pattern detection.

---

## Core Principle

> "The more your tests resemble the way your software is used, the more confidence they can give you."
> — Testing Library Philosophy

**Test Behavior, Not Implementation**

This means:
- Test what users see and experience
- Avoid testing internal state or private methods
- Focus on outcomes, not mechanics
- Tests should survive refactoring

---

## Testing Trophy Model

Recommended over traditional Testing Pyramid:

```
           /  E2E Tests  \           Few, high confidence
          /  Integration  \          Most tests here (recommended)
         /   Unit Tests    \         More than E2E, less than integration
        / Static Analysis   \        TypeScript, ESLint, Prettier
```

**Why Trophy over Pyramid**:
- Integration tests catch more real bugs
- Unit tests often test implementation details
- E2E tests are slow but provide highest confidence
- Static analysis catches errors before runtime

---

## Mock Policy

### Clear Boundary Definitions

| Category | Examples | Mock? | Reason |
|----------|----------|-------|--------|
| **External Services** | REST APIs, GraphQL, third-party SDKs | YES | Network dependency, rate limits, cost |
| **Infrastructure** | Databases, Redis, message queues | DEPENDS | Real in integration, mock in unit |
| **System Resources** | File system, time, random | SOMETIMES | Use real when possible, mock for determinism |
| **Internal Code** | Your own modules, utilities, services | **NO** | Must test real behavior |

### Test Double Taxonomy

| Type | Purpose | When to Use |
|------|---------|-------------|
| **Stub** | Returns canned answers | Replace external dependency responses |
| **Mock** | Verifies interactions | When you care HOW something is called |
| **Spy** | Records calls while preserving behavior | Verify side effects without changing behavior |
| **Fake** | Working implementation with shortcuts | In-memory database, fake server |
| **Dummy** | Satisfies parameter requirements | Fill required arguments you don't care about |

### Mock Hierarchy (Prefer Top to Bottom)

```
1. No mock (real implementation)        ← BEST
2. Fake (working lightweight alternative)
3. Stub (controlled responses)
4. Spy (observe real behavior)
5. Mock (full control + verification)   ← LAST RESORT
```

---

## Anti-Pattern Library

### 1. Testing Implementation Details

**BAD**:
```typescript
// Tests internal state, not behavior
it('should set isLoading to true when fetching', () => {
  const component = mount(<UserList />)
  component.instance().fetchUsers()
  expect(component.state('isLoading')).toBe(true)
})
```

**GOOD**:
```typescript
// Tests what user sees
it('should show loading spinner while fetching users', async () => {
  render(<UserList />)
  expect(screen.getByRole('progressbar')).toBeInTheDocument()
  await waitForElementToBeRemoved(() => screen.queryByRole('progressbar'))
})
```

**Why Bad**: Breaks when you rename state, refactor to hooks, or change loading strategy.

---

### 2. Over-Mocking (The "Mock Everything" Trap)

**BAD**:
```typescript
// Mocks even internal utilities
jest.mock('../utils/formatDate')
jest.mock('../utils/validateEmail')
jest.mock('../services/userService')
jest.mock('../hooks/useAuth')

it('should register user', async () => {
  await register('user@example.com', 'password')
  expect(mockUserService.create).toHaveBeenCalled()
  // Tests literally nothing - all behavior is mocked away
})
```

**GOOD**:
```typescript
// Only mock external HTTP calls
const server = setupServer(
  rest.post('/api/users', (req, res, ctx) => {
    return res(ctx.json({ id: '123', email: req.body.email }))
  })
)

it('should register user and show success message', async () => {
  render(<RegistrationForm />)

  await userEvent.type(screen.getByLabelText(/email/i), 'user@example.com')
  await userEvent.type(screen.getByLabelText(/password/i), 'SecurePass123!')
  await userEvent.click(screen.getByRole('button', { name: /register/i }))

  expect(await screen.findByText(/registration successful/i)).toBeInTheDocument()
})
```

**Why Bad**: Tests only verify that mocks were called, not that real code works.

---

### 3. Snapshot Overuse

**BAD**:
```typescript
// Snapshots everything
it('should render correctly', () => {
  const { container } = render(<ComplexDashboard data={mockData} />)
  expect(container).toMatchSnapshot()  // 500+ line snapshot
})
```

**GOOD**:
```typescript
// Tests specific behaviors
it('should display user count from data', () => {
  render(<ComplexDashboard data={{ users: 42, orders: 100 }} />)
  expect(screen.getByText('42 users')).toBeInTheDocument()
})

it('should highlight negative growth in red', () => {
  render(<ComplexDashboard data={{ growth: -5 }} />)
  expect(screen.getByText('-5%')).toHaveClass('text-red-500')
})
```

**Why Bad**: Large snapshots are never reviewed, hide regressions, and break on every UI change.

---

### 4. Testing Private Methods

**BAD**:
```typescript
// Exposes and tests private implementation
it('should correctly hash password internally', () => {
  const service = new AuthService()
  // @ts-ignore - accessing private method
  const hash = service._hashPassword('password123')
  expect(hash).toMatch(/^\$2b\$/)
})
```

**GOOD**:
```typescript
// Tests through public interface
it('should not store plaintext password', async () => {
  const user = await authService.register('user@example.com', 'password123')
  expect(user.password).not.toBe('password123')
  expect(user.password).toMatch(/^\$2b\$/)  // bcrypt format
})
```

**Why Bad**: Private methods are implementation details; change them freely without breaking tests.

---

### 5. Coupling to CSS Selectors

**BAD**:
```typescript
// Brittle - breaks on CSS/class changes
it('should show error', async () => {
  render(<LoginForm />)
  await userEvent.click(document.querySelector('.btn-primary.submit-form'))
  expect(document.querySelector('.error-container > .error-text')).toHaveTextContent('Required')
})
```

**GOOD**:
```typescript
// Uses accessible queries
it('should show error when email is empty', async () => {
  render(<LoginForm />)
  await userEvent.click(screen.getByRole('button', { name: /submit/i }))
  expect(screen.getByRole('alert')).toHaveTextContent('Email is required')
})
```

**Why Bad**: Class names change frequently; accessible queries are stable and match user experience.

---

### 6. Assertion-Free Tests

**BAD**:
```typescript
// No assertions - tests nothing
it('should render without crashing', () => {
  render(<UserProfile user={mockUser} />)
})

it('should call API', async () => {
  await fetchUsers()
  // No assertion!
})
```

**GOOD**:
```typescript
it('should display user name and email', () => {
  render(<UserProfile user={{ name: 'John', email: 'john@example.com' }} />)
  expect(screen.getByText('John')).toBeInTheDocument()
  expect(screen.getByText('john@example.com')).toBeInTheDocument()
})
```

**Why Bad**: Test passes even if code is completely broken.

---

### 7. Test Interdependence

**BAD**:
```typescript
// Tests depend on order and shared state
let userId: string

it('should create user', async () => {
  const user = await createUser({ name: 'John' })
  userId = user.id  // Shared mutable state!
})

it('should update user', async () => {
  await updateUser(userId, { name: 'Jane' })  // Depends on previous test
})

it('should delete user', async () => {
  await deleteUser(userId)  // Chain dependency
})
```

**GOOD**:
```typescript
// Each test is self-contained
it('should create user', async () => {
  const user = await createUser({ name: 'John' })
  expect(user.name).toBe('John')
})

it('should update user', async () => {
  const user = await createUser({ name: 'John' })  // Own setup
  const updated = await updateUser(user.id, { name: 'Jane' })
  expect(updated.name).toBe('Jane')
})

it('should delete user', async () => {
  const user = await createUser({ name: 'John' })  // Own setup
  await deleteUser(user.id)
  await expect(getUser(user.id)).rejects.toThrow('Not found')
})
```

**Why Bad**: Tests fail randomly when run in isolation or different order.

---

### 8. Hardcoded Waits

**BAD**:
```typescript
it('should show success message', async () => {
  render(<AsyncForm />)
  await userEvent.click(screen.getByRole('button'))

  await new Promise(resolve => setTimeout(resolve, 2000))  // Magic number!

  expect(screen.getByText('Success')).toBeInTheDocument()
})
```

**GOOD**:
```typescript
it('should show success message', async () => {
  render(<AsyncForm />)
  await userEvent.click(screen.getByRole('button'))

  // Waits dynamically until element appears
  expect(await screen.findByText('Success')).toBeInTheDocument()
})
```

**Why Bad**: Slows tests, fails intermittently on slow CI, hides timing issues.

---

### 9. Testing Framework Features

**BAD**:
```typescript
// Tests that React hooks work, not your code
it('should update state when useState is called', () => {
  const { result } = renderHook(() => useState(0))
  act(() => result.current[1](5))
  expect(result.current[0]).toBe(5)  // Testing React, not your code
})
```

**GOOD**:
```typescript
// Tests your custom hook's behavior
it('should increment counter and persist to localStorage', () => {
  const { result } = renderHook(() => usePersistedCounter('test-key'))

  act(() => result.current.increment())

  expect(result.current.count).toBe(1)
  expect(localStorage.getItem('test-key')).toBe('1')
})
```

**Why Bad**: Tests framework internals that are already tested by the framework.

---

### 10. Coverage-Driven Testing

**BAD**:
```typescript
// Written just to hit coverage numbers
it('should cover line 42', () => {
  const result = someFunction(null)  // Just to cover null branch
  expect(result).toBeDefined()  // Meaningless assertion
})
```

**GOOD**:
```typescript
// Tests meaningful behavior
it('should return default config when input is null', () => {
  const config = parseConfig(null)
  expect(config).toEqual({
    timeout: 5000,
    retries: 3,
    debug: false
  })
})
```

**Why Bad**: High coverage with useless tests gives false confidence.

---

## Test Authenticity Score (TAS)

Automated detection of fake tests based on:

| Component | Weight | Good | Bad |
|-----------|--------|------|-----|
| Mock Ratio | 25% | <30% internal mocks | >50% internal mocks |
| Assertion Quality | 35% | Behavioral assertions | Mock-only assertions |
| Real Execution | 25% | Real code paths | Mock-driven paths |
| Pattern Compliance | 15% | No anti-patterns | Multiple anti-patterns |

**Grade Thresholds**:
- A (85-100): High quality tests
- B (70-84): Good tests with minor issues
- C (50-69): **BLOCKED** - Needs improvement
- D/F (<50): **BLOCKED** - Fake tests detected

---

## Community References

- [Testing Library Guiding Principles](https://testing-library.com/docs/guiding-principles)
- [Kent C. Dodds: Write Tests](https://kentcdodds.com/blog/write-tests)
- [Martin Fowler: Practical Test Pyramid](https://martinfowler.com/articles/practical-test-pyramid.html)
- [Test Double Taxonomy (Gerard Meszaros)](http://xunitpatterns.com/Test%20Double.html)

---

**OUTPUT: User messages in Chinese at runtime; keep this file English-only.**
