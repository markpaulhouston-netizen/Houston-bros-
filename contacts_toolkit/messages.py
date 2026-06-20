"""Generate personalized birthday message *drafts* for contacts.

This module is **text-only**: it never sends anything. It turns a list of
:class:`~contacts_toolkit.models.Contact` objects into ready-to-skim birthday
message drafts that Mark Houston can copy-paste (or feed to a sender).

The four tones (``warm``, ``casual``, ``professional``, ``funny``) each have a
small pool of templates. A template is chosen *deterministically* per contact
(via ``contact.index``) so the same contact always yields the same message,
which keeps the output stable and testable.

Typical use::

    from contacts_toolkit.parse import load_contacts
    from contacts_toolkit.messages import generate_drafts, write_drafts_markdown

    contacts = load_contacts("contacts.csv")
    drafts = generate_drafts(contacts, tone="warm")
    write_drafts_markdown("drafts.md", drafts)
"""

from __future__ import annotations

import csv
from typing import Dict, List

from .models import Contact

# --------------------------------------------------------------------------- #
# Constants
# --------------------------------------------------------------------------- #

DEFAULT_SENDER_NAME = "Mark Houston"

#: Friendly stand-in when a contact has no usable name at all.
_FALLBACK_NAME = "there"

#: Tones whose templates always sign off with the sender's name.
_SIGNED_TONES = ("warm", "professional")

# Each template contains a ``{name}`` slot (and, for signed tones, a
# ``{sender}`` slot). Keep them short (1-3 sentences). No placeholder may
# survive into the rendered output.
_TEMPLATES: Dict[str, List[str]] = {
    "warm": [
        "Happy Birthday, {name}! Wishing you a wonderful day filled with "
        "joy and good company. Warmly, {sender}",
        "Happy Birthday, {name}! I hope this year brings you health, "
        "happiness, and everything you've been hoping for. All the best, {sender}",
        "Thinking of you today, {name} - Happy Birthday! May your day be as "
        "special as you are. Warm wishes, {sender}",
    ],
    "casual": [
        "Happy Birthday, {name}! Hope you have an awesome day!",
        "Hey {name}, Happy Birthday! Have a great one!",
        "Happy Birthday, {name}! Hope it's a good one - enjoy!",
    ],
    "professional": [
        "Happy Birthday, {name}. Wishing you a great day and continued "
        "success in the year ahead. Best regards, {sender}",
        "Happy Birthday, {name}. I hope you have a pleasant and restful day. "
        "Kind regards, {sender}",
        "Wishing you a Happy Birthday, {name}, and all the best for the year "
        "to come. Sincerely, {sender}",
    ],
    "funny": [
        "Happy Birthday, {name}! Another trip around the sun - you're not "
        "older, just a limited edition!",
        "Happy Birthday, {name}! Don't count the candles, just enjoy the cake!",
        "Happy Birthday, {name}! You're officially one year cooler today. "
        "Act accordingly!",
    ],
}


# --------------------------------------------------------------------------- #
# Public helpers
# --------------------------------------------------------------------------- #

def first_name_for(contact: Contact) -> str:
    """Return the best first name to greet ``contact`` with.

    Prefers the parsed :attr:`Contact.first`; falls back to the first token of
    :attr:`Contact.display_name`; finally falls back to a friendly stand-in
    (``"there"``) so a greeting like ``"Happy Birthday, there!"`` still reads OK.
    """
    first = (contact.first or "").strip()
    if first:
        return first.split()[0]

    display = (contact.display_name or "").strip()
    if display:
        token = display.split()[0].strip()
        # Avoid greeting with the synthetic "(unnamed #N)" placeholder.
        if token and not token.startswith("("):
            return token

    return _FALLBACK_NAME


def draft_message(
    contact: Contact,
    tone: str = "warm",
    sender_name: str = DEFAULT_SENDER_NAME,
) -> str:
    """Build a short, personalized birthday message for ``contact``.

    ``tone`` is one of ``"warm"``, ``"casual"``, ``"professional"`` or
    ``"funny"`` (unknown tones fall back to ``"warm"``). The template is chosen
    deterministically from the contact's :attr:`~Contact.index`, so calling this
    twice for the same contact and tone always yields the same text.
    """
    templates = _TEMPLATES.get(tone) or _TEMPLATES["warm"]
    name = first_name_for(contact)
    sender = (sender_name or DEFAULT_SENDER_NAME).strip() or DEFAULT_SENDER_NAME

    template = templates[contact.index % len(templates)]
    return template.format(name=name, sender=sender)


def suggest_channel(contact: Contact) -> str:
    """Return the best delivery channel: ``"email"``, ``"sms"`` or ``"none"``."""
    if any(e.strip() for e in contact.emails):
        return "email"
    if any(p.strip() for p in contact.phones):
        return "sms"
    return "none"


def _best_to(contact: Contact, channel: str) -> str:
    """Pick the best destination address for ``channel`` (email or phone)."""
    if channel == "email":
        for e in contact.emails:
            if e.strip():
                return e.strip()
    elif channel == "sms":
        for p in contact.phones:
            if p.strip():
                return p.strip()
    return ""


def generate_drafts(
    contacts: List[Contact],
    tone: str = "warm",
    sender_name: str = DEFAULT_SENDER_NAME,
    only_with_contact_info: bool = True,
) -> List[dict]:
    """Build one draft dict per contact.

    Each dict has keys ``name``, ``first_name``, ``channel``, ``to``, ``tone``
    and ``message``. When ``only_with_contact_info`` is true (the default),
    contacts with no email and no phone (channel ``"none"``) are skipped.
    """
    drafts: List[dict] = []
    for contact in contacts:
        channel = suggest_channel(contact)
        if only_with_contact_info and channel == "none":
            continue
        drafts.append(
            {
                "name": contact.display_name,
                "first_name": first_name_for(contact),
                "channel": channel,
                "to": _best_to(contact, channel),
                "tone": tone,
                "message": draft_message(contact, tone=tone, sender_name=sender_name),
            }
        )
    return drafts


# --------------------------------------------------------------------------- #
# Output writers
# --------------------------------------------------------------------------- #

def write_drafts_csv(path: str, drafts: List[dict]) -> None:
    """Write ``drafts`` to a CSV with columns: name, channel, to, tone, message."""
    fieldnames = ["name", "channel", "to", "tone", "message"]
    with open(path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for d in drafts:
            writer.writerow({k: d.get(k, "") for k in fieldnames})


def write_drafts_markdown(
    path: str,
    drafts: List[dict],
    title: str = "Birthday Message Drafts",
) -> None:
    """Write a readable ``.md`` file grouping drafts by channel.

    Each entry shows the contact name, the destination (``to``), and the
    message rendered as a blockquote - easy for Mark to skim and copy-paste.
    """
    # Group preserving first-seen order within each channel.
    groups: Dict[str, List[dict]] = {"email": [], "sms": [], "none": []}
    for d in drafts:
        groups.setdefault(d.get("channel", "none"), []).append(d)

    headings = {"email": "Email", "sms": "SMS / Text", "none": "No Contact Info"}

    lines: List[str] = [f"# {title}", ""]
    lines.append(f"Total drafts: {len(drafts)}")
    lines.append("")

    for channel in ("email", "sms", "none"):
        items = groups.get(channel) or []
        if not items:
            continue
        lines.append(f"## {headings.get(channel, channel)} ({len(items)})")
        lines.append("")
        for d in items:
            name = d.get("name", "")
            to = d.get("to", "")
            header = f"### {name}" if not to else f"### {name} - {to}"
            lines.append(header)
            lines.append("")
            message = (d.get("message", "") or "").replace("\n", " ")
            lines.append(f"> {message}")
            lines.append("")

    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write("\n".join(lines).rstrip() + "\n")
