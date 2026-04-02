# Marketing Agent Build Spec

## Domain
Marketing operations and content automation.

## User goal
Help a team discover promising topics, draft posts, publish approved content, monitor performance, and improve future posts.

## Success condition
The agent consistently turns campaign goals into approved, on-brand posts and produces structured performance feedback that the team can act on.

## Core workflow
- fetch trends and campaign context
- draft one or more posts
- ask for approval before publishing
- publish approved content
- collect analytics after posting
- summarize results and next actions

## Controller loop
1. gather context for the current campaign
2. identify the next best action
3. call a tool when outside data or external action is needed
4. stop for approval before publishing
5. save outputs and metrics into session state
6. continue until the campaign step is complete

## Context inputs
- campaign brief
- brand guide
- audience profile
- channel constraints
- prior post performance
- approval state

## Tools
- `get_trending_topics`
- `get_campaign_brief`
- `get_brand_guide`
- `draft_post`
- `publish_post`
- `fetch_post_metrics`

## Session state
- current campaign id
- candidate topics
- draft history
- approved assets
- publish results
- analytics snapshots
- last recommended next step

## Permissions and approvals
- reads and drafting are auto-allow
- `publish_post` requires approval
- deleting or editing already published content is deny by default

## Stop conditions
- a requested deliverable is completed
- approval is denied
- required context is missing and cannot be recovered
- failure budget is exceeded

## Observability
- log every publish attempt
- log tool latency and failures
- track approval wait time
- record engagement metrics by post and campaign

## Evaluation
- brand-quality rubric
- approval acceptance rate
- post engagement metrics
- time from request to approved draft

## Reliability and failure handling
- retry trend and analytics reads with backoff
- never blindly retry publishing without idempotency protection
- return a structured failure summary when blocked

## Rollout phases
- v0: drafting assistant with no auto-publish
- v1: approval-gated publishing
- v2: analytics-driven recommendations and experiments
