# Agent Memory And Sessions

Session state keeps a multi-step agent coherent. Without it, every turn is a fresh start and the agent cannot build on prior work.

## Sessions Are Structured State

A session is not a chat log. In production agent systems, the session stores:

- **Session metadata**: ID, creation timestamp, last update timestamp, version.
- **Structured messages**: each with a role (user, assistant, tool) and typed content blocks (text, tool_use, tool_result).
- **Compaction state**: whether history has been summarized, how many messages were removed, and the summary text.
- **Fork information**: if this session branched from another, the parent session ID and branch label.
- **Persistence path**: where the session is saved on disk for resume and recovery.

The critical insight is that messages are not just text. They are structured content blocks that let the runtime distinguish between what the user said, what the model proposed, which tool was called, and what the tool returned.

## What State To Track

For a domain agent, your session should include:

- **User request**: the original goal and any refinements.
- **Current objective**: what the agent is working toward right now.
- **Tool results**: structured output from each tool invocation, not just the last one.
- **Approval status**: pending, approved, or denied for any gated action.
- **Partial outputs**: drafts, intermediate analyses, or work in progress.
- **Retry counters**: how many retries remain before the agent stops.
- **Turn history**: summarized or full record of prior turns.
- **Token usage**: cumulative input and output tokens for cost tracking.

## Compaction: Managing Context Window Limits

LLMs have finite context windows. A long-running agent accumulates history that eventually exceeds the limit. Compaction solves this by summarizing older history while preserving recent detail.

A practical compaction system works like this:

1. **Estimate token usage** of the current session. Production systems set thresholds (e.g., 100,000 input tokens) that trigger compaction.
2. **Preserve recent messages** in full — typically the last N turns, where N is configurable.
3. **Summarize older messages** into a structured summary that preserves: the conversation scope, key decisions, files or entities referenced, pending work, and a timeline of what happened.
4. **Replace** the older messages with the summary and continue.

Good compaction is not "delete old stuff." It is deciding what the model still needs to do its job. Preserve what matters, compress what is repetitive.

### The Compaction Tradeoff

| Preserve too much | Preserve too little |
|---|---|
| Context gets too large | Model forgets important facts |
| Cost increases per turn | Task may drift |
| Latency increases | Agent may repeat completed work |

## Persistence And Resume

Production agents persist sessions to disk so users can:
- Resume interrupted work.
- Inspect history after the fact.
- Export a conversation for review or audit.
- Recover from crashes without losing progress.

Implement persistence as append-only writes with a size cap and rotation policy. When the session file exceeds a threshold (e.g., 256 KB), rotate to a new file and keep a bounded number of old files.

## Session Forking

Some agent systems support forking: branching a session from an earlier state to explore alternate strategies. This is useful when the agent needs to try different approaches to the same problem without losing the original path.

Forking treats sessions as a first-class data structure, not just a side effect of the conversation.

## Common Mistakes

- **Appending everything forever**: real agents need summarization and bounded history. Unbounded growth breaks context limits and inflates costs.
- **Treating memory as a string**: sessions should be structured (typed messages, content blocks) so the runtime can manipulate them programmatically.
- **No persistence**: if the agent can't resume after an interruption, long-running tasks become unreliable.
- **Ignoring compaction**: if you wait until context is full to think about summarization, you will lose important information in a rush.
