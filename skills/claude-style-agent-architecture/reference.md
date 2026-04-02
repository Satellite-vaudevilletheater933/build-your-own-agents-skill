# Claude-Style Agent Architecture Reference

## Reusable Pattern
1. user gives a goal
2. runtime builds context
3. model decides the next step or requests a tool
4. runtime checks permissions and approval state
5. runtime executes the tool
6. runtime stores the result in session state
7. runtime observes outcomes and continues
8. loop stops on success, limit, failure, or policy boundary

## Universal Components
- controller loop
- context builder
- tool registry
- tool executor
- session memory
- permissions and approvals
- observability
- evaluation
- reliability rules

## Worked Mini Example
A marketing agent may use:
- `get_trending_topics`
- `get_brand_guide`
- `draft_post`
- `publish_post`
- `fetch_post_metrics`

Publishing should require approval. Metrics and quality should be tracked. Failures should be visible.
