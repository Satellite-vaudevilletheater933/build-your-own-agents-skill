# Code Review Agent Build Spec

## Domain
Automated pull-request (PR) review for software teams: ingesting repository events, analyzing diffs and surrounding code, enforcing engineering standards, and surfacing actionable feedback on the hosting platform (e.g. GitHub, GitLab, Azure DevOps).

## User goal
Keep default branches healthy by catching defects, style drift, security issues, and architectural violations early—without drowning authors in noise—while giving maintainers visibility into review quality and author engagement over time.

## Success condition
Meaningful reduction in defects merged to protected branches (reverts, hotfixes, post-merge linter failures) paired with high signal-to-noise: most posted comments are accepted or addressed, blocking feedback is rare and justified, and review latency stays within SLO for watched repositories.

## Core workflow
- Subscribe to or poll configured repositories for new and updated PRs (opened, synchronized, ready-for-review).
- Resolve PR scope: base and head SHAs, changed files, labels, draft state, and required reviewer rules.
- Fetch unified diff, full file contents at head (and base when needed for context), and commit history on the PR branch.
- Run static analysis: language linters, type checkers, dependency and secret scanners, and optional SAST where licensed and allowed.
- Load and apply project style guide, coding conventions, and architecture rules (layering, forbidden imports, API stability).
- Synthesize structured findings with severity (info, suggestion, warning, blocking) and map each to file, line range, and rationale.
- Post inline and summary review comments on the PR; require explicit approval before any blocking-level or request-changes outcome.
- Persist coverage metadata and author response signals for dashboards and continuous improvement of prompts and rules.

## Controller loop
1. **Ingest event**: Receive webhook or dequeue job; validate signature, repo allowlist, and PR eligibility (not bot-only, not excluded paths unless configured).
2. **Hydrate context**: Resolve installation token or credentials; fetch PR metadata, diff stats, and lock status to avoid duplicate work on the same head SHA.
3. **Gather artifacts**: Pull diff patches, file blobs at head, relevant tests or configs touched, and abbreviated commit messages for intent hints.
4. **Execute checks**: Run static analysis jobs (queued or sandboxed), merge results with rule-engine evaluation against style and architecture corpora.
5. **Plan feedback**: Deduplicate overlapping findings; assign severity; draft human-readable comments with suggested fixes and doc links.
6. **Approval gate**: If any blocking finding or policy requires it, pause and wait for maintainer approval before publishing those items or setting review state to “changes requested.”
7. **Publish and record**: Post comments via platform API with idempotency keys; update session state, coverage counters, and emit telemetry.
8. **Follow-up**: On new pushes, invalidate stale inline threads where appropriate and re-run from step 2 with updated SHAs until PR is merged or closed.

## Context inputs
- Repository identifier, default branch, and protected-branch policy hints.
- PR number, title, body, author, reviewers, labels, and draft/ready state.
- Base and head SHAs, merge-base, and list of changed paths with patch hunks.
- File contents at head (and selectively at base) for context outside the diff.
- Commit history (messages, authors, timestamps) for the PR branch since merge-base.
- CI configuration snapshots (e.g. workflow files, `Makefile`, package scripts) when they affect interpretation of failures.
- Curated rule packs: style guide excerpts, architecture decision records (ADRs), and team-specific “do not” lists.

## Tools
- `fetch_pr_context` — metadata, labels, review state, and merge eligibility in one call.
- `get_pr_diff_and_files` — unified diff plus optional full-file fetches for touched paths.
- `list_commits_for_pr` — ordered commits from merge-base to head with metadata.
- `run_static_analysis` — linters, typecheck, security/secret scans in an isolated runner with timeouts.
- `evaluate_style_and_architecture_rules` — declarative rules over AST/graph or path patterns, with explanations.
- `publish_pr_review` — inline comments, summary review body, and optional review event (approve / comment / request changes).

## Session state
- `tenant_id`, `installation_id`, `repo_full_name`, `pr_number`, `pr_head_sha`, `pr_base_sha`.
- `last_reviewed_head_sha` and `review_run_id` for idempotency and deduplication.
- `findings[]` with stable `finding_id`, severity, path, line range, rule id, and fingerprint.
- `posted_comment_ids` mapping findings to platform comment identifiers for updates and resolution.
- `approval_status` for blocking publish gate (pending, approved, denied, not_required).
- `analysis_artifacts` URIs or hashes for logs, SARIF, and stdout captures.
- `coverage_stats` per run: files reviewed, lines in diff, rules evaluated, findings by severity.
- `author_response_history` aggregates: time-to-first-response, resolve rate, repeat-offense flags (privacy-preserving).

## Permissions and approvals
- Read-only access to code, metadata, checks, and (where needed) Actions/logs for the watched repos; no force-push or branch protection edits.
- `publish_pr_review` in “comment only” mode may proceed without human approval for non-blocking severities if policy allows.
- Any **blocking** severity, `request_changes` outcome, or automated dismissal of existing reviews requires maintainer or on-call approval per repo.
- Secrets and tokens are scoped to least privilege; the agent never exfiltrates full repository tarballs to external LLM endpoints without an explicit data-processing agreement path.
- Opt-out paths (e.g. `[skip-ai-review]`, label `no-bot-review`) are honored before expensive analysis.

## Stop conditions
- PR merged, closed, or converted to draft without “review drafts” enabled.
- Head SHA unchanged and a complete review for that SHA already exists (unless a manual re-run is requested).
- PR exceeds size thresholds (files or lines) and policy is to defer with a summary comment rather than full analysis.
- Required credentials missing, repository archived, or user revoked installation.
- Repeated infrastructure failures exhaust the per-PR failure budget for the rolling window.

## Observability
- Structured logs per run: correlation id, repo, pr, head SHA, duration, tool latencies, and exit codes.
- Metrics: reviews started/completed, findings by severity, comment post success rate, queue depth, and p95 end-to-end latency.
- Traces spanning webhook handling, sandbox scheduling, rule evaluation, and platform API calls.
- Audit trail for approval-gated actions: who approved, when, and which findings were published.
- Dashboards for review coverage (fraction of org PRs touched) and author engagement (response time, resolution) with sampling and aggregation.

## Evaluation
- **Precision/recall** on a golden set of PRs with human-labeled defects and acceptable style nits (offline replay).
- **Noise metrics**: author-rejected or ignored suggestion rate; maintainer overrides of blocking classifications.
- **Outcome metrics**: defect escape rate post-merge, CI failure rate on main, and revert frequency attributed to reviewed PRs.
- **Latency SLO**: percentage of PRs receiving first bot pass within N minutes of ready-for-review.
- **Safety**: red-team prompts and repos attempting prompt injection via PR bodies and malicious file names.
- Periodic human spot audits of a random sample of published reviews for tone, accuracy, and policy alignment.

## Reliability and failure handling
- Idempotent publishes: fingerprint findings and reuse or update existing comments instead of spamming duplicates on retries.
- Exponential backoff and jitter on platform API rate limits; respect `Retry-After` headers.
- Sandbox timeouts and resource caps; partial results degrade to a summary comment with links to full logs rather than silent failure.
- Circuit-breaking per repo or installation when error rates spike; alert on-call and pause new runs.
- Graceful degradation: if static analysis fails, still post rule-based and diff-only findings with explicit “analysis incomplete” banner.
- Secrets rotation and credential refresh without dropping in-flight jobs when possible.

## Rollout phases
- **v0 (shadow / internal)**: Single org or pilot repos; full analysis and structured output logged only or posted as draft comments visible to bot maintainers; no blocking severity; tune rules and prompts from false-positive reviews.
- **v1 (assisted review)**: Production posting for info/suggestion/warning; blocking and request-changes behind approval workflow; SARIF and check-run integration optional; SLO dashboards live; author response tracking enabled for aggregate reporting.
- **v2 (scaled governance)**: Org-wide rollout with policy-as-code packs per team, automatic re-review on push with thread invalidation, deeper architecture graphs (cross-package), prioritized queueing for high-risk paths, and closed-loop evaluation driving monthly rule and model updates.
