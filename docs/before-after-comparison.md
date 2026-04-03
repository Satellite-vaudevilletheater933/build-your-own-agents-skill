# Before And After: Naive Prompt vs Skill-Guided Output

This document shows the difference between asking an AI coding agent to "build an agent" with a vague prompt versus using the production agent architecture skill.

## The Naive Prompt

> "Design me a marketing agent that can post on social media."

### Typical Naive Output

```markdown
# Marketing Agent

## Overview
This agent helps with social media marketing by generating and posting content.

## How It Works
1. User provides a topic or campaign brief
2. Agent generates a post using the LLM
3. Agent posts it to the configured social channel

## Tech Stack
- Python
- OpenAI API (or Anthropic)
- Tweepy for Twitter

## Code

def generate_post(topic):
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": f"Write a social media post about {topic}"}]
    )
    return response.choices[0].message.content

def post_to_twitter(text):
    client = tweepy.Client(...)
    client.create_tweet(text=text)
```

### What Is Wrong With This

- Single API call, no loop, no iteration
- No session state across turns
- No approval before publishing
- No failure handling or retries
- No observability, no logs, no metrics
- No evaluation plan
- No permission model
- No stop conditions
- No rollout plan; the "v1" is also the production version
- No tool contracts; the model just calls functions directly
- This is a script, not an agent

---

## The Skill-Guided Prompt

> "Use the production agent architecture skill. Design a production-ready agent for marketing operations. Do not return a one-shot chatbot design. Include loop pseudocode, tool contracts, session state schema, approval matrix, observability minimums, evaluation plan, reliability strategy, and rollout phases."

### What The Skill Produces

A complete Agent Build Spec covering:

**1. Controller loop with explicit steps**

```
loop:
  context = build_context(campaign_brief, brand_guide, session_state)
  response = model.next_step(context)
  if response.requests_tool:
    check_permissions(response.tool, approval_state)
    result = execute_tool(response.tool, response.input)
    session_state.update(result)
    log(tool_call, result, latency)
  else:
    return response.final_answer
  if stop_condition_met(session_state):
    break
```

**2. Tool contracts with defined boundaries**

| Tool | Permission | Timeout | Retry | Side Effects |
|------|-----------|---------|-------|--------------|
| get_trending_topics | auto-allow | 15s | bounded backoff | none |
| draft_post | auto-allow | 30s | bounded backoff | none |
| publish_post | ask-first | 20s | idempotent only | publishes content |
| fetch_post_metrics | auto-allow | 15s | bounded backoff | none |

**3. Session state schema**

```json
{
  "campaign_id": "string",
  "drafts": [],
  "approval_state": "pending | approved | denied",
  "analytics_snapshots": [],
  "retry_budget": 3,
  "last_tool_result": {}
}
```

**4. Explicit approval matrix**

- Reads and drafting: auto-allow
- Publishing: requires human approval
- Editing published content: deny by default
- Budget changes: requires human approval

**5. Failure and retry strategy**

- Transient read failures: retry with bounded exponential backoff, max 3 attempts
- Publish failures: do not retry unless idempotency is confirmed
- Approval denial: stop and surface reason to user
- Missing context: stop and request missing input

**6. Observability minimums**

- Session ID on every log line
- Tool call name, latency, and outcome per invocation
- Approval wait time tracking
- Token and cost tracking per session
- Engagement metrics per post and campaign

**7. Evaluation plan**

- Brand-quality rubric scored per draft
- Approval acceptance rate over time
- Post engagement relative to baseline
- Time from request to approved draft

**8. Rollout phases**

- v0: drafting assistant, no publishing, human copies output manually
- v1: approval-gated publishing with full logging
- v2: analytics-driven recommendations and A/B experiments

---

## Side-By-Side Summary

| Concern | Naive Prompt | Skill-Guided |
|---------|-------------|--------------|
| Architecture | Single function call | Loop-based controller |
| Tool boundaries | Implicit function calls | Explicit contracts with schemas |
| Permissions | None | Tiered: auto-allow, ask-first, deny |
| Approval flow | None | Explicit matrix with blocking |
| Session state | None | Structured schema with history |
| Failure handling | Crashes | Bounded retries, structured errors |
| Observability | None | Logs, metrics, cost tracking |
| Evaluation | None | Rubrics, acceptance rate, engagement |
| Rollout | Ship it | v0 through v2 with increasing autonomy |
| Stop conditions | None | Defined: completion, denial, budget, missing context |
| Production readiness | Not close | Defined path with checkpoints |

## The Key Difference

The naive prompt produces a script that calls an API once and hopes for the best.

The skill produces an architecture document that a team can actually build, operate, evaluate, and improve over time. It separates what the model decides from what the runtime enforces, and it treats permissions, failures, and observability as first-class concerns rather than afterthoughts.
