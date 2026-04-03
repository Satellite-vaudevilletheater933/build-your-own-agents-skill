# Research Assistant Agent Build Spec

## Domain
- Scholarly literature discovery, synthesis, and reporting across STEM and biomedical domains.
- Primary indexes: arXiv (preprints and physics or CS or math), Semantic Scholar (broad metadata and citations), PubMed or PMC (life sciences and clinical abstracts or links).
- Emphasis on reproducible citations, transparent provenance, and explicit gap or contradiction analysis rather than generic summaries.
- Boundaries: the agent advises on research direction but does not fabricate empirical results, patient guidance, or legal or regulatory determinations.
- Outputs are structured documents (sections, tables of methods, bibliographies) suitable for team review, grant prep, or stakeholder briefings.

## User goal
- Accept a research question or topic and optional constraints (years, methods, populations, geography, language).
- Search and rank relevant work across arXiv, Semantic Scholar, and PubMed with deduplication and source transparency.
- Fetch abstracts and full text where allowed; fall back gracefully when only metadata or abstract exists.
- Extract key findings, methods, datasets, limitations, and citation relationships into reusable notes.
- Build a structured literature review that names agreements, disagreements, and open questions in the field.
- Deliver a formatted report with inline citations and a maintained bibliography; preserve reading progress for iterative refinement.

## Success condition
- The delivered review includes a bibliography aligned with every substantive citation in the body (no orphan cites, no missing entries).
- Claims about individual papers are traceable to retrieved text or abstract; uncertain or conflicting evidence is labeled as such.
- Research gaps and contradictions are called out with pointers to specific papers or sets of papers, not vague language.
- Scope, depth, tone, and citation style match the user brief (e.g., expert technical vs. executive summary).
- Reading progress and corpus decisions are recoverable if the user resumes the same thread or session.
- The user can verify top-cited or central papers via DOI, PMID, arXiv id, or stable URLs recorded in session state.

## Core workflow
- Ingest and clarify the research question, scope, inclusion or exclusion criteria, and output format (length, citation style, section outline).
- Query arXiv, Semantic Scholar, and PubMed (and deduplicate across sources) to build a ranked candidate corpus.
- Apply transparent ranking heuristics (recency, citation count where available, query relevance, study type) and let the user override or freeze the shortlist when policy allows.
- Fetch metadata, abstracts, and full text where licensed or openly available; record provenance and access path for each document.
- Extract claims, methods, datasets, limitations, and citation networks; cluster by theme and chronology where helpful.
- Synthesize themes, contradictions, and research gaps; align conclusions strictly to retrieved text (no invented studies).
- Assemble a formatted report with a maintained bibliography and a reading-progress ledger the user can resume later.

## Controller loop
1. Normalize the user request into a research brief (question, boundaries, deliverable, citation style, language).
2. Plan retrieval: choose query variants, filters (years, study type), and per-source quotas to balance recall and cost.
3. Execute searches and merge results; deduplicate by DOI, arXiv ID, PMID, or title or author fingerprint.
4. For each prioritized paper, fetch abstract and full text when permitted; update session bibliography and reading status.
5. Extract structured notes (findings, methods, sample size, limitations, key citations); cross-check for inconsistency across papers.
6. Draft and refine the literature review sections; insert citations; highlight gaps and conflicting evidence explicitly.
7. Offer optional user checkpoints (e.g., confirm corpus before deep read, confirm outline before final prose) based on policy.
8. Finalize the report artifact, export bibliography, and persist state for follow-up questions or iterative refinement.

## Context inputs
- Original research question or topic statement and any sub-questions or hypotheses the user cares about.
- Scope constraints: field, date range, geography, population, intervention type, or methodology filters.
- Citation and formatting requirements (e.g., APA, Chicago, BibTeX) and target length or audience.
- Institutional or subscription context (what full-text access the runtime may assume, if any).
- Prior session state: bibliography, papers already summarized, and user edits to the running outline.
- User risk preferences: how aggressive to be about paywalled content, preprints vs. peer-reviewed only, and language of sources.

## Tools
- `search_scholarly_indexes`
- `fetch_paper_record`
- `retrieve_full_text`
- `extract_structured_paper_notes`
- `synthesize_literature_review`
- `export_report_and_bibliography`

## Session state
- `research_brief` (normalized question, scope, deliverable, citation style).
- `candidate_papers` (ranked list with source ids, scores, and dedupe keys).
- `reading_ledger` (per paper: status abstract or full text, timestamps, excerpts hash).
- `extracted_notes` (structured fields per paper: methods, results, limitations, citations).
- `synthesis_outline` (sections, themes, gap and contradiction flags).
- `bibliography_entries` (canonical records with URLs, DOIs, PMIDs, arXiv ids).
- `user_checkpoints` (pending approvals or answered decisions affecting the run).

## Permissions and approvals
- Search and metadata fetch are auto-allow within configured rate limits and allowed domains or API keys.
- Full-text retrieval is allow only for open access, user-uploaded PDFs, or paths covered by explicit entitlement; otherwise stop and request user-provided files or links.
- Large batch downloads or unusually broad queries require confirmation to control cost and compliance.
- No circumvention of paywalls, robots.txt, or terms of service; agent must surface “unavailable full text” honestly.
- Export of reports containing third-party abstracts or long quotations may require user acknowledgment of fair-use or institutional policy where applicable.

## Stop conditions
- The deliverable report and bibliography meet the brief and are emitted to the user.
- Corpus is empty or irrecoverably low quality after expanded queries and user is informed with next-step options.
- Required full text cannot be obtained for papers central to the question and user declines alternatives.
- Repeated tool failures exceed the failure budget or APIs return sustained authorization errors.
- User cancels, narrows scope to a closed follow-up, or explicitly ends the session.

## Observability
- Structured logs per tool call: source (arXiv, Semantic Scholar, PubMed), latency, result counts, and error class.
- Trace identifiers tying search batches to final citations in the report for auditability.
- Metrics on deduplication rate, abstract vs. full-text coverage, and tokens or pages processed.
- User-visible progress events (e.g., papers scanned, sections drafted) without leaking restricted content in logs.
- Alerts on quota exhaustion, abnormal empty-result rates, or citation integrity checks failing (broken DOI links, mismatched titles).

## Evaluation
- Citation correctness: sampled references resolve and match quoted claims in the report body.
- Coverage: recall proxy against a human-curated gold set for benchmark topics; precision via irrelevant-paper rate in top-k.
- Synthesis quality: rubric for gap and contradiction identification vs. expert review on held-out questions.
- Faithfulness: no unsupported factual claims about papers not present in session state; abstention when evidence is thin.
- Usability: time to first useful outline, edit burden on the user, and satisfaction on clarity of methods and limitations sections.

## Reliability and failure handling
- Exponential backoff and jitter on idempotent search and metadata reads; respect `Retry-After` when APIs provide it.
- Idempotent full-text fetches keyed by stable paper id; cache blobs and hashes to avoid redundant downloads.
- Graceful degradation: if one index is down, continue with others and note coverage bias in the report.
- Partial runs persist state so the user can resume; never silently drop papers already in the bibliography.
- On ambiguous paper identity, disambiguate with authors, year, and venue before merging or citing.

## Rollout phases
- **v0**
  - Question intake, scope normalization, and multi-index search with deduplication.
  - Abstract-level reading and synthesis only; open-URL full text only if trivially reachable without entitlement.
  - Bibliography export and reading ledger; operator or user heavily reviews draft prose and citations.
  - Baseline observability: search and fetch success rates, no PII in logs.
- **v1**
  - Full-text ingestion for open access and user-supplied PDFs; structured extraction templates per paper type (RCT, review, preprint).
  - Explicit gap and contradiction subsections; automated citation-integrity checks (resolver spot checks, title or year mismatches).
  - Checkpointed approvals: confirm corpus size, exclusion rules, and outline before long extraction runs.
  - Rate limits and cost caps enforced per tenant; resume from last persisted `reading_ledger` state.
- **v2**
  - Citation graph traversals (e.g., influential surveys, conflicting clusters) and optional method-comparison tables.
  - Configurable offline evaluation on benchmark questions with human-labeled gold corpora.
  - Institutional entitlement integration (library link resolvers, SSO-gated fetches where contractually allowed).
  - Operator dashboards: coverage bias by source, faithfulness regressions, and user satisfaction trends.
