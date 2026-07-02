# The Board — how it works

Your AI board of advisors reviews the business every week and tells you, straight, whether
your effort (and your work with Claude) is turning into **leads, revenue, and savings** —
and whether the **bookings/talent** engine is healthy.

## Run the weekly review
Say **"run the board review"** (or use the `/weekly-board-review` skill). The Chair will:
1. Set the week's date range.
2. Pull your intake form + notes + data + live tools.
3. Send the four specialists to work.
4. Hand you one report with a verdict, a scorecard, a straight answer on whether Claude is
   paying off, a bookings/talent watchlist, and your top 3 priorities.
5. Offer to post it to Slack and email it.

## Your 5-minute weekly job
Copy `intake/weekly-intake-template.md` → `intake/<YYYY>-W<WW>.md` and fill in what you can.
Blanks are fine — the board flags what's missing. Drop any exports/screenshots into `notes/`
or `data/`. That's it.

## Folders
- `intake/` — your weekly form (one file per week).
- `notes/` — drop-in notes, screenshots, DMs, event recaps.
- `data/` — CSV/exports (bookings, revenue, leads, guest counts).
- `reports/` — the board's weekly reports land here (version-controlled history).

## Delivery channels
- **Slack** ✅ — connected. Posts to your board channel (you + hello@houstonhospitalutyla.com).
- **Email** ✅ — connected. Sends to hello@houstonhospitalutyla.com.
- **iMessage** ⚙️ — no native iMessage tool exists in this environment. To get the report on
  iMessage/SMS, wire a **Zapier** action (Zapier is connected):
  1. In Zapier, create an action that sends an iMessage/SMS (e.g. via an Apple Shortcuts,
     Twilio SMS, or a Mac-based iMessage integration).
  2. Enable it, then tell the board "also send the report to my phone via Zapier."
  The board will only claim it texted you if a Zapier action actually ran.

## Ask a single board member
You don't have to run the whole meeting. Examples:
- "Have the **bookings-talent-scout** list proven talent I should re-book and 5 new brands to chase."
- "Ask the **cost-labor-analyst**: did Claude save me money this week?"
- "Have the **revenue-leads-analyst** check if my outreach turned into pipeline."
