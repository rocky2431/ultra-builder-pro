# Interactive Question Design - Progressive Discovery

**Purpose**: Standardized AskUserQuestion templates for each step of the 6-step interactive cycle across all 4 research rounds.

**Design Principle**: "What not How" - This file provides question templates (what to ask), not implementation code (how to ask).

**Language Protocol**: Questions are in English for system instructions. At runtime, Claude will translate these to Chinese for user-facing output.

---

## Round 1: Problem Discovery (20-25 min)

### Step 1: Requirement Clarification

**Goal**: Understand problem essence, target users, and success criteria before analysis.

#### Question 1: Target Users

```typescript
{
  question: "Who are the primary target users for this project?",
  header: "Target Users",
  multiSelect: true,
  options: [
    {
      label: "End Consumers (B2C)",
      description: "Individual users, general public, consumer-facing applications"
    },
    {
      label: "Enterprise Clients (B2B)",
      description: "Business customers, corporate clients, enterprise solutions"
    },
    {
      label: "Internal Teams",
      description: "Company employees, internal tools, workflow automation"
    },
    {
      label: "Developers (B2D)",
      description: "Developer tools, APIs, libraries, frameworks"
    }
  ]
}
```

#### Question 2: Core Pain Point

```typescript
{
  question: "What is the most critical problem this project aims to solve?",
  header: "Pain Point",
  multiSelect: false,
  options: [
    {
      label: "Performance Issues",
      description: "Slow response time, high latency, scalability problems"
    },
    {
      label: "Usability Problems",
      description: "Poor user experience, complex workflows, accessibility issues"
    },
    {
      label: "Missing Features",
      description: "Gaps in functionality, unmet user needs, competitive disadvantage"
    },
    {
      label: "Cost Constraints",
      description: "High operational costs, expensive infrastructure, budget limitations"
    },
    {
      label: "Reliability Concerns",
      description: "Frequent downtime, data loss risks, system instability"
    }
  ]
}
```

#### Question 3: Success Criteria

```typescript
{
  question: "How will you measure success for this project?",
  header: "Success Metrics",
  multiSelect: true,
  options: [
    {
      label: "User Growth",
      description: "Active users, user acquisition rate, retention metrics"
    },
    {
      label: "Performance Metrics",
      description: "Response time, throughput, Core Web Vitals (LCP/INP/CLS)"
    },
    {
      label: "Business Metrics",
      description: "Revenue, conversion rate, customer satisfaction"
    },
    {
      label: "Technical Quality",
      description: "Test coverage, code quality, deployment frequency"
    },
    {
      label: "Cost Efficiency",
      description: "Infrastructure costs, development velocity, time to market"
    }
  ]
}
```

---

### Step 3: Analysis Validation

**Goal**: Verify problem understanding accuracy before proceeding to spec generation.

#### Satisfaction Check

```typescript
{
  question: "Does this problem analysis align with your understanding?",
  header: "Validation",
  multiSelect: false,
  options: [
    {
      label: "Satisfied - Continue",
      description: "Analysis is accurate, proceed to spec generation"
    },
    {
      label: "Needs Adjustment",
      description: "Some points need refinement, provide feedback for iteration"
    },
    {
      label: "Critical Miss",
      description: "Major misunderstanding, need to re-clarify requirements"
    }
  ]
}
```

**If "Needs Adjustment" selected**:

```typescript
{
  question: "What aspects need adjustment? (Provide specific feedback)",
  header: "Feedback",
  multiSelect: false,
  options: [
    {
      label: "Provide feedback via text",
      description: "Type your specific adjustment needs"
    }
  ]
}
```

---

### Step 6: Round Satisfaction Rating

**Goal**: Collect quality metrics for continuous improvement.

#### Round Rating

```typescript
{
  question: "Rate your satisfaction with Round 1 (Problem Discovery)",
  header: "Round Rating",
  multiSelect: false,
  options: [
    {
      label: "5 Stars - Excellent",
      description: "Problem fully understood, analysis highly accurate"
    },
    {
      label: "4 Stars - Good",
      description: "Problem well understood, minor improvements possible"
    },
    {
      label: "3 Stars - Acceptable",
      description: "Basic understanding achieved, some gaps remain"
    },
    {
      label: "2 Stars - Poor",
      description: "Significant gaps in understanding, needs major improvement"
    },
    {
      label: "1 Star - Unsatisfactory",
      description: "Failed to understand problem, recommend restart"
    }
  ]
}
```

**If rating < 4**:

```typescript
{
  question: "What could be improved in this round?",
  header: "Improvements",
  multiSelect: false,
  options: [
    {
      label: "Provide suggestions via text",
      description: "Specific improvement suggestions"
    }
  ]
}
```

---

## Round 2: Solution Exploration (20-25 min)

### Step 1: Requirement Clarification

**Goal**: Understand feature priorities and key user scenarios before solution design.

#### Question 1: Feature Priority

```typescript
{
  question: "What are the must-have features for MVP (Minimum Viable Product)?",
  header: "MVP Features",
  multiSelect: true,
  options: [
    {
      label: "Core Functionality",
      description: "Essential features without which the product cannot function"
    },
    {
      label: "User Management",
      description: "Authentication, authorization, user profiles"
    },
    {
      label: "Data Management",
      description: "CRUD operations, data persistence, search/filter"
    },
    {
      label: "Integration",
      description: "Third-party APIs, external services, webhooks"
    },
    {
      label: "Analytics",
      description: "User behavior tracking, reporting, dashboards"
    }
  ]
}
```

#### Question 2: User Scenarios

```typescript
{
  question: "What are the top 3 user scenarios to prioritize?",
  header: "Key Scenarios",
  multiSelect: false,
  options: [
    {
      label: "Describe scenarios via text",
      description: "List 3 most important user journeys"
    }
  ]
}
```

#### Question 3: Non-Functional Requirements

```typescript
{
  question: "What are the critical non-functional requirements?",
  header: "NFRs",
  multiSelect: true,
  options: [
    {
      label: "Performance",
      description: "Response time < 2s, support 10K+ concurrent users"
    },
    {
      label: "Security",
      description: "Data encryption, authentication, OWASP compliance"
    },
    {
      label: "Scalability",
      description: "Horizontal scaling, load balancing, distributed architecture"
    },
    {
      label: "Reliability",
      description: "99.9% uptime, fault tolerance, disaster recovery"
    },
    {
      label: "Accessibility",
      description: "WCAG 2.1 AA compliance, keyboard navigation, screen reader support"
    }
  ]
}
```

---

### Step 3: Analysis Validation

**Goal**: Verify user stories and requirements coverage.

```typescript
{
  question: "Do the generated user stories cover your expected functionality?",
  header: "Coverage Check",
  multiSelect: false,
  options: [
    {
      label: "Satisfied - Comprehensive",
      description: "All key scenarios covered, proceed to Round 3"
    },
    {
      label: "Needs Adjustment",
      description: "Some scenarios missing or incorrect, provide feedback"
    },
    {
      label: "Critical Miss",
      description: "Major functionality missing, need to re-clarify"
    }
  ]
}
```

---

### Step 6: Round Satisfaction Rating

```typescript
{
  question: "Rate your satisfaction with Round 2 (Solution Exploration)",
  header: "Round Rating",
  multiSelect: false,
  options: [
    {
      label: "5 Stars - Excellent",
      description: "User stories comprehensive, requirements clear"
    },
    {
      label: "4 Stars - Good",
      description: "Most scenarios covered, minor additions needed"
    },
    {
      label: "3 Stars - Acceptable",
      description: "Basic functionality defined, some gaps remain"
    },
    {
      label: "2 Stars - Poor",
      description: "Significant functionality gaps, needs major rework"
    },
    {
      label: "1 Star - Unsatisfactory",
      description: "Failed to capture requirements, recommend restart"
    }
  ]
}
```

---

## Round 3: Technology Selection (15-20 min)

### Step 1: Requirement Clarification

**Goal**: Understand tech constraints, team skills, and performance requirements.

#### Question 1: Tech Stack Constraints

```typescript
{
  question: "Are there any technology constraints or preferences?",
  header: "Tech Constraints",
  multiSelect: true,
  options: [
    {
      label: "Must use specific language",
      description: "TypeScript, Python, Go, Java, etc."
    },
    {
      label: "Must use specific framework",
      description: "React, Vue, Next.js, Django, FastAPI, etc."
    },
    {
      label: "Cloud provider constraint",
      description: "AWS, Azure, GCP, self-hosted"
    },
    {
      label: "Database preference",
      description: "PostgreSQL, MongoDB, MySQL, Redis"
    },
    {
      label: "No constraints",
      description: "Open to any technology that fits requirements"
    }
  ]
}
```

#### Question 2: Team Skills

```typescript
{
  question: "What is the team's current skill level?",
  header: "Team Skills",
  multiSelect: true,
  options: [
    {
      label: "Frontend (React/Vue/Angular)",
      description: "Strong experience with modern frontend frameworks"
    },
    {
      label: "Backend (Node.js/Python/Go)",
      description: "Strong experience with backend development"
    },
    {
      label: "DevOps/Cloud",
      description: "Strong experience with CI/CD, cloud infrastructure"
    },
    {
      label: "Database/Data",
      description: "Strong experience with database design, optimization"
    },
    {
      label: "Beginner/Learning",
      description: "Team is learning, prefer technologies with good documentation"
    }
  ]
}
```

#### Question 3: Performance Requirements

```typescript
{
  question: "What are the critical performance requirements?",
  header: "Performance",
  multiSelect: true,
  options: [
    {
      label: "Low Latency (< 100ms)",
      description: "Real-time applications, high-frequency trading, gaming"
    },
    {
      label: "High Throughput (10K+ RPS)",
      description: "Large-scale APIs, data processing, analytics"
    },
    {
      label: "Core Web Vitals (LCP < 2.5s)",
      description: "User-facing web apps, SEO-critical sites"
    },
    {
      label: "Cost Efficiency",
      description: "Optimize for low infrastructure costs"
    },
    {
      label: "Standard Performance",
      description: "Typical web application performance expectations"
    }
  ]
}
```

---

### Step 3: Analysis Validation

**Goal**: Confirm technology selection and trade-offs understanding.

```typescript
{
  question: "Do you agree with the recommended technology stack and trade-offs?",
  header: "Tech Validation",
  multiSelect: false,
  options: [
    {
      label: "Satisfied - Proceed",
      description: "Technology choices are well-justified, proceed to Round 4"
    },
    {
      label: "Needs Adjustment",
      description: "Some technology choices need reconsideration, provide feedback"
    },
    {
      label: "Critical Miss",
      description: "Technology choices don't fit requirements, need to re-evaluate"
    }
  ]
}
```

---

### Step 6: Round Satisfaction Rating

```typescript
{
  question: "Rate your satisfaction with Round 3 (Technology Selection)",
  header: "Round Rating",
  multiSelect: false,
  options: [
    {
      label: "5 Stars - Excellent",
      description: "Technology choices well-justified, confident in decisions"
    },
    {
      label: "4 Stars - Good",
      description: "Technology choices sound, minor concerns addressed"
    },
    {
      label: "3 Stars - Acceptable",
      description: "Technology choices acceptable, some trade-offs unclear"
    },
    {
      label: "2 Stars - Poor",
      description: "Technology choices questionable, need more research"
    },
    {
      label: "1 Star - Unsatisfactory",
      description: "Technology choices inappropriate, recommend restart"
    }
  ]
}
```

---

## Round 4: Risk & Constraints (15-20 min)

### Step 1: Requirement Clarification

**Goal**: Identify critical risks and constraints from user perspective.

#### Question 1: Critical Risks

```typescript
{
  question: "What are your biggest concerns or risks for this project?",
  header: "Risk Concerns",
  multiSelect: true,
  options: [
    {
      label: "Technical Complexity",
      description: "Worried about implementation difficulty, team capability"
    },
    {
      label: "Time Constraints",
      description: "Tight deadlines, market timing, competitive pressure"
    },
    {
      label: "Budget Limitations",
      description: "Limited funding, cost overruns, resource constraints"
    },
    {
      label: "Scalability Risks",
      description: "Uncertain user growth, infrastructure scaling challenges"
    },
    {
      label: "Security Concerns",
      description: "Data breaches, compliance requirements, threat modeling"
    },
    {
      label: "Vendor Lock-in",
      description: "Dependency on specific vendors, migration difficulty"
    }
  ]
}
```

#### Question 2: Project Constraints

```typescript
{
  question: "What are the hard constraints that cannot be negotiated?",
  header: "Constraints",
  multiSelect: true,
  options: [
    {
      label: "Fixed Deadline",
      description: "Must launch by specific date, no extensions"
    },
    {
      label: "Fixed Budget",
      description: "Hard budget cap, cannot exceed allocation"
    },
    {
      label: "Compliance Requirements",
      description: "GDPR, HIPAA, SOC2, industry regulations"
    },
    {
      label: "Technology Restrictions",
      description: "Cannot use certain technologies due to policy/security"
    },
    {
      label: "Team Size",
      description: "Fixed team size, cannot hire more developers"
    }
  ]
}
```

---

### Step 3: Analysis Validation

**Goal**: Verify risk assessment and mitigation strategies.

```typescript
{
  question: "Do the identified risks and mitigation strategies address your concerns?",
  header: "Risk Validation",
  multiSelect: false,
  options: [
    {
      label: "Satisfied - Complete",
      description: "All major risks identified, mitigation strategies sound"
    },
    {
      label: "Needs Adjustment",
      description: "Some risks overlooked or mitigation strategies insufficient"
    },
    {
      label: "Critical Miss",
      description: "Major risks not addressed, need comprehensive risk reassessment"
    }
  ]
}
```

---

### Step 6: Round Satisfaction Rating

```typescript
{
  question: "Rate your satisfaction with Round 4 (Risk & Constraints)",
  header: "Round Rating",
  multiSelect: false,
  options: [
    {
      label: "5 Stars - Excellent",
      description: "All risks identified, confident in mitigation strategies"
    },
    {
      label: "4 Stars - Good",
      description: "Most risks covered, minor additions suggested"
    },
    {
      label: "3 Stars - Acceptable",
      description: "Basic risk assessment complete, some uncertainties remain"
    },
    {
      label: "2 Stars - Poor",
      description: "Significant risks overlooked, need more thorough analysis"
    },
    {
      label: "1 Star - Unsatisfactory",
      description: "Risk assessment inadequate, recommend restart"
    }
  ]
}
```

---

## Final Validation

**Goal**: Overall quality check and improvement suggestions.

### Overall Satisfaction

```typescript
{
  question: "Overall satisfaction with the research process (all rounds)?",
  header: "Overall Rating",
  multiSelect: false,
  options: [
    {
      label: "5 Stars - Excellent",
      description: "Specs 100% complete, confident in proceeding to planning"
    },
    {
      label: "4 Stars - Good",
      description: "Specs mostly complete, minor refinements may be needed"
    },
    {
      label: "3 Stars - Acceptable",
      description: "Specs adequate, some areas need further clarification"
    },
    {
      label: "2 Stars - Poor",
      description: "Specs incomplete, need to revisit specific rounds"
    },
    {
      label: "1 Star - Unsatisfactory",
      description: "Specs inadequate, recommend full research restart"
    }
  ]
}
```

### Improvement Suggestions

```typescript
{
  question: "Any suggestions for improving the research process?",
  header: "Improvements",
  multiSelect: false,
  options: [
    {
      label: "Provide suggestions via text",
      description: "Specific suggestions for process improvement"
    },
    {
      label: "No suggestions",
      description: "Process is satisfactory as-is"
    }
  ]
}
```

---

## Implementation Notes

**For Claude**: When executing /ultra-research, use these question templates directly:

1. **Step 1 (Requirement Clarification)**: Use the corresponding round's Step 1 questions
2. **Step 3 (Analysis Validation)**: Use the corresponding round's Step 3 satisfaction check
3. **Step 6 (Round Rating)**: Use the corresponding round's Step 6 rating questions

**Translation at runtime**: All questions should be translated to Chinese when presented to users, following Language Protocol.

**Customization**: If user context suggests different options are needed, Claude may adapt question options while maintaining question structure.

---

## Quality Assurance

**Question Design Principles**:
- ✅ Clear, unambiguous language
- ✅ 2-4 options per question (not too many to overwhelm)
- ✅ Descriptive labels + detailed descriptions
- ✅ Support multiSelect where options are not mutually exclusive
- ✅ Include "Other" handling via text input when needed

**Expected Outcomes**:
- 80-90% users provide sufficient context in Step 1
- <10% users select "Critical Miss" in Step 3
- Average round rating ≥4 stars
- <5% users request research restart

---

**OUTPUT: User messages in Chinese at runtime; keep this file English-only.**
