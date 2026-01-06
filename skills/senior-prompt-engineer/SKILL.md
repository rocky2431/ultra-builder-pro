---
name: senior-prompt-engineer
description: Expert prompt engineering for LLM optimization. Use when designing prompts, implementing few-shot/CoT patterns, building RAG systems, designing agents, or evaluating LLM outputs.
---

# Senior Prompt Engineer

Expert-level prompt engineering for production LLM systems.

## When to Use

- Designing or optimizing prompts for Claude/GPT/other LLMs
- Implementing advanced patterns (few-shot, CoT, self-consistency)
- Building RAG pipelines with effective retrieval prompts
- Designing multi-agent orchestration
- Evaluating and benchmarking LLM outputs

## Core Prompt Patterns

### 1. Few-Shot Learning

```markdown
You are a sentiment classifier.

Examples:
Input: "This product exceeded my expectations!"
Output: {"sentiment": "positive", "confidence": 0.95}

Input: "Terrible experience, would not recommend."
Output: {"sentiment": "negative", "confidence": 0.92}

Input: "It's okay, nothing special."
Output: {"sentiment": "neutral", "confidence": 0.78}

Now classify:
Input: "{user_input}"
Output:
```

**Best Practices**:
- 3-5 diverse examples covering edge cases
- Consistent format across examples
- Include confidence scores for calibration

### 2. Chain-of-Thought (CoT)

```markdown
Solve this step by step:

Question: {question}

Let's think through this:
1. First, identify the key information...
2. Then, consider the relationships...
3. Finally, calculate/conclude...

Answer:
```

**Variants**:
- Zero-shot CoT: "Let's think step by step"
- Self-consistency: Generate multiple reasoning paths, vote on answer
- Tree-of-Thought: Explore branching reasoning paths

### 3. Structured Output

```markdown
Respond in this exact JSON format:
{
  "analysis": "string - your analysis",
  "decision": "approve" | "reject" | "review",
  "confidence": number between 0 and 1,
  "reasoning": ["string array of reasons"]
}

Do not include any text outside the JSON.
```

**Tips**:
- Use JSON Schema or TypeScript types for complex structures
- Provide examples of valid output
- Explicitly state constraints

### 4. Role Prompting

```markdown
You are a {role} with expertise in {domain}.

Your responsibilities:
- {responsibility_1}
- {responsibility_2}

Your constraints:
- {constraint_1}
- {constraint_2}

Respond as this expert would.
```

### 5. Meta-Prompting (Prompt Generation)

```markdown
Generate a prompt for the following task:

Task: {task_description}
Input format: {input_format}
Output format: {output_format}
Quality criteria: {criteria}

The generated prompt should:
1. Be clear and unambiguous
2. Include relevant examples
3. Handle edge cases
4. Produce consistent outputs
```

## RAG Prompt Design

### Query Rewriting

```markdown
Original query: {user_query}

Rewrite this query to improve retrieval:
1. Expand abbreviations
2. Add relevant synonyms
3. Make implicit context explicit
4. Split compound questions

Rewritten queries (return as JSON array):
```

### Context Integration

```markdown
Use the following context to answer the question.
If the context doesn't contain the answer, say "I don't have enough information."

Context:
{retrieved_chunks}

Question: {user_question}

Answer (cite sources with [1], [2], etc.):
```

### Hallucination Prevention

```markdown
STRICT RULES:
1. Only use information from the provided context
2. If uncertain, say "Based on the context, I'm not sure about..."
3. Never invent facts, dates, or statistics
4. Quote directly when possible

Context: {context}
Question: {question}
```

## Agent Prompt Design

### ReAct Pattern

```markdown
You have access to these tools:
{tool_descriptions}

Use this format:
Thought: What I need to do next
Action: tool_name
Action Input: {"param": "value"}
Observation: [tool result will appear here]
... (repeat Thought/Action/Observation)
Thought: I now have enough information
Final Answer: {answer}

Question: {user_question}
```

### Planning Agent

```markdown
Break down this task into steps:

Task: {complex_task}

For each step:
1. What needs to be done
2. What tools/resources are needed
3. Dependencies on other steps
4. Success criteria

Output as numbered plan:
```

## Evaluation Framework

### Output Quality Dimensions

| Dimension | Criteria |
|-----------|----------|
| **Accuracy** | Factually correct, no hallucinations |
| **Relevance** | Addresses the actual question |
| **Completeness** | Covers all aspects |
| **Coherence** | Logical flow, well-structured |
| **Conciseness** | No unnecessary content |

### LLM-as-Judge Prompt

```markdown
Evaluate the following response on a scale of 1-5:

Question: {question}
Response: {response}
Reference (if available): {reference}

Criteria:
- Accuracy (1-5): Is the information correct?
- Relevance (1-5): Does it answer the question?
- Completeness (1-5): Are all aspects covered?

Provide scores and brief justification for each.
```

### A/B Testing Framework

```markdown
Compare these two responses:

Question: {question}

Response A:
{response_a}

Response B:
{response_b}

Which is better? Consider:
1. Accuracy
2. Helpfulness
3. Clarity
4. Completeness

Winner: A/B/Tie
Reasoning:
```

## Optimization Techniques

### 1. Prompt Compression

- Remove redundant instructions
- Use concise examples
- Leverage model's prior knowledge

### 2. Temperature Tuning

| Use Case | Temperature |
|----------|-------------|
| Factual Q&A | 0.0 - 0.3 |
| Creative writing | 0.7 - 1.0 |
| Code generation | 0.0 - 0.2 |
| Brainstorming | 0.8 - 1.0 |

### 3. Iterative Refinement

```
Initial prompt → Test on examples → Identify failures →
Refine prompt → Test again → Repeat until satisfactory
```

## Anti-Patterns to Avoid

| Anti-Pattern | Problem | Fix |
|--------------|---------|-----|
| Vague instructions | Inconsistent outputs | Be specific and concrete |
| No examples | Model guesses format | Add 2-3 clear examples |
| Conflicting rules | Confusion | Prioritize rules explicitly |
| Too many constraints | Rigid, unnatural output | Focus on key requirements |
| No error handling | Fails silently | Add fallback instructions |

## Quick Reference

```bash
# Optimize existing prompt
/senior-prompt-engineer optimize: {your_prompt}

# Design prompt for task
/senior-prompt-engineer design prompt for: {task_description}

# Evaluate prompt effectiveness
/senior-prompt-engineer evaluate: {prompt} against {test_cases}

# RAG prompt design
/senior-prompt-engineer rag prompt for: {use_case}

# Agent prompt design
/senior-prompt-engineer agent prompt with tools: {tool_list}
```
