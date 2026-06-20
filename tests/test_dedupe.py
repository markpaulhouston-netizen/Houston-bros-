"""Unit tests for :mod:`contacts_toolkit.dedupe`.

Run with::

    python3 -m unittest tests.test_dedupe -v
"""

from __future__ import annotations

import unittest

from contacts_toolkit.dedupe import (
    deduplicate,
    find_duplicate_groups,
    groups_with_duplicates,
    merge_group,
)
from contacts_toolkit.models import Contact


def make_contact(
    index: int,
    *,
    name: str = "",
    first: str = "",
    last: str = "",
    emails=None,
    phones=None,
    birthday: str = "",
    notes: str = "",
    labels: str = "",
) -> Contact:
    """Build a Contact with a matching raw row (Google multi-column dialect)."""
    emails = emails or []
    phones = phones or []
    raw = {
        "Name": name,
        "Given Name": first,
        "Family Name": last,
        "Birthday": birthday,
        "Notes": notes,
        "Labels": labels,
        "E-mail 1 - Value": emails[0] if len(emails) > 0 else "",
        "E-mail 2 - Value": emails[1] if len(emails) > 1 else "",
        "Phone 1 - Value": phones[0] if len(phones) > 0 else "",
        "Phone 2 - Value": phones[1] if len(phones) > 1 else "",
    }
    return Contact(
        index=index,
        raw=raw,
        first=first,
        last=last,
        full_name=name,
        emails=list(emails),
        phones=list(phones),
        birthday_raw=birthday,
        notes=notes,
        labels=labels,
    )


class TestFindDuplicateGroups(unittest.TestCase):
    def test_shared_email_merges(self):
        a = make_contact(0, name="Jane Doe", emails=["jane@example.com"])
        b = make_contact(1, name="J. Doe", emails=["JANE@example.com"])
        dups = groups_with_duplicates(find_duplicate_groups([a, b]))
        self.assertEqual(len(dups), 1)
        self.assertEqual(len(dups[0]), 2)

    def test_shared_phone_merges(self):
        a = make_contact(0, name="Bob Roe", phones=["+1 (415) 555-1212"])
        b = make_contact(1, name="Bobby Roe", phones=["415-555-1212"])
        dups = groups_with_duplicates(find_duplicate_groups([a, b]))
        self.assertEqual(len(dups), 1)
        self.assertEqual(len(dups[0]), 2)

    def test_transitive_merge_email_then_phone(self):
        # A ~ B by email, B ~ C by phone  =>  one group of three.
        a = make_contact(0, name="A", emails=["x@example.com"])
        b = make_contact(1, name="B", emails=["x@example.com"], phones=["5551234567"])
        c = make_contact(2, name="C", phones=["555-123-4567"])
        groups = find_duplicate_groups([a, b, c])
        dups = groups_with_duplicates(groups)
        self.assertEqual(len(dups), 1)
        self.assertEqual(len(dups[0]), 3)

    def test_same_name_different_info_does_not_merge(self):
        # Two distinct, fully-populated people sharing a name must stay apart.
        a = make_contact(0, name="John Smith", emails=["john1@example.com"],
                         phones=["1112223333"])
        b = make_contact(1, name="John Smith", emails=["john2@example.com"],
                         phones=["4445556666"])
        groups = find_duplicate_groups([a, b])
        self.assertEqual(len(groups_with_duplicates(groups)), 0)
        self.assertEqual(len(groups), 2)

    def test_bare_name_dup_merges(self):
        # A name-only record folds into a populated one of the same name.
        a = make_contact(0, name="Kim Lee", emails=["kim@example.com"])
        b = make_contact(1, name="Kim Lee")  # no email/phone
        dups = groups_with_duplicates(find_duplicate_groups([a, b]))
        self.assertEqual(len(dups), 1)
        self.assertEqual(len(dups[0]), 2)

    def test_singletons_returned(self):
        a = make_contact(0, name="Solo One", emails=["one@example.com"])
        b = make_contact(1, name="Solo Two", emails=["two@example.com"])
        groups = find_duplicate_groups([a, b])
        self.assertEqual(len(groups), 2)
        self.assertTrue(all(len(g) == 1 for g in groups))


class TestMergeGroup(unittest.TestCase):
    def test_emails_unioned_without_dupes(self):
        a = make_contact(0, name="Jane Doe", emails=["jane@example.com"])
        b = make_contact(1, name="Jane Doe",
                         emails=["JANE@example.com", "jane.doe@work.com"])
        merged = merge_group([a, b])
        norm = merged.norm_emails
        self.assertEqual(len(norm), 2)
        self.assertIn("jane@example.com", norm)
        self.assertIn("jane.doe@work.com", norm)

    def test_phones_unioned_without_dupes(self):
        a = make_contact(0, phones=["+1 (415) 555-1212"], emails=["p@x.com"])
        b = make_contact(1, phones=["415-555-1212", "2025550000"], emails=["p@x.com"])
        merged = merge_group([a, b])
        self.assertEqual(len(merged.norm_phones), 2)

    def test_keeps_birthday_from_one_member(self):
        a = make_contact(0, name="Jane Doe", emails=["jane@example.com"])
        b = make_contact(1, name="Jane Doe", emails=["jane@example.com"],
                         birthday="1985-03-14")
        merged = merge_group([a, b])
        self.assertEqual(merged.birthday_raw, "1985-03-14")
        self.assertTrue(merged.has_birthday)
        self.assertEqual(merged.raw.get("Birthday"), "1985-03-14")

    def test_keeps_longest_notes(self):
        a = make_contact(0, emails=["n@x.com"], notes="short")
        b = make_contact(1, emails=["n@x.com"], notes="a much longer note here")
        merged = merge_group([a, b])
        self.assertEqual(merged.notes, "a much longer note here")

    def test_labels_unioned(self):
        a = make_contact(0, emails=["l@x.com"], labels="Friends")
        b = make_contact(1, emails=["l@x.com"], labels="Family ::: Work")
        merged = merge_group([a, b])
        tokens = set(merged.labels.split(" ::: "))
        self.assertEqual(tokens, {"Friends", "Family", "Work"})

    def test_raw_reflects_merged_emails(self):
        # Extra emails must land in indexed columns so export re-imports cleanly.
        a = make_contact(0, emails=["a1@x.com"])
        b = make_contact(1, emails=["a1@x.com", "a2@x.com", "a3@x.com"])
        merged = merge_group([a, b])
        self.assertEqual(merged.raw.get("E-mail 1 - Value"), "a1@x.com")
        self.assertEqual(merged.raw.get("E-mail 2 - Value"), "a2@x.com")
        self.assertEqual(merged.raw.get("E-mail 3 - Value"), "a3@x.com")


class TestDeduplicate(unittest.TestCase):
    def test_stats_shape_and_counts(self):
        a = make_contact(0, name="A", emails=["x@example.com"])
        b = make_contact(1, name="B", emails=["x@example.com"], phones=["5551234567"])
        c = make_contact(2, name="C", phones=["555-123-4567"])
        d = make_contact(3, name="Solo", emails=["solo@example.com"])
        merged, stats = deduplicate([a, b, c, d])

        self.assertEqual(stats["input_count"], 4)
        self.assertEqual(stats["output_count"], 2)
        self.assertEqual(stats["duplicates_removed"], 2)
        self.assertEqual(stats["groups_with_duplicates"], 1)
        self.assertEqual(stats["largest_group_size"], 3)
        self.assertEqual(len(merged), 2)

    def test_no_duplicates(self):
        a = make_contact(0, name="A", emails=["a@example.com"])
        b = make_contact(1, name="B", emails=["b@example.com"])
        merged, stats = deduplicate([a, b])
        self.assertEqual(stats["duplicates_removed"], 0)
        self.assertEqual(stats["output_count"], 2)
        self.assertEqual(stats["largest_group_size"], 1)


if __name__ == "__main__":
    unittest.main()
