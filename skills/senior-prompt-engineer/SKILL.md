---
name: senior-prompt-engineer
description: World-class prompt engineering skill for LLM optimization, prompt patterns, structured outputs, and AI product development. Expertise in Claude, GPT-4, prompt design patterns, few-shot learning, chain-of-thought, and AI evaluation. Includes RAG optimization, agent design, and LLM system architecture. Use when building AI products, optimizing LLM performance, designing agentic systems, or implementing advanced prompting techniques.
---

# Senior Prompt Engineer

Production-grade prompt engineering for modern LLM systems.

## When to Use

- Designing or optimizing prompts for Claude/GPT/other LLMs
- Implementing advanced patterns (CoT, Self-Consistency, Meta-Prompting)
- Building RAG pipelines with effective retrieval prompts
- Designing multi-agent orchestration
- Evaluating and benchmarking LLM outputs
- Troubleshooting prompt failures

---

## Part 1: Core Principles

> Source: [Anthropic Claude 4.x Best Practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-4-best-practices)

### 1.1 Be Explicit with Instructions

Claude 4.x models follow instructions precisely. Vague prompts yield vague results.

```markdown
# Less effective
Create an analytics dashboard

# More effective
Create an analytics dashboard. Include as many relevant features
and interactions as possible. Go beyond the basics to create
a fully-featured implementation.
```

### 1.2 Add Context and Motivation

Explain WHY, not just WHAT. Context helps models generalize.

```markdown
# Less effective
NEVER use ellipses

# More effective
Your response will be read aloud by a text-to-speech engine,
so never use ellipses since the TTS engine cannot pronounce them.
```

### 1.3 Match Prompt Style to Output Style

The formatting in your prompt influences the response style:
- Want prose? Write your prompt in prose
- Want structured data? Use structured format in prompt
- Want minimal markdown? Remove markdown from your prompt

### 1.4 Tell What TO DO, Not What NOT TO DO

```markdown
# Less effective
Do not use markdown in your response

# More effective
Your response should be composed of smoothly flowing prose paragraphs.
```

---

## Part 2: Foundational Patterns

### 2.1 Zero-Shot Prompting

Direct instruction without examples. Works well for Claude 4.x due to strong instruction following.

```markdown
Classify the sentiment of this review as positive, negative, or neutral.
Output only the classification label.

Review: "{text}"
Classification:
```

**When to use**: Simple tasks, well-defined outputs, when examples might bias

### 2.2 Few-Shot Prompting

Provide 2-5 examples to establish pattern. Critical for format consistency.

```markdown
Extract names and roles from text. Output as JSON.

Text: "Alice is a software engineer and Bob is a doctor."
Output: [{"name": "Alice", "role": "software engineer"}, {"name": "Bob", "role": "doctor"}]

Text: "Charlie teaches math and Diana practices law."
Output: [{"name": "Charlie", "role": "teacher"}, {"name": "Diana", "role": "lawyer"}]

Text: "{user_input}"
Output:
```

**Best practices**:
- Use diverse examples covering edge cases
- Maintain consistent format across all examples
- Include boundary cases (empty input, ambiguous cases)
- Order: simple → complex

### 2.3 Chain-of-Thought (CoT)

Decompose reasoning into explicit steps. Essential for math, logic, multi-step problems.

```markdown
Solve this problem step by step.

Question: {question}

Let me work through this systematically:
1. First, I'll identify the key information...
2. Then, I'll analyze the relationships...
3. Finally, I'll calculate the answer...

Answer:
```

**Variants**:
| Variant | Description | Use Case |
|---------|-------------|----------|
| Zero-shot CoT | Add "Let's think step by step" | Quick reasoning boost |
| Manual CoT | Provide reasoning examples | Complex domain-specific tasks |
| Auto-CoT | Let model generate diverse chains | Research, exploration |

### 2.4 Structured Output

Force specific output format using schemas, XML tags, or prefill.

**JSON with Schema**:
```markdown
Analyze this text and respond in this exact JSON format:
{
  "sentiment": "positive" | "negative" | "neutral",
  "confidence": number between 0 and 1,
  "key_phrases": ["string array"],
  "summary": "string under 100 chars"
}

Text: "{input}"
Output:
```

**XML Tags** (Claude-optimized):
```markdown
Analyze the code and provide feedback.

<code>
{code_snippet}
</code>

Respond with:
<analysis>Your detailed analysis</analysis>
<suggestions>Improvement suggestions</suggestions>
<rating>1-10 score</rating>
```

**Prefill Technique** (Claude-specific):
```python
# Force JSON output by prefilling assistant response
response = client.messages.create(
    model="claude-sonnet-4-5-20250929",
    messages=[
        {"role": "user", "content": prompt},
        {"role": "assistant", "content": "{"}  # Prefill
    ]
)
```

---

## Part 3: Advanced Techniques

### 3.1 Self-Consistency

Generate multiple reasoning paths, select most common answer. 3-5x accuracy boost on reasoning tasks.

**How it works**:
1. Sample N responses with temperature > 0
2. Extract final answer from each
3. Return majority answer

```python
def self_consistency(prompt, n=5, temperature=0.7):
    answers = []
    for _ in range(n):
        response = generate(prompt, temperature=temperature)
        answer = extract_final_answer(response)
        answers.append(answer)
    return most_common(answers)
```

**When to use**: Arithmetic, logic puzzles, multi-step reasoning where single-pass fails

### 3.2 Tree of Thoughts (ToT)

Explore multiple reasoning branches, evaluate each, backtrack if needed.

```markdown
Consider this problem: {problem}

Generate 3 different initial approaches:
<approach_1>First possible direction...</approach_1>
<approach_2>Second possible direction...</approach_2>
<approach_3>Third possible direction...</approach_3>

Evaluate each approach (score 1-10):
<evaluation>
Approach 1: [score] - [reasoning]
Approach 2: [score] - [reasoning]
Approach 3: [score] - [reasoning]
</evaluation>

Pursue the highest-scoring approach and develop it further...
```

**When to use**: Creative problem-solving, strategic planning, complex puzzles

### 3.3 Meta-Prompting

Two-stage process: first generate optimal prompt structure, then use it.

```markdown
# Stage 1: Generate meta-prompt
Given this task: {task_description}

Design an optimal prompt structure that includes:
1. Clear role definition
2. Input/output format specification
3. Relevant constraints
4. Quality criteria

Output the prompt template:

# Stage 2: Use generated prompt
{generated_prompt_template}

Input: {actual_input}
```

**Advantages**:
- Token efficient (structure over examples)
- Reduces few-shot bias
- Works well for novel tasks

### 3.4 Reflection and Self-Critique

Have model evaluate and improve its own output.

```markdown
<task>{original_task}</task>

<initial_response>{first_attempt}</initial_response>

Now critically evaluate your response:
1. What assumptions did you make?
2. What could be wrong or incomplete?
3. What would a skeptical expert question?

<critique>Your self-evaluation</critique>

Based on this critique, provide an improved response:
<improved_response>...</improved_response>
```

---

## Part 4: Domain-Specific Patterns

### 4.1 RAG (Retrieval-Augmented Generation)

**Query Rewriting** - Transform user query for better retrieval:
```markdown
Original query: {user_query}

Rewrite this query to improve search retrieval:
1. Expand abbreviations and acronyms
2. Add relevant synonyms
3. Make implicit context explicit
4. Split compound questions if needed

Return 2-3 rewritten queries as JSON array:
```

**Context Integration** - Grounded generation with citations:
```markdown
Answer the question using ONLY the provided context.
If the context doesn't contain the answer, say "I don't have enough information."

<context>
{retrieved_chunks}
</context>

Question: {user_question}

Instructions:
- Quote directly when possible
- Cite sources with [1], [2], etc.
- Never invent facts not in context
- If uncertain, say "Based on the context, I'm not certain about..."

Answer:
```

**Hallucination Prevention**:
```markdown
STRICT GROUNDING RULES:
1. ONLY use information from <context> tags
2. If a claim cannot be traced to context, prefix with "I cannot verify this"
3. Never invent dates, statistics, or proper nouns
4. When quoting, use exact text with citation
5. If asked about something not in context, say "The provided documents don't contain information about this"
```

### 4.2 Agent Design

**ReAct Pattern** (Reasoning + Acting):
```markdown
You have access to these tools:
{tool_descriptions}

Use this format for each step:
Thought: What I need to do and why
Action: tool_name
Action Input: {"param": "value"}
Observation: [tool result appears here]
... (repeat Thought/Action/Observation as needed)
Thought: I have enough information to answer
Final Answer: {answer}

Question: {user_question}
```

**Planning Agent**:
```markdown
Break down this complex task into steps:

Task: {complex_task}

For each step, specify:
1. What needs to be done (action)
2. What tools/resources are needed
3. Dependencies on other steps
4. Success criteria
5. Estimated complexity (low/medium/high)

Output as numbered plan with dependencies marked.
```

**Tool Definition Best Practices**:
```json
{
  "name": "search_database",
  "description": "Search the product database. Use when user asks about product availability, pricing, or specifications. Returns up to 10 matching products.",
  "parameters": {
    "query": {
      "type": "string",
      "description": "Search query - product name, category, or feature"
    },
    "filters": {
      "type": "object",
      "description": "Optional filters: {price_max, category, in_stock}",
      "required": false
    }
  }
}
```

### 4.3 Multi-Turn Conversation

**Context Carryover**:
```markdown
<conversation_summary>
Key facts established:
- User is building a React app
- Using TypeScript
- Needs authentication feature
</conversation_summary>

<current_turn>
User: How should I structure the auth components?
</current_turn>

Continue the conversation maintaining context consistency.
```

**State Management Across Windows** (Claude 4.5):
```markdown
Your context window will be automatically compacted as it approaches limit.
Before compaction:
1. Save progress to progress.txt
2. Update tests.json with current status
3. Commit any working code to git

When resuming:
1. Read progress.txt for context
2. Check tests.json for remaining work
3. Review git log for recent changes
```

---

## Part 5: Model-Specific Guidelines

### 5.1 Claude 4.x (Sonnet/Opus 4.5)

| Behavior | Guidance |
|----------|----------|
| Precise instruction following | Be explicit; vague = vague output |
| Thinking sensitivity (Opus) | Replace "think" with "consider", "evaluate", "analyze" |
| Parallel tool calling | Claude aggressively parallelizes; add sequencing if needed |
| File creation tendency | Add "clean up temporary files" instruction |
| Over-engineering | Add "minimal solution, no extra features" |

**XML Tags Work Best**:
```markdown
<context>Background information</context>
<task>What to do</task>
<constraints>Rules to follow</constraints>
<output_format>Expected structure</output_format>
```

**Thinking/Extended Thinking**:
```markdown
After receiving tool results, carefully reflect on their quality
and determine optimal next steps before proceeding. Use your thinking
to plan and iterate based on this new information.
```

### 5.2 GPT-5.x

| Behavior | Guidance |
|----------|----------|
| Agentic task handling | Provide preambles before major tool decisions |
| TODO tracking | Use TODO tool for workflow progress |
| Long context (>10k tokens) | Have model outline key sections first |
| Token efficiency | More efficient on medium-to-complex tasks |

**Agentic Best Practices**:
```markdown
For this task:
1. Plan thoroughly before acting
2. Decompose into sub-tasks
3. Reflect after each tool call
4. Track progress with TODO updates
5. Resolve completely before yielding control
```

---

## Part 6: Evaluation Framework

### 6.1 Output Quality Dimensions

| Dimension | Criteria | Weight |
|-----------|----------|--------|
| **Accuracy** | Factually correct, no hallucinations | High |
| **Relevance** | Addresses actual question | High |
| **Completeness** | Covers all aspects | Medium |
| **Coherence** | Logical flow, well-structured | Medium |
| **Conciseness** | No unnecessary content | Low |

### 6.2 LLM-as-Judge

```markdown
Evaluate this response on a scale of 1-5:

<question>{question}</question>
<response>{response}</response>
<reference>{reference_answer}</reference>

Score each dimension:
- Accuracy (1-5): Is information correct?
- Relevance (1-5): Does it answer the question?
- Completeness (1-5): Are all aspects covered?
- Clarity (1-5): Is it easy to understand?

<scores>
accuracy: X
relevance: X
completeness: X
clarity: X
</scores>

<justification>Brief reasoning for each score</justification>
```

### 6.3 A/B Comparison

```markdown
Compare these two responses:

Question: {question}

<response_a>{response_a}</response_a>
<response_b>{response_b}</response_b>

Evaluate on: accuracy, helpfulness, clarity, completeness

<comparison>
Winner: A | B | Tie
Confidence: High | Medium | Low
Reasoning: [specific differences that determined winner]
</comparison>
```

---

## Part 7: Production Considerations

### 7.1 Token Efficiency

| Strategy | Savings | Trade-off |
|----------|---------|-----------|
| Shorter examples in few-shot | 30-50% | Slight accuracy drop |
| Meta-prompting over few-shot | 40-60% | Needs model with strong priors |
| Structured output over prose | 20-30% | Less natural language |
| Remove redundant instructions | 10-20% | None if done carefully |

### 7.2 Temperature Tuning

| Task Type | Temperature | Reasoning |
|-----------|-------------|-----------|
| Factual Q&A | 0.0-0.3 | Consistency, accuracy |
| Code generation | 0.0-0.2 | Correctness over creativity |
| Creative writing | 0.7-1.0 | Diversity, novelty |
| Self-consistency | 0.5-0.8 | Need diverse paths |
| Classification | 0.0 | Deterministic output |

### 7.3 Error Handling

```markdown
<error_handling>
If you cannot complete the task:
1. Explain what specific information is missing
2. Suggest what additional context would help
3. Provide partial answer if possible with caveats
4. Never fabricate information to fill gaps
</error_handling>
```

### 7.4 Latency Optimization

- **Streaming**: Use for long outputs to improve perceived latency
- **Caching**: Cache common prompt prefixes
- **Parallel calls**: Run independent evaluations concurrently
- **Model selection**: Use smaller models for simple tasks (Haiku for classification)

---

## Part 8: Anti-Patterns

| Anti-Pattern | Problem | Fix |
|--------------|---------|-----|
| Vague instructions | Inconsistent outputs | Be specific and explicit |
| No examples | Model guesses format | Add 2-3 clear examples |
| Conflicting rules | Confusion, random behavior | Prioritize rules explicitly |
| Too many constraints | Rigid, unnatural output | Focus on key requirements |
| Negative instructions | Model focuses on forbidden | Tell what TO DO instead |
| Assuming model knowledge | Hallucinations | Provide context explicitly |
| Long monolithic prompts | Lost in middle | Use XML structure |
| Over-prompting for Claude 4.x | Over-triggering | Use normal language |

---

## Quick Reference

```bash
# Optimize existing prompt
/senior-prompt-engineer optimize: {your_prompt}

# Design prompt for task
/senior-prompt-engineer design: {task_description}

# Evaluate prompt effectiveness
/senior-prompt-engineer evaluate: {prompt} with {test_cases}

# RAG prompt design
/senior-prompt-engineer rag: {use_case}

# Agent prompt design
/senior-prompt-engineer agent: {tools_and_goals}

# Debug failing prompt
/senior-prompt-engineer debug: {prompt} failure: {observed_issue}
```

---

## Sources

- [Anthropic Claude 4.x Best Practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-4-best-practices)
- [Anthropic Courses - Prompt Engineering](https://github.com/anthropics/courses)
- [Anthropic Cookbook](https://github.com/anthropics/anthropic-cookbook)
- [OpenAI GPT-5 Prompting Guide](https://cookbook.openai.com/examples/gpt-5/gpt-5_prompting_guide)
- [Prompt Engineering Guide](https://www.promptingguide.ai/techniques)
- [OpenAI Orchestrating Agents](https://cookbook.openai.com/examples/orchestrating_agents)
