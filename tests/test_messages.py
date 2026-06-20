"""Unit tests for :mod:`contacts_toolkit.messages`.

Run with::

    python3 -m unittest tests.test_messages -v
"""

from __future__ import annotations

import unittest

from contacts_toolkit.messages import (
    draft_message,
    first_name_for,
    generate_drafts,
    suggest_channel,
)
from contacts_toolkit.models import Contact

_TONES = ("warm", "casual", "professional", "funny")


def _contact(index=0, first="", full_name="", emails=None, phones=None) -> Contact:
    return Contact(
        index=index,
        first=first,
        full_name=full_name,
        emails=list(emails or []),
        phones=list(phones or []),
    )


class FirstNameForTests(unittest.TestCase):
    def test_uses_parsed_first_name(self):
        c = _contact(first="Sarah", full_name="Sarah Patel")
        self.assertEqual(first_name_for(c), "Sarah")

    def test_falls_back_to_display_name_token(self):
        c = _contact(first="", full_name="Jordan Lee")
        self.assertEqual(first_name_for(c), "Jordan")

    def test_fallback_for_empty_name(self):
        c = _contact(first="", full_name="")  # display_name -> "(unnamed #N)"
        name = first_name_for(c)
        self.assertEqual(name, "there")
        self.assertFalse(name.startswith("("))

    def test_strips_whitespace(self):
        c = _contact(first="  Mark  ")
        self.assertEqual(first_name_for(c), "Mark")


class DraftMessageTests(unittest.TestCase):
    def test_greeting_includes_first_name(self):
        c = _contact(first="Sarah")
        for tone in _TONES:
            msg = draft_message(c, tone=tone)
            self.assertIn("Sarah", msg, f"tone={tone} missing greeting name")

    def test_empty_name_falls_back_gracefully(self):
        c = _contact(first="", full_name="")
        for tone in _TONES:
            msg = draft_message(c, tone=tone)
            self.assertTrue(msg.strip())
            self.assertNotIn("{", msg, f"tone={tone} left a placeholder")
            self.assertNotIn("}", msg)
            self.assertIn("there", msg)

    def test_all_tones_nonempty_and_distinctish(self):
        c = _contact(first="Alex")
        outputs = {tone: draft_message(c, tone=tone) for tone in _TONES}
        for tone, msg in outputs.items():
            self.assertTrue(msg.strip(), f"tone={tone} empty")
        # At least 3 of the 4 tones should produce distinct text.
        self.assertGreaterEqual(len(set(outputs.values())), 3)

    def test_no_placeholder_remains(self):
        c = _contact(first="Pat")
        for tone in _TONES:
            msg = draft_message(c, tone=tone, sender_name="Mark Houston")
            self.assertNotIn("{name}", msg)
            self.assertNotIn("{sender}", msg)

    def test_signed_tones_contain_sender_name(self):
        c = _contact(first="Dana")
        for tone in ("warm", "professional"):
            msg = draft_message(c, tone=tone, sender_name="Mark Houston")
            self.assertIn("Mark Houston", msg, f"tone={tone} missing sender")

    def test_deterministic(self):
        c = _contact(index=7, first="Sam")
        for tone in _TONES:
            self.assertEqual(
                draft_message(c, tone=tone),
                draft_message(c, tone=tone),
                f"tone={tone} not deterministic",
            )

    def test_index_selects_template(self):
        # Two contacts with different indices may differ; same index matches.
        a = _contact(index=0, first="Sam")
        b = _contact(index=0, first="Sam")
        self.assertEqual(draft_message(a), draft_message(b))

    def test_unknown_tone_falls_back(self):
        c = _contact(first="Sam")
        msg = draft_message(c, tone="nonsense")
        self.assertTrue(msg.strip())
        self.assertIn("Sam", msg)


class SuggestChannelTests(unittest.TestCase):
    def test_email_wins(self):
        c = _contact(emails=["a@b.com"], phones=["+1 555 111 2222"])
        self.assertEqual(suggest_channel(c), "email")

    def test_sms_when_only_phone(self):
        c = _contact(phones=["+1 555 111 2222"])
        self.assertEqual(suggest_channel(c), "sms")

    def test_none_when_no_contact_info(self):
        c = _contact()
        self.assertEqual(suggest_channel(c), "none")

    def test_blank_values_treated_as_missing(self):
        c = _contact(emails=["   "], phones=[""])
        self.assertEqual(suggest_channel(c), "none")


class GenerateDraftsTests(unittest.TestCase):
    def _mixed(self):
        return [
            _contact(index=0, first="Sarah", emails=["sarah@x.com"]),
            _contact(index=1, first="Jordan", phones=["+1 555 222 3333"]),
            _contact(index=2, first="NoInfo"),  # no email, no phone
        ]

    def test_excludes_no_contact_info_by_default(self):
        drafts = generate_drafts(self._mixed())
        self.assertEqual(len(drafts), 2)
        self.assertTrue(all(d["channel"] != "none" for d in drafts))

    def test_includes_all_when_flag_false(self):
        drafts = generate_drafts(self._mixed(), only_with_contact_info=False)
        self.assertEqual(len(drafts), 3)

    def test_draft_dict_shape(self):
        drafts = generate_drafts(self._mixed())
        expected_keys = {"name", "first_name", "channel", "to", "tone", "message"}
        for d in drafts:
            self.assertEqual(set(d.keys()), expected_keys)

    def test_to_matches_channel(self):
        drafts = generate_drafts(self._mixed())
        email_draft = next(d for d in drafts if d["channel"] == "email")
        sms_draft = next(d for d in drafts if d["channel"] == "sms")
        self.assertEqual(email_draft["to"], "sarah@x.com")
        self.assertEqual(sms_draft["to"], "+1 555 222 3333")

    def test_tone_is_recorded(self):
        drafts = generate_drafts(self._mixed(), tone="funny")
        self.assertTrue(all(d["tone"] == "funny" for d in drafts))

    def test_deterministic_across_calls(self):
        contacts = self._mixed()
        first = generate_drafts(contacts)
        second = generate_drafts(contacts)
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
