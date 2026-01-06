---
name: senior-prompt-engineer
description: World-class prompt engineering skill for LLM optimization, prompt patterns, structured outputs, and AI product development. Expertise in Claude, GPT-4, prompt design patterns, few-shot learning, chain-of-thought, and AI evaluation. Includes RAG optimization, agent design, and LLM system architecture. Use when building AI products, optimizing LLM performance, designing agentic systems, or implementing advanced prompting techniques.
---

# Senior Prompt Engineer

将用户的模糊需求转化为生产级 Prompt。

---

## 触发场景

用户请求：
- "帮我优化这个 prompt"
- "帮我设计一个 prompt 来做 X"
- "这个 prompt 效果不好，帮我改进"
- "我想让 AI 完成 X 任务，帮我写 prompt"

---

## 执行流程

### Step 1: 需求澄清

使用 AskUserQuestion 收集关键信息：

```
必须明确：
1. 目标 LLM（Claude/GPT/其他）
2. 任务类型（生成/分类/推理/对话/Agent）
3. 输入格式（用户会提供什么）
4. 输出格式（期望得到什么）
5. 使用场景（一次性/API调用/嵌入应用）
```

**问题模板**：
```
为了设计最优的 prompt，我需要确认：

1. **目标模型**：这个 prompt 用于哪个模型？
   - Claude (Sonnet/Opus/Haiku)
   - GPT (4o/4/3.5)
   - 其他

2. **任务类型**：
   - 内容生成（文章/代码/创意）
   - 信息提取/分类
   - 推理/分析
   - 对话/客服
   - Agent/工具调用

3. **输出要求**：
   - 格式（JSON/Markdown/纯文本/代码）
   - 长度限制
   - 特殊要求

4. **使用方式**：
   - 手动使用
   - API 集成
   - 嵌入应用
```

### Step 2: 分析与设计

根据收集的信息，选择合适的 prompt 结构：

| 任务类型 | 推荐结构 |
|---------|---------|
| 内容生成 | 角色 + 上下文 + 任务 + 约束 + 输出格式 |
| 分类/提取 | 任务 + 示例(few-shot) + 输入 + 输出格式 |
| 推理分析 | 任务 + CoT 引导 + 输入 |
| 对话系统 | System prompt + 人设 + 规则 + 示例对话 |
| Agent | 角色 + 工具描述 + 行为模式 + 输出格式 |
| RAG | 上下文规则 + 引用要求 + 防幻觉指令 |

### Step 3: 构建 Prompt

**通用结构**（按需组合）：

```markdown
# 1. 角色定义（可选）
You are a [specific role] with expertise in [domain].

# 2. 上下文（如有）
<context>
{background_information}
</context>

# 3. 任务指令
Your task is to [specific action].

# 4. 输入说明
You will receive [input description].

# 5. 输出要求
Respond in [format] with the following structure:
[output_schema]

# 6. 约束/规则
Rules:
- [constraint_1]
- [constraint_2]

# 7. 示例（few-shot，如需要）
Example:
Input: [example_input]
Output: [example_output]

# 8. 实际输入
[Input placeholder or variable]
```

### Step 4: 模型适配

**Claude 优化**：
- 使用 XML 标签分隔结构：`<context>`, `<task>`, `<rules>`
- 避免 "think" 一词（Opus），改用 "consider", "analyze"
- 正向指令优先（说做什么，不说不做什么）

**GPT 优化**：
- 使用 Markdown 结构
- System message 放核心指令
- User message 放输入数据

### Step 5: 输出交付

输出格式：

```markdown
## 优化后的 Prompt

[完整的 prompt 内容]

---

## 使用说明

- **变量**：`{variable_name}` 需要替换为实际值
- **调用方式**：[API/手动/...]
- **推荐参数**：temperature=[X], max_tokens=[Y]

## 设计说明

[简要解释为什么这样设计，关键决策点]
```

---

## Prompt 模板库

### 模板 1: 内容生成

```markdown
You are a professional [role] specializing in [domain].

<task>
Write a [content_type] about [topic].
</task>

<requirements>
- Tone: [formal/casual/technical]
- Length: [word_count] words
- Audience: [target_audience]
- Include: [specific_elements]
</requirements>

<output_format>
[Specify structure: sections, headings, etc.]
</output_format>
```

### 模板 2: 信息提取 (Few-shot)

```markdown
Extract [target_info] from the text and output as JSON.

Example 1:
Input: "[example_text_1]"
Output: {"field1": "value1", "field2": "value2"}

Example 2:
Input: "[example_text_2]"
Output: {"field1": "value3", "field2": "value4"}

Now extract from:
Input: "{user_input}"
Output:
```

### 模板 3: 推理分析 (CoT)

```markdown
Analyze the following and provide your conclusion.

<input>
{data_or_question}
</input>

Think through this step by step:
1. First, identify the key information
2. Then, analyze the relationships
3. Consider potential issues or edge cases
4. Finally, form your conclusion

<analysis>
[Your step-by-step reasoning]
</analysis>

<conclusion>
[Your final answer]
</conclusion>
```

### 模板 4: 对话系统 (System Prompt)

```markdown
You are [character_name], a [role] at [organization].

<personality>
- [trait_1]
- [trait_2]
- [communication_style]
</personality>

<capabilities>
You can help users with:
- [capability_1]
- [capability_2]
</capabilities>

<rules>
- Always [required_behavior]
- Never [prohibited_behavior]
- If asked about [topic], respond with [guidance]
</rules>

<response_format>
Keep responses [length]. Use [tone] tone.
</response_format>
```

### 模板 5: Agent (工具调用)

```markdown
You are an AI assistant with access to the following tools:

<tools>
{tool_definitions_json}
</tools>

<behavior>
When the user asks a question:
1. Determine if tools are needed
2. If yes, call the appropriate tool with correct parameters
3. Use tool results to formulate your response
4. If no tools needed, answer directly
</behavior>

<output_format>
For tool calls, use this exact format:
Action: tool_name
Action Input: {"param": "value"}

For final answers:
Final Answer: [your response]
</output_format>

User: {user_query}
```

### 模板 6: RAG (检索增强)

```markdown
Answer the question using ONLY the provided context.

<context>
{retrieved_documents}
</context>

<rules>
- Only use information from the context above
- If the answer is not in the context, say "I don't have this information in the provided documents"
- Cite sources using [1], [2], etc.
- Never invent facts, dates, or statistics
</rules>

Question: {user_question}

Answer:
```

---

## 质量检查清单

交付前确认：

- [ ] 指令是否明确具体（无歧义）
- [ ] 输出格式是否清晰定义
- [ ] 是否包含必要的示例
- [ ] 是否有处理边界情况的指引
- [ ] 是否适配目标模型的特性
- [ ] 变量占位符是否标注清楚

---

## 反模式警示

| 用户常犯错误 | 我应该如何修正 |
|-------------|---------------|
| "帮我写个好的 prompt" | 追问具体任务和期望输出 |
| 指令过于笼统 | 拆解为具体步骤 |
| 没有输出格式 | 添加明确的格式要求 |
| 示例不一致 | 统一示例格式 |
| 否定指令过多 | 转换为正向指令 |
| 一个 prompt 做太多事 | 建议拆分为多个 prompt |
