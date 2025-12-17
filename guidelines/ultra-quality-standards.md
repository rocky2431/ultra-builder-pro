# Quality Standards - Complete Baselines

**Ultra Builder Pro 4.0** - All baselines are **non-negotiable**. Violations block task completion.

---

## Code Quality Baseline

### Core Requirements

- ✅ **Follow SOLID/DRY/KISS/YAGNI** - See `~/.claude/guidelines/solid-principles.md`
- ✅ **All public functions must have clear comments** - JSDoc format with @param, @returns, @example
- ✅ **Unit test coverage ≥80%** - Enforced by guarding-quality skill

### Code Smells Detection

Immediately fix when detected:
- ❌ Functions >50 lines → Split
- ❌ Nesting depth >3 levels → Refactor
- ❌ Magic numbers → Extract to named constants
- ❌ Commented-out code → Delete (use git history)
- ❌ Duplicate code >3 lines → Extract to shared function
- ❌ God classes (>500 lines) → Split by responsibility
- ❌ Long parameter lists (>5 params) → Use object parameters
- ❌ Cryptic variable names → Use descriptive names

### Code Documentation Example

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

## Frontend Quality Baseline

**Mandatory for frontend projects only** (React, Vue, Angular, etc.)

### UI Design Anti-Patterns (Enforced)

**Enforced by guarding-quality skill**

- ❌ **Prohibited**: Default fonts (Inter, Roboto, Open Sans, Lato, system-ui)
- ❌ **Prohibited**: Purple gradients on white backgrounds
- ❌ **Prohibited**: Hard-coded colors (use design tokens/CSS variables)
- ❌ **Prohibited**: Inconsistent spacing (use theme spacing multiples)

**Rationale**: Prevents distributional convergence ("AI slop" appearance)

### Design Best Practices (Suggested)

**Guided by guarding-quality skill**

- ✅ **Typography**: 3x+ size jumps, high-contrast font pairing
- ✅ **Color**: Design tokens, one dominant color with accents
- ✅ **Motion**: CSS-only first, orchestrated page load animations
- ✅ **Component Libraries**: Prefer established libraries (MUI, Ant Design, Chakra, Radix, shadcn/ui)
- ✅ **Design Systems**: Support multiple (Material Design, Tailwind, Chakra UI, Ant Design, custom)

### Internationalization

- ✅ Implement bilingual support: Chinese (simplified) + English
- ✅ Use react-i18next (React) or vue-i18n (Vue)
- ✅ All UI strings translatable, date/time/number formatting localized

### Core Web Vitals

**Measured with Lighthouse CLI** (industry standard):
- ✅ **LCP** < 2.5s - Optimize images, reduce server response time
- ✅ **INP** < 200ms - Break up long tasks, use web workers
- ✅ **CLS** < 0.1 - Include size attributes, reserve space for dynamic content

**Measurement**: Use Lighthouse CLI directly (see Playwright Skill documentation for details)

---

## Testing Quality Baseline

### Core Philosophy

> "The more your tests resemble the way your software is used, the more confidence they can give you."
> — Testing Library Philosophy

**Test Behavior, Not Implementation** - Focus on outcomes, not mechanics.

**Reference**: `guidelines/ultra-testing-philosophy.md` for complete philosophy and 10 anti-patterns.

---

### Test Authenticity Score (TAS) - NEW

**Enforced by**: `guarding-test-quality` skill

| Gate | Requirement | Action |
|------|-------------|--------|
| TAS Score | ≥70% | Pass (Grade A/B) |
| TAS Score | <70% | **BLOCKED** (Grade C/D/F) |
| Tautologies | 0 | Pass |
| Empty Tests | 0 | Pass |
| Mock Ratio | ≤50% | Pass |

**Anti-Patterns Detected** (Critical):
- `expect(true).toBe(true)` → Automatic F grade
- Empty test body `it('...', () => {})` → Automatic F grade
- Over-mocking internal modules → TAS penalty

---

### Realistic Test Execution

- ✅ Execute tests 100% realistically
- ❌ Minimal mocking: Only mock external services (APIs, databases, SDKs)
- ✅ Use real implementations for internal dependencies
- ✅ Test environment approximates production

**Why**: Over-mocked tests give false confidence.

### Six-Dimensional Test Coverage

**All six dimensions mandatory** - Enforced by guarding-quality skill.

| Dimension | Focus |
|-----------|-------|
| **1. Functional** | Core business logic, happy paths, component integration |
| **2. Boundary** | Edge cases (empty/max/min), null/undefined, zero/negative, large inputs |
| **3. Exception** | Error handling (network/timeout), invalid input, error messages, graceful degradation |
| **4. Performance** | Load tests, response time, memory leaks, N+1 query detection |
| **5. Security** | Input validation (SQL/XSS), auth/authz, sensitive data, rate limiting |
| **6. Compatibility** | Cross-browser/platform/mobile, responsive design |

### Test Coverage Requirements

- ✅ **Overall coverage ≥80%**
- ✅ **Critical paths: 100%** (authentication, payment, data integrity)
- ✅ **Branch coverage ≥75%** (all if/else branches tested)
- ✅ **Function coverage ≥85%** (most functions tested)

**Measurement**:
- JavaScript/TypeScript: `npm test -- --coverage`
- Python: `pytest --cov=src --cov-report=html`
- Go: `go test -coverprofile=coverage.out ./...`

---

## Quality Enforcement

### Automated Enforcement

- **guarding-quality** - SOLID/DRY/KISS/YAGNI violations, six-dimensional coverage, UI anti-patterns prevention + design guidance
- **guarding-test-quality** (NEW) - TAS calculation, fake test detection, anti-pattern scanning
- **automating-e2e-tests** - E2E testing + Core Web Vitals monitoring

### Manual Enforcement

- **Code review** - Peer review required before merge
- **CI/CD pipeline** - Tests must pass, coverage must meet threshold
- **Production monitoring** - Core Web Vitals tracked in real-time

### Violation Consequences

- ❌ Code quality violations → Task cannot be marked complete
- ❌ Test coverage <80% → PR blocked
- ❌ **TAS <70%** → Task cannot be marked complete (NEW)
- ❌ **Tautology/empty tests detected** → Task cannot be marked complete (NEW)
- ❌ Core Web Vitals failing → Deployment blocked
- ❌ Security issues → Immediate rollback and fix

---

## Quality Metrics Dashboard

| Metric | Target | Current | Trend |
|--------|--------|---------|-------|
| Test Coverage | ≥80% | _Track_ | _Monitor_ |
| **TAS Score** | **≥70%** | _Track_ | _Monitor_ |
| Code Smells | 0 | _Track_ | _Monitor_ |
| LCP | <2.5s | _Measure_ | _Monitor_ |
| INP | <200ms | _Measure_ | _Monitor_ |
| CLS | <0.1 | _Measure_ | _Monitor_ |
| Build Time | <5min | _Track_ | _Monitor_ |
| Deployment Frequency | Daily | _Track_ | _Monitor_ |

---

**Remember**: Quality is not negotiable. It's the foundation of sustainable software development.
