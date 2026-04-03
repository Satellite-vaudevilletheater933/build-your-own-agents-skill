# Launch Copy

Copy-paste ready. Pick one per platform, add your repo link, and post.

---

## GitHub Short Description
Build AI agents using the same architecture patterns as Claude Code. Skill + 6 examples + runnable Python code. No framework.

---

## Twitter/X — Version A (the "Claude Code" hook, highest virality potential)

I studied how Claude Code's agent harness actually works.

Not the model. The runtime.

The controller loop. The permission pipeline (PreToolUse / PostToolUse hooks). The tiered permission modes. The session compaction. The tool contracts.

Then I open-sourced the architecture pattern so anyone can build agents at that level.

Includes:
- A skill you install in Cursor / Claude Code / Codex
- 6 domain examples
- Runnable Python agent (clone + run in 5 min)
- No framework dependency

https://github.com/xuanhieu2611/build-your-own-agents-skill

## Twitter/X — Version B (problem/solution, shorter)

"Build me an agent" -> you get a script that calls an API once.

Claude Code uses a completely different architecture: controller loop, tool contracts, runtime permissions, session compaction, hook pipelines.

I extracted those patterns into a public repo with 6 examples and runnable code.

No framework. Just the architecture.

https://github.com/xuanhieu2611/build-your-own-agents-skill

## Twitter/X — Version C (contrarian, punchy)

You don't need LangChain.
You don't need CrewAI.

You need the same architecture that Claude Code uses:
- Controller loop
- Tool contracts
- Runtime permissions
- Session state with compaction
- PreToolUse / PostToolUse hooks
- Observability

I open-sourced the pattern with 6 examples and a runnable Python agent.

https://github.com/xuanhieu2611/build-your-own-agents-skill

---

## LinkedIn

Everyone is building "AI agents." Most of them are chatbot wrappers — one API call, one response, no loop, no memory, no safety.

I wanted to understand how the serious ones actually work. So I studied the Claude Code agent harness in depth — not the model, but the runtime that makes it reliable.

What I found:
- A controller loop, not a one-shot call
- Tool contracts with JSON Schema, permission levels, and timeouts
- A runtime permission pipeline (PreToolUse / PostToolUse hooks) that can allow, deny, or modify tool calls — safety enforced in code, not just prompts
- Tiered permission modes: ReadOnly, WorkspaceWrite, DangerFullAccess
- Session compaction that summarizes old context when the window fills up
- Structured events for observability and cost tracking

I packaged these patterns into a public repo that any developer or AI coding agent can use:

- A skill you install in Cursor, Claude Code, Codex, or any AI coding tool — it acts as a checklist that ensures your agent design covers all production concerns
- 6 worked examples: marketing, support, DevOps, code review, data pipelines, research
- A runnable Python reference agent you can clone and run in 5 minutes
- A scaffolder that generates structured projects from your design spec

You don't have to reverse-engineer a production codebase to build at that level. That's the point.

If you're building agents for any domain, this should save you time.

https://github.com/xuanhieu2611/build-your-own-agents-skill

---

## Reddit — r/ClaudeAI or r/cursor

**Title: I studied how Claude Code's agent runtime works and open-sourced the architecture pattern (6 examples + runnable code)**

Everyone talks about which model is behind Claude Code, but the thing that makes it feel like an actual agent (not a chatbot) is the runtime architecture.

I spent a lot of time studying it. Here's what I found:

- **Controller loop**: model proposes a tool call, runtime checks permissions, executes it, stores the result, loops until done. Not one-shot.
- **Tool contracts**: every tool has a JSON Schema, a required permission level (ReadOnly / WorkspaceWrite / DangerFullAccess), a timeout, and declared side effects.
- **Hook pipeline**: PreToolUse and PostToolUse hooks can allow, deny, modify tool input, or annotate results — this is how safety is enforced in code, not just in the prompt.
- **Session compaction**: when context exceeds ~100k tokens, older history is summarized while recent turns are preserved. This is why long sessions don't degrade.
- **Permission outcomes**: tool requests result in Allow, Deny, or Ask — not a boolean.

I turned these patterns into a public repo:

- A skill you can install in Cursor, Claude Code, Codex, etc.
- 6 worked examples across domains (marketing, support, DevOps, code review, data pipelines, research)
- A runnable Python marketing agent with a real loop, tool contracts, permission checks, human-in-the-loop approval, and structured logging
- A scaffolder that generates projects from specs

The skill works as a production checklist. When you ask your coding agent to "design me an agent," it ensures the output includes all the concerns — tool schemas, runtime permissions, approval flows, retry strategies, observability, evaluation, rollout phases — even if you don't think to ask for them.

No framework dependency. No lock-in. MIT licensed.

https://github.com/xuanhieu2611/build-your-own-agents-skill

---

## Reddit — r/MachineLearning or r/LocalLLaMA

**Title: Open-sourced the architecture pattern behind Claude Code's agent runtime — no framework, just the pattern**

Most "AI agents" are one API call in a for loop. Production agents like Claude Code use a fundamentally different runtime architecture.

I studied how it works and extracted the patterns into a public repo with 6 domain examples and a runnable Python reference implementation.

Key patterns:
- Controller loop with tool-use detection and stop conditions
- Tool contracts (JSON Schema, permission level, timeout, side effects)
- PreToolUse / PostToolUse hook pipeline for runtime safety enforcement
- Tiered permission modes (ReadOnly, WorkspaceWrite, DangerFullAccess)
- Session compaction at configurable token thresholds
- Structured assistant events for observability

The repo includes a reusable "skill" you install in your AI coding tool. It acts as a checklist — it forces the agent to produce a complete design with all production concerns covered, rather than a chatbot wrapper.

MIT licensed. Feedback welcome.

https://github.com/xuanhieu2611/build-your-own-agents-skill

---

## Hacker News

**Title: Show HN: Build agents with Claude Code's architecture pattern – skill + 6 examples + runnable code**

I studied how Claude Code's agent runtime works and extracted the architecture patterns into a public repo.

The insight: the thing that makes Claude Code feel like an agent (not a chatbot) isn't the model — it's the runtime. A controller loop that iterates until the task is done. Tool contracts with schemas and permission levels. A hook pipeline (PreToolUse/PostToolUse) that enforces safety in code. Session compaction that summarizes old context to stay within window limits. Structured events for every tool call.

These patterns aren't novel individually, but the combination is specific and well-tested. Most people building "agents" skip half of them.

This repo packages the patterns as:
1. A "skill" you install in your AI coding tool (Cursor, Claude Code, Codex). It's a checklist — ask your coding agent to design an agent, and the skill ensures all production concerns are covered.
2. Six worked examples (marketing, support, DevOps, code review, data pipelines, research).
3. A runnable Python reference implementation with a real loop, tool contracts, permission checks, approval flows, and logging. Clone it, swap the mock tools for your integrations.

No framework. No dependencies beyond the Anthropic SDK. MIT licensed.

https://github.com/xuanhieu2611/build-your-own-agents-skill

---

## Suggested Hashtags
#buildinpublic #aiagents #claudecode #opensource #cursor #anthropic #developers

---

## Notes To Self
- The Claude Code angle is your strongest hook right now. Everyone is talking about it. Use it.
- Lead every post with the insight about the runtime, not "I built a thing."
- The specific details (PreToolUse hooks, 100k token compaction threshold, tiered permission modes) make it credible. Generic claims like "production-ready patterns" do not.
- Post Twitter first (weekday, 9-11am or 12-1pm US time). Engage with every reply for the first 2 hours.
- Post LinkedIn same day, 1-2 hours after Twitter.
- Post Reddit in the evening. r/ClaudeAI and r/cursor are your highest-signal audiences.
- HN: submit as "Show HN" on a Tuesday or Wednesday morning.
- Pin the repo on your GitHub profile.
- When someone asks "how is this different from LangChain/CrewAI?" answer: "Those are frameworks you install. This is the architecture pattern you learn. No dependency. Clone the marketing agent example to see it working."
- When someone asks "isn't this just a prompt?" answer: "It's a production checklist backed by a runnable reference implementation. Try asking Claude Code to 'build me an agent' without it, then with it. The difference is the 10 concerns you forgot to ask for."
