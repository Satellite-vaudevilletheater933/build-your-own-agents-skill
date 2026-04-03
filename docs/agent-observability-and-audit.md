# Agent Observability And Audit

If you cannot see what the agent did, you cannot operate it safely. Observability is not a nice-to-have for production agents. It is a requirement.

## What To Log

Every agent session should emit structured events for:

### Tool Calls

```json
{
  "event": "tool_call",
  "timestamp": "2025-01-15T14:23:01Z",
  "session_id": "abc123",
  "turn": 3,
  "tool": "publish_post",
  "latency_ms": 142.5,
  "success": true,
  "error": null
}
```

Log every tool invocation with: the tool name, input hash (not full input if it contains PII), latency, outcome, and a correlation ID tied to the session.

### Approval Decisions

```json
{
  "event": "approval_decision",
  "timestamp": "2025-01-15T14:22:58Z",
  "session_id": "abc123",
  "turn": 3,
  "tool": "publish_post",
  "approved": true
}
```

Record every time the agent requested human approval: who was asked, when, what tool and input, and whether it was approved or denied. This is your audit trail.

### Turn Summaries

```json
{
  "event": "turn_complete",
  "timestamp": "2025-01-15T14:23:02Z",
  "session_id": "abc123",
  "turn": 3,
  "input_tokens": 4521,
  "output_tokens": 312
}
```

Track token usage per turn for cost monitoring and anomaly detection (e.g., a sudden spike in tokens may indicate a compaction failure or prompt injection).

### Session Lifecycle

```json
{
  "event": "session_end",
  "timestamp": "2025-01-15T14:25:00Z",
  "session_id": "abc123",
  "turns": 7,
  "completed": true,
  "failure_reason": null,
  "total_input_tokens": 28450,
  "total_output_tokens": 3100,
  "tool_calls": 12,
  "approval_decisions": 1
}
```

## Minimum Metrics

Track these metrics for any production agent:

| Metric | What it tells you |
|--------|------------------|
| Session completion rate | Is the agent finishing tasks? |
| Mean turns per session | Is the agent efficient or looping? |
| Tool call latency (p50, p95) | Are integrations healthy? |
| Tool error rate | Are tools failing? Which ones? |
| Approval wait time | Is the human-in-the-loop bottleneck acceptable? |
| Token cost per session | Is cost under control? |
| Policy denial rate | Is the agent trying to do things it shouldn't? |

## Tracing

For complex agent sessions, structured logs alone may not be enough. Distributed tracing (e.g., OpenTelemetry spans) gives you:

- End-to-end visibility from user request through tool execution to final response.
- Latency breakdown: how much time is spent in the model, in tools, and in approval waits.
- Correlation between agent turns and downstream system calls.

Production agent runtimes often include a `SessionTracer` that ties the controller loop to session-level tracing, so every span is tagged with the session ID and turn number.

## Dashboards

Build dashboards for two audiences:

**Operators** need:
- Error rate and latency trends.
- Active session count and queue depth.
- Cost burn rate.
- Alert panels for anomalies (spike in denials, tool failures, token usage).

**Evaluators** need:
- Task success rate over time.
- Quality scores by domain category.
- Approval acceptance rate.
- Human edit distance on agent-generated outputs.

## Audit Requirements

For agents that take real-world actions (publishing, sending messages, modifying data), maintain an audit trail that answers:

- **What** action was taken?
- **When** did it happen?
- **Who** approved it (or was it auto-allowed)?
- **What** was the input and output?
- **Can** the action be rolled back, and how?

This is not just good practice. For many domains (finance, healthcare, legal), it is a compliance requirement.

## Common Mistakes

- **Logging to stdout only**: logs disappear when the process ends. Write to a durable log store.
- **Unstructured log messages**: `"Something went wrong with the tool"` is not actionable. Structured JSON with event type, session ID, and error details is.
- **No cost tracking**: agents can be expensive. If you don't track token usage per session, you won't notice cost problems until the bill arrives.
- **Logging PII**: customer data, credentials, and personal information should never appear in logs. Use hashed identifiers and redact sensitive fields.
- **No alerts**: dashboards that nobody watches are useless. Set up alerts for error rate spikes, latency degradation, and cost anomalies.
