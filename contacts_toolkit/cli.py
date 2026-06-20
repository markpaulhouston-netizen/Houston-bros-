"""Command-line orchestrator for the Birthday Contacts Toolkit.

One command takes a Google Contacts CSV export and produces, in an output
folder:

* ``contacts_clean.csv``        — deduplicated, re-importable into Google Contacts
* ``missing_birthdays.csv``     — everyone with no/invalid birthday (to fill in)
* ``upcoming_birthdays.csv``    — rolling 12-month birthday schedule
* ``birthdays.ics``             — import once into Google Calendar; every
                                  birthday becomes a yearly all-day reminder
* ``birthday_drafts.md`` / ``.csv`` — personalized message drafts
* ``SUMMARY.txt``               — what changed, at a glance

Examples
--------
    python -m contacts_toolkit.cli all  sample_data/contacts_sample.csv  -o output
    python -m contacts_toolkit.cli all  ~/Downloads/contacts.csv  --tone warm
    python -m contacts_toolkit.cli birthdays  contacts.csv          # just the calendar
"""

from __future__ import annotations

import argparse
import os
from datetime import date

from .parse import load_contacts, write_contacts
from .dedupe import deduplicate
from .birthdays import (
    birthday_stats,
    missing_birthday_report,
    upcoming_birthdays,
    write_ics,
)
from .messages import generate_drafts, write_drafts_csv, write_drafts_markdown


def _ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def _write_missing_csv(path: str, contacts) -> None:
    import csv

    with open(path, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["name", "emails", "phones", "raw_birthday_value"])
        for c in contacts:
            w.writerow([
                c.display_name,
                " ::: ".join(c.emails),
                " ::: ".join(c.phones),
                c.birthday_raw,
            ])


def _write_upcoming_csv(path: str, rows) -> None:
    import csv

    with open(path, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["name", "next_date", "days_away", "turning_age", "emails", "phones"])
        for r in rows:
            w.writerow([
                r["name"], r["date"], r["days_away"],
                r["turning_age"] if r["turning_age"] is not None else "",
                " ::: ".join(r["emails"]), " ::: ".join(r["phones"]),
            ])


def run_all(args) -> None:
    out = args.output
    _ensure_dir(out)

    print(f"Loading contacts from {args.input} ...")
    contacts = load_contacts(args.input)
    print(f"  loaded {len(contacts)} rows")

    # 1. Deduplicate & clean -------------------------------------------------
    cleaned, stats = deduplicate(contacts)
    clean_path = os.path.join(out, "contacts_clean.csv")
    write_contacts(clean_path, cleaned)
    print(f"\n[1/4] Dedupe & clean: {stats['input_count']} -> {stats['output_count']} "
          f"({stats['duplicates_removed']} duplicates merged across "
          f"{stats['groups_with_duplicates']} people)")
    print(f"      wrote {clean_path}")

    # 2. Missing birthdays ---------------------------------------------------
    bstats = birthday_stats(cleaned)
    missing = missing_birthday_report(cleaned)
    missing_path = os.path.join(out, "missing_birthdays.csv")
    _write_missing_csv(missing_path, missing)
    print(f"\n[2/4] Birthdays on file: {bstats['with_valid_birthday']} / {bstats['total']}  "
          f"({bstats['missing']} missing)")
    print(f"      wrote {missing_path}  (the list to fill in)")

    # 3. Calendar (.ics) + upcoming schedule --------------------------------
    today = date.today()
    upcoming = upcoming_birthdays(cleaned, from_date=today, days=365)
    upcoming_path = os.path.join(out, "upcoming_birthdays.csv")
    _write_upcoming_csv(upcoming_path, upcoming)
    ics_path = os.path.join(out, "birthdays.ics")
    write_ics(ics_path, cleaned, calendar_name="Birthdays",
              reminder_days_before=args.reminder_days)
    print(f"\n[3/4] Calendar: {len(upcoming)} birthdays in the next 12 months")
    print(f"      wrote {ics_path}  (import once into Google Calendar)")
    print(f"      wrote {upcoming_path}")

    # 4. Message drafts ------------------------------------------------------
    drafts = generate_drafts(cleaned, tone=args.tone, sender_name=args.sender)
    drafts_md = os.path.join(out, "birthday_drafts.md")
    drafts_csv = os.path.join(out, "birthday_drafts.csv")
    write_drafts_markdown(drafts_md, drafts)
    write_drafts_csv(drafts_csv, drafts)
    print(f"\n[4/4] Drafted {len(drafts)} '{args.tone}' birthday messages from {args.sender}")
    print(f"      wrote {drafts_md} and {drafts_csv}")

    # Summary ----------------------------------------------------------------
    summary_path = os.path.join(out, "SUMMARY.txt")
    next3 = upcoming[:3]
    with open(summary_path, "w", encoding="utf-8") as fh:
        fh.write("BIRTHDAY CONTACTS TOOLKIT — SUMMARY\n")
        fh.write(f"Generated: {today.isoformat()}\n\n")
        fh.write(f"Input contacts:         {stats['input_count']}\n")
        fh.write(f"After dedupe:           {stats['output_count']}\n")
        fh.write(f"Duplicates merged:      {stats['duplicates_removed']}\n")
        fh.write(f"Birthdays on file:      {bstats['with_valid_birthday']}\n")
        fh.write(f"Missing birthdays:      {bstats['missing']}\n")
        fh.write(f"Birthdays next 12 mo.:  {len(upcoming)}\n")
        fh.write(f"Message drafts:         {len(drafts)}\n\n")
        if next3:
            fh.write("Next up:\n")
            for r in next3:
                age = f" (turning {r['turning_age']})" if r["turning_age"] is not None else ""
                fh.write(f"  - {r['date']}  {r['name']}{age}  [{r['days_away']}d]\n")
    print(f"\nDone. See {summary_path}\n")


def _add_common(p):
    p.add_argument("input", help="Path to a Google Contacts CSV export")
    p.add_argument("-o", "--output", default="output", help="Output folder (default: output)")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="contacts_toolkit", description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)

    p_all = sub.add_parser("all", help="Run the full pipeline (recommended)")
    _add_common(p_all)
    p_all.add_argument("--tone", default="warm",
                       choices=["warm", "casual", "professional", "funny"],
                       help="Tone for birthday message drafts")
    p_all.add_argument("--sender", default="Mark Houston", help="Name to sign messages")
    p_all.add_argument("--reminder-days", type=int, default=1,
                       help="Days before each birthday to alert (calendar)")
    p_all.set_defaults(func=run_all)

    args = parser.parse_args(argv)
    args.func(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
