# Agent Context And Prompting

A strong model with poor context will still perform badly. Context design is the practice of deciding what information the model sees on each turn, and it is one of the highest-leverage areas in agent engineering.

## What Goes Into Context

Every model call in an agent loop sends:

1. **System prompt**: fixed instructions that define the agent's role, rules, and constraints. This stays relatively stable across turns.
2. **Session messages**: the conversation history — user messages, assistant responses, tool_use requests, and tool_result outputs.
3. **Tool definitions**: the list of available tools with their schemas, so the model knows what actions it can request.

The model can only reason about what the runtime sends it. If important information is missing from context, the model cannot use it, no matter how capable it is.

## System Prompt Design

The system prompt should include:

- **Role description**: what the agent is and what domain it operates in.
- **Behavioral rules**: what the agent should always do, should never do, and should ask about.
- **Tool summary**: a list of available tool names so the model knows its action surface.
- **Current state**: a snapshot of the session state (objective, progress, approval status) so the model has situational awareness.

### Dynamic System Prompts

In production agents, the system prompt is not static. It is rebuilt on each turn with current state:

```python
SYSTEM_PROMPT = """
You are a {domain} agent. Your current objective is: {objective}.

Available tools: {tool_names}

Current state:
{state_summary}

Rules:
- {rule_1}
- {rule_2}
"""
```

This pattern — template with injected state — keeps the model grounded in what is actually happening, not just what was true at the start of the session.

## Context Window Management

### The Problem

Agent sessions accumulate history fast. Each turn adds user messages, assistant responses, and tool results. Long tool outputs (logs, file contents, API responses) can consume thousands of tokens in a single turn.

### The Solution: Layered Context

Organize context into layers by recency and importance:

1. **Always present**: system prompt, current objective, tool definitions.
2. **Recent**: the last N turns in full detail.
3. **Summarized**: older turns compressed into a structured summary (see compaction in the memory docs).
4. **Retrieved**: relevant information pulled on demand (knowledge base articles, file contents, database records).

### Avoid Context Dumping

A common mistake is sending everything on every turn. This wastes tokens, increases latency, and can confuse the model with irrelevant information.

Instead:
- Include what matters now.
- Summarize old history when it is no longer needed in full.
- Keep policies and rules separate from task content.
- Use tools to retrieve information on demand rather than pre-loading everything.

## Prompt Caching

Modern APIs support prompt caching: when the beginning of your prompt is identical across turns, the API can cache and reuse that prefix. This reduces latency and cost significantly for agent loops where the system prompt and early context are stable.

Design your prompts with caching in mind:
- Put stable content (system prompt, rules, tool definitions) at the beginning.
- Put dynamic content (recent messages, current state) at the end.
- Minimize unnecessary changes to the prefix between turns.

## Separating Concerns In Prompts

Keep these concerns separate in your prompt structure:

| Section | Purpose | Changes between turns? |
|---------|---------|----------------------|
| Role and rules | Define the agent's identity and constraints | Rarely |
| Tool definitions | Available actions | Only when tools are added/removed |
| Current state | Where the agent is in its workflow | Every turn |
| Recent history | What happened recently | Every turn |
| Policy rules | What the agent is and isn't allowed to do | Rarely |

Mixing these together makes prompts hard to maintain and debug.

## Common Mistakes

- **No state in context**: the model starts every turn without knowing what it already accomplished.
- **Stale context**: the model sees outdated information because the prompt was not rebuilt.
- **Too much context**: sending entire file contents, full API responses, and complete history when summaries would suffice.
- **Policy in task content**: mixing "what to do" instructions with "what you are allowed to do" constraints makes both harder to parse and maintain.
