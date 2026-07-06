# CLAUDE.md

Operating rules for working with Claude on Houston Bros Hospitality.

## Business context

Houston Bros Hospitality is a hospitality business. Most work here is a mix of
operations, analytics, marketing, and customer communication — not only writing
code. When a task involves data or metrics, treat the connected tools as the
source of truth (PostHog for product/web analytics, HubSpot for CRM, Ahrefs for
SEO, Apollo for prospecting, Gmail/Slack for communication). Never guess a number
you can look up.

## Engineering rules

### 1. Role routing

Before starting any non-trivial task, identify the right mode (planning,
building, reviewing, debugging, testing). State your role and what you will and
won't do in this mode. Skip the ceremony for quick questions — just answer them.

### 2. Search before building

Before writing new code, search the existing codebase for similar functionality.
Never duplicate what already exists.

### 3. Effort matching

Match your depth to the task. Quick fixes and quick questions get quick
responses. Architecture decisions and anything that affects customers or revenue
get thorough analysis with tradeoffs.

## Business & customer guardrails

### 4. Protect customer data

Never put guest or customer PII — names, contact details, reviews, booking
records, contact lists — into external tools or public output without explicit
approval first. When in doubt, ask.

### 5. Draft, don't send

Anything guest-facing (emails, Slack messages, social posts, campaigns) is a
draft until Mark confirms it. Never send, publish, or schedule customer-facing
communication automatically.

### 6. Cite the source of every number

When reporting a metric or result, state which connected tool it came from
(e.g. "PostHog", "HubSpot") and the time range, so the number can be trusted and
re-checked.

## Kickoff

### 7. Scope before building

For any non-trivial build — code, a workflow, an automation, a campaign, or a
report — run a short kickoff interview before starting, and summarize the answers
back before doing any work:

- What is the core problem this solves?
- Who is this for?
- What does success look like?
- What should this NOT do?
- What's the simplest version?
- How will we verify it works?

Pairs with Rule 2: first scope it, then search for what already exists, then
build.
