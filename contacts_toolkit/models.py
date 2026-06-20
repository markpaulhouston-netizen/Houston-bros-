"""Shared data model for the Birthday Contacts Toolkit.

The :class:`Contact` object is the single representation every module in the
toolkit operates on. It keeps the *original* CSV row intact (``raw``) so that a
cleaned export remains faithfully re-importable into Google Contacts, while also
exposing convenient parsed fields (names, emails, phones, birthday).

Google exports contacts in two header dialects:

* Legacy "Google CSV":  ``Given Name`` / ``Family Name`` / ``E-mail 1 - Value`` /
  ``Phone 1 - Value`` / ``Birthday`` / ``Group Membership`` ...
* Newer "Google CSV":   ``First Name`` / ``Last Name`` / ``E-mail 1 - Value`` /
  ``Phone 1 - Value`` / ``Birthday`` / ``Labels`` ...

The parser (see ``parse.py``) normalizes both into this model.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional


# --------------------------------------------------------------------------- #
# Normalization helpers (used by dedupe + birthday matching)
# --------------------------------------------------------------------------- #

_WS_RE = re.compile(r"\s+")
_NON_DIGIT_RE = re.compile(r"\D+")


def normalize_name(value: Optional[str]) -> str:
    """Lower-cased, whitespace-collapsed name for fuzzy comparison."""
    if not value:
        return ""
    return _WS_RE.sub(" ", value.strip().lower())


def normalize_email(value: Optional[str]) -> str:
    """Lower-cased, trimmed email for exact matching."""
    if not value:
        return ""
    return value.strip().lower()


def normalize_phone(value: Optional[str]) -> str:
    """Digits-only phone, reduced to the national 10-digit core when possible.

    US/iPhone exports mix ``+1 (415) 555-1212``, ``415-555-1212`` and
    ``4155551212``; reducing to the last 10 digits lets those match.
    """
    if not value:
        return ""
    digits = _NON_DIGIT_RE.sub("", value)
    if len(digits) > 10:
        digits = digits[-10:]
    return digits


@dataclass
class Contact:
    """One contact, parsed from a Google CSV row.

    Attributes
    ----------
    index:
        Original 0-based row position in the source file (stable id).
    raw:
        The untouched original CSV row (``header -> value``). Writing this back
        out reproduces the source format exactly.
    first / middle / last:
        Parsed name components (either header dialect).
    full_name:
        Best available display name (``Name`` column, else assembled).
    emails / phones:
        All non-empty email / phone values found across the indexed columns.
    birthday_raw:
        The raw ``Birthday`` cell, exactly as exported (may be ``""``).
    labels:
        Raw group/label membership string (``Labels`` or ``Group Membership``).
    notes:
        Raw ``Notes`` cell.
    """

    index: int
    raw: Dict[str, str] = field(default_factory=dict)
    first: str = ""
    middle: str = ""
    last: str = ""
    full_name: str = ""
    emails: List[str] = field(default_factory=list)
    phones: List[str] = field(default_factory=list)
    birthday_raw: str = ""
    labels: str = ""
    notes: str = ""

    # -- derived / convenience ------------------------------------------- #

    @property
    def display_name(self) -> str:
        """A human label for reports, never empty."""
        if self.full_name.strip():
            return self.full_name.strip()
        assembled = " ".join(p for p in (self.first, self.middle, self.last) if p).strip()
        if assembled:
            return assembled
        if self.emails:
            return self.emails[0]
        if self.phones:
            return self.phones[0]
        return f"(unnamed #{self.index})"

    @property
    def norm_name(self) -> str:
        return normalize_name(self.display_name)

    @property
    def norm_emails(self) -> List[str]:
        return [normalize_email(e) for e in self.emails if e.strip()]

    @property
    def norm_phones(self) -> List[str]:
        out = []
        for p in self.phones:
            n = normalize_phone(p)
            if n:
                out.append(n)
        return out

    @property
    def has_birthday(self) -> bool:
        return bool(self.birthday_raw and self.birthday_raw.strip())
