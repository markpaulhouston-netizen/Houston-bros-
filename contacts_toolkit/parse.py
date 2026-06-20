"""Load and save Google Contacts CSV exports into :class:`Contact` objects.

Handles both Google CSV header dialects (legacy ``Given Name`` and newer
``First Name``) and an arbitrary number of indexed ``E-mail N - Value`` /
``Phone N - Value`` columns. Writing preserves the original column order so a
cleaned file re-imports cleanly into Google Contacts.
"""

from __future__ import annotations

import csv
import io
import re
from typing import Dict, List, Optional

from .models import Contact

# Header candidates for each logical field (first match wins, case-insensitive).
_FIRST = ("first name", "given name")
_MIDDLE = ("middle name", "additional name")
_LAST = ("last name", "family name")
_FULL = ("name",)
_BIRTHDAY = ("birthday",)
_NOTES = ("notes",)
_LABELS = ("labels", "group membership")

_EMAIL_VALUE_RE = re.compile(r"^e-?mail\s*\d+\s*-\s*value$", re.IGNORECASE)
_PHONE_VALUE_RE = re.compile(r"^phone\s*\d+\s*-\s*value$", re.IGNORECASE)


def _find_header(fieldnames: List[str], candidates) -> Optional[str]:
    lowered = {f.lower().strip(): f for f in fieldnames}
    for cand in candidates:
        if cand in lowered:
            return lowered[cand]
    return None


def _split_multi(value: str) -> List[str]:
    """Google packs multiple values in one cell with ' ::: '. Split + clean."""
    if not value:
        return []
    parts = re.split(r"\s*:::\s*|\s*;\s*", value)
    return [p.strip() for p in parts if p.strip()]


def load_contacts_from_text(text: str) -> List[Contact]:
    """Parse CSV text into Contacts. Tolerates a UTF-8 BOM."""
    if text and text[0] == "﻿":
        text = text[1:]
    reader = csv.DictReader(io.StringIO(text))
    fieldnames = reader.fieldnames or []

    h_first = _find_header(fieldnames, _FIRST)
    h_middle = _find_header(fieldnames, _MIDDLE)
    h_last = _find_header(fieldnames, _LAST)
    h_full = _find_header(fieldnames, _FULL)
    h_bday = _find_header(fieldnames, _BIRTHDAY)
    h_notes = _find_header(fieldnames, _NOTES)
    h_labels = _find_header(fieldnames, _LABELS)
    email_cols = [f for f in fieldnames if _EMAIL_VALUE_RE.match(f.strip())]
    phone_cols = [f for f in fieldnames if _PHONE_VALUE_RE.match(f.strip())]

    contacts: List[Contact] = []
    for i, row in enumerate(reader):
        emails: List[str] = []
        for col in email_cols:
            emails.extend(_split_multi(row.get(col, "")))
        phones: List[str] = []
        for col in phone_cols:
            phones.extend(_split_multi(row.get(col, "")))

        contacts.append(
            Contact(
                index=i,
                raw=dict(row),
                first=(row.get(h_first, "") or "").strip() if h_first else "",
                middle=(row.get(h_middle, "") or "").strip() if h_middle else "",
                last=(row.get(h_last, "") or "").strip() if h_last else "",
                full_name=(row.get(h_full, "") or "").strip() if h_full else "",
                emails=emails,
                phones=phones,
                birthday_raw=(row.get(h_bday, "") or "").strip() if h_bday else "",
                labels=(row.get(h_labels, "") or "").strip() if h_labels else "",
                notes=(row.get(h_notes, "") or "").strip() if h_notes else "",
            )
        )
    return contacts


def load_contacts(path: str) -> List[Contact]:
    """Load Contacts from a Google CSV file on disk."""
    with open(path, "r", encoding="utf-8-sig", newline="") as fh:
        return load_contacts_from_text(fh.read())


def header_for(contacts: List[Contact]) -> List[str]:
    """Recover the original column order from the parsed rows."""
    for c in contacts:
        if c.raw:
            return list(c.raw.keys())
    return []


def write_contacts(path: str, contacts: List[Contact], fieldnames: Optional[List[str]] = None) -> None:
    """Write Contacts back to a Google-importable CSV using their ``raw`` rows.

    Any field added/changed in ``raw`` (e.g. a filled-in ``Birthday``) is
    preserved; new columns not present in the recovered header are appended.
    """
    if fieldnames is None:
        fieldnames = header_for(contacts)
    # Make sure every key present in any raw row is in the header.
    extra: List[str] = []
    seen = set(fieldnames)
    for c in contacts:
        for k in c.raw.keys():
            if k not in seen:
                seen.add(k)
                extra.append(k)
    out_fields = list(fieldnames) + extra

    with open(path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=out_fields, extrasaction="ignore")
        writer.writeheader()
        for c in contacts:
            writer.writerow({k: c.raw.get(k, "") for k in out_fields})


def set_birthday(contact: Contact, value: str) -> None:
    """Set/overwrite a contact's Birthday in both the parsed field and raw row."""
    contact.birthday_raw = value
    bday_key = _find_header(list(contact.raw.keys()), _BIRTHDAY)
    if bday_key is None:
        bday_key = "Birthday"
    contact.raw[bday_key] = value
