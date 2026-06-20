"""Generate a realistic Google Contacts CSV export for testing.

Mimics the messy reality of an iPhone -> Google Contacts merge:
* duplicate people (same person via phone-only + email-only + full records),
* mixed birthday formats (``1985-03-14``, ``--03-14`` year-less, ``3/14/1985``),
* many contacts with NO birthday,
* multiple emails/phones packed into ' ::: ' cells.

Usage:  python sample_data/make_sample.py [count] [out.csv]
"""

from __future__ import annotations

import csv
import random
import sys

HEADER = [
    "Name", "Given Name", "Additional Name", "Family Name",
    "Nickname", "Birthday", "Notes", "Group Membership",
    "E-mail 1 - Type", "E-mail 1 - Value",
    "E-mail 2 - Type", "E-mail 2 - Value",
    "Phone 1 - Type", "Phone 1 - Value",
    "Phone 2 - Type", "Phone 2 - Value",
]

FIRST = ["James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael",
         "Linda", "David", "Elizabeth", "Maria", "Carlos", "Aisha", "Wei",
         "Priya", "Liam", "Noah", "Olivia", "Emma", "Sofia", "Mark", "Sarah"]
LAST = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
        "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez",
        "Wilson", "Anderson", "Thomas", "Lee", "Patel", "Nguyen", "Houston"]
DOMAINS = ["gmail.com", "yahoo.com", "outlook.com", "icloud.com", "hotmail.com"]


def _birthday(rng: random.Random) -> str:
    """Return a birthday in one of several formats, or '' (missing)."""
    if rng.random() < 0.55:          # most contacts have NO birthday
        return ""
    month = rng.randint(1, 12)
    day = rng.randint(1, 28)
    style = rng.random()
    if style < 0.45:
        year = rng.randint(1945, 2005)
        return f"{year:04d}-{month:02d}-{day:02d}"      # ISO with year
    if style < 0.75:
        return f"--{month:02d}-{day:02d}"               # ISO, year unknown
    year = rng.randint(1945, 2005)
    return f"{month}/{day}/{year}"                       # US slash format


def _phone(rng: random.Random) -> str:
    return f"+1 ({rng.randint(200,989)}) {rng.randint(200,989)}-{rng.randint(1000,9999)}"


def build_rows(count: int, seed: int = 42):
    rng = random.Random(seed)
    rows = []
    while len(rows) < count:
        first = rng.choice(FIRST)
        last = rng.choice(LAST)
        name = f"{first} {last}"
        email = f"{first}.{last}@{rng.choice(DOMAINS)}".lower()
        phone = _phone(rng)
        bday = _birthday(rng)

        base = {h: "" for h in HEADER}
        base.update({
            "Name": name, "Given Name": first, "Family Name": last,
            "Birthday": bday, "Group Membership": "My Contacts",
            "E-mail 1 - Type": "Home", "E-mail 1 - Value": email,
            "Phone 1 - Type": "Mobile", "Phone 1 - Value": phone,
        })
        rows.append(base)

        # ~18% of the time, inject a duplicate variant of this person.
        if rng.random() < 0.18 and len(rows) < count:
            variant = {h: "" for h in HEADER}
            kind = rng.random()
            if kind < 0.4:
                # phone-only duplicate, phone re-formatted, no birthday
                variant.update({
                    "Name": name, "Given Name": first, "Family Name": last,
                    "Phone 1 - Type": "iPhone",
                    "Phone 1 - Value": phone.replace("+1 ", "").replace("(", "").replace(") ", "-"),
                })
            elif kind < 0.75:
                # email-only duplicate, sometimes WITH the birthday this time
                variant.update({
                    "Name": name, "Given Name": first, "Family Name": last,
                    "E-mail 1 - Type": "Work", "E-mail 1 - Value": email,
                    "Birthday": bday if rng.random() < 0.5 else "",
                })
            else:
                # near-identical full duplicate w/ extra email packed in
                variant.update({
                    "Name": name, "Given Name": first, "Family Name": last,
                    "Birthday": bday,
                    "E-mail 1 - Type": "Home", "E-mail 1 - Value": email,
                    "E-mail 2 - Type": "Work",
                    "E-mail 2 - Value": f"{first}.{last}@work.com".lower(),
                    "Phone 1 - Type": "Mobile", "Phone 1 - Value": phone,
                })
            rows.append(variant)
    return rows[:count]


def main():
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 300
    out = sys.argv[2] if len(sys.argv) > 2 else "sample_data/contacts_sample.csv"
    rows = build_rows(count)
    with open(out, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=HEADER)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} rows to {out}")


if __name__ == "__main__":
    main()
