# Research Metadata Schema

**Purpose**: Define standardized quality metrics structure for Progressive Interactive Discovery research sessions.

**Use Case**: Saved to `.ultra/docs/research/metadata.json` after each /ultra-research completion for:
- Quality tracking and continuous improvement
- Cross-session comparison and trend analysis
- Research process optimization based on user feedback
- Future ML training data for predictive quality models

---

## Complete JSON Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Ultra Research Metadata",
  "description": "Quality metrics for Progressive Interactive Discovery research sessions",
  "type": "object",
  "required": [
    "projectType",
    "roundsExecuted",
    "roundSatisfaction",
    "overallSatisfaction",
    "totalDuration",
    "timestamp"
  ],
  "properties": {
    "projectType": {
      "type": "string",
      "enum": ["New Project", "Incremental Feature", "Tech Decision", "Custom"],
      "description": "Project type selected in Phase 0"
    },
    "roundsExecuted": {
      "type": "array",
      "items": {
        "type": "integer",
        "minimum": 1,
        "maximum": 4
      },
      "minItems": 1,
      "maxItems": 4,
      "uniqueItems": true,
      "description": "Array of round numbers executed (e.g., [1, 2, 3, 4] for New Project)"
    },
    "roundSatisfaction": {
      "type": "object",
      "properties": {
        "round1": {
          "type": "number",
          "minimum": 1,
          "maximum": 5,
          "description": "User satisfaction rating (1-5 stars) for Round 1"
        },
        "round2": {
          "type": "number",
          "minimum": 1,
          "maximum": 5,
          "description": "User satisfaction rating (1-5 stars) for Round 2"
        },
        "round3": {
          "type": "number",
          "minimum": 1,
          "maximum": 5,
          "description": "User satisfaction rating (1-5 stars) for Round 3"
        },
        "round4": {
          "type": "number",
          "minimum": 1,
          "maximum": 5,
          "description": "User satisfaction rating (1-5 stars) for Round 4"
        }
      },
      "description": "Per-round satisfaction ratings (only include executed rounds)"
    },
    "iterationCounts": {
      "type": "object",
      "properties": {
        "round1": {
          "type": "integer",
          "minimum": 0,
          "maximum": 2,
          "description": "Number of iterations (retries) in Round 1 (max 2)"
        },
        "round2": {
          "type": "integer",
          "minimum": 0,
          "maximum": 2,
          "description": "Number of iterations (retries) in Round 2 (max 2)"
        },
        "round3": {
          "type": "integer",
          "minimum": 0,
          "maximum": 2,
          "description": "Number of iterations (retries) in Round 3 (max 2)"
        },
        "round4": {
          "type": "integer",
          "minimum": 0,
          "maximum": 2,
          "description": "Number of iterations (retries) in Round 4 (max 2)"
        }
      },
      "description": "Per-round iteration counts (0 = no iteration, 1-2 = adjusted)"
    },
    "overallSatisfaction": {
      "type": "number",
      "minimum": 1,
      "maximum": 5,
      "description": "Overall satisfaction rating (1-5 stars) after all rounds complete"
    },
    "totalDuration": {
      "type": "string",
      "pattern": "^\\d+ minutes$",
      "description": "Total time spent on research (e.g., '85 minutes')"
    },
    "improvementSuggestions": {
      "type": "array",
      "items": {
        "type": "string"
      },
      "description": "User-provided suggestions for process improvement"
    },
    "timestamp": {
      "type": "string",
      "format": "date-time",
      "description": "ISO 8601 timestamp when research completed"
    },
    "projectName": {
      "type": "string",
      "description": "Optional project name for tracking"
    },
    "userId": {
      "type": "string",
      "description": "Optional user identifier for multi-user analytics"
    },
    "questionQuality": {
      "type": "object",
      "description": "Quality metrics for core and dynamically generated questions (Hybrid Model tracking)",
      "properties": {
        "coreQuestions": {
          "type": "object",
          "description": "Quality ratings for standardized core questions",
          "patternProperties": {
            "^round[1-4]_q(1[0-3]|[1-9])$": {
              "type": "object",
              "properties": {
                "rating": {
                  "type": "number",
                  "minimum": 1,
                  "maximum": 5,
                  "description": "User rating (1-5 stars) for core question relevance"
                },
                "useful": {
                  "type": "boolean",
                  "description": "Whether user found this question useful"
                }
              },
              "required": ["rating", "useful"]
            }
          }
        },
        "dynamicQuestions": {
          "type": "array",
          "description": "Quality metrics for dynamically generated extension questions",
          "items": {
            "type": "object",
            "properties": {
              "round": {
                "type": "integer",
                "minimum": 1,
                "maximum": 4,
                "description": "Which round this dynamic question was used in"
              },
              "question": {
                "type": "string",
                "description": "The actual question text generated"
              },
              "header": {
                "type": "string",
                "maxLength": 12,
                "description": "Question header (≤12 chars)"
              },
              "context": {
                "type": "string",
                "description": "Project context that triggered this question generation"
              },
              "rating": {
                "type": "number",
                "minimum": 1,
                "maximum": 5,
                "description": "User rating (1-5 stars) for dynamic question relevance"
              },
              "useful": {
                "type": "boolean",
                "description": "Whether user found this dynamic question useful"
              },
              "validationPassed": {
                "type": "boolean",
                "description": "Whether question passed validation on first attempt"
              },
              "retryCount": {
                "type": "integer",
                "minimum": 0,
                "maximum": 2,
                "description": "Number of retries needed (0 = passed first time, 1-2 = needed adjustment)"
              }
            },
            "required": ["round", "question", "header", "context", "rating", "useful", "validationPassed", "retryCount"]
          }
        }
      }
    }
  }
}
```

---

## Example Instances

### Example 1: New Project (Full 4-Round Research)

```json
{
  "projectType": "New Project",
  "roundsExecuted": [1, 2, 3, 4],
  "roundSatisfaction": {
    "round1": 4.5,
    "round2": 5.0,
    "round3": 4.0,
    "round4": 4.5
  },
  "iterationCounts": {
    "round1": 1,
    "round2": 0,
    "round3": 2,
    "round4": 1
  },
  "overallSatisfaction": 4.5,
  "totalDuration": "85 minutes",
  "improvementSuggestions": [
    "Round 3 tech options could include more detail on performance benchmarks",
    "Would be helpful to see cost estimates for each tech stack option"
  ],
  "questionQuality": {
    "coreQuestions": {
      "round1_q1": { "rating": 5.0, "useful": true },
      "round1_q2": { "rating": 4.5, "useful": true },
      "round1_q3": { "rating": 5.0, "useful": true },
      "round1_q4": { "rating": 4.0, "useful": true },
      "round1_q5": { "rating": 4.5, "useful": true },
      "round2_q6": { "rating": 4.5, "useful": true },
      "round2_q7": { "rating": 5.0, "useful": true },
      "round2_q8": { "rating": 4.0, "useful": true },
      "round3_q9": { "rating": 3.5, "useful": true },
      "round3_q10": { "rating": 4.5, "useful": true },
      "round3_q11": { "rating": 4.0, "useful": true },
      "round4_q12": { "rating": 5.0, "useful": true },
      "round4_q13": { "rating": 4.5, "useful": true }
    },
    "dynamicQuestions": [
      {
        "round": 1,
        "question": "是否需要符合 GDPR 数据保护规定？",
        "header": "GDPR",
        "context": "E-commerce platform with EU users",
        "rating": 5.0,
        "useful": true,
        "validationPassed": true,
        "retryCount": 0
      },
      {
        "round": 2,
        "question": "数据量级预期？",
        "header": "Data Volume",
        "context": "Large-scale e-commerce platform",
        "rating": 4.0,
        "useful": true,
        "validationPassed": false,
        "retryCount": 1
      },
      {
        "round": 3,
        "question": "是否需要支持多语言？",
        "header": "i18n",
        "context": "Global e-commerce platform",
        "rating": 3.5,
        "useful": true,
        "validationPassed": true,
        "retryCount": 0
      }
    ]
  },
  "timestamp": "2025-01-19T10:30:00Z",
  "projectName": "E-commerce Platform Redesign"
}
```

### Example 2: Incremental Feature (Round 2-3 Only)

```json
{
  "projectType": "Incremental Feature",
  "roundsExecuted": [2, 3],
  "roundSatisfaction": {
    "round2": 4.0,
    "round3": 5.0
  },
  "iterationCounts": {
    "round2": 1,
    "round3": 0
  },
  "overallSatisfaction": 4.5,
  "totalDuration": "30 minutes",
  "improvementSuggestions": [],
  "timestamp": "2025-01-19T14:00:00Z",
  "projectName": "Add real-time notifications feature"
}
```

### Example 3: Tech Decision (Round 3 Only)

```json
{
  "projectType": "Tech Decision",
  "roundsExecuted": [3],
  "roundSatisfaction": {
    "round3": 4.0
  },
  "iterationCounts": {
    "round3": 1
  },
  "overallSatisfaction": 4.0,
  "totalDuration": "15 minutes",
  "improvementSuggestions": [
    "Include more real-world case studies for each tech option"
  ],
  "timestamp": "2025-01-19T16:00:00Z",
  "projectName": "Choose React vs Vue for new dashboard"
}
```

### Example 4: Custom Flow (Round 1 and 3)

```json
{
  "projectType": "Custom",
  "roundsExecuted": [1, 3],
  "roundSatisfaction": {
    "round1": 5.0,
    "round3": 4.5
  },
  "iterationCounts": {
    "round1": 0,
    "round3": 1
  },
  "overallSatisfaction": 4.5,
  "totalDuration": "40 minutes",
  "improvementSuggestions": [],
  "timestamp": "2025-01-19T18:00:00Z",
  "projectName": "API Gateway Architecture Decision"
}
```

---

## Data Validation Rules

### Required Fields Check

```typescript
function validateRequired(metadata: ResearchMetadata): ValidationResult {
  const required = [
    'projectType',
    'roundsExecuted',
    'roundSatisfaction',
    'overallSatisfaction',
    'totalDuration',
    'timestamp'
  ];

  const missing = required.filter(field => !(field in metadata));

  return {
    valid: missing.length === 0,
    errors: missing.map(field => `Missing required field: ${field}`)
  };
}
```

### Consistency Checks

```typescript
function validateConsistency(metadata: ResearchMetadata): ValidationResult {
  const errors: string[] = [];

  // Check 1: roundSatisfaction keys must match roundsExecuted
  const executedRounds = metadata.roundsExecuted;
  const ratedRounds = Object.keys(metadata.roundSatisfaction)
    .map(key => parseInt(key.replace('round', '')));

  const missingRatings = executedRounds.filter(
    round => !ratedRounds.includes(round)
  );

  if (missingRatings.length > 0) {
    errors.push(`Missing satisfaction ratings for rounds: ${missingRatings}`);
  }

  // Check 2: iterationCounts keys should match roundsExecuted
  const iteratedRounds = Object.keys(metadata.iterationCounts || {})
    .map(key => parseInt(key.replace('round', '')));

  const extraIterations = iteratedRounds.filter(
    round => !executedRounds.includes(round)
  );

  if (extraIterations.length > 0) {
    errors.push(`Iteration counts for non-executed rounds: ${extraIterations}`);
  }

  // Check 3: Satisfaction ratings should be 1-5
  Object.entries(metadata.roundSatisfaction).forEach(([round, rating]) => {
    if (rating < 1 || rating > 5) {
      errors.push(`Invalid rating for ${round}: ${rating} (must be 1-5)`);
    }
  });

  return {
    valid: errors.length === 0,
    errors
  };
}
```

---

## Analysis Queries

### Query 1: Average Satisfaction by Project Type

```typescript
function avgSatisfactionByProjectType(
  metadataList: ResearchMetadata[]
): Record<string, number> {
  const grouped = metadataList.reduce((acc, metadata) => {
    if (!acc[metadata.projectType]) {
      acc[metadata.projectType] = [];
    }
    acc[metadata.projectType].push(metadata.overallSatisfaction);
    return acc;
  }, {} as Record<string, number[]>);

  return Object.entries(grouped).reduce((acc, [type, ratings]) => {
    acc[type] = ratings.reduce((sum, r) => sum + r, 0) / ratings.length;
    return acc;
  }, {} as Record<string, number>);
}

// Example output:
// {
//   "New Project": 4.3,
//   "Incremental Feature": 4.6,
//   "Tech Decision": 4.1,
//   "Custom": 4.5
// }
```

### Query 2: Most Common Iteration Rounds

```typescript
function mostIteratedRounds(
  metadataList: ResearchMetadata[]
): Record<string, number> {
  const iterationFrequency = {
    round1: 0,
    round2: 0,
    round3: 0,
    round4: 0
  };

  metadataList.forEach(metadata => {
    Object.entries(metadata.iterationCounts || {}).forEach(([round, count]) => {
      if (count > 0) {
        iterationFrequency[round as keyof typeof iterationFrequency]++;
      }
    });
  });

  return iterationFrequency;
}

// Example output:
// {
//   "round1": 12,  // 12 sessions had Round 1 iterations
//   "round2": 5,
//   "round3": 18,  // Round 3 most frequently iterated
//   "round4": 8
// }
```

### Query 3: Duration vs Satisfaction Correlation

```typescript
function durationSatisfactionCorrelation(
  metadataList: ResearchMetadata[]
): { correlation: number; data: Array<{duration: number; satisfaction: number}> } {
  const data = metadataList.map(metadata => ({
    duration: parseInt(metadata.totalDuration.split(' ')[0]),
    satisfaction: metadata.overallSatisfaction
  }));

  // Simple Pearson correlation coefficient calculation
  const n = data.length;
  const sumX = data.reduce((sum, d) => sum + d.duration, 0);
  const sumY = data.reduce((sum, d) => sum + d.satisfaction, 0);
  const sumXY = data.reduce((sum, d) => sum + d.duration * d.satisfaction, 0);
  const sumX2 = data.reduce((sum, d) => sum + d.duration ** 2, 0);
  const sumY2 = data.reduce((sum, d) => sum + d.satisfaction ** 2, 0);

  const correlation = (n * sumXY - sumX * sumY) /
    Math.sqrt((n * sumX2 - sumX ** 2) * (n * sumY2 - sumY ** 2));

  return { correlation, data };
}

// Example output:
// {
//   correlation: 0.65,  // Positive correlation: longer duration → higher satisfaction
//   data: [{ duration: 85, satisfaction: 4.5 }, ...]
// }
```

### Query 4: Improvement Suggestions Frequency

```typescript
function topImprovementSuggestions(
  metadataList: ResearchMetadata[]
): Array<{ suggestion: string; count: number }> {
  const suggestionCounts = new Map<string, number>();

  metadataList.forEach(metadata => {
    metadata.improvementSuggestions?.forEach(suggestion => {
      const normalized = suggestion.toLowerCase().trim();
      suggestionCounts.set(
        normalized,
        (suggestionCounts.get(normalized) || 0) + 1
      );
    });
  });

  return Array.from(suggestionCounts.entries())
    .map(([suggestion, count]) => ({ suggestion, count }))
    .sort((a, b) => b.count - a.count)
    .slice(0, 10);
}

// Example output:
// [
//   { suggestion: "include more performance benchmarks", count: 15 },
//   { suggestion: "provide cost estimates", count: 12 },
//   { suggestion: "add more real-world examples", count: 9 },
//   ...
// ]
```

---

## Quality Metrics Dashboard

### Target Thresholds

| Metric | Target | Action if Below Target |
|--------|--------|------------------------|
| **Average Overall Satisfaction** | ≥4.0 | Review low-rated sessions, identify patterns |
| **Round Satisfaction** | All rounds ≥3.5 | Redesign questions for low-rated rounds |
| **Iteration Rate** | <30% need iteration | Improve Step 1 questions to reduce misunderstandings |
| **Completion Rate** | ≥95% | Investigate abandonment reasons |
| **Average Duration** | 70-90 min (New Project) | Optimize if consistently over 100 min |

### Continuous Improvement Workflow

```
1. Collect metadata.json from all research sessions
    ↓
2. Run analysis queries weekly/monthly
    ↓
3. Identify patterns:
   - Which rounds have lowest satisfaction?
   - Which project types have most iterations?
   - What are most common improvement suggestions?
    ↓
4. Update interaction-points.md questions based on findings
    ↓
5. Monitor impact of changes in next period
```

---

## Integration with Ultra Research

### When to Save Metadata

**Trigger**: After Final Validation step in /ultra-research completes

**Location**: `.ultra/docs/research/metadata.json`

**Process**:
1. Collect all quality metrics during research session
2. Construct metadata object following schema
3. Validate using `validateRequired()` and `validateConsistency()`
4. Write to `.ultra/docs/research/metadata.json`
5. Append to global analytics file (optional): `~/.claude/analytics/research-sessions.jsonl`

### Example Save Operation

```typescript
// After Final Validation completes
const metadata: ResearchMetadata = {
  projectType: selectedProjectType,
  roundsExecuted: completedRounds,
  roundSatisfaction: collectedRatings,
  iterationCounts: recordedIterations,
  overallSatisfaction: finalRating,
  totalDuration: `${elapsedMinutes} minutes`,
  improvementSuggestions: collectedSuggestions,
  timestamp: new Date().toISOString(),
  projectName: projectContext.name
};

// Validate
const validation = validateRequired(metadata);
if (!validation.valid) {
  console.error('Metadata validation failed:', validation.errors);
  return;
}

// Save to project-specific location
await writeFile(
  '.ultra/docs/research/metadata.json',
  JSON.stringify(metadata, null, 2)
);

// Optionally append to global analytics (one line per session)
await appendFile(
  '~/.claude/analytics/research-sessions.jsonl',
  JSON.stringify(metadata) + '\n'
);
```

---

## Future Enhancements

### Phase 2: ML Training Data

Once sufficient data collected (100+ sessions):

1. **Predictive Models**:
   - Predict likely satisfaction based on early round performance
   - Predict which rounds will need iteration based on project type
   - Suggest optimal question sequence based on user profile

2. **Personalization**:
   - Learn user preferences (prefers detailed questions vs high-level)
   - Adapt question complexity based on user expertise level
   - Customize options based on previous selections

3. **Process Optimization**:
   - Identify bottleneck rounds (highest iteration rate)
   - A/B test different question phrasings
   - Dynamic question selection based on context

---

**OUTPUT: This schema is for system use; user-facing messages should be in Chinese at runtime.**
