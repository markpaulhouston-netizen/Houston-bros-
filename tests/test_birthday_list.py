"""Tests for the Birthday Outreach master-list adapter."""

from __future__ import annotations

import os
import tempfile
import unittest

from contacts_toolkit.birthday_list import (
    _to_iso_birthday,
    load_birthday_list,
    run,
)

SAMPLE = (
    "Name,DOB (Month Day),Birth Year,Type,Notes / Context,Social Handle,"
    "Channel (Text/Call/DM/Email),Reach Out? (Y/N),Last Contacted,Status,"
    "Raw Calendar Title\n"
    "Toast,January 7,,Birthday,Toast,@nouveaunomad,,,,,Toast's birthday\n"
    "Alex Black,September 3,,Birthday,Alex Black Friend,,,,,,Alex Black's birthday\n"
    "Alex Black,September 3,,Birthday,Alex Black,,,,,,Alex Black's birthday\n"
    "Jenna Prescott,November 17,1987,Birthday,Jenna,,,,,,Jenna's birthday\n"
)


class IsoBirthdayTests(unittest.TestCase):
    def test_month_day_no_year(self):
        self.assertEqual(_to_iso_birthday("January 7", ""), "--01-07")

    def test_month_day_with_year(self):
        self.assertEqual(_to_iso_birthday("November 17", "1987"), "1987-11-17")

    def test_unparseable(self):
        self.assertEqual(_to_iso_birthday("", ""), "")
        self.assertEqual(_to_iso_birthday("Smarch 40", ""), "")


class LoadTests(unittest.TestCase):
    def _write(self) -> str:
        fd, path = tempfile.mkstemp(suffix=".csv")
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(SAMPLE)
        return path

    def test_loads_all_rows_with_iso_birthday(self):
        path = self._write()
        try:
            contacts = load_birthday_list(path)
            self.assertEqual(len(contacts), 4)
            self.assertEqual(contacts[0].full_name, "Toast")
            self.assertEqual(contacts[0].birthday_raw, "--01-07")
            self.assertEqual(contacts[3].birthday_raw, "1987-11-17")
        finally:
            os.remove(path)

    def test_run_dedupes_and_writes_outputs(self):
        path = self._write()
        out = tempfile.mkdtemp()
        try:
            stats = run(path, out_dir=out, sender_name="Mark")
            # The two "Alex Black" rows collapse to one.
            self.assertEqual(stats["input_rows"], 4)
            self.assertEqual(stats["after_dedupe"], 3)
            self.assertEqual(stats["duplicates_merged"], 1)
            self.assertEqual(stats["with_valid_birthday"], 3)
            for key in ("ics", "agenda", "clean_csv", "drafts"):
                self.assertTrue(os.path.exists(stats[key]), key)
            ics = open(stats["ics"], encoding="utf-8").read()
            self.assertEqual(ics.count("BEGIN:VEVENT"), 3)
            self.assertIn("RRULE:FREQ=YEARLY", ics)
            # Toast's draft should route to his Instagram handle.
            dms = open(stats["drafts"], encoding="utf-8").read()
            self.assertIn("@nouveaunomad", dms)
            self.assertIn("Happy Birthday, Toast", dms)
        finally:
            os.remove(path)


if __name__ == "__main__":
    unittest.main()
