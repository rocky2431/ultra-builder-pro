# Integration Checklist

## Entry Point Tracing

For every new module/service/class:
- **Ask**: "What entry point calls this code?"
- **If none**: Flag as orphan code (P1)
- **Trace**: handler → use case → domain → persistence (all layers reachable?)

## Contract Validation

For every boundary crossing:
- **Ask**: "Is there a shared interface/type that both sides use?"
- **If no shared type**: Flag missing contract (P2)
- **Ask**: "Is there a test validating the contract?"
- **If no contract test**: Flag missing contract test (P1)

## Vertical Slice Assessment

For the change as a whole:
- **Ask**: "Does this change deliver a working end-to-end path for at least one user scenario?"
- **If horizontal-only**: Flag as horizontal layer (P2)
- **Ask**: "Can a user exercise this change right now, or does it need unfinished work?"
- **If blocked by unfinished work**: Informational note (P3)

## Integration Test Coverage

| Boundary Type | Required Test | Common Mistake |
|---------------|---------------|----------------|
| HTTP endpoint | Real HTTP request/response | Testing handler function directly without HTTP layer |
| Database query | Testcontainers with real DB | InMemoryRepository or jest.mock |
| Queue/event | Real publish + consume | Mocking the event bus |
| External API | Test Double with rationale | No test at all |

## Data Flow Continuity

- **Ask**: "Does data flow from source to destination without gaps?"
- Check: Input validation → transformation → persistence → response
- **Flag**: Any link in the chain that exists in code but has no test proving data flows through it

## Key Questions

- "What happens if I deploy this change alone? Does anything work?"
- "Which entry point exercises this code path?"
- "Where does the data this component produces get consumed?"
- "Where does the data this component needs come from?"
