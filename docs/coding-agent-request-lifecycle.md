# Coding Agent Request Lifecycle

Coding agents are a useful learning surface because their request lifecycle is unusually visible.

## Typical Flow
1. user asks for a goal
2. runtime gathers context
3. model proposes a next step or tool call
4. runtime checks permissions
5. tool runs and returns structured output
6. state is updated
7. model continues until done

The same high-level pattern transfers to marketing, support, operations, and research agents.
