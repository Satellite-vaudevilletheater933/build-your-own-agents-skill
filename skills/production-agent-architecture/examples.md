# Example Outputs

## Good Prompt To Give An AI Coding Agent
"Use the production-agent-architecture skill from this repo. Design a production-ready agent for [domain]. Do not return a one-shot chatbot design. Include loop pseudocode, tool contracts, session state schema, approval matrix, observability minimums, evaluation plan, reliability strategy, and rollout phases."

## Worked Examples
See the [`examples/`](../../examples/) directory for complete Agent Build Specs across six domains:

| Example | What to notice |
|---------|---------------|
| [`marketing-agent`](../../examples/marketing-agent/) | Full spec + **runnable Python code** — start here |
| [`code-review-agent`](../../examples/code-review-agent/) | Webhook-driven loop, SARIF integration, finding deduplication |
| [`data-pipeline-agent`](../../examples/data-pipeline-agent/) | Multi-orchestrator correlation, retry ledger, cost-aware caps |
| [`devops-incident-agent`](../../examples/devops-incident-agent/) | Sandboxed diagnostics, change correlation, postmortem export |
| [`research-agent`](../../examples/research-agent/) | Multi-index deduplication, citation integrity, reading ledger |
| [`support-agent`](../../examples/support-agent/) | Intent classification, brand voice, escalation routing |
