# Agent Tool Schemas And Contracts

A tool contract defines exactly what a tool does, what it accepts, what it returns, and what risks it carries. Without contracts, tool calling becomes fragile and unpredictable.

## Why Contracts Matter

The model does not call tools directly. It proposes an action, and the runtime validates, authorizes, and executes it. The contract is the boundary between model reasoning and real-world action.

If the contract is vague or missing:
- The model may hallucinate input fields that don't exist.
- The runtime has no way to validate requests before execution.
- Permission decisions have no schema to anchor to.
- Timeouts and retry policies are guesswork.

## Anatomy Of A Tool Contract

Every tool contract should include these fields:

| Field | Purpose |
|-------|---------|
| `name` | Stable identifier the model uses to request the tool |
| `description` | What the tool does, written for the model to understand when to use it |
| `input_schema` | JSON Schema defining required and optional parameters |
| `permission` | Risk tier: `auto-allow`, `ask-first`, or `deny` |
| `timeout_seconds` | Maximum execution time before the runtime kills the call |
| `side_effects` | What changes in the outside world (none, writes data, publishes content, sends email) |
| `retry_policy` | How failures are retried: `bounded_backoff`, `idempotent_only`, or `no_retry` |

## Concrete Example

A production coding agent's `read_file` tool contract looks like this:

```json
{
  "name": "read_file",
  "description": "Read the contents of a file at the given path. Supports optional line offset and limit for large files.",
  "input_schema": {
    "type": "object",
    "properties": {
      "path": { "type": "string", "description": "Absolute path to the file" },
      "offset": { "type": "integer", "description": "Line number to start reading from" },
      "limit": { "type": "integer", "description": "Maximum number of lines to return" }
    },
    "required": ["path"]
  },
  "permission": "auto-allow",
  "timeout_seconds": 10,
  "side_effects": "none",
  "retry_policy": "bounded_backoff"
}
```

Compare that to a higher-risk tool:

```json
{
  "name": "bash",
  "description": "Execute a shell command. Runs in a sandbox with filesystem and network restrictions.",
  "input_schema": {
    "type": "object",
    "properties": {
      "command": { "type": "string" },
      "timeout": { "type": "integer", "description": "Max seconds before kill" }
    },
    "required": ["command"]
  },
  "permission": "ask-first",
  "timeout_seconds": 120,
  "side_effects": "arbitrary system changes",
  "retry_policy": "no_retry"
}
```

The `bash` tool requires higher permission, has a longer timeout, and cannot be blindly retried because its effects may not be idempotent.

## The Four-Layer Separation

Production tool systems separate four concerns:

1. **Tool spec**: name, description, and input schema. This is what the model sees.
2. **Tool registry**: the list of available tools, filtered by the current session's configuration and allowlist. The model sees a controlled menu, not "everything the OS can do."
3. **Tool executor**: the code that actually runs the tool after permission is granted. The model never executes actions directly.
4. **Tool result**: structured output that gets appended to the session as a message, so the model can observe what happened.

This separation is one of the most important patterns in agent engineering. It means you can change the executor (e.g., swap mock for real) without changing the schema, and you can change the permission policy without changing the executor.

## Schema Design Tips

- Use `required` fields sparingly. Only require what the tool genuinely cannot function without.
- Use `enum` constraints for fields with a known set of values (channels, environments, severity levels).
- Write `description` strings for the model's benefit, not for developers. The model reads them to decide when to call the tool.
- Avoid catch-all schemas like `"additionalProperties": true` unless the tool genuinely accepts arbitrary input.

## Versioning

When you change a tool's schema, consider it a breaking change for the model. If you rename a field, add a new required parameter, or change the output shape, the model's learned behavior around that tool may break. Version your contracts and test changes against real agent runs before deploying.
