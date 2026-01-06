---
name: senior-prompt-engineer
description: World-class prompt engineering skill for LLM optimization, prompt patterns, structured outputs, and AI product development. Expertise in Claude, GPT-4, prompt design patterns, few-shot learning, chain-of-thought, and AI evaluation. Includes RAG optimization, agent design, and LLM system architecture. Use when building AI products, optimizing LLM performance, designing agentic systems, or implementing advanced prompting techniques.
allowed-tools: AskUserQuestion, Read, Write, Glob, Grep
---

# Prompt Engineer Skill Guide

> **Purpose**: Transform user's vague requirements into production-grade prompts for any LLM.

## Use Cases

| Task | Template | Output |
|------|----------|--------|
| Content generation prompt | content-gen | Prompt for articles/code/creative |
| Data extraction prompt | extraction | Few-shot prompt for structured output |
| Reasoning/analysis prompt | reasoning | CoT prompt for complex tasks |
| Chatbot system prompt | dialogue | System prompt with persona/rules |
| Agent prompt | agent | ReAct pattern with tool definitions |
| RAG prompt | rag | Grounded generation with citations |

## Running a Task

### Defaults
- **Target Model**: Claude (Sonnet 4.5)
- **Output Language**: English
- **Template**: Auto-detect based on task type

### Invocation Flow

**Step 1: Gather Requirements**

Use `AskUserQuestion` with these questions:

```
Question 1: Target Model
Header: "Model"
Options:
- "Claude (Sonnet/Opus/Haiku)" (Recommended)
- "GPT (4o/4/3.5)"
- "Other LLM"

Question 2: Task Type
Header: "Task"
Options:
- "Content Generation (articles, code, creative)"
- "Data Extraction / Classification"
- "Reasoning / Analysis"
- "Chatbot / Dialogue System"
- "Agent with Tools"
- "RAG (Retrieval-Augmented)"

Question 3: Output Format
Header: "Output"
Options:
- "JSON (structured data)"
- "Markdown (formatted text)"
- "Plain text"
- "Code"

Question 4: Usage Context
Header: "Usage"
Options:
- "API integration (production)"
- "Manual use (one-off)"
- "Embedded in application"
```

**Step 2: Select Template**

Based on user's answers, select appropriate template from Templates section below.

**Step 3: Customize Template**

Ask follow-up questions specific to the selected template:

| Template | Follow-up Questions |
|----------|---------------------|
| content-gen | Role, tone, length, audience |
| extraction | Target fields, example input/output |
| reasoning | Problem domain, reasoning depth |
| dialogue | Persona name, capabilities, restrictions |
| agent | Available tools, behavior rules |
| rag | Citation format, grounding strictness |

**Step 4: Generate Prompt**

Fill template with collected information. Apply model-specific optimizations:

| Model | Optimizations |
|-------|---------------|
| Claude | Use XML tags (`<context>`, `<task>`), avoid "think" word for Opus, positive instructions |
| GPT | Use Markdown structure, separate system/user messages |
| Other | Use clear delimiters, explicit format instructions |

**Step 5: Deliver Output**

Output format:
```
## Optimized Prompt

[Complete prompt content]

---

## Usage Instructions

- **Variables**: `{variable}` placeholders to replace
- **API Call**: Model, temperature, max_tokens recommendations
- **Notes**: Key design decisions explained
```

## Quick Reference

| User Request | Action |
|--------------|--------|
| "Help me write a prompt" | Ask target model + task type first |
| "Optimize this prompt" | Analyze existing prompt, identify issues, apply template |
| "This prompt doesn't work" | Diagnose issue, ask for expected vs actual output |
| "I want AI to do X" | Map X to task type, select template |

## Following Up

- After delivering prompt, use `AskUserQuestion`:
  - Option A: "Test this prompt now" - help user test
  - Option B: "Modify the prompt" - iterate on design
  - Option C: "Done" - end session
- If user reports issues, diagnose and iterate

## Error Handling

- If user request is too vague, ask for concrete example of desired output
- If task doesn't fit templates, build custom prompt using general structure
- If user can't decide, recommend most common choice

---

## Templates

### content-gen

| Config | Value |
|--------|-------|
| Pattern | Role + Context + Task + Constraints + Format |
| Best For | Articles, code, creative writing, marketing copy |

**Template**:
```
You are a {role} with expertise in {domain}.

<task>
{task_description}
</task>

<requirements>
- Tone: {tone}
- Length: {length}
- Audience: {audience}
- Include: {elements}
</requirements>

<output_format>
{format_specification}
</output_format>

<input>
{user_input}
</input>
```

---

### extraction

| Config | Value |
|--------|-------|
| Pattern | Few-shot with consistent examples |
| Best For | Data extraction, classification, parsing |

**Template**:
```
Extract {target_info} from the text and output as {format}.

Example 1:
Input: "{example_input_1}"
Output: {example_output_1}

Example 2:
Input: "{example_input_2}"
Output: {example_output_2}

Example 3:
Input: "{example_input_3}"
Output: {example_output_3}

Now process:
Input: "{user_input}"
Output:
```

**Best Practices**:
- Use 3-5 diverse examples
- Include edge cases in examples
- Maintain exact format consistency

---

### reasoning

| Config | Value |
|--------|-------|
| Pattern | Chain-of-Thought with structured output |
| Best For | Math, logic, analysis, decision-making |

**Template**:
```
Analyze the following and provide your conclusion.

<problem>
{problem_description}
</problem>

Work through this systematically:
1. Identify the key information and constraints
2. Break down into sub-problems if needed
3. Analyze each component
4. Consider edge cases and potential issues
5. Form your conclusion with reasoning

<analysis>
[Step-by-step reasoning here]
</analysis>

<conclusion>
[Final answer with confidence level]
</conclusion>
```

---

### dialogue

| Config | Value |
|--------|-------|
| Pattern | System prompt with persona + rules + examples |
| Best For | Chatbots, customer service, virtual assistants |

**Template**:
```
You are {character_name}, a {role} at {organization}.

<persona>
- Personality: {traits}
- Communication style: {style}
- Expertise: {expertise}
</persona>

<capabilities>
You can help users with:
- {capability_1}
- {capability_2}
- {capability_3}
</capabilities>

<rules>
- Always: {required_behaviors}
- Never: {prohibited_behaviors}
- When asked about {sensitive_topic}: {handling_instruction}
</rules>

<response_format>
- Length: {max_length}
- Tone: {tone}
- Include: {elements}
</response_format>
```

---

### agent

| Config | Value |
|--------|-------|
| Pattern | ReAct with tool definitions |
| Best For | Tool-using agents, automation, multi-step tasks |

**Template**:
```
You are an AI assistant with access to the following tools:

<tools>
{tool_definitions}
</tools>

<behavior>
When responding to user requests:
1. Determine if tools are needed to complete the task
2. If yes, select the appropriate tool and provide correct parameters
3. Wait for tool results before proceeding
4. Use results to formulate your response
5. If no tools needed, respond directly
</behavior>

<output_format>
When using tools:
Action: {tool_name}
Action Input: {parameters_json}

When providing final answer:
Final Answer: {your_response}
</output_format>

<rules>
- {rule_1}
- {rule_2}
</rules>

User request: {user_query}
```

---

### rag

| Config | Value |
|--------|-------|
| Pattern | Grounded generation with citation rules |
| Best For | Q&A over documents, knowledge bases, search |

**Template**:
```
Answer the question using ONLY the provided context.

<context>
{retrieved_documents}
</context>

<grounding_rules>
- Only use information explicitly stated in the context
- If the answer is not in the context, say "I don't have this information in the provided documents"
- Cite sources using [{source_id}] format
- Never invent facts, dates, statistics, or proper nouns
- When uncertain, say "Based on the context, I'm not certain about..."
</grounding_rules>

<output_format>
- Provide direct answer first
- Include citations inline
- List sources at the end if multiple used
</output_format>

Question: {user_question}

Answer:
```

---

## Anti-Pattern Handling

| User Mistake | How to Handle |
|--------------|---------------|
| "Write me a good prompt" | Ask: "What task should this prompt accomplish?" |
| Instructions too vague | Ask for example of desired output |
| No output format specified | Add explicit format requirement |
| Examples inconsistent | Normalize example format |
| Too many negative rules | Convert to positive instructions |
| One prompt doing too much | Recommend splitting into multiple prompts |
| Assuming model knowledge | Add explicit context |

---

## Model-Specific Tips

### Claude (Sonnet/Opus 4.5)

- Use XML tags for structure: `<context>`, `<task>`, `<rules>`, `<output>`
- For Opus: Replace "think" with "consider", "analyze", "evaluate"
- Prefer positive instructions over negative ones
- Claude follows instructions precisely - be explicit

### GPT (4o/4/3.5)

- Use Markdown headers for structure
- Put core instructions in system message
- Put input data in user message
- GPT generalizes well from short, clear prompts

### General Tips

- Match prompt style to desired output style
- Include 2-3 examples for format consistency
- Specify edge case handling explicitly
- Keep instructions concise but complete
