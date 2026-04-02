# Agent Tooling System

Tools are how an agent interacts with the outside world.

## Separate These Layers
1. tool name and purpose
2. input schema
3. runtime executor
4. permission level

The model proposes actions. The runtime validates, authorizes, executes, and returns structured results.
