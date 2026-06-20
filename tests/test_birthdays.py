"""Unit tests for :mod:`contacts_toolkit.birthdays`.

Run with::

    python3 -m unittest tests.test_birthdays -v
"""

from __future__ import annotations

import unittest
from datetime import date

from contacts_toolkit.models import Contact
from contacts_toolkit.birthdays import (
    BirthdayDate,
    parse_birthday,
    missing_birthday_report,
    upcoming_birthdays,
    build_ics,
    birthday_stats,
)


def _contact(index, name, birthday="", emails=None, phones=None):
    return Contact(
        index=index,
        full_name=name,
        birthday_raw=birthday,
        emails=list(emails or []),
        phones=list(phones or []),
    )


class TestParseBirthday(unittest.TestCase):
    def test_iso_with_year(self):
        self.assertEqual(parse_birthday("1985-03-14"), BirthdayDate(1985, 3, 14))

    def test_iso_year_unknown(self):
        bd = parse_birthday("--03-14")
        self.assertIsNotNone(bd)
        self.assertIsNone(bd.year)
        self.assertEqual((bd.month, bd.day), (3, 14))

    def test_us_mdy(self):
        self.assertEqual(parse_birthday("3/14/1985"), BirthdayDate(1985, 3, 14))

    def test_us_mmddyyyy(self):
        self.assertEqual(parse_birthday("03/14/1985"), BirthdayDate(1985, 3, 14))

    def test_md_year_unknown(self):
        bd = parse_birthday("3/14")
        self.assertEqual(bd, BirthdayDate(None, 3, 14))

    def test_yyyymmdd_slash(self):
        self.assertEqual(parse_birthday("1985/03/14"), BirthdayDate(1985, 3, 14))

    def test_empty_and_garbage(self):
        for bad in ["", "   ", "not a date", "13/40/2000", "2000-13-01", "abc/def"]:
            self.assertIsNone(parse_birthday(bad), bad)

    def test_leap_day_parses(self):
        self.assertEqual(parse_birthday("--02-29"), BirthdayDate(None, 2, 29))


class TestMissingReport(unittest.TestCase):
    def test_counts_empties_and_garbage(self):
        contacts = [
            _contact(0, "Has BD", "1990-05-05"),
            _contact(1, "Empty", ""),
            _contact(2, "Whitespace", "   "),
            _contact(3, "Garbage", "xyz"),
            _contact(4, "Also valid", "7/4/1976"),
        ]
        missing = missing_birthday_report(contacts)
        names = {c.display_name for c in missing}
        self.assertEqual(names, {"Empty", "Whitespace", "Garbage"})


class TestUpcoming(unittest.TestCase):
    def test_sorted_and_next_occurrence(self):
        contacts = [
            _contact(0, "Far", "12/31/1980"),
            _contact(1, "Soon", "1/5/1990"),
            _contact(2, "Mid", "6/15/2000"),
        ]
        frm = date(2026, 1, 1)
        rows = upcoming_birthdays(contacts, from_date=frm, days=365)
        # Sorted ascending by days_away.
        days = [r["days_away"] for r in rows]
        self.assertEqual(days, sorted(days))
        # "Soon" is Jan 5 -> 4 days away from Jan 1.
        soon = next(r for r in rows if r["name"] == "Soon")
        self.assertEqual(soon["date"], "2026-01-05")
        self.assertEqual(soon["days_away"], 4)
        self.assertEqual(soon["turning_age"], 36)

    def test_year_unknown_age_none(self):
        contacts = [_contact(0, "NoYear", "--08-20")]
        rows = upcoming_birthdays(contacts, from_date=date(2026, 1, 1))
        self.assertEqual(len(rows), 1)
        self.assertIsNone(rows[0]["turning_age"])

    def test_days_window_excludes(self):
        contacts = [_contact(0, "WayOut", "6/15/1990")]
        rows = upcoming_birthdays(contacts, from_date=date(2026, 1, 1), days=30)
        self.assertEqual(rows, [])

    def test_leap_day_non_leap_year_no_crash(self):
        contacts = [_contact(0, "LeapBaby", "2/29/1992")]
        # 2026 is not a leap year; should roll to Feb 28 without raising.
        rows = upcoming_birthdays(contacts, from_date=date(2026, 1, 1), days=365)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["date"], "2026-02-28")


class TestBuildIcs(unittest.TestCase):
    def test_structure_and_event_count(self):
        contacts = [
            _contact(0, "Alice", "1985-03-14"),
            _contact(1, "Bob", "--07-04"),
            _contact(2, "NoBirthday", ""),
            _contact(3, "Garbage", "nope"),
        ]
        ics = build_ics(contacts)
        self.assertIn("BEGIN:VCALENDAR", ics)
        self.assertIn("END:VCALENDAR", ics)
        self.assertIn("RRULE:FREQ=YEARLY", ics)
        self.assertIn("BEGIN:VALARM", ics)
        # One VEVENT per valid birthday (Alice + Bob = 2).
        self.assertEqual(ics.count("BEGIN:VEVENT"), 2)
        self.assertEqual(ics.count("END:VEVENT"), 2)
        # CRLF line endings.
        self.assertIn("\r\n", ics)

    def test_leap_day_event_no_crash(self):
        contacts = [_contact(0, "Leap", "2/29/1991")]  # 1991 not leap
        ics = build_ics(contacts)
        self.assertIn("DTSTART;VALUE=DATE:19910228", ics)


class TestStats(unittest.TestCase):
    def test_stats(self):
        contacts = [
            _contact(0, "A", "1985-03-14"),
            _contact(1, "B", "--07-04"),
            _contact(2, "C", ""),
            _contact(3, "D", "garbage"),
        ]
        stats = birthday_stats(contacts)
        self.assertEqual(stats["total"], 4)
        self.assertEqual(stats["with_valid_birthday"], 2)
        self.assertEqual(stats["missing"], 2)
        self.assertEqual(stats["with_year"], 1)
        self.assertEqual(stats["without_year"], 1)


if __name__ == "__main__":
    unittest.main()
