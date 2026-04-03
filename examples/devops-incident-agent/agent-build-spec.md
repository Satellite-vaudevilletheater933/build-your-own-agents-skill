# DevOps Incident Response Agent Build Spec

## Domain
- On-call incident triage, correlation, and remediation for cloud-native services (Kubernetes, serverless, and managed data stores).
- Integration with paging (PagerDuty, OpsGenie) and observability (Datadog, CloudWatch, optional log aggregation).
- Change-aware diagnostics: linking alerts to deployments, feature flags, and infrastructure rollouts.
- Safe execution of read-heavy and bounded mutating actions in sandboxed runtimes (ephemeral shells, job runners, or approved CI agents).
- Structured incident lifecycle: timeline capture, stakeholder comms hooks, and postmortem-ready artifacts.

## User goal
- Reduce mean time to acknowledge (MTTA) and mean time to resolve (MTTR) for Sev2–Sev4 incidents without bypassing org change controls.
- Give on-call engineers a single “copilot” that ingests alerts, pulls the right telemetry, and proposes ranked hypotheses with evidence.
- Automate repetitive triage (log pulls, metric snapshots, deployment lookups) so humans focus on judgment calls and customer impact.
- When confidence is high and risk is within policy, apply pre-approved remediations (restarts, scale-out, cache clears) with audit trails.
- Escalate clearly when severity, blast radius, or uncertainty exceeds thresholds, carrying a concise briefing and timeline.

## Success condition
- For in-scope incidents, the agent produces a defensible incident brief (symptoms, blast radius, correlated changes, top hypotheses) within SLA-aligned time windows.
- Remediation proposals include explicit confidence, rollback plan, and blast-radius assessment; no production mutation occurs without recorded approval (human or policy-gated auto-allow list).
- Post-incident, the session exports a timeline, decision log, and metric/log excerpts suitable for a blameless postmortem without manual copy-paste.
- Escalations are timely: high-severity or low-confidence situations reach the right channel with no silent failures in paging or chat.

## Core workflow
- Ingest and normalize incoming alerts (PagerDuty/OpsGenie): dedupe, enrich with service map and ownership metadata.
- Pull correlated logs, metrics, traces, and synthetic checks from Datadog and/or CloudWatch for the alert window and a lookback period.
- Correlate with recent deployments, config changes, feature flags, and infra events; surface a ranked “what changed” narrative.
- Run read-only and sandboxed diagnostic commands (health probes, targeted queries, canary comparisons) within CPU/time/network quotas.
- Draft remediation options (mitigation vs root fix), request approval for mutating actions, execute approved steps with idempotency keys, and verify via metrics.
- Maintain a living incident timeline, update stakeholders via templated summaries, and package postmortem inputs when the incident resolves or is handed off.

## Controller loop
1. Receive or poll for new/updated incidents and classify severity, service, and environment from alert payload and CMDB tags.
2. Load session state and org policy (allow lists, maintenance windows, freeze periods); abort or narrow scope if policy forbids action.
3. Gather observability bundles (logs, metrics, traces, top errors, saturation signals) scoped to the affected service and dependencies.
4. Query deployment and change feeds; compute temporal correlation scores and produce 2–4 hypotheses with supporting evidence links.
5. If diagnostics require it, run sandboxed commands or canned playbooks; never exceed declared resource and network egress limits.
6. If a fix is proposed, require approval for mutating tools; on approval, apply with verification checks and rollback hooks.
7. Append timeline events (detected, triaged, mitigated, resolved); trigger escalation if severity rises, confidence drops, or human timeout elapses.
8. On resolution or handoff, finalize session state, export postmortem draft sections, and close the control loop with metrics emission.

## Context inputs
- Active incident record from PagerDuty/OpsGenie (id, title, severity, service, escalation policy, assignees).
- Service catalog entry: owners, runbooks, SLOs, dependencies, and allowed regions/clusters.
- Observability context: Datadog monitors/dashboards, CloudWatch alarms, log groups, trace retention, and saved views for the service.
- Deployment and change history: CI/CD releases, Helm/Kustomize revisions, Terraform applies, and feature-flag flip events in the incident window.
- Org policy: maintenance windows, change freezes, auto-remediation allow lists, data residency rules, and secrets-handling constraints.
- Prior session notes for the same incident id (deduplicated merges, human overrides, and approval decisions).

## Tools
- `fetch_oncall_incidents`
- `pull_observability_bundle`
- `correlate_deployments_and_changes`
- `run_sandboxed_diagnostics`
- `propose_remediation_plan`
- `apply_approved_remediation`

## Session state
- incident id and paging provider reference
- severity, environment, and affected service graph (nodes + edges)
- normalized alert payloads and dedupe keys
- observability snapshot ids (queries, time ranges, links)
- ranked hypotheses with evidence pointers and confidence scores
- sandbox job ids, command transcripts (redacted), and quota usage
- remediation proposals, approval records, and execution results (with idempotency keys)
- timeline event stream and escalation history
- postmortem draft sections (impact, timeline, root cause candidates, action items)

## Permissions and approvals
- Read-only observability and incident APIs are auto-allow within scoped services and time windows; cross-team reads require explicit scope expansion or human ack.
- Sandbox execution is allow-listed by command template, image digest, and egress policy; interactive shells and arbitrary package installs are deny by default.
- Mutating remediations (`apply_approved_remediation`) require human approval except for vetted auto-allow actions (e.g., single pod restart on a named deployment) defined per service tier.
- Secrets never pass through the model in clear text; the agent references secret names and delegates retrieval to the runtime secret store.
- Production changes during change freezes route to explicit break-glass approval with mandatory justification and audit log entry.

## Stop conditions
- Incident is resolved or closed in the paging system, and verification metrics are stable for the configured soak period.
- Human on-call takes exclusive control and disables agent automation for the incident.
- Required context cannot be obtained (permissions, missing telemetry, or API outage) after bounded retries; agent returns a structured handoff brief.
- Policy violation detected (wrong env, disallowed mutation, or data classification conflict); agent halts all mutating paths.
- Repeated failed remediations or rising error rates after an attempted fix trigger automatic rollback (if defined) and stop further auto-apply.

## Observability
- Structured logs for every tool invocation: inputs hash, latency, outcome, correlation id tied to incident id.
- Metrics: triage duration, hypothesis count, approval wait time, remediation success rate, escalation count by reason.
- Traces spanning alert ingestion through remediation for end-to-end debugging of the agent runtime.
- Audit events for approvals, sandbox runs, and production mutations (who/when/what/rollback token).
- Dashboards for safety: auto-apply volume, policy denials, and blast-radius estimates vs actual impact.

## Evaluation
- Offline replay on historical incidents: does the agent surface the same top root cause within N minutes compared to human triage notes?
- Human rating of brief quality: clarity, evidence, and appropriateness of proposed fixes (Likert + free text).
- Safety metrics: false-positive remediations, rollbacks triggered, and policy violations (target: near zero).
- Operational impact: delta in MTTA/MTTR for pilot services vs control cohort; on-call survey load reduction.
- Postmortem completeness score: required sections present, timeline accuracy vs ground truth, and link integrity to raw telemetry.

## Reliability and failure handling
- Exponential backoff and jitter on vendor APIs; circuit-break per integration with graceful degradation to partial briefs.
- Idempotent remediation: stable keys, pre-flight checks, and automatic verification; no double-apply on webhook retries.
- Partial failure modes: if logs are missing, fall back to metrics and traces; if deployment API is down, flag “change correlation unavailable.”
- Secrets and PII redaction in transcripts before model context and before external storage; fail closed on redaction errors.
- Human-in-the-loop timeouts: if approval stalls, re-notify and optionally escalate per paging rules rather than silently waiting.

## Rollout phases
- v0: read-only copilot—incident enrichment, observability pulls, deployment correlation, and sandboxed diagnostics with no production mutations; shadow mode evaluation on recorded incidents.
- v1: approval-gated remediation for a narrow auto-allow list plus full human approval for broader fixes; full timeline and postmortem export; paging escalation integration with explicit severity and confidence gates.
- v2: expanded auto-allow policies per service maturity, richer multi-service blast-radius reasoning, deeper integration with runbooks and status-page updates, and continuous learning from postmortems (policy-tuned, not unbounded self-change).
