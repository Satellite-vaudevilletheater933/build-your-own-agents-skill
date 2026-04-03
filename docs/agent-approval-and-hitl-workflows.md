# Agent Approval And HITL Workflows

Most production agents should not be fully autonomous. Human-in-the-loop (HITL) workflows let agents handle routine work at machine speed while routing high-stakes decisions to humans.

## When To Require Approval

Not every tool call needs approval. The key question is: what is the cost of getting it wrong?

| Action Type | Risk | Approval Strategy |
|-------------|------|------------------|
| Reading data | Low | Auto-allow |
| Generating drafts | Low | Auto-allow (no side effects) |
| Sending external messages | Medium-High | Ask-first |
| Publishing content | High | Ask-first |
| Financial transactions | High | Ask-first |
| Destructive changes | Very High | Ask-first or deny |
| Legal or compliance-sensitive | Very High | Escalate to specialist |

## Approval Flow Architecture

A well-designed approval flow has five parts:

1. **Detection**: the runtime identifies that the requested tool requires approval (from the tool contract's `permission` field).
2. **Presentation**: the runtime shows the human what the agent wants to do, with enough context to make a decision (tool name, input data, rationale).
3. **Decision**: the human approves, denies, or modifies the request.
4. **Recording**: the decision is logged in the audit trail with who, when, and what.
5. **Continuation**: the agent resumes on approval, stops or adjusts on denial.

## Approval Channels

The approval mechanism should match your operational context:

- **CLI prompt**: good for developer tools and local agents.
- **Slack/Teams message**: good for team-operated agents (marketing, support, DevOps).
- **Web UI modal**: good for customer-facing products with dashboards.
- **Email with approve/deny links**: good for async workflows with low urgency.
- **Queue with SLA**: good for high-volume operations where approvals must not block indefinitely.

## Timeout And Escalation

Never wait silently for approval forever. Every approval request should have:

- A **timeout**: if no response in N minutes, re-notify or escalate.
- An **escalation path**: if the primary approver does not respond, route to a secondary.
- A **fallback action**: if nobody responds within the SLA, either safe-stop the agent or take a conservative default action.

Silent approval waits are one of the most common operational failures in agent systems.

## Approval Granularity

Design approval at the right level of granularity:

- **Per-tool**: every call to `publish_post` requires approval. Simple but can be noisy.
- **Per-category**: all publishing tools require approval, but all read tools are auto-allowed.
- **Per-condition**: approval required only when the action exceeds a threshold (e.g., refund above $100, post during a campaign freeze).
- **Per-session**: approve the agent's plan once at the start, then auto-allow within the approved scope.

## Integrating Approval With Session State

Track approval status in session state so the agent and the runtime both know where things stand:

```python
class ApprovalState(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    DENIED = "denied"
    EXPIRED = "expired"
```

When approval is denied, the agent should receive a structured message explaining why, so it can adjust its approach or report to the user.

## Common Mistakes

- **No approval for high-risk actions**: the agent publishes, sends, or deletes without any human check.
- **Approval fatigue**: requiring approval for every low-risk action trains humans to auto-approve everything, defeating the purpose.
- **No timeout on approval waits**: the agent hangs forever waiting for a human who is offline.
- **No audit trail**: you cannot prove who approved what, when, for compliance reviews.
- **Approval as prompt text**: telling the model to "ask before publishing" is guidance, not enforcement. The runtime must block execution until approval is received.
