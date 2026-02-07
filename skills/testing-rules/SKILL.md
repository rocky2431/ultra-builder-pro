---
name: testing-rules
description: Ultra Builder Pro testing discipline rules
user-invocable: false
---

# Testing Rules

These rules are mandatory for all test-related work.

## TDD Workflow

RED → GREEN → REFACTOR (all new code).

## Test Strategy

| Layer | Test Type | Mock Strategy |
|-------|-----------|---------------|
| Functional Core | Unit Test | No mocks needed (pure input→output) |
| Imperative Shell | Integration | Testcontainers (real DB/services) |
| External APIs | Test Double | With `// Test Double rationale: [reason]` |

## Forbidden Patterns

These patterns are **never** acceptable:

| Pattern | Why Forbidden | Alternative |
|---------|---------------|-------------|
| `jest.fn()` for Repository/Service/Domain | Invalid test — doesn't prove production works | Testcontainers |
| `class InMemoryRepository` | Diverges from real DB behavior | Real DB container |
| `class MockXxx` / `class FakeXxx` | Hides integration issues | Direct instantiation or Testcontainers |
| `jest.mock('../services/X')` | Skips real collaboration | Test real collaboration |
| `it.skip('...database...')` | "Too slow" is not valid | Testcontainers are fast enough |

## Coverage Requirements

- 80% overall minimum
- 100% Functional Core (pure logic must be fully tested)
- Critical paths for Imperative Shell

## Dev/Prod Parity

Tests must use real dependencies:
- Real database via Testcontainers (not in-memory substitutes)
- Config via environment variables
- Mock tests passing ≠ production working

## Detection Checklist

When analyzing test files, flag:
1. Any `jest.fn()` usage on Repository, Service, or Domain classes
2. Any `InMemory*` or `Mock*` or `Fake*` class definitions
3. Any `jest.mock()` calls on internal modules
4. Any skipped tests with database/slow excuses
5. Missing error case coverage
6. Missing edge case coverage
