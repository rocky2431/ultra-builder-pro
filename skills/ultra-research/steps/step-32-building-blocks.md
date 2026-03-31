# Step 32: Building Blocks & Runtime Scenarios

## MANDATORY EXECUTION RULES

- MODULE DECOMPOSITION must follow Functional Core / Imperative Shell pattern
- EVERY MODULE must trace to at least one feature from product.md §5
- RUNTIME SCENARIOS must cover the top 3 user scenarios from product.md §3
- WRITE output to spec file BEFORE presenting to user
- ALL output in English (spec files); conversation in Chinese

## PREREQUISITES

- Step 31 (Solution Strategy) completed with [C]
- `.ultra/specs/architecture.md` §1-4 exist

## CONTEXT BOUNDARIES

- Focus: Module decomposition and runtime behavior (arc42 §5-6)
- Structure follows: `src/{domain/, application/usecases/, infrastructure/}`
- Domain logic is pure (no IO); Infrastructure handles IO
- This step bridges product (WHAT) to code (HOW)

## EXECUTION SEQUENCE

### 1. Module Decomposition

Based on features from product.md §5 and tech stack from §4:

**Layer structure**:
```
src/
├── domain/           # Functional Core (pure logic)
│   ├── entities/     # Domain objects
│   ├── values/       # Value objects
│   └── services/     # Domain services (pure functions)
├── application/      # Use cases (orchestration)
│   └── usecases/     # One file per use case
├── infrastructure/   # Imperative Shell (IO)
│   ├── http/         # HTTP handlers/routes
│   ├── persistence/  # Database repositories
│   └── external/     # External API clients
└── config/           # Configuration
```

Map each feature to modules:
- Feature 1 → domain/entities/X, application/usecases/Y, infrastructure/http/Z

### 2. Define Key Interfaces

For each module boundary, define the contract:

| Interface | Provider | Consumer | Data |
|-----------|---------|----------|------|
| [Interface A] | [Module] | [Module] | [DTO/Entity] |

### 3. Runtime Scenarios

For the top 3 user scenarios from product.md §3, describe the runtime flow:

**Scenario S1**: [Name]
```
User → HTTP Handler → Use Case → Domain Service → Repository → Database
                                                              ↓
User ← HTTP Response ← Use Case ← Domain Entity ← Repository ← Query Result
```

### 4. Write Output

**WRITE IMMEDIATELY** to `.ultra/specs/architecture.md` §5-6:

```markdown
## §5 Building Block View

### Level 1: System Decomposition

| Module | Layer | Responsibility | Dependencies |
|--------|-------|---------------|-------------|
| [Module A] | Domain | [What it does] | None (pure) |
| [Module B] | Application | [What it orchestrates] | [Module A] |
| [Module C] | Infrastructure | [What IO it handles] | [Module B] |

### Module Details

#### domain/
- **entities/[Entity]**: [Description, key fields, business rules]
- **values/[ValueObject]**: [Description, validation rules]
- **services/[Service]**: [Pure functions, input → output]

#### application/usecases/
- **[UseCase1]**: [Input → orchestration → output]
- **[UseCase2]**: [Input → orchestration → output]

#### infrastructure/
- **http/[Handler]**: [Routes, request/response mapping]
- **persistence/[Repository]**: [Database operations]
- **external/[Client]**: [External API integration]

### Feature → Module Mapping

| Feature | Domain | Application | Infrastructure |
|---------|--------|------------|---------------|
| [Feature 1] | [Entities] | [UseCases] | [Handlers, Repos] |
| [Feature 2] | [Entities] | [UseCases] | [Handlers, Repos] |

## §6 Runtime Scenarios

### Scenario 1: [S1 Name from product.md]

**Trigger**: [User action]
**Flow**:
1. User sends [request type] to [endpoint]
2. [Handler] validates input, maps to [DTO]
3. [UseCase] orchestrates: loads [Entity] via [Repository]
4. [DomainService] applies business logic (pure)
5. [Repository] persists result
6. [Handler] returns [response]

**Data flow**: [Input] → [Transformation] → [Output]
**Error paths**: [What can go wrong and how it's handled]

### Scenario 2: [S2 Name]
[Same structure]

### Scenario 3: [S3 Name]
[Same structure]

### Round 3 Summary

**Architecture Design Confidence**:
- **Quality goal coverage**: [X]%
- **Tech stack confidence**: [X]%
- **Module clarity**: [X]%
- **Overall R3 confidence**: [X]%
```

### 5. Write Round 3 Research Report

**WRITE** to `.ultra/docs/research/architecture-design-{date}.md`:

```markdown
# Round 3: Architecture Design

> **Confidence**: [X]%
> **Steps completed**: 30-32
> **Completed**: [date]

## Key Decisions
[Tech stack choices with rationale]

## Architecture Pattern
[Functional Core / Imperative Shell overview]

## Risk Areas
[Where architecture is weakest]
```

### 6. Present to User and Gate

```
[C] Continue — Architecture defined, proceed to Round 4 (Deployment & Quality)
[R] Revise — Adjust modules or scenarios
```

**HALT — wait for user response before proceeding.**

### 7. Handle Response

- **[C]**: Load next step: `./step-40-deployment.md`
- **[R]**: Revise, update architecture.md §5-6, re-present

## SUCCESS METRICS

- Every module traces to a feature
- Functional Core / Imperative Shell separation clear
- Top 3 runtime scenarios documented with data flow
- Error paths identified
- Round 3 research report written

## FAILURE MODES

- Modules that don't map to any feature (orphan code)
- Business logic in infrastructure layer
- Missing error paths in runtime scenarios
- No interface contracts between modules

## NEXT STEP

After user selects [C], read and follow: `./step-40-deployment.md`
