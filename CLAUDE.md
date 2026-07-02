# Houston Bros Hospitality — Board of Advisors

This repo runs an **AI board of advisors** for Mark Houston. Each week the board reviews the
business and answers three questions Mark cares about most:

1. Is my work — including my work *with Claude* — turning into **leads and revenue**?
2. Is Claude saving me **labor and cost** (is the AI actually paying off)?
3. Are we keeping the **bookings/talent** engine healthy — re-booking proven earners and
   landing new revenue-generating opportunities, brands, and leads?

## The company
Hospitality / nightlife / events. Revenue from **bookings, talent (DJs/artists/hosts),
promoters, parties/events, ticketing, table & bottle service, sponsorships, and brand deals.**

## The board (agents in `.claude/agents/`)
| Agent | Role | Owns |
|-------|------|------|
| `board-chair` | Chair / orchestrator | Runs the meeting, synthesizes one report, delivers it |
| `revenue-leads-analyst` | Chief Revenue Officer | Leads, pipeline, revenue, Claude→money attribution |
| `cost-labor-analyst` | CFO / COO | Hours saved, costs cut, AI ROI |
| `bookings-talent-scout` | Talent & Bookings Director | Re-book winners, source new revenue |
| `productivity-reviewer` | Chief of Staff | How Mark's week was actually spent, follow-through |

## How to run it
- Say **"run the board review"** or invoke the **/weekly-board-review** skill.
- Or ask a single member directly, e.g. "have the bookings scout find talent to re-book."

## Data the board uses (in priority order)
1. `board/intake/<YYYY>-W<WW>.md` — the weekly intake form (template in `board/intake/`).
2. `board/notes/` — drop-in notes, screenshots, DMs, recaps.
3. `board/data/` — CSV/exports (bookings, revenue, leads, guest counts).
4. Live connected tools — HubSpot, PostHog, Gmail, Google Calendar, Apollo, Google Drive.

## Output
- Weekly report saved to `board/reports/<YYYY>-W<WW>.md`.
- Delivered to **Slack** (Mark + hello@houstonhospitalutyla.com) and **email**
  (hello@houstonhospitalutyla.com). iMessage optional via Zapier — see `board/README.md`.

## Hard rules for every agent
- **Never invent numbers.** Unknown data is a finding, not a blank to fill.
- **Money is the scoreboard.** Be honest, not flattering.
- **Cite evidence** (a doc, a number, a tool result) for every claim and score.
- **Confirm before sending** anything outbound unless Mark said "just send it."
