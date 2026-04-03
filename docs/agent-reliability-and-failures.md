# Agent Reliability And Failures

Real agents fail. Production systems plan for that. The question is not whether failures will happen, but whether the agent handles them gracefully.

## Failure Types

Classify failures by whether they are worth retrying:

| Type | Description | Example | Retry? |
|------|-------------|---------|--------|
| **Transient** | Temporary infrastructure issue | API timeout, rate limit, network blip | Yes, with backoff |
| **Permanent** | Fundamental problem that won't resolve on retry | Invalid input, missing resource, code bug | No |
| **Policy** | Blocked by permission or approval rules | Tool denied, approval rejected | No (route to human) |
| **Partial** | Some parts succeeded, some failed | 3 of 5 files read, 1 timed out | Retry failed parts only |

The agent must classify failures correctly. Retrying a permanent failure wastes budget and time. Failing to retry a transient error leaves recoverable work on the table.

## Retry Strategies

### Bounded Exponential Backoff

For transient failures on idempotent operations (reads, searches, fetches):

```
attempt 1: immediate
attempt 2: wait 1s + jitter
attempt 3: wait 2s + jitter
attempt 4: give up, return structured error
```

Always add jitter to avoid thundering herd problems when multiple tool calls retry simultaneously.

### Idempotent-Only Retry

For operations with side effects (publishing, sending emails, creating tickets):

- Only retry if the operation has an idempotency key.
- If the previous attempt might have succeeded (ambiguous timeout), do NOT retry blindly.
- Use pre-flight checks: verify current state before re-attempting.

### No Retry

For operations where retrying is dangerous or meaningless:

- Destructive actions without rollback (deletes, force pushes).
- Approval requests (re-asking is a product decision, not a retry).
- Operations that failed due to invalid input (fix the input first).

## Retry Budget

Every agent session should have a retry budget: a maximum number of retries across all tools before the agent stops and reports failure. This prevents infinite retry loops.

```python
state.retry_budget = 3  # total retries allowed this session

# On failure:
state.retry_budget -= 1
if state.retry_budget <= 0:
    state.failure_reason = "Retry budget exhausted"
    state.completed = True
```

## Structured Failure Responses

When a tool fails, return a structured error to the model, not a raw exception string:

```json
{
  "error": "API rate limited",
  "error_type": "transient",
  "retryable": true,
  "retry_after_seconds": 5,
  "tool": "fetch_post_metrics",
  "attempt": 2,
  "max_attempts": 3
}
```

This gives the model enough information to decide whether to wait and retry, try an alternative approach, or report the issue to the user.

## Graceful Degradation

When partial failure occurs, degrade gracefully instead of failing completely:

- If logs are unavailable, proceed with metrics and flag the gap.
- If one data source is down, use the others and note reduced confidence.
- If the knowledge base is unreachable, draft a shorter response and flag it for human review.

## Circuit Breaking

If a specific integration (API, database, external service) fails repeatedly, stop calling it for a cooldown period rather than burning through the retry budget on every turn:

```
if error_count_for("metrics_api") > 5 in last 60 seconds:
    skip metrics_api calls for 120 seconds
    add note: "Metrics temporarily unavailable"
```

## Human-In-The-Loop Timeout

When the agent is waiting for human approval and no response comes:

- Re-notify after a configured window (e.g., 5 minutes).
- Escalate to a secondary approver or on-call channel.
- Never wait silently forever. Silent waits are one of the most common operational failures in agent systems.

## Common Mistakes

- **Retrying unsafe side effects blindly**: publishing the same post twice, creating duplicate tickets, sending duplicate emails.
- **No retry budget**: the agent retries forever and burns through API credits.
- **Raw error strings to the model**: the model cannot make good decisions from `"ConnectionRefusedError: [Errno 111]"`.
- **No degradation path**: either everything works or nothing does, with no middle ground.
- **Ignoring partial success**: throwing away results from 4 successful tool calls because the 5th failed.
