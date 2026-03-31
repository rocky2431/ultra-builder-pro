# Step 40: Deployment & Infrastructure

## MANDATORY EXECUTION RULES

- WEB SEARCH REQUIRED — verify infrastructure pricing and capabilities
- INCLUDE cost estimates with sources
- DEFINE environments: dev, staging, production
- WRITE output to spec file BEFORE presenting to user
- ALL output in English (spec files); conversation in Chinese

## PREREQUISITES

- Step 32 (Building Blocks) completed with [C]
- `.ultra/specs/architecture.md` §1-6 exist

## SEARCH STRATEGY (MANDATORY)

```
Search: "{{chosen_hosting}} pricing calculator {{product_domain}}"
Search: "{{chosen_hosting}} deployment best practices"
Search: "{{chosen_tech_stack}} CI/CD pipeline setup"
Search: "{{chosen_tech_stack}} docker deployment production"
```

## EXECUTION SEQUENCE

### 1. Define Deployment Topology

Map the infrastructure for each environment.

### 2. Define CI/CD Pipeline

Build → Test → Deploy stages with quality gates.

### 3. Estimate Costs

Use web search for real pricing data.

### 4. Write Output

**WRITE IMMEDIATELY** to `.ultra/specs/architecture.md` §7-9:

```markdown
## §7 Deployment View

### Environments

| Environment | Purpose | Infrastructure | URL Pattern |
|------------|---------|---------------|-------------|
| Development | Local dev | [Docker Compose / local] | localhost:X |
| Staging | Pre-prod testing | [Cloud provider details] | staging.X |
| Production | Live users | [Cloud provider details] | X.com |

### Production Topology
- **Compute**: [Service type, instance size, count]
- **Database**: [Managed service, tier, backup]
- **Cache**: [Service, tier]
- **CDN**: [Provider]
- **DNS**: [Provider]

### CI/CD Pipeline

| Stage | Tool | Trigger | Quality Gate |
|-------|------|---------|-------------|
| Build | [Tool] | Push to branch | Compilation success |
| Unit Test | [Runner] | Post-build | 80%+ coverage, 0 failures |
| Integration Test | [Runner] | Post-unit | All green |
| Security Scan | [Tool] | Post-test | No critical/high |
| Deploy Staging | [Tool] | Merge to main | All gates passed |
| Deploy Production | [Tool] | Manual approval | Staging verified |

## §8 Crosscutting Concerns

### Logging
- **Format**: Structured JSON
- **Fields**: timestamp, level, service, traceId, message, context
- **Tool**: [Logging framework]

### Authentication
- **Method**: [JWT / OAuth2 / etc]
- **Provider**: [Auth service]
- **Session**: [Strategy]

### Error Handling
- **Pattern**: Result/Either in domain, global handler in infrastructure
- **Alerting**: [When and how]

## §9 Cost Estimate

| Service | Monthly Cost | Annual Cost | Source |
|---------|-------------|------------|--------|
| Compute | $[X] | $[X] | [URL] |
| Database | $[X] | $[X] | [URL] |
| Other | $[X] | $[X] | [URL] |
| **Total** | **$[X]** | **$[X]** | |

_Assumptions: [user count, traffic, storage]_
```

### 5. Present to User and Gate

```
[C] Continue — Deployment defined, proceed to Quality & Risks
[R] Revise — Adjust infrastructure or costs
```

**HALT — wait for user response before proceeding.**

### 6. Handle Response

- **[C]**: Load next step: `./step-41-quality-risks.md`
- **[R]**: Revise, update architecture.md §7-9, re-present

## SUCCESS METRICS

- All environments defined
- CI/CD pipeline with quality gates
- Cost estimates with sources
- Crosscutting concerns (logging, auth, errors) addressed

## NEXT STEP

After user selects [C], read and follow: `./step-41-quality-risks.md`
