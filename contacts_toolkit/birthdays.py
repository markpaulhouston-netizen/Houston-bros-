"""Birthday parsing, reporting, and iCalendar export for the Contacts Toolkit.

This module turns the messy, mixed-format ``Birthday`` cells found in Google
Contacts exports into structured data, then derives useful views from it:

* :func:`parse_birthday` normalizes every birthday dialect we see in the wild
  (ISO with/without year, US ``M/D/Y``, ``YYYY/MM/DD``, bare ``M/D``) into a
  small :class:`BirthdayDate` value.
* :func:`missing_birthday_report` lists the contacts a user still needs to fill
  in (empty *or* unparseable birthdays).
* :func:`upcoming_birthdays` computes the next occurrence of each known
  birthday, with age and days-away, sorted soonest-first.
* :func:`build_ics` / :func:`write_ics` emit an RFC-5545 calendar of all-day,
  yearly-recurring birthday events with a display reminder.
* :func:`birthday_stats` summarizes coverage across a contact list.

Only the standard library is used.
"""

from __future__ import annotations

import calendar
from dataclasses import dataclass
from datetime import date, datetime
from typing import List, Optional

from .models import Contact

__all__ = [
    "BirthdayDate",
    "parse_birthday",
    "missing_birthday_report",
    "upcoming_birthdays",
    "build_ics",
    "write_ics",
    "birthday_stats",
]


# --------------------------------------------------------------------------- #
# Parsed value
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class BirthdayDate:
    """A parsed birthday.

    ``year`` is ``None`` when the source only recorded month/day (e.g. the ISO
    ``--MM-DD`` form or a bare ``M/D``). ``month`` and ``day`` are always set
    and validated to plausible calendar ranges.
    """

    year: Optional[int]
    month: int
    day: int


# Maximum day allowed per month (uses 29 for February so leap-day birthdays
# parse even when the year is unknown).
_MAX_DAY = {1: 31, 2: 29, 3: 31, 4: 30, 5: 31, 6: 30,
            7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31}


def _make(year: Optional[int], month: int, day: int) -> Optional[BirthdayDate]:
    """Validate components and build a :class:`BirthdayDate`, or ``None``."""
    if not (1 <= month <= 12):
        return None
    if not (1 <= day <= _MAX_DAY[month]):
        return None
    if year is not None and not (1 <= year <= 9999):
        return None
    return BirthdayDate(year=year, month=month, day=day)


def parse_birthday(raw: str) -> Optional[BirthdayDate]:
    """Parse a raw birthday cell into a :class:`BirthdayDate`.

    Handles: ``YYYY-MM-DD``, ``--MM-DD`` (year unknown), ``M/D/YYYY`` /
    ``MM/DD/YYYY``, ``M/D`` (year unknown), and ``YYYY/MM/DD``. Returns ``None``
    for empty or unrecognized/garbage input. Never raises.
    """
    if not raw:
        return None
    text = raw.strip()
    if not text:
        return None

    try:
        # ISO year-unknown form: --MM-DD
        if text.startswith("--"):
            body = text[2:]
            parts = body.split("-")
            if len(parts) == 2:
                month, day = int(parts[0]), int(parts[1])
                return _make(None, month, day)
            return None

        # Dash-separated: YYYY-MM-DD (ISO with year)
        if "-" in text and "/" not in text:
            parts = text.split("-")
            if len(parts) == 3 and parts[0] and parts[1] and parts[2]:
                year, month, day = int(parts[0]), int(parts[1]), int(parts[2])
                return _make(year, month, day)
            return None

        # Slash-separated forms.
        if "/" in text:
            parts = text.split("/")
            if len(parts) == 3:
                a, b, c = (p.strip() for p in parts)
                if not (a and b and c):
                    return None
                # YYYY/MM/DD vs M/D/YYYY disambiguated by which end is the year.
                if len(a) == 4:
                    year, month, day = int(a), int(b), int(c)
                else:
                    month, day, year = int(a), int(b), int(c)
                    if year < 100:  # two-digit year -> assume 19xx/20xx
                        year += 2000 if year < 70 else 1900
                return _make(year, month, day)
            if len(parts) == 2:  # M/D, year unknown
                month, day = int(parts[0]), int(parts[1])
                return _make(None, month, day)
            return None
    except (ValueError, TypeError):
        return None

    return None


# --------------------------------------------------------------------------- #
# Reports
# --------------------------------------------------------------------------- #


def missing_birthday_report(contacts: List[Contact]) -> List[Contact]:
    """Return contacts whose birthday is empty or cannot be parsed.

    These are the contacts the user needs to fill in.
    """
    out: List[Contact] = []
    for c in contacts:
        if not c.has_birthday or parse_birthday(c.birthday_raw) is None:
            out.append(c)
    return out


def _next_occurrence(bd: BirthdayDate, from_date: date) -> date:
    """Next on/after ``from_date`` occurrence of ``bd`` (month/day).

    Feb-29 birthdays roll to Feb-28 in non-leap years.
    """
    def _on(year: int) -> date:
        month, day = bd.month, bd.day
        if month == 2 and day == 29 and not calendar.isleap(year):
            day = 28
        return date(year, month, day)

    occ = _on(from_date.year)
    if occ < from_date:
        occ = _on(from_date.year + 1)
    return occ


def upcoming_birthdays(
    contacts: List[Contact],
    from_date: Optional[date] = None,
    days: int = 365,
) -> List[dict]:
    """Next birthday occurrences within ``days`` of ``from_date`` (default today).

    Returns one dict per qualifying contact, sorted by ``days_away`` ascending.
    Each dict has: ``name``, ``date`` (ISO string of the next occurrence),
    ``month``, ``day``, ``turning_age`` (``int`` or ``None`` when the birth year
    is unknown), ``days_away``, ``emails``, ``phones``.
    """
    if from_date is None:
        from_date = date.today()

    rows: List[dict] = []
    for c in contacts:
        bd = parse_birthday(c.birthday_raw)
        if bd is None:
            continue
        occ = _next_occurrence(bd, from_date)
        days_away = (occ - from_date).days
        if days_away > days:
            continue
        turning_age = occ.year - bd.year if bd.year is not None else None
        rows.append(
            {
                "name": c.display_name,
                "date": occ.isoformat(),
                "month": bd.month,
                "day": bd.day,
                "turning_age": turning_age,
                "days_away": days_away,
                "emails": list(c.emails),
                "phones": list(c.phones),
            }
        )

    rows.sort(key=lambda r: r["days_away"])
    return rows


# --------------------------------------------------------------------------- #
# iCalendar (RFC 5545) export
# --------------------------------------------------------------------------- #


def _escape_text(value: str) -> str:
    """Escape a TEXT value per RFC 5545 (backslash, comma, semicolon, newline)."""
    return (
        value.replace("\\", "\\\\")
        .replace(";", "\\;")
        .replace(",", "\\,")
        .replace("\r\n", "\\n")
        .replace("\n", "\\n")
        .replace("\r", "\\n")
    )


def _fold(line: str) -> str:
    """Fold a content line to <=75 octets, continuation lines start with a space."""
    encoded = line.encode("utf-8")
    if len(encoded) <= 75:
        return line
    out = []
    chunk = bytearray()
    count = 0
    limit = 75
    for ch in line:
        ch_bytes = ch.encode("utf-8")
        if count + len(ch_bytes) > limit:
            out.append(chunk.decode("utf-8"))
            chunk = bytearray(b" ")
            count = 1
            limit = 74  # continuation lines: 1 leading space + 74 = 75 octets
        chunk.extend(ch_bytes)
        count += len(ch_bytes)
    out.append(chunk.decode("utf-8"))
    return "\r\n".join(out)


def _uid(contact: Contact, calendar_name: str) -> str:
    """Build a stable UID from name + index + a fixed domain."""
    slug = "".join(
        ch if ch.isalnum() else "-" for ch in contact.display_name.lower()
    ).strip("-") or "contact"
    return f"birthday-{slug}-{contact.index}@contacts-toolkit.local"


def _dtstamp() -> str:
    return datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")


def build_ics(
    contacts: List[Contact],
    calendar_name: str = "Birthdays",
    reminder_days_before: int = 1,
) -> str:
    """Build an RFC-5545 VCALENDAR string of yearly birthday events.

    One all-day, yearly-recurring VEVENT is emitted per contact with a valid
    birthday. Each event carries a stable UID, a ``RRULE:FREQ=YEARLY``, and a
    display ``VALARM`` triggering ``reminder_days_before`` days before. When the
    birth year is known, the event description includes the age; when it is
    unknown the recurrence simply starts in the current year.
    """
    lines: List[str] = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Contacts Toolkit//Birthdays//EN",
        "CALSCALE:GREGORIAN",
        f"X-WR-CALNAME:{_escape_text(calendar_name)}",
    ]

    stamp = _dtstamp()
    current_year = date.today().year

    for c in contacts:
        bd = parse_birthday(c.birthday_raw)
        if bd is None:
            continue

        start_year = bd.year if bd.year is not None else current_year
        month, day = bd.month, bd.day
        # Feb-29 with an unknown/known non-leap start year: clamp to Feb-28.
        if month == 2 and day == 29 and not calendar.isleap(start_year):
            day = 28

        dtstart = f"{start_year:04d}{month:02d}{day:02d}"
        name = c.display_name
        summary = f"\U0001F382 {name}’s Birthday"

        if bd.year is not None:
            description = f"{name} was born in {bd.year}."
        else:
            description = f"{name}’s birthday (year unknown)."

        lines.append("BEGIN:VEVENT")
        lines.append(f"UID:{_uid(c, calendar_name)}")
        lines.append(f"DTSTAMP:{stamp}")
        lines.append(f"DTSTART;VALUE=DATE:{dtstart}")
        lines.append("RRULE:FREQ=YEARLY")
        lines.append(f"SUMMARY:{_escape_text(summary)}")
        lines.append(f"DESCRIPTION:{_escape_text(description)}")
        lines.append("TRANSP:TRANSPARENT")
        lines.append("BEGIN:VALARM")
        lines.append(f"TRIGGER:-P{int(reminder_days_before)}D")
        lines.append("ACTION:DISPLAY")
        lines.append(f"DESCRIPTION:{_escape_text(summary)}")
        lines.append("END:VALARM")
        lines.append("END:VEVENT")

    lines.append("END:VCALENDAR")

    return "\r\n".join(_fold(line) for line in lines) + "\r\n"


def write_ics(path: str, contacts: List[Contact], **kwargs) -> None:
    """Write the ICS calendar to ``path`` (UTF-8, CRLF line endings).

    Extra keyword arguments are forwarded to :func:`build_ics`
    (``calendar_name``, ``reminder_days_before``).
    """
    text = build_ics(contacts, **kwargs)
    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(text)


# --------------------------------------------------------------------------- #
# Stats
# --------------------------------------------------------------------------- #


def birthday_stats(contacts: List[Contact]) -> dict:
    """Summarize birthday coverage across a contact list."""
    total = len(contacts)
    with_valid = 0
    with_year = 0
    without_year = 0
    for c in contacts:
        bd = parse_birthday(c.birthday_raw)
        if bd is None:
            continue
        with_valid += 1
        if bd.year is not None:
            with_year += 1
        else:
            without_year += 1
    return {
        "total": total,
        "with_valid_birthday": with_valid,
        "missing": total - with_valid,
        "with_year": with_year,
        "without_year": without_year,
    }
