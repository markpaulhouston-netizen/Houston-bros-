"""Deduplicate a large Google Contacts export (iPhone -> Google merge).

The real workload is ~11,000 contacts where the same person appears several
times: once from an iPhone sync (phone only), once from an email client (email
only), and sometimes as a near-identical full record. Comparing every pair is
O(n^2) and far too slow at that scale, so this module instead:

* Builds dictionaries keyed by *normalized email* and *normalized phone* and
  unions every contact that shares a key. That makes the matching passes O(n).
* Uses a union-find / disjoint-set structure so matching is transitive: if A
  shares an email with B and B shares a phone with C, all three collapse into a
  single cluster automatically.

Matching rules
--------------
Two contacts are treated as the same person when they share **any** normalized
email **or any** normalized phone. As an extra heuristic, contacts with the
exact same non-empty ``norm_name`` are merged *only* when at least one of them
has no email and no phone at all (a "bare name" duplicate left behind by a
partial sync). Two fully-populated people who merely happen to share a name are
never merged.

Public API
----------
* :func:`find_duplicate_groups` -- cluster contacts. Returns **all** clusters,
  including singletons, so callers can iterate uniformly; use
  :func:`groups_with_duplicates` to keep only the 2+ member clusters.
* :func:`merge_group` -- collapse one cluster into a single cleaned
  :class:`Contact` whose ``raw`` row is re-importable into Google Contacts.
* :func:`deduplicate` -- run the whole pipeline and return merged contacts plus
  summary statistics.
"""

from __future__ import annotations

import re
from typing import Dict, List, Tuple

from .models import Contact, normalize_email, normalize_phone

# Column-name patterns matching the parser's dialect detection.
_EMAIL_VALUE_RE = re.compile(r"^e-?mail\s*(\d+)\s*-\s*value$", re.IGNORECASE)
_PHONE_VALUE_RE = re.compile(r"^phone\s*(\d+)\s*-\s*value$", re.IGNORECASE)


# --------------------------------------------------------------------------- #
# Union-Find (disjoint set)
# --------------------------------------------------------------------------- #


class _UnionFind:
    """Minimal disjoint-set with path compression and union by rank."""

    def __init__(self, n: int) -> None:
        self._parent = list(range(n))
        self._rank = [0] * n

    def find(self, x: int) -> int:
        root = x
        while self._parent[root] != root:
            root = self._parent[root]
        # Path compression.
        while self._parent[x] != root:
            self._parent[x], x = root, self._parent[x]
        return root

    def union(self, a: int, b: int) -> None:
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return
        if self._rank[ra] < self._rank[rb]:
            ra, rb = rb, ra
        self._parent[rb] = ra
        if self._rank[ra] == self._rank[rb]:
            self._rank[ra] += 1


# --------------------------------------------------------------------------- #
# Grouping
# --------------------------------------------------------------------------- #


def find_duplicate_groups(contacts: List[Contact]) -> List[List[Contact]]:
    """Cluster contacts that represent the same person.

    Returns **all** clusters, including singletons, so callers can iterate over
    every contact uniformly. Use :func:`groups_with_duplicates` to filter down
    to clusters that actually contain duplicates (2+ members).

    Matching is transitive (via union-find): sharing an email or a phone with
    any current member pulls a contact into the cluster.
    """
    n = len(contacts)
    uf = _UnionFind(n)

    # Pass 1: union by shared normalized email. O(n) thanks to the dict keying.
    email_owner: Dict[str, int] = {}
    for i, c in enumerate(contacts):
        for email in c.norm_emails:
            owner = email_owner.get(email)
            if owner is None:
                email_owner[email] = i
            else:
                uf.union(owner, i)

    # Pass 2: union by shared normalized phone.
    phone_owner: Dict[str, int] = {}
    for i, c in enumerate(contacts):
        for phone in c.norm_phones:
            owner = phone_owner.get(phone)
            if owner is None:
                phone_owner[phone] = i
            else:
                uf.union(owner, i)

    # Pass 3: bare-name duplicates. Group contacts that share an exact non-empty
    # normalized name when at least one member of that name-bucket has no email
    # and no phone at all. This catches partial records ("just a name") without
    # merging two distinct, fully-populated people who happen to share a name.
    name_buckets: Dict[str, List[int]] = {}
    for i, c in enumerate(contacts):
        name = c.norm_name
        if name:
            name_buckets.setdefault(name, []).append(i)

    for name, members in name_buckets.items():
        if len(members) < 2:
            continue
        has_bare = any(
            not contacts[i].norm_emails and not contacts[i].norm_phones
            for i in members
        )
        if not has_bare:
            continue
        # Chain the whole name-bucket together; transitivity does the rest.
        first = members[0]
        for other in members[1:]:
            uf.union(first, other)

    # Collect clusters keyed by their union-find root, preserving input order.
    clusters: Dict[int, List[Contact]] = {}
    for i, c in enumerate(contacts):
        clusters.setdefault(uf.find(i), []).append(c)

    # Order clusters by the smallest member index for deterministic output.
    return [clusters[root] for root in sorted(clusters, key=lambda r: clusters[r][0].index)]


def groups_with_duplicates(groups: List[List[Contact]]) -> List[List[Contact]]:
    """Filter clusters down to those with 2+ members (actual duplicates)."""
    return [g for g in groups if len(g) > 1]


# --------------------------------------------------------------------------- #
# Merging
# --------------------------------------------------------------------------- #


def _populated_score(c: Contact) -> int:
    """Count how many useful fields a contact has populated (for base choice)."""
    score = 0
    score += len(c.norm_emails)
    score += len(c.norm_phones)
    if c.full_name.strip() or c.first or c.last:
        score += 1
    if c.has_birthday:
        score += 1
    if c.notes.strip():
        score += 1
    if c.labels.strip():
        score += 1
    return score


def _dedup_preserve(values: List[str], key=lambda v: v) -> List[str]:
    """Dedup a list preserving first-seen order, comparing via ``key``."""
    seen = set()
    out: List[str] = []
    for v in values:
        if not v or not v.strip():
            continue
        k = key(v)
        if k in seen:
            continue
        seen.add(k)
        out.append(v.strip())
    return out


def _split_label_tokens(labels: str) -> List[str]:
    """Split a labels/group-membership cell into individual tokens."""
    if not labels:
        return []
    parts = re.split(r"\s*:::\s*|\s*,\s*", labels)
    return [p.strip() for p in parts if p.strip()]


def _email_phone_columns(raw: Dict[str, str]) -> Tuple[List[str], List[str]]:
    """Return the existing email/phone *value* columns in the base raw row.

    Sorted by their numeric index so ``E-mail 1 - Value`` comes before
    ``E-mail 2 - Value`` regardless of dict ordering.
    """
    emails: List[Tuple[int, str]] = []
    phones: List[Tuple[int, str]] = []
    for key in raw.keys():
        m = _EMAIL_VALUE_RE.match(key.strip())
        if m:
            emails.append((int(m.group(1)), key))
            continue
        m = _PHONE_VALUE_RE.match(key.strip())
        if m:
            phones.append((int(m.group(1)), key))
    emails.sort()
    phones.sort()
    return [k for _, k in emails], [k for _, k in phones]


def _repack(raw: Dict[str, str], value_cols: List[str], values: List[str], kind: str) -> None:
    """Write ``values`` back into ``raw`` across the indexed value columns.

    Extra values beyond the available columns are appended as new
    ``E-mail N - Value`` / ``Phone N - Value`` keys (matching whichever header
    dialect is already in use). If only a single value column exists, surplus
    values are joined into it with ' ::: ' (which Google accepts on import).
    """
    label = "E-mail" if kind == "email" else "Phone"

    if not value_cols:
        # No indexed columns at all -- create the canonical first one.
        raw[f"{label} 1 - Value"] = " ::: ".join(values)
        return

    if len(value_cols) == 1:
        # Single column dialect: pack everything into it.
        raw[value_cols[0]] = " ::: ".join(values)
        return

    # Multi-column dialect: fill columns 1..k, append new columns for the rest.
    for idx, col in enumerate(value_cols):
        raw[col] = values[idx] if idx < len(values) else ""
    if len(values) > len(value_cols):
        start = len(value_cols) + 1
        for offset, val in enumerate(values[len(value_cols):]):
            raw[f"{label} {start + offset} - Value"] = val


def merge_group(group: List[Contact]) -> Contact:
    """Collapse a cluster of duplicate contacts into one cleaned Contact.

    The most-populated member is used as the base. Emails and phones are unioned
    (order-preserving, case-insensitive dedup for emails). A non-empty birthday,
    the longest notes, and the union of label tokens are carried over. The
    merged contact's ``raw`` row is rebuilt from the base row and then
    overwritten so a cleaned export reflects the merged values and re-imports
    cleanly into Google Contacts.
    """
    if not group:
        raise ValueError("merge_group() requires at least one contact")
    if len(group) == 1:
        return group[0]

    # Choose the richest record as the base (ties -> earliest input index).
    base = max(group, key=lambda c: (_populated_score(c), -c.index))

    # Union emails (case-insensitive) and phones (by normalized digits),
    # starting from the base so its values keep priority/order.
    ordered = [base] + [c for c in group if c is not base]

    emails: List[str] = []
    for c in ordered:
        emails.extend(c.emails)
    emails = _dedup_preserve(emails, key=normalize_email)

    phones: List[str] = []
    for c in ordered:
        phones.extend(c.phones)
    phones = _dedup_preserve(phones, key=normalize_phone)

    # Birthday: first member (base-priority) with a non-empty value.
    birthday = ""
    for c in ordered:
        if c.has_birthday:
            birthday = c.birthday_raw.strip()
            break

    # Notes: keep the longest.
    notes = ""
    for c in group:
        if len(c.notes.strip()) > len(notes):
            notes = c.notes.strip()

    # Labels: union of tokens across all members, order-preserving.
    label_tokens: List[str] = []
    for c in ordered:
        label_tokens.extend(_split_label_tokens(c.labels))
    label_tokens = _dedup_preserve(label_tokens)
    labels = " ::: ".join(label_tokens)

    # Build the merged Contact, copying base name fields.
    merged = Contact(
        index=base.index,
        raw=dict(base.raw),
        first=base.first,
        middle=base.middle,
        last=base.last,
        full_name=base.full_name,
        emails=emails,
        phones=phones,
        birthday_raw=birthday,
        labels=labels,
        notes=notes,
    )

    # Rebuild raw row from the base, then overwrite the merged fields so the
    # cleaned export reflects the union.
    raw = merged.raw
    email_cols, phone_cols = _email_phone_columns(base.raw)
    _repack(raw, email_cols, emails, "email")
    _repack(raw, phone_cols, phones, "phone")

    # Birthday cell.
    bday_key = _find_raw_key(raw, ("birthday",))
    if bday_key is None and birthday:
        bday_key = "Birthday"
    if bday_key is not None:
        raw[bday_key] = birthday

    # Notes cell.
    notes_key = _find_raw_key(raw, ("notes",))
    if notes_key is None and notes:
        notes_key = "Notes"
    if notes_key is not None:
        raw[notes_key] = notes

    # Labels cell (whichever dialect the base used).
    labels_key = _find_raw_key(raw, ("labels", "group membership"))
    if labels_key is None and labels:
        labels_key = "Labels"
    if labels_key is not None:
        raw[labels_key] = labels

    return merged


def _find_raw_key(raw: Dict[str, str], candidates) -> str | None:
    """Case-insensitive lookup of a header key in a raw row."""
    lowered = {k.lower().strip(): k for k in raw.keys()}
    for cand in candidates:
        if cand in lowered:
            return lowered[cand]
    return None


# --------------------------------------------------------------------------- #
# Top-level pipeline
# --------------------------------------------------------------------------- #


def deduplicate(contacts: List[Contact]) -> Tuple[List[Contact], dict]:
    """Deduplicate ``contacts`` and return ``(merged_contacts, stats)``.

    ``merged_contacts`` has one Contact per detected person, in stable input
    order. ``stats`` reports the merge outcome with the keys:

    * ``input_count`` -- contacts in.
    * ``output_count`` -- merged contacts out.
    * ``duplicates_removed`` -- how many records were folded away.
    * ``groups_with_duplicates`` -- number of clusters that had 2+ members.
    * ``largest_group_size`` -- size of the biggest duplicate cluster.
    """
    groups = find_duplicate_groups(contacts)

    merged: List[Contact] = [merge_group(g) for g in groups]

    dup_groups = [g for g in groups if len(g) > 1]
    stats = {
        "input_count": len(contacts),
        "output_count": len(merged),
        "duplicates_removed": len(contacts) - len(merged),
        "groups_with_duplicates": len(dup_groups),
        "largest_group_size": max((len(g) for g in groups), default=0),
    }
    return merged, stats
