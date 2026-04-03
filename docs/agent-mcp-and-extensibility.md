# Agent MCP And Extensibility

Not every v1 agent needs an extensibility layer, but mature systems often do. The question is when to add it and how to keep it safe.

## When To Add Extensibility

**Start narrow.** Begin with a small, explicit tool surface and get the core workflow stable. Extensibility added too early creates a large surface area to secure and maintain before you understand what users actually need.

**Add extensibility when:**
- Users need tools your core set does not cover.
- Different deployments need different tool sets (e.g., one customer uses Jira, another uses Linear).
- You want third parties to contribute integrations without modifying the core runtime.

## Model Context Protocol (MCP)

MCP is a standardized protocol for connecting agents to external tool servers. Instead of hardcoding every integration into the agent runtime, MCP lets you:

- Define tool servers that expose tools over a standard interface.
- Connect and disconnect tools at runtime without restarting the agent.
- Share tool implementations across different agent runtimes.

### How It Works

1. The agent runtime discovers available MCP servers from configuration.
2. On startup or on demand, the runtime connects to each server and fetches its tool definitions.
3. Those tools are merged into the tool registry alongside built-in tools.
4. When the model requests an MCP-provided tool, the runtime routes the call to the appropriate server.
5. The server executes the tool and returns a structured result.

### Safety Considerations

MCP tools are external code. They require the same permission and safety treatment as built-in tools — or more:

- Each MCP tool should declare its permission level and side effects.
- The runtime should validate MCP tool inputs against their schemas before forwarding.
- MCP servers should run with least-privilege access and bounded resource limits.
- The agent should not trust MCP tool outputs more than it trusts built-in tool outputs.

## Plugin Architecture

Beyond MCP, some agent systems support a plugin model:

- **Plugin registration**: install, enable, disable, and update plugins.
- **Plugin discovery**: find available plugins from a registry or marketplace.
- **Plugin isolation**: plugins run in sandboxed contexts to prevent interference with the core runtime.
- **Plugin lifecycle**: validate, load, refresh, and unload plugins at runtime.

## The Extensibility Tradeoff

| More extensibility | Less extensibility |
|---|---|
| More flexible for diverse use cases | Simpler to secure and maintain |
| Larger attack surface | Smaller attack surface |
| Harder to test exhaustively | Easier to test completely |
| Requires a plugin/MCP security model | Core tools are fully controlled |

## Recommendation For v1 Agents

For your first version:
- Hardcode your core tools in the tool registry.
- Use environment variables or configuration files for integration endpoints and credentials.
- Do not build a plugin system until the core workflow is stable and users are requesting integrations you cannot anticipate.

For v2 and beyond:
- Consider MCP for standardized tool connectivity.
- Consider plugins for domain-specific extensions.
- Always treat external tools with the same (or stricter) permission policies as internal tools.
