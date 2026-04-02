# Agent Architecture Overview

The reusable pattern looks like this:

1. user provides a goal
2. runtime builds context
3. model decides the next step or requests a tool
4. runtime checks policy
5. runtime executes the tool if allowed
6. runtime stores the result in session state
7. loop continues until a stop condition is reached

## Core Components
- controller loop
- context builder
- tool registry
- tool executor
- session state
- permissions and approval rules
- stop conditions
- observability and evaluation
