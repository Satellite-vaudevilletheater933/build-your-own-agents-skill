# Data Pipeline Monitor Agent — Build Spec

## Domain

- **Scope**: Batch and incremental data pipelines orchestrated by **Apache Airflow**, **Dagster**, and **dbt** (Cloud and Core), plus adjacent schedulers when DAGs invoke them (e.g., Kubernetes CronJobs, cloud vendor schedulers) when explicitly wired into the same monitoring surface.
- **Stakeholders**: Data engineering, analytics engineering, platform/SRE, and downstream consumers who depend on freshness, completeness, and schema stability.
- **Non-goals**: Real-time stream processing SLOs (unless a DAG explicitly models them), ad-hoc notebook execution without a defined run identity, and business logic approval of data *values* (only pipeline *health* and *quality gate* outcomes).

## User goal

- Reduce time-to-detect and time-to-resolve for failed or stalled pipeline runs without manual dashboard hopping.
- Classify failures so transient infrastructure issues are retried safely while code/schema regressions are escalated with evidence.
- Maintain a durable record of incidents, retries, and quality regressions for audits and postmortems.
- Surface trends (flaky tasks, growing durations, drifting row counts) so teams can prioritize hardening work.

## Success condition

- **Detection**: Failed runs and stall conditions (no heartbeat, queue backlog beyond threshold, run duration exceeding historical p95 + margin) are identified within the agent’s polling or event window, with correct linkage to DAG/run/task/dbt node identity.
- **Triage**: Each incident receives a **root-cause hypothesis** (transient vs permanent) backed by logs, metrics, and recent change signals; false-positive rate on “permanent” classification stays within agreed bounds after v1 calibration.
- **Action**: Transient failures trigger **bounded, idempotent retries** with backoff; permanent failures produce a **ticket or incident** with attachments and suggested owners.
- **Governance**: All automated retries and ticket creation are auditable; no silent cross-environment promotion or schema mutation.

## Core workflow

1. **Ingest signals** from orchestrators (run state, task instances, op events, dbt run/test results) and observability backends (logs, metrics, traces where available).
2. **Correlate** a single “incident” view: one logical failure may span Airflow task retry, dbt test failure, and downstream Dagster asset materialization.
3. **Classify** using rules + evidence: exit codes, OOM, spot preemption, connection timeouts vs compilation errors, schema drift, failed assertions.
4. **Act**: enqueue retry (with caps), open/update ticket, notify on-call channel, or attach to an existing incident if deduplication matches.
5. **Learn**: update session-local health snapshots and periodic recommendations (e.g., “increase pool size for DAG X,” “stabilize test Y”).

## Controller loop

1. Pull or receive **run/task/asset state** updates for configured namespaces, projects, and environments (dev/stage/prod).
2. For each **new terminal failure** or **suspected stall**, resolve **stable IDs** (dag_id, run_id, task_id / op / asset key / dbt unique_id) and fetch **last N log segments** and **relevant metrics** (duration, rows processed, executor stats).
3. Load **session state** and **recent incident history** for deduplication and retry budget checks.
4. Run **classification**: transient (infra, quota, network, preemption) vs permanent (code, SQL, contract, schema, data test) vs unknown; if unknown, prefer **narrow investigation** (single extra log pull, dependency graph slice) before acting.
5. If **transient** and **within retry policy**: schedule **retry with exponential backoff and jitter**; record attempt metadata; if **permanent** or **budget exhausted**: **open or update incident ticket** with summary, evidence links, and blast-radius note.
6. **Emit** structured events for observability; if no new work and no open incidents requiring follow-up, **sleep** until next poll or webhook.

## Context inputs

- Orchestrator metadata: DAG/asset definitions (versions), schedule, pools/concurrency, retry defaults, and last successful run timestamps.
- **Run manifests**: task try number, executor, pod/node identity, region, warehouse size (where applicable).
- **Logs and stderr** (truncated, redacted) from failing steps; optional **OpenTelemetry** trace IDs when jobs emit them.
- **Data quality outputs**: dbt test results, Great Expectations or custom checks, anomaly detectors on row counts/null rates.
- **Change signals**: recent merges to dbt repo, Airflow variable/connection changes, image tags, and infra change windows (maintenance notices).
- **Org policy**: allowed environments for auto-retry, PII redaction rules, on-call rotations, and severity rubric.

## Tools

1. **`orchestrator_status`** — Query Airflow / Dagster / dbt APIs for run and task/node state, including history and dependencies.
2. **`log_fetch`** — Retrieve bounded log lines from centralized logging (e.g., Loki, CloudWatch, Datadog) with correlation by run ID.
3. **`metrics_query`** — Time-series queries for duration, queue depth, slot usage, warehouse credit burn, and custom pipeline KPIs.
4. **`retry_run`** — Trigger safe retries (task clear + trigger, dbt re-run subset, Dagster re-execution) according to policy and idempotency keys.
5. **`incident_ticket`** — Create/update tickets (Jira, ServiceNow, PagerDuty) with templates, severity, and artifact links.
6. **`quality_catalog`** — Read/write metadata about checks, SLAs, and last-known-good baselines for comparisons.

## Session state

- `tenant_id`, `environment`, `pipeline_scope` (allowlist of DAGs/assets/projects).
- `open_incidents`: map of dedupe key → ticket id, severity, first_seen, last_updated.
- `retry_ledger`: per logical task/node, attempt count, last_attempt_at, backoff_next_at, last_error_fingerprint.
- `health_snapshots`: rolling windows of success rate, p95 duration, flaky task list, last schema hash seen per model.
- `classification_cache`: short TTL cache of fingerprints → {label, confidence, evidence pointers} to avoid thrashing APIs.
- `user_approvals_pending`: optional human gates for cross-env actions or high-blast-radius retries.
- `audit_tail`: append-only record of tool calls and decisions for this session (bounded size, exportable).

## Permissions and approvals

- **Read-only by default** across orchestrators and logs; **retry** and **ticket** tools require scoped credentials per environment.
- **Auto-retry** only in non-prod or in prod for allowlisted DAGs/tasks with **max attempts** and **cooldown** caps; prod-wide auto-retry requires explicit policy flag.
- **Human-in-the-loop** for: first-time permanent classification on a new error signature, retries that touch shared warehouses above cost threshold, and any action that could **reprocess PII** outside approved windows.
- Secrets never stored in session state; only **references** to secret mounts or vault paths; logs scrubbed per DLP rules.

## Stop conditions

- Incident **resolved** (successful run after retry or owner closes ticket with documented waiver).
- **Escalation** to human on-call when SLA breach is imminent and automated path is exhausted.
- **Safety stop**: conflicting concurrent runs detected, retry would violate idempotency, or policy marks the failure type as “do not retry” (e.g., checksum mismatch on source contract).
- **Session bound**: maximum wall-clock or tool-call budget per incident to avoid infinite loops; remainder summarized for handoff.

## Observability

- Structured **decision logs**: incident id, inputs hash, classification, actions taken, latency per tool, and outcome.
- **Counters**: incidents opened, auto-retries succeeded/failed, false transient rate, mean time to detect/resolve.
- **Traces**: optional OpenTelemetry spans around each controller loop iteration and external API call.
- **Dashboards**: pipeline reliability scorecards and flaky-task heatmaps fed by agent-emitted events (not only raw orchestrator UI).

## Evaluation

- **Offline**: replay labeled incidents (historical failures with known root cause) and measure precision/recall on transient vs permanent labels and appropriate action (retry vs ticket).
- **Online shadow mode**: classify and recommend actions without executing retries/tickets; compare to human outcomes for a calibration period.
- **SLOs**: target MTTD/MTTR improvement vs baseline; cap on **retry-induced duplicate work** (duplicate rows, double spend) measured via warehouse/job cost tags.
- **Quality gate**: periodic review of tickets opened by the agent for noise rate and completeness of attachments.

## Reliability and failure handling

- **Idempotent** ticket creation using stable dedupe keys; tolerate duplicate webhooks without double-escalation.
- **Backoff and circuit breaking** when upstream APIs (Airflow, Dagster, dbt, logging) rate-limit or error; degrade to “collect evidence only” rather than blind retry.
- **Partial data**: if logs are missing, still open a ticket with available metadata and mark confidence low.
- **Clock skew / out-of-order events**: reconcile using run start/end timestamps and monotonic sequence numbers from APIs.
- **Disaster**: if orchestrator is unreachable, fall back to **metric-based stall detection** on known schedules and notify platform.

## Rollout phases

### v0 — Read-only copilot

- Ingest status from one orchestrator family (e.g., Airflow only) in a single environment; summarize failures and draft ticket text **without** automated actions.
- Validate redaction, deduplication keys, and log correlation; no retries.

### v1 — Guarded automation

- Add Dagster and dbt read paths; enable **auto-retry** for a narrow allowlist of transient signatures in non-prod; prod limited to **ticketing + notify** with optional one-click human approval for retry.
- Session state, audit tail, and basic dashboards live; shadow evaluation for classification.

### v2 — Production operator

- **Cross-system correlation** (e.g., dbt failure → downstream Dagster asset stale); **SLA monitoring** with predictive stall warnings; **retry with backoff** in prod per policy; **continuous health trends** and prioritized improvement backlog.
- Integration with change management (link tickets to deploys) and cost-aware retry caps; periodic automated evaluation reports for stewards.
