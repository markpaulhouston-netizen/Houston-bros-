# Birthday Contacts Toolkit 🎂

A dependency-free (Python standard library only) toolkit that takes a **Google
Contacts CSV export** — even a messy iPhone→Google merge of ~11,000 contacts —
and does four jobs in one command:

1. **Dedupe & clean** the duplicate records iPhone+Gmail imports always create.
2. **Find missing birthdays** — a list of who has no birthday on file, to fill in.
3. **Build a birthday calendar** — an `.ics` file you import **once** into Google
   Calendar; every birthday becomes a yearly all-day reminder.
4. **Draft personalized birthday messages** for everyone, ready to copy-send.

No accounts, API keys, or installs required. Your contact data never leaves your
machine, and the included `.gitignore` keeps real contacts/output out of git.

---

## Step 1 — Export your contacts (the only manual step)

This needs your Google login, so only you can do it:

1. Go to **[contacts.google.com](https://contacts.google.com)** on a computer.
2. Left sidebar → **Export**.
3. Choose **"Export ALL"** (or a label) → format **"Google CSV"**.
4. Save the file (e.g. `contacts.csv`).

> Both Google CSV header styles are supported (legacy `Given Name…` and newer
> `First Name…`), with any number of email/phone columns.

## Step 2 — Run the toolkit

```bash
python3 -m contacts_toolkit.cli all /path/to/contacts.csv -o output
```

Options:

```
--tone {warm,casual,professional,funny}   message style (default: warm)
--sender "Mark Houston"                    name to sign messages
--reminder-days 1                          days before birthday to alert
```

## Step 3 — Use the results (everything lands in `output/`)

| File | What it is | What to do with it |
|------|-----------|--------------------|
| `contacts_clean.csv` | Deduplicated contacts | Re-import into Google Contacts (Import → select file). Optionally delete-all-then-import for a clean slate. |
| `missing_birthdays.csv` | Everyone with no/invalid birthday | Fill these in over time. |
| `birthdays.ics` | Birthday calendar | Google Calendar → Settings → **Import & export** → import this once. |
| `upcoming_birthdays.csv` | Next 12 months, sorted | Your at-a-glance schedule. |
| `birthday_drafts.md` / `.csv` | Personalized messages | Skim the `.md`, copy/paste to send. |
| `SUMMARY.txt` | What changed | Quick overview. |

---

## Try it now with sample data

A realistic 300-row sample (with duplicates, missing + mixed-format birthdays) is
included so you can see the output before touching your real file:

```bash
python3 -m contacts_toolkit.cli all sample_data/contacts_sample.csv -o output
cat output/SUMMARY.txt
```

Generate a larger synthetic file (e.g. 11,000 rows) to test scale:

```bash
python3 sample_data/make_sample.py 11000 sample_data/big_sample.csv
python3 -m contacts_toolkit.cli all sample_data/big_sample.csv -o output
```

## Project layout

```
contacts_toolkit/
  models.py      Contact data model + normalization (names, emails, phones)
  parse.py       Google CSV load/save (both header dialects, faithful re-export)
  dedupe.py      Union-find dedupe + record merging  (scales to 11k in <1s)
  birthdays.py   Birthday parsing, missing report, upcoming, .ics calendar
  messages.py    Personalized message drafts (4 tones)
  cli.py         Orchestrator: `python3 -m contacts_toolkit.cli all <csv>`
sample_data/     Sample export + generator
tests/           52 unit tests  (run: python3 -m unittest discover -s tests)
```

## Tests

```bash
python3 -m unittest discover -s tests -v
```

## How matching works (so you can trust the dedupe)

Two records are treated as the same person when they **share a normalized email
or a normalized phone** (phones reduced to their last 10 digits, emails
lowercased). Matching is transitive via union-find — if A shares a phone with B
and B shares an email with C, all three merge. Records with the **same name but
different contact info are kept separate** (different real people). When merging,
the richest record wins and all emails/phones are unioned; a birthday held by any
member is preserved.
