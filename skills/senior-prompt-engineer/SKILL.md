---
name: senior-prompt-engineer
description: Transform vague requirements into production-grade prompts using evidence-based principles. Diagnose prompt issues, define boundaries (when RAG/fine-tuning is better), and iterate to quality.
allowed-tools: AskUserQuestion, Read, Write, Glob, Grep
---

# Prompt Engineering Skill

> **Purpose**: Transform user's vague requirements into production-grade prompts using evidence-based principles, not hardcoded templates.

## Core Philosophy

**Prompts are communication, not magic formulas.**

A good prompt is clear communication with a capable assistant. There are principles, not templates.

## When NOT to Use Prompt Engineering

Before writing any prompt, evaluate if prompt engineering is the right approach:

| Signal | Better Approach | Why |
|--------|-----------------|-----|
| Need private/recent knowledge | RAG | Models have knowledge cutoff |
| Need consistent specialized behavior | Fine-tuning | Prompts can't change base behavior |
| Need domain-specific terminology | Fine-tuning + RAG | Models may not know jargon |
| Task requires real-time data | Tool use / RAG | Prompts are static |
| Need to learn from examples at scale | Fine-tuning | Few-shot has limits |

**If any signal matches**: Recommend the better approach, explain why, offer to help with that instead.

---

## Invocation Flow

### Step 1: Understand the Task

Use `AskUserQuestion` to gather:

```
Question 1: Task Description
Header: "Task"
Options:
- "Generate content (articles, code, creative)"
- "Extract/classify data from text"
- "Analyze/reason about a problem"
- "Build a chatbot/assistant persona"
- "Create an agent with tools"
```

**Follow-up based on answer**:
- Ask for a concrete example of desired output
- Ask for constraints (length, format, tone)
- Ask what the prompt will be used for (one-off vs API integration)

### Step 2: Check Boundaries

Evaluate if prompt engineering is sufficient:

| Question | If Yes → |
|----------|----------|
| Does this need knowledge the model doesn't have? | Recommend RAG |
| Does this need consistent specialized behavior at scale? | Recommend Fine-tuning |
| Is this a simple, one-time task? | Proceed with prompt |

If boundary crossed, explain and offer alternatives.

### Step 3: Apply Principles

Build the prompt using these evidence-based principles (from Anthropic official docs):

#### Principle 1: Be Explicit

```
BAD:  "Write something about AI"
GOOD: "Write a 500-word blog post explaining how transformers work to a non-technical audience"
```

#### Principle 2: Provide Context and Motivation

```
BAD:  "Never use ellipses"
GOOD: "Your response will be read by a text-to-speech engine, so never use ellipses since it won't know how to pronounce them"
```

The model generalizes from understanding WHY.

#### Principle 3: Say What TO Do, Not What NOT to Do

```
BAD:  "Don't use markdown"
GOOD: "Write in flowing prose paragraphs without formatting"
```

#### Principle 4: Structure with XML Tags

```xml
<context>
Background information here
</context>

<task>
What you want the model to do
</task>

<constraints>
- Length: 500 words
- Tone: Professional
- Format: Prose paragraphs
</constraints>

<output_format>
How the response should be structured
</output_format>
```

#### Principle 5: Examples Must Match Desired Behavior

If using few-shot, examples must be:
- Consistent in format
- Representative of edge cases
- Free of behaviors you don't want

```
BAD:  One example shows JSON, another shows plain text
GOOD: All examples show identical JSON structure
```

#### Principle 6: For Reasoning, Use Chain-of-Thought

```xml
<task>
Analyze this problem step by step.
</task>

<thinking_format>
Work through this systematically:
1. Identify key information
2. Break into sub-problems
3. Analyze each component
4. Form conclusion with reasoning
</thinking_format>
```

### Step 4: Construct and Deliver

**Output format**:

```markdown
## Prompt

[Complete prompt with XML structure]

---

## Usage Notes

- **Variables**: `{variable}` placeholders to replace
- **When to use**: [Specific scenarios]
- **Limitations**: [What this prompt can't do]
- **Iteration hints**: [How to improve if results aren't good]
```

### Step 5: Offer Iteration

Use `AskUserQuestion`:

```
Question: Next Steps
Header: "Action"
Options:
- "Test this prompt and report results"
- "Modify the prompt"
- "Explain the design decisions"
- "Done"
```

If user reports issues, diagnose:

| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| Too verbose | No length constraint | Add explicit length |
| Wrong format | No format example | Add output_format tag |
| Hallucinating | Task too vague | Add constraints, context |
| Inconsistent | Examples inconsistent | Fix example format |
| Ignoring instructions | Instructions buried | Move to top, use XML |

---

## Quality Checklist

Before delivering, verify:

- [ ] Task is explicit (no guessing required)
- [ ] Context explains WHY, not just WHAT
- [ ] Instructions are positive (do X, not don't Y)
- [ ] Structure uses XML tags for separation
- [ ] Examples (if any) are consistent
- [ ] Output format is specified
- [ ] Limitations are acknowledged

---

## Anti-Patterns

| Pattern | Problem | Fix |
|---------|---------|-----|
| "Be creative" | Too vague | Define what creative means |
| "Don't hallucinate" | Negative instruction | "Only use information from the provided context" |
| "Think step by step" alone | No structure | Provide thinking format |
| Multiple roles in one prompt | Conflicting behaviors | Split into separate prompts |
| Prompt > 2000 tokens | Too complex | Simplify or use RAG |

---

## Advanced Techniques

### Grounded Generation (RAG Pattern)

```xml
<context>
{retrieved_documents}
</context>

<grounding_rules>
- Only use information from the context
- Cite sources using [source_id]
- If not in context, say "I don't have this information"
</grounding_rules>

<question>
{user_question}
</question>
```

### Agent Pattern (Tool Use)

```xml
<tools>
{tool_definitions}
</tools>

<behavior>
1. Determine if tools are needed
2. Select appropriate tool with correct parameters
3. Wait for results before proceeding
4. Use results to formulate response
</behavior>

<output_format>
When using tools: Action: {tool} / Input: {params}
When answering: Final Answer: {response}
</output_format>
```

### Persona Pattern (Chatbot)

```xml
<persona>
You are {name}, a {role} at {org}.
- Personality: {traits}
- Expertise: {areas}
- Communication style: {style}
</persona>

<capabilities>
You can help with: {list}
</capabilities>

<rules>
- Always: {required}
- Never: {prohibited}
- When asked about {sensitive}: {handling}
</rules>
```

---

## Evaluation Criteria

A good prompt should score well on:

| Criterion | Question |
|-----------|----------|
| **Clarity** | Can someone else understand what this prompt wants? |
| **Specificity** | Are edge cases and constraints defined? |
| **Structure** | Is information organized logically? |
| **Completeness** | Does it include all necessary context? |
| **Minimalism** | Is every part necessary? (No bloat) |

---

## Error Recovery

If user says "the prompt doesn't work":

1. **Ask for specifics**: What output did you get? What did you expect?
2. **Check boundaries**: Is this actually a prompt engineering problem?
3. **Diagnose**: Match symptoms to causes table above
4. **Iterate**: Make one change at a time, test

---

## References

- Anthropic Claude 4 Best Practices (platform.claude.com)
- Anthropic Prompt Engineering Interactive Tutorial
- DAIR.AI Prompt Engineering Guide
