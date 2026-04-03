# Support Agent Build Spec

## Domain
Customer support triage, reply assistance, and escalation for SaaS and e-commerce teams handling inbound tickets across email, chat, and web forms.

## User goal
Help support teams gather case context from internal systems, classify ticket intent and urgency, draft safe replies that follow policy, and escalate to the right team when risk, sentiment, or complexity requires it. Reduce time-to-first-response and improve consistency without bypassing compliance or tone guidelines.

## Success condition
- First-response time improves measurably for ticket categories where the agent is active.
- Drafted replies pass quality review at a high rate without heavy human editing.
- Escalations are timely and route to the correct team with a useful briefing; no silent drops.
- Policy-sensitive topics (refunds, account closures, legal requests) always route through approval or escalation, never auto-sent.
- Customer satisfaction scores remain stable or improve in agent-assisted channels.

## Core workflow
- Ingest new or updated ticket from helpdesk (Zendesk, Intercom, Freshdesk, or similar).
- Enrich the ticket with customer context: account status, recent orders, prior tickets, product usage data.
- Classify intent (billing, technical, feature request, complaint, legal) and urgency (low, normal, high, critical).
- Check policy: does this ticket type allow an agent-drafted reply, or must it escalate immediately?
- Draft a reply using the knowledge base, brand voice guide, and case context.
- Route for approval or send directly, depending on ticket category and policy.
- Track resolution, customer response, and satisfaction signals for evaluation.

## Controller loop
1. Receive ticket event (new, updated, or reopened) and load ticket metadata, customer profile, and conversation history.
2. Classify intent and urgency using ticket content, customer signals, and historical patterns.
3. Check routing policy: if the category requires immediate escalation (legal, safety, VIP), route and stop.
4. Gather additional context: pull order history, product logs, knowledge base articles, and prior resolution notes.
5. Draft a reply following the brand voice guide and relevant knowledge base content.
6. If the ticket category allows auto-send for low-risk replies, send directly; otherwise queue for human review.
7. On human feedback (edit, approve, reject, escalate), record the decision and update session state.
8. If the ticket is resolved, log outcomes and satisfaction; if not, loop from step 1 on the next customer reply.

## Context inputs
- Ticket metadata: id, channel, subject, body, timestamps, tags, and assignee.
- Customer profile: account tier, tenure, recent orders, open tickets, lifetime value.
- Conversation history: prior messages in this ticket and related recent tickets.
- Knowledge base: articles, macros, and canned responses relevant to the classified intent.
- Brand voice guide: tone rules, forbidden phrases, escalation language templates.
- Policy rules: which ticket categories allow auto-send, which require review, which must escalate.

## Tools
- `fetch_ticket_context` — ticket metadata, conversation history, and tags from the helpdesk API.
- `lookup_customer_profile` — account, orders, usage, and prior ticket history.
- `search_knowledge_base` — retrieve relevant articles, macros, and resolution templates.
- `classify_ticket` — determine intent, urgency, and routing disposition.
- `draft_reply` — generate a reply draft using context and brand voice rules.
- `send_or_escalate` — send the approved reply, assign to a human queue, or escalate to a specialized team.

## Session state
- `ticket_id`, `channel`, `customer_id`, `account_tier`.
- `intent_classification` and `urgency_level` with confidence scores.
- `context_gathered`: order history snippets, KB article ids, prior resolution notes.
- `draft_history`: list of drafts with timestamps and reviewer feedback.
- `approval_status`: pending, approved, rejected, escalated.
- `resolution_status`: open, waiting_on_customer, resolved, escalated.
- `satisfaction_signal`: CSAT score, response sentiment, or reopen flag.
- `tool_call_log`: append-only record of tool invocations and outcomes.

## Permissions and approvals
- Read-only access to helpdesk, CRM, and knowledge base is auto-allow.
- Sending replies for low-risk categories (FAQ, order status) may be auto-allow if policy permits and confidence is high.
- Refund actions, account modifications, and any financial commitment require human approval.
- Legal, safety, and compliance-flagged tickets always escalate; the agent must not draft replies for these.
- Customer PII is never logged in full; session state stores references and hashed identifiers.

## Stop conditions
- Ticket is resolved and customer confirms or no response within SLA window.
- Ticket is escalated to a human team and the agent's role is complete.
- Policy violation detected: ticket reclassified to a restricted category mid-conversation.
- Required context unavailable (CRM down, customer not found) after bounded retries; agent surfaces a handoff summary.
- Human reviewer rejects the draft and takes over the ticket.

## Observability
- Structured logs per turn: ticket id, intent, tool calls with latency, draft version, and routing decision.
- Metrics: first-response time, drafts per ticket, approval rate, escalation rate by category, and auto-send rate.
- Audit trail for every sent reply and escalation: who approved, when, and what was sent.
- Dashboards for quality: human edit distance on drafts, rejection reasons, and CSAT by agent-assisted vs manual.
- Alerts on anomalies: sudden escalation spikes, high rejection rates, or repeated failures on a ticket type.

## Evaluation
- Draft quality: human edit distance between agent draft and final sent reply (lower is better).
- Classification accuracy: intent and urgency predictions vs human labels on a golden set.
- Resolution rate: percentage of tickets where the agent-assisted reply resolved the issue without follow-up.
- Safety: zero policy-violating auto-sends; escalation recall on sensitive categories.
- Customer satisfaction: CSAT and reopen rates for agent-assisted tickets vs baseline.

## Reliability and failure handling
- Bounded retries with backoff on helpdesk and CRM API failures; degrade to manual routing if context is unavailable.
- Idempotent reply sends: dedupe by ticket id and draft hash to prevent duplicate customer messages.
- Graceful degradation: if the knowledge base is unreachable, draft a shorter reply and flag it for human review.
- Rate limiting on outbound replies to prevent spam in case of loop bugs.
- Timeout on human approval: if no reviewer acts within the configured window, re-notify or auto-escalate.

## Rollout phases
- **v0**: Read-only assistant — classifies tickets, gathers context, and drafts replies visible only to the support team in an internal panel. No auto-send. Evaluate draft quality and classification accuracy against human outcomes.
- **v1**: Approval-gated sending for low-risk categories (FAQ, order status). All other categories remain draft-only or auto-escalate. Full observability and audit trail live. CSAT monitoring active.
- **v2**: Expanded auto-send for categories where v1 demonstrated high approval rates and stable CSAT. Proactive suggestions (e.g., "similar tickets resolved with..."). Cross-ticket pattern detection for systemic issues. Continuous evaluation with monthly quality reviews.
