---
name: integration-rules
description: Ultra Builder Pro system integration rules
user-invocable: false
---

# Integration Rules

These rules are mandatory for all code review and development work involving multi-component systems.

## Vertical Slice Principle

Every task MUST deliver a thin, working end-to-end path:

| Good (Vertical Slice) | Bad (Horizontal Layer) |
|------------------------|------------------------|
| "User can send message" (UI + API + LLM + response display) | "Create all database tables" |
| "Display product list" (API call + domain filter + UI render) | "Build all API endpoints" |
| "Process payment" (UI form + gateway + order update) | "Create all UI components" |

## Walking Skeleton

The FIRST deliverable of any multi-component feature must be a walking skeleton:
- One request flows through ALL layers
- Returns real data (not hardcoded/mocked)
- Proves the architecture connects end-to-end
- Does NOT need to be feature-complete — just connected

## Contract-First Development

When two components will communicate:

| Step | Action | Artifact |
|------|--------|----------|
| 1 | Define interface before implementation | TypeScript interface, OpenAPI schema, or protobuf |
| 2 | Both sides code against the contract | Import shared types or generated clients |
| 3 | Contract test validates both sides | Test that producer output matches consumer expectation |

## Integration Test Requirements

| Boundary | Required Test |
|----------|---------------|
| HTTP API endpoint | Request with real HTTP client, validate response shape + status |
| Database operation | Testcontainers with real queries, validate data persisted |
| Message queue | Real producer + consumer, validate message delivered |
| External service | Test Double with `// Test Double rationale:` (only exception) |
| In-process module boundary | Real function call, validate input/output contract |

## Orphan Detection

Code without a live entry point is dead-on-arrival.

**Valid entry points** (at least one required per new module):
- HTTP/WebSocket handler
- CLI command handler
- Event/message listener
- Scheduled job/cron handler
- Exported function called by a module that has an entry point

**Detection**: Trace from new code upward — if no path reaches an entry point, the code is an orphan.

## Detection Checklist

When reviewing code, flag:
1. New module/service without any caller (orphan code)
2. Task structured as horizontal layer instead of vertical slice
3. Two components communicating without shared interface/contract
4. New boundary crossing without integration test
5. Use case with DB/API dependency but only unit tests
6. Component "works in isolation" but not wired to any entry point
7. Interface defined but no contract test validating compatibility
