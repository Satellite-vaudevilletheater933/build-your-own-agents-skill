# Agent Context And Prompting

A strong model with poor context will still perform badly.

## Good Context Inputs
- system instructions
- current user goal
- recent session state
- relevant retrieved data
- recent tool results
- policy or approval state

## Good Context Design
- include what matters now
- avoid dumping everything every turn
- keep policies separate from task content
- summarize old history when needed
