# Agent Tooling System

Tools are how an agent interacts with the outside world. Without tools, an agent is just a chatbot that generates text. With tools, it can read data, take actions, inspect results, and continue working.

## The Four-Layer Architecture

Production tool systems separate four distinct concerns:

### 1. Tool Spec (What The Model Sees)

The spec describes a tool before it runs: name, description, and input schema. This is what the model uses to decide when and how to call a tool. The model sees a controlled menu of actions, not "everything the OS can do."

### 2. Tool Registry (What Is Available)

The registry is the runtime's list of available tools. It answers:
- Which tools exist in this session?
- Which are built-in vs. from plugins or extensions?
- Which are allowed by the current session configuration?

A typical registry merges built-in tools with plugin tools, filters by an allowlist, and normalizes aliases (e.g., `read` maps to `read_file`).

### 3. Tool Executor (What Actually Runs)

The executor is the code that runs after the model requests a tool and the runtime grants permission. The model never directly executes anything. The flow is:

1. Model proposes a named tool with structured input.
2. Runtime validates the request against the schema.
3. Runtime checks permissions and runs hooks.
4. Executor runs the tool.
5. Executor returns a structured result.

This separation is one of the most important patterns in agent engineering. It means the model proposes actions, but the runtime is the gatekeeper.

### 4. Tool Result (What Goes Back To The Model)

Every tool run produces output that gets appended to the session as a tool_result message. The model sees this result on the next loop iteration and decides what to do next. Results may contain successful output, error output, structured data, or permission denials.

## Built-In Tool Categories

A production coding agent typically includes tools across these categories:

| Category | Examples | Permission Level |
|----------|----------|-----------------|
| File reading | `read_file`, `glob_search`, `grep_search` | Read-only |
| File writing | `write_file`, `edit_file` | Workspace write |
| Execution | `bash`, `REPL` | Full access (dangerous) |
| Web | `WebFetch`, `WebSearch` | Read-only |
| Agent control | `TodoWrite`, `Agent` (sub-agents), `Skill` | Varies |
| Configuration | `Config`, `EnterPlanMode`, `ExitPlanMode` | Workspace write |

The key observation is that tools do not all have the same risk. A `grep_search` and a `bash` command are both "tools," but they require fundamentally different trust levels.

## Schema Design Matters

Each tool has a JSON Schema for its expected input. This matters because:

- The model needs to know how to call the tool correctly.
- The runtime needs to validate input before execution.
- The system needs a stable contract between reasoning and action.

Without schemas, tool calling becomes fragile. The model may hallucinate parameters that don't exist, or provide input in the wrong shape.

## How This Transfers To Any Domain

The four-layer architecture transfers directly to any agent:

**Support agent tools:**
- `get_customer` (read-only)
- `list_open_tickets` (read-only)
- `draft_reply` (no side effects)
- `send_email` (ask-first, has side effects)
- `update_ticket` (workspace-write equivalent)

**DevOps agent tools:**
- `fetch_alerts` (read-only)
- `pull_logs` (read-only)
- `run_diagnostics` (sandboxed, time-limited)
- `apply_fix` (ask-first, has side effects)

The architecture stays the same: define tool specs, expose them to the model, validate inputs, execute safely, and feed results back into the loop. Only the tools themselves change.
