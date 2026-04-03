# Marketing Agent — Runnable Example

A working implementation of the marketing agent from the Agent Build Spec, built using the production agent architecture pattern.

This is not a one-shot script. It is a loop-based agent with tool contracts, session state, permission checks, human-in-the-loop approval, observability logging, and defined stop conditions.

## Quick Start

Requires **Python 3.10+**.

```bash
cd examples/marketing-agent

# Install dependencies
pip install -r requirements.txt

# Set your API key
export ANTHROPIC_API_KEY="your-key-here"

# Run with default goal
python -m src.main

# Run with a custom goal
python -m src.main "Draft two Twitter posts about our open-source launch"

# Specify a campaign
python -m src.main --campaign launch-2025 "Create a LinkedIn post for launch week"
```

## What Happens When You Run It

1. The agent receives your goal and builds context (campaign brief, session state).
2. The model decides the next action — usually fetching trends or the campaign brief first.
3. Read-only tools (trending topics, campaign brief, metrics) execute automatically.
4. Draft tools execute automatically but do not publish.
5. When the model requests `publish_post`, the runtime **blocks and asks you for approval**.
6. If you approve, the post is published. If you deny, the agent stops.
7. The agent loops until the goal is complete, approval is denied, or the turn limit is reached.
8. Every tool call, approval decision, and turn is logged as structured JSON to stderr.

## Architecture

```
src/
  agent.py         Controller loop — builds context, calls model, checks permissions, executes tools
  tools.py         Tool contracts (schemas) and executors (mock implementations)
  permissions.py   Runtime permission policy — auto-allow, ask-first, deny
  state.py         Session state dataclass with history tracking
  observability.py Structured JSON logging for every event
  main.py          CLI entry point
```

## Adapting This To Your Domain

1. Replace the tool contracts and executors in `tools.py` with your domain tools.
2. Update the system prompt in `agent.py` with your agent's rules.
3. Adjust the permission levels in the tool contracts.
4. Update the session state fields in `state.py` to match your domain.
5. The controller loop, permission checks, observability, and stop conditions stay the same.

## Environment Variables

| Variable | Purpose | Default |
|----------|---------|---------|
| `ANTHROPIC_API_KEY` | API authentication | (required) |
| `ANTHROPIC_MODEL` | Model to use | claude-sonnet-4-20250514 |

## Mock Tools

The tool executors return simulated data so you can run the agent without real social media integrations. To connect real services, replace the `_exec_*` functions in `tools.py` with your API calls.
