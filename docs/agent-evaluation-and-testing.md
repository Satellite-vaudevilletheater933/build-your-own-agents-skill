# Agent Evaluation And Testing

An agent is not production-ready just because it works once. Evaluation is how you know whether the agent is actually reliable, safe, and useful over time.

## What To Evaluate

### 1. Task Success

Does the agent accomplish what the user asked? Measure this with:

- **Completion rate**: percentage of sessions that reach a successful end state.
- **Quality rubrics**: domain-specific scoring. For a marketing agent, score brand alignment and engagement. For a code review agent, score precision and recall against human-labeled defects.
- **Time to completion**: how many turns and how much wall-clock time the agent takes.

### 2. Safety Behavior

Does the agent stay within bounds? Measure this with:

- **Policy violations**: count of times the agent attempted a denied action.
- **Approval recall**: for categories that require approval, did the agent always stop and ask?
- **False-positive remediations**: did the agent take an action that made things worse?
- **Prompt injection resistance**: does the agent handle adversarial input (malicious tool inputs, manipulative user messages) without breaking policy?

### 3. Tool Correctness

Do individual tools behave as expected? Measure this with:

- **Input validation**: are malformed inputs caught before execution?
- **Output accuracy**: does the tool return correct data? (Especially important for mock-to-real transitions.)
- **Latency**: are tool calls completing within their declared timeouts?
- **Error handling**: do failures produce structured error messages, not raw exceptions?

### 4. Operational Trustworthiness

Can you operate this agent in production? Measure this with:

- **Observability coverage**: is every tool call, approval decision, and turn logged?
- **Recovery**: can the agent resume after an interruption without losing critical state?
- **Cost tracking**: do you know how much each session costs in tokens and API calls?
- **Alert quality**: when something goes wrong, do your alerts fire and are they actionable?

## Evaluation Methods

### Offline Replay

Record real or synthetic sessions and replay them with known expected outcomes. This lets you:

- Test against a golden set of scenarios with labeled correct behavior.
- Measure regression: did a prompt or tool change make things worse?
- Run at scale without consuming live API credits (replay tool results from recordings).

### Shadow Mode

Run the agent on real inputs but do not execute side-effecting actions. Log what the agent would have done and compare to what humans actually did. This is the safest way to evaluate a new agent or a major change before going live.

### A/B Comparison

For agents that assist humans (support, review, drafting), measure outcomes for the assisted group vs the unassisted group:

- Response time, resolution rate, customer satisfaction, defect escape rate.
- This requires statistical rigor: sample sizes, confidence intervals, controlling for confounds.

### Periodic Human Audit

No automated evaluation replaces human review. Schedule regular spot audits:

- Random sample of sessions reviewed by a domain expert.
- Check tone, accuracy, policy compliance, and edge case handling.
- Feed findings back into prompt and rule improvements.

## Evaluation Cadence

| Stage | What to evaluate | How often |
|-------|-----------------|-----------|
| Development | Golden set, unit tests | Every change |
| Staging | Shadow mode, replay | Before each release |
| Production | Live metrics, alerts | Continuously |
| Review | Human audit | Monthly or quarterly |

## Common Mistakes

- **Evaluating only happy paths**: the agent works on demo inputs but fails on real edge cases.
- **No baseline**: you cannot measure improvement without knowing the starting point.
- **Evaluating too late**: if you wait until production to discover problems, the cost of fixing them is much higher.
- **Ignoring safety evaluation**: task success does not mean the agent is safe. A highly capable agent that violates policy is worse than a less capable one that stays in bounds.
