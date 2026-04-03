# Agent Orchestration And Product Design

The core loop is the engine. The product layer makes it usable. An agent can have a technically correct runtime and still be painful to use if the surrounding product experience is weak.

## What Orchestration Means

Orchestration is the layer that coordinates how users interact with the agent beyond a single model turn. It includes:

- **Session management**: starting, resuming, forking, and exporting sessions.
- **Command surfaces**: user-triggered actions that control the harness (compact history, switch model, check status, adjust permissions).
- **Workflow helpers**: planning modes, debugging tools, undo/redo, and rollback.
- **Multi-agent coordination**: sub-agents for specialized tasks, parallel work, and result aggregation.

## Tools vs Product Commands

A critical distinction in agent products:

- **Tools** are actions the model can request during the loop (read_file, publish_post, fetch_metrics).
- **Product commands** are actions the human triggers to control the agent itself (/compact, /status, /permissions, /cost, /resume).

These are two separate interfaces:
- The agent's action surface (tools)
- The user's control surface (commands)

Both need to be well-designed, but they serve different purposes.

## Product Controls That Matter

### Session Controls
- **Resume**: pick up where you left off after interruption or across work sessions.
- **Fork**: branch a session to explore an alternate strategy without losing the original.
- **Export**: save the conversation, decision log, or outputs for review or compliance.
- **Compact**: manually trigger history summarization when the context window is getting full.

### Operational Controls
- **Status**: see what the agent is doing, how many turns it has taken, and how much it has cost.
- **Permissions**: view or change the current permission mode mid-session.
- **Cost**: see token usage and estimated API spend for the current session.
- **Model**: switch the underlying model (e.g., from a fast model to a more capable one for difficult tasks).

### Planning And Debugging
- **Plan mode**: switch the agent from executing to planning, so it proposes steps without taking action.
- **Diff**: see what changes the agent has made during the session.
- **Undo**: revert the last action or set of actions.

## Why Product Design Matters For Adoption

Two agents with equally strong models can feel completely different because of product-layer choices:

- How is approval surfaced? (Inline prompt vs. separate queue vs. Slack message)
- How is history shown to the user? (Full transcript vs. summary vs. collapsible turns)
- What happens when the agent gets stuck? (Silent failure vs. structured handoff vs. retry suggestion)
- How easy is it to override the agent? (Take over mid-task vs. start over)

These choices determine whether people trust and continue using the agent, or abandon it after the first frustrating experience.

## Multi-Agent Orchestration

For complex tasks, a single agent loop may not be enough. Orchestration patterns include:

- **Sub-agents**: the main agent delegates specialized sub-tasks to focused agents (e.g., an explore agent for codebase search, a review agent for code quality).
- **Parallel execution**: multiple independent tool calls or sub-tasks run concurrently.
- **Handoff**: one agent completes its phase and passes context to the next agent in a pipeline.

The key constraint is that orchestration should be managed by the runtime, not by the model improvising coordination through prompt hacking.

## Designing For Your Domain

| Domain | Key product controls |
|--------|---------------------|
| Marketing | Campaign session switching, approval queues, analytics dashboards, content calendar integration |
| Support | Ticket session switching, escalation commands, CSAT tracking, transcript export |
| DevOps | Incident timeline, runbook integration, postmortem export, on-call handoff |
| Research | Source management, citation controls, reading progress, bibliography export |
