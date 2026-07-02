---
name: weekly-board-review
description: >
  Run the Houston Bros Hospitality weekly board review. Use when Mark says "run the board
  review", "what does the board think", "how did my week go", or on a weekly cadence. This
  convenes the board-chair, which delegates to the four specialist members and produces one
  synthesized board report, then offers to deliver it via Slack and email.
---

# Weekly Board Review

You are kicking off the weekly board meeting for Houston Bros Hospitality. Follow these steps.

## Step 1 — Set the period
Default to the **last 7 days ending today**. State the exact date range and the week number
(`<YYYY>-W<WW>`).

## Step 2 — Gather inputs (use what exists; never fabricate)
1. Look for this week's intake at `board/intake/<YYYY>-W<WW>.md`.
   - **If it's missing**, either (a) walk Mark through the questions in
     `board/intake/weekly-intake-template.md` right now and save his answers to that path,
     or (b) proceed with tools + notes only and flag that intake was skipped.
2. Read anything in `board/notes/` and `board/data/`.
3. Read last week's report in `board/reports/` (for follow-through checking).
4. Note which live tools are connected (HubSpot, PostHog, Gmail, Calendar, Apollo, Drive).

## Step 3 — Convene the board
Dispatch the **board-chair** agent with the period and the gathered inputs. The Chair always
runs the core four (revenue-leads-analyst, cost-labor-analyst, bookings-talent-scout,
productivity-reviewer) and adds the specialist seats (brand-marketing-advisor,
guest-reputation-advisor, risk-compliance-advisor, growth-vision-advisor) when the week's
inputs touch their area or Mark asks for a "full board." The Chair reconciles their findings
and produces the report in the standard format.

## Step 4 — Save the report
Write it to `board/reports/<YYYY>-W<WW>.md`.

## Step 5 — Deliver
Show Mark the report, then offer delivery:
- **Slack** — post to the board channel (Mark + hello@houstonhospitalutyla.com).
- **Email** — send to hello@houstonhospitalutyla.com, subject `Board Review — <date range>`.
- **iMessage** — only via a Zapier action if configured (see `board/README.md`).

Confirm before sending anything outbound unless Mark has already said "just send it."

## Guardrails
- Never invent revenue, hours, or attendance figures. Unknown = unknown, and it goes in
  "What I need from Mark."
- Keep the final report to the standard format — verdict, scorecard, Claude-ROI answer,
  wins, risks, bookings/talent watch, top 3 priorities.
