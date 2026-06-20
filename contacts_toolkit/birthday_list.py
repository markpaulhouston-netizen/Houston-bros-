"""Adapter for the "Birthday & Contact Outreach — Master List" sheet.

This is a *different* schema from a Google Contacts export. It comes from
birthday events pulled out of Google Calendar, with columns::

    Name | DOB (Month Day) | Birth Year | Type | Notes / Context |
    Social Handle | Channel (Text/Call/DM/Email) | Reach Out? (Y/N) |
    Last Contacted | Status | Raw Calendar Title

This module maps each row onto the toolkit's :class:`Contact` model so the
existing dedupe / birthday / message machinery can run on it, and produces a
clean calendar (``.ics``), a de-duplicated list, a month-by-month agenda, and
DM/text-ready message drafts that use the social handle + context notes.
"""

from __future__ import annotations

import csv
import os
from typing import List, Optional

from .models import Contact
from .dedupe import deduplicate
from .birthdays import parse_birthday, build_ics, upcoming_birthdays
from .messages import first_name_for

_MONTHS = {
    "january": 1, "february": 2, "march": 3, "april": 4, "may": 5, "june": 6,
    "july": 7, "august": 8, "september": 9, "october": 10, "november": 11,
    "december": 12,
}

# Column headers (tolerant of minor variants).
_C_NAME = "Name"
_C_DOB = "DOB (Month Day)"
_C_YEAR = "Birth Year"
_C_TYPE = "Type"
_C_NOTES = "Notes / Context"
_C_HANDLE = "Social Handle"
_C_CHANNEL = "Channel (Text/Call/DM/Email)"


def _to_iso_birthday(dob_month_day: str, birth_year: str) -> str:
    """Turn 'January 1' (+ optional '1987') into an ISO birthday string.

    Returns 'YYYY-MM-DD' when a year is known, else '--MM-DD' (year unknown).
    Returns '' if the month/day can't be parsed.
    """
    if not dob_month_day:
        return ""
    parts = dob_month_day.strip().split()
    if len(parts) < 2:
        return ""
    month = _MONTHS.get(parts[0].strip().lower())
    try:
        day = int(parts[1].strip().lstrip(",").strip())
    except ValueError:
        return ""
    if not month or not (1 <= day <= 31):
        return ""
    year = (birth_year or "").strip()
    if year.isdigit() and len(year) == 4:
        return f"{int(year):04d}-{month:02d}-{day:02d}"
    return f"--{month:02d}-{day:02d}"


def load_birthday_list(path: str) -> List[Contact]:
    """Parse the master-list CSV into Contact objects (birthday in ISO form)."""
    contacts: List[Contact] = []
    with open(path, "r", encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        for i, row in enumerate(reader):
            name = (row.get(_C_NAME, "") or "").strip()
            iso = _to_iso_birthday(row.get(_C_DOB, ""), row.get(_C_YEAR, ""))
            # Preserve everything in raw, but normalize the Birthday so the
            # generic writer/parser see a standard column too.
            raw = dict(row)
            raw["Birthday"] = iso
            contacts.append(
                Contact(
                    index=i,
                    raw=raw,
                    full_name=name,
                    birthday_raw=iso,
                    notes=(row.get(_C_NOTES, "") or "").strip(),
                )
            )
    return contacts


def _channel_and_target(contact: Contact) -> tuple[str, str]:
    """Decide how to reach this person from the sheet's hints."""
    handle = (contact.raw.get(_C_HANDLE, "") or "").strip()
    channel = (contact.raw.get(_C_CHANNEL, "") or "").strip()
    if handle:
        return ("DM", handle if handle.startswith("@") else f"@{handle}")
    if channel:
        return (channel, "")
    return ("text/call", "")


def draft_for(contact: Contact, sender_name: str = "Mark") -> str:
    """A short, warm birthday note suited to a DM/text."""
    name = first_name_for(contact)
    return (f"Happy Birthday, {name}! 🎂 Hope you're doing great — "
            f"thinking of you today and sending good vibes. — {sender_name}")


def run(path: str, out_dir: str = "output", sender_name: str = "Mark",
        reminder_days: int = 2) -> dict:
    """Process the master list end-to-end and write all artifacts.

    Returns a small stats dict for reporting.
    """
    os.makedirs(out_dir, exist_ok=True)
    raw_contacts = load_birthday_list(path)

    # Dedupe (the sheet has repeats like Alex Black / Amanda Maclachlan / etc.)
    cleaned, dstats = deduplicate(raw_contacts)
    valid = [c for c in cleaned if parse_birthday(c.birthday_raw)]

    # 1) Calendar
    ics_path = os.path.join(out_dir, "birthday_calendar.ics")
    with open(ics_path, "w", encoding="utf-8", newline="") as fh:
        fh.write(build_ics(valid, calendar_name="Birthdays",
                           reminder_days_before=reminder_days))

    # 2) Month-by-month agenda
    agenda_path = os.path.join(out_dir, "birthday_agenda.md")
    _write_agenda(agenda_path, valid)

    # 3) Cleaned CSV
    clean_path = os.path.join(out_dir, "birthday_list_clean.csv")
    _write_clean_csv(clean_path, cleaned)

    # 4) DM/text drafts
    drafts_path = os.path.join(out_dir, "birthday_dms.md")
    _write_drafts(drafts_path, valid, sender_name)

    return {
        "input_rows": dstats["input_count"],
        "after_dedupe": dstats["output_count"],
        "duplicates_merged": dstats["duplicates_removed"],
        "with_valid_birthday": len(valid),
        "ics": ics_path,
        "agenda": agenda_path,
        "clean_csv": clean_path,
        "drafts": drafts_path,
    }


_MONTH_NAMES = ["", "January", "February", "March", "April", "May", "June",
                "July", "August", "September", "October", "November", "December"]


def _write_agenda(path: str, contacts: List[Contact]) -> None:
    by_month: dict = {m: [] for m in range(1, 13)}
    for c in contacts:
        bd = parse_birthday(c.birthday_raw)
        if bd:
            by_month[bd.month].append((bd.day, c.display_name))
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("# Birthday Agenda (by month)\n\n")
        for m in range(1, 13):
            people = sorted(by_month[m])
            if not people:
                continue
            fh.write(f"## {_MONTH_NAMES[m]} ({len(people)})\n\n")
            for day, name in people:
                fh.write(f"- **{_MONTH_NAMES[m]} {day}** — {name}\n")
            fh.write("\n")


def _write_clean_csv(path: str, contacts: List[Contact]) -> None:
    cols = [_C_NAME, "Birthday", _C_TYPE, _C_NOTES, _C_HANDLE, _C_CHANNEL]
    with open(path, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(cols)
        for c in contacts:
            w.writerow([c.raw.get(col, "") for col in cols])


def _write_drafts(path: str, contacts: List[Contact], sender_name: str) -> None:
    rows = []
    for c in contacts:
        bd = parse_birthday(c.birthday_raw)
        channel, target = _channel_and_target(c)
        rows.append((bd.month, bd.day, c.display_name, channel, target,
                     draft_for(c, sender_name)))
    rows.sort(key=lambda r: (r[0], r[1]))
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("# Birthday Message Drafts (DM / text ready)\n\n")
        for month, day, name, channel, target, msg in rows:
            tgt = f" → {target}" if target else ""
            fh.write(f"### {_MONTH_NAMES[month]} {day} — {name}  "
                     f"_[{channel}{tgt}]_\n\n> {msg}\n\n")
