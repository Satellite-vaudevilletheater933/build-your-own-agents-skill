# Agent Permissions And Safety

Prompting can guide behavior, but runtime policy must enforce behavior. This is one of the biggest differences between a toy demo and a usable agent product.

## Why Prompting Alone Is Not Enough

A common beginner approach is to tell the model "do not do dangerous things" in the system prompt. That helps, but it is not enforcement. Models can make mistakes, and prompts are suggestions, not guardrails. A robust agent needs both:

- **Behavioral guidance** in prompts (soft steering)
- **Runtime enforcement** in code (hard guardrails)

## Permission Modes

Production agent runtimes define permission modes that represent how much trust the current session has:

| Mode | What it allows |
|------|---------------|
| `read-only` | Safe inspection tools: read files, search, fetch |
| `workspace-write` | Local modifications: write files, edit files, create directories |
| `danger-full-access` | Powerful actions: shell commands, network requests, system changes |

Each tool declares which permission mode it requires. The runtime compares the session's active mode against the tool's requirement and decides whether to allow, deny, or prompt.

## Permission Outcomes

A tool request does not produce a simple yes/no. It produces one of several outcomes:

- **Allow**: tool executes immediately.
- **Deny**: tool is blocked and the model receives a denial message.
- **Ask user**: the runtime pauses, asks the human for approval, and resumes based on the answer.

This matters because different tools have different risks. Reading a file is much lower risk than executing a shell command. The same agent session may auto-allow reads while requiring approval for writes.

## The PreToolUse / PostToolUse Hook Pipeline

Mature agent runtimes run hooks at two points in the tool execution path:

**PreToolUse hooks** fire before the tool executes. They can:
- Inspect the tool name and input.
- Override the permission decision (force allow, force deny).
- Modify the tool input before execution.
- Add context or annotations for audit.
- Cancel the tool request entirely.

**PostToolUse hooks** fire after the tool executes. They can:
- Inspect the tool output.
- Annotate results for logging.
- Trigger follow-up actions.
- Handle failure-specific logic.

This pipeline gives the runtime fine-grained control beyond static permission modes. For example, a hook can deny `bash` commands that match certain patterns (e.g., `rm -rf /`) even when the session has full-access mode enabled.

### Hook Result Structure

A hook returns a structured result, not just a boolean:

```
HookRunResult:
  denied: bool
  failed: bool
  cancelled: bool
  messages: list of strings (feedback to the model)
  permission_override: optional (force-allow or force-deny)
  updated_input: optional (modified tool input)
```

This lets hooks provide nuanced decisions. A hook might deny a tool but include a message explaining why, so the model can adjust its approach.

## Rules And Overrides

Static permission modes are often not enough. Real systems need per-tool rules:

- **Allow rules**: specific tools that are always permitted (e.g., `read_file` in any mode).
- **Deny rules**: specific tools that are always blocked (e.g., `publish_post` during a freeze period).
- **Ask rules**: specific tools that always require confirmation regardless of the session mode.

These rules layer on top of the base permission mode and give operators fine-grained control.

## Sandboxing vs Permissions

Permissions answer: *should this action be allowed?*

Sandboxing answers: *even if allowed, how constrained is the execution environment?*

For example, a shell command may be permitted, but still run with:
- Filesystem restrictions (read-only mounts, no access to sensitive directories)
- Network restrictions (no egress, or limited to specific domains)
- Resource limits (CPU time, memory, execution timeout)

Sandboxing is an execution-environment control that provides defense in depth beyond permission decisions.

## How This Transfers To Any Domain

The pattern is the same for every agent:

| Domain | Auto-allow | Ask-first | Deny |
|--------|-----------|-----------|------|
| Marketing agent | Read analytics, fetch trends | Publish posts | Delete campaigns |
| Support agent | Read tickets, search KB | Send customer replies | Issue refunds above threshold |
| DevOps agent | Read logs, fetch metrics | Restart services | Modify production config |
| Research agent | Search papers, read abstracts | Download paywalled content | Submit papers |

Define risk levels, assign them to tools, add rules, and check them inside the runtime loop.

## Integration With The Controller Loop

Permission checks are not a separate afterthought. They are integrated directly into the tool-execution path:

1. Model requests a tool.
2. Runtime runs PreToolUse hooks.
3. Runtime checks permissions against the session mode and tool requirement.
4. If allowed, runtime executes the tool.
5. Runtime runs PostToolUse hooks.
6. Result is returned to the model as a tool_result message.

Safety lives inside the loop, not bolted on externally.
