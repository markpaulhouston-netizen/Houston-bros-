# n8n — Recurring Content Automation (Spec)

The autopilot that drafts each week's posts so a human only has to approve and
attach media. Built on the n8n MCP server (account already connected).

## Goal

Turn the weekly calendar (`content-calendar.md`) + caption banks
(`captions/`) + accounts (`automation/blotato-accounts.md`) into **pre-drafted
Blotato posts every week**, with a human approval gate before anything fires.

## Workflow A — Weekly Draft Builder

```
Schedule Trigger (Mon 10:30 AM PT)
   │
   ▼
Code/Set node — load this week's slots from the calendar grid
   │  (venue, night, accountId, caption pool, posting window)
   ▼
For each slot:
   ├─ pick caption (rotate from captions/<venue>.md)
   ├─ build scheduleTime from day + window
   └─ create Blotato DRAFT post (no media yet → flagged "needs asset")
   │
   ▼
Notify (Slack/email) — "This week's drafts are ready. Attach media & approve."
```

**Why drafts, not live posts:** every post needs real media, and media is
human-supplied. The workflow does 90% of the work; the human attaches the
photo/video and approves.

## Workflow B — Performance Recap (optional, Friday)

```
Schedule Trigger (Fri 4:00 PM PT)
   │
   ▼
Pull last 7 days of post metrics (Blotato + PostHog/IG)
   │
   ▼
Rank by shares/saves → identify what worked
   │
   ▼
Notify — weekly recap + next-week recommendations
```

## Build order (when ready to implement)

1. `get_sdk_reference` (mandatory) → `get_suggested_nodes` → `search_nodes`
   for: Schedule Trigger, Code/Set, HTTP Request (Blotato), Slack/Email.
2. `get_node_types` for exact params.
3. Write workflow code → `validate_node_config` per node → `validate_workflow`.
4. `create_workflow_from_code`.

## Blockers before going live

- [ ] Connect `@madamesiamla` + `@andys_weho` in Blotato.
- [ ] Decide notification channel (Slack vs email).
- [ ] Confirm media-supply process (who uploads photos, where).
- [ ] Verify BRR Dine & Delight price.

## Manual fallback (works today, no n8n)

Until the workflow is built, posts can be scheduled directly:
`blotato_create_visual` (host media) → `blotato_create_post` (accountId +
caption + media URL + scheduleTime). See `automation/blotato-accounts.md`.
