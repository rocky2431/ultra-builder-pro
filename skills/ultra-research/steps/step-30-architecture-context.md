# Step 30: Architecture Context

## MANDATORY EXECUTION RULES

- WEB SEARCH REQUIRED — verify technology claims against official docs
- USE Context7 MCP for framework/library documentation lookups
- ARCHITECTURE FOLLOWS PRODUCT — decisions must trace to product requirements
- WRITE output to spec file BEFORE presenting to user
- ALL output in English (spec files); conversation in Chinese

## PREREQUISITES

- Round 2 completed (steps 20-22) with [C], OR user chose "Architecture Change" starting at step-30
- `.ultra/specs/architecture.md` exists

## CONTEXT BOUNDARIES

- Focus: Quality goals, constraints, and system context (arc42 §1-3)
- Decisions must be grounded in product requirements from product.md
- This is about WHAT the system must achieve, not HOW to build it (that's step-31)

## SEARCH STRATEGY (MANDATORY)

```
Search: "{{product_domain}} architecture quality attributes"
Search: "{{product_domain}} system integration patterns"
Search: "{{product_domain}} technical constraints regulations"
```

Use Context7 MCP for specific framework/library documentation.

## EXECUTION SEQUENCE

### 1. Define Quality Goals

Derive from product.md §6 (Success Metrics) and user scenarios:

| Quality Attribute | Concrete Scenario | Priority |
|------------------|-------------------|----------|
| Performance | [e.g., "API response < 200ms for 95th percentile"] | [1-3] |
| Scalability | [e.g., "Handle 10K concurrent users"] | [1-3] |
| Security | [e.g., "SOC 2 compliance, encrypted at rest"] | [1-3] |
| Availability | [e.g., "99.9% uptime, < 5min recovery"] | [1-3] |
| Maintainability | [e.g., "New developer productive in < 1 week"] | [1-3] |

Ask user via AskUserQuestion: "Which quality attributes matter most? Performance? Security? Scalability?"

### 2. Identify Constraints

**Technical constraints**:
- Required platforms/browsers
- Mandatory integrations
- Technology restrictions (e.g., "must use Python for ML team compatibility")

**Organizational constraints**:
- Team size and skill profile
- Budget limitations
- Timeline constraints

**Regulatory constraints**:
- Data privacy (GDPR, CCPA)
- Industry regulations
- Compliance requirements

### 3. Map System Context

Identify all external systems and interfaces:

**Users**: Who interacts with the system?
**External systems**: What APIs, services, databases does it connect to?
**Data flows**: What data enters and leaves the system?

### 4. Write Output

**WRITE IMMEDIATELY** to `.ultra/specs/architecture.md` §1-3:

```markdown
## §1 Quality Goals

| Priority | Quality Attribute | Scenario | Metric |
|----------|------------------|----------|--------|
| 1 | [Attribute] | [Concrete scenario] | [Measurable target] |
| 2 | [Attribute] | [Concrete scenario] | [Measurable target] |
| 3 | [Attribute] | [Concrete scenario] | [Measurable target] |

## §2 Constraints

### Technical Constraints
| Constraint | Rationale | Impact |
|-----------|-----------|--------|
| [Constraint] | [Why this exists] | [What it limits] |

### Organizational Constraints
| Constraint | Rationale | Impact |
|-----------|-----------|--------|
| [Constraint] | [Why this exists] | [What it limits] |

### Regulatory Constraints
| Constraint | Rationale | Impact |
|-----------|-----------|--------|
| [Constraint] | [Why this exists] | [What it limits] |

## §3 System Context

### Context Diagram

**Users**:
- [User type 1]: [How they interact]
- [User type 2]: [How they interact]

**External Systems**:
| System | Direction | Data | Protocol | Notes |
|--------|-----------|------|----------|-------|
| [System A] | Inbound | [What data] | [REST/gRPC/etc] | [Notes] |
| [System B] | Outbound | [What data] | [Protocol] | [Notes] |
| [System C] | Bidirectional | [What data] | [Protocol] | [Notes] |

**Data Flows**:
- [User] → [System] → [External]: [Description of flow]
- [External] → [System] → [User]: [Description of flow]
```

### 5. Present to User and Gate

```
[C] Continue — Context defined, proceed to Solution Strategy
[R] Revise — Adjust quality goals, constraints, or context
```

**HALT — wait for user response before proceeding.**

### 6. Handle Response

- **[C]**: Load next step: `./step-31-solution-strategy.md`
- **[R]**: Revise, update architecture.md §1-3, re-present

## SUCCESS METRICS

- Quality goals are specific and measurable (not "good performance")
- Constraints identified across technical/organizational/regulatory
- System context shows all external interfaces
- All quality goals trace to product requirements
- Output written to architecture.md §1-3

## FAILURE MODES

- Vague quality goals ("system should be fast")
- Missing regulatory constraints
- System context missing key external integrations
- Quality goals not derived from product requirements

## NEXT STEP

After user selects [C], read and follow: `./step-31-solution-strategy.md`
