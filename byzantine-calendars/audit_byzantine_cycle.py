"""Audit Pascha offsets, Octoechos tone, Matins gospel, and Pentecost ordinals.

Reads readings.csv (2024-2026) and reports mismatches against the planned
two-anchor Byzantine model. Fragment/OCR rows are skip-listed.

Usage:
    python audit_byzantine_cycle.py
"""
from __future__ import annotations

import csv
import re
from collections import Counter, defaultdict
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CSV_PATH = ROOT / "readings.csv"

SKIP_TITLE_RE = re.compile(
    r"^(?:/|\d{1,2}/\d{1,2}\b)|23/30|13th SUNDAY AFTER HOLY CROSS",
    re.I,
)
ORDINAL_RE = re.compile(
    r"(\d+)(?:st|nd|rd|th)\s+SUNDAY\s+AFTER\s+PENTECOST",
    re.I,
)
TONE_CYCLE = 8
MATINS_CYCLE = 11

PASCHA_SUNDAY_OFFSETS = {
    -76: "zacchaeus",
    -70: "publican",
    -63: "prodigal",
    -56: "meatfare",
    -49: "cheesefare",
    -42: "lent1",
    -35: "lent2",
    -28: "lent3",
    -21: "lent4",
    -14: "lent5",
    -7: "palm",
    0: "pascha",
    7: "thomas",
    14: "myrrhbearers",
    21: "paralytic",
    28: "samaritan",
    35: "blind",
    39: "ascension",
    42: "fathers",
    49: "pentecost",
    56: "allsaints",
}


def gregorian_easter(year: int) -> date:
    a = year % 19
    b = year // 100
    c = year % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31
    day = ((h + l - 7 * m + 114) % 31) + 1
    return date(year, month, day)


def parse_mmddyy(value: str) -> date:
    month = int(value[:2])
    day = int(value[2:4])
    year = 2000 + int(value[4:6])
    return date(year, month, day)


def is_skip_row(title: str) -> bool:
    text = (title or "").strip()
    if not text:
        return True
    if SKIP_TITLE_RE.search(text):
        return True
    if "SUNDAY AFTER PENTECOST" in text.upper() and "/" in text and "SUNDAY" in text.split("/")[-1].upper():
        return True
    return False


def predicted_tone(d: date, pascha: date) -> int | None:
    if d == pascha or d == pascha + timedelta(days=49):
        return None
    if d.weekday() != 6:
        return None
    thomas = pascha + timedelta(days=7)
    if d >= thomas:
        weeks = (d - thomas).days // 7
        return (weeks % TONE_CYCLE) + 1
    prev_thomas = gregorian_easter(d.year - 1) + timedelta(days=7)
    weeks = (d - prev_thomas).days // 7
    return (weeks % TONE_CYCLE) + 1


def predicted_matins_from_thomas(d: date, pascha: date) -> int | None:
    if d.weekday() != 6:
        return None
    if d == pascha or d == pascha + timedelta(days=49):
        return None
    thomas = pascha + timedelta(days=7)
    if d >= thomas:
        weeks = (d - thomas).days // 7
        return (weeks % MATINS_CYCLE) + 1
    prev_thomas = gregorian_easter(d.year - 1) + timedelta(days=7)
    weeks = (d - prev_thomas).days // 7
    return (weeks % MATINS_CYCLE) + 1


def predicted_matins_from_allsaints(d: date, pascha: date) -> int | None:
    if d.weekday() != 6:
        return None
    pentecost = pascha + timedelta(days=49)
    allsaints = pentecost + timedelta(days=7)
    zacchaeus_next = gregorian_easter(d.year + 1) - timedelta(days=76)
    if d < allsaints or d > zacchaeus_next:
        return None
    weeks = (d - allsaints).days // 7
    return (weeks % MATINS_CYCLE) + 1


def pentecost_ordinal(d: date, pascha: date) -> int | None:
    if d.weekday() != 6:
        return None
    pentecost = pascha + timedelta(days=49)
    zacchaeus_next = gregorian_easter(d.year + 1) - timedelta(days=76)
    if d.month <= 2:
        zacchaeus_next = pascha - timedelta(days=76)
        pentecost = gregorian_easter(d.year - 1) + timedelta(days=49)
    if d <= pentecost or d > zacchaeus_next:
        return None
    return (d - pentecost).days // 7


def load_rows(path: Path) -> list[dict]:
    rows = []
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for raw in reader:
            key = (raw.get("Date") or "").strip()
            if len(key) != 6 or not key.isdigit():
                continue
            try:
                d = parse_mmddyy(key)
            except ValueError:
                continue
            rows.append(
                {
                    "date": d,
                    "title": (raw.get("Title") or "").strip(),
                    "tone": (raw.get("Tone") or "").strip() or None,
                    "matins": (raw.get("Matins Gospel") or "").strip() or None,
                    "epistle": (raw.get("Epistle") or "").strip() or None,
                    "gospel": (raw.get("Gospel") or "").strip() or None,
                    "fasting": (raw.get("Fasting") or "").strip() or None,
                    "holy": (raw.get("Holy Day of Obligation") or "").strip().lower() == "true",
                    "skip": is_skip_row(raw.get("Title") or ""),
                }
            )
    return rows


def main() -> None:
    rows = load_rows(CSV_PATH)
    sundays = [r for r in rows if r["date"].weekday() == 6]
    print(f"rows={len(rows)} sundays={len(sundays)} skipped={sum(1 for r in rows if r['skip'])}")

    print("\n=== Pascha / Pentecost / Thomas from CSV titles ===")
    for year in (2024, 2025, 2026):
        eas = gregorian_easter(year)
        print(f"{year} computus Pascha={eas} Pentecost={eas + timedelta(days=49)} Thomas={eas + timedelta(days=7)} Zacchaeus={eas - timedelta(days=76)}")

    named = defaultdict(list)
    for row in rows:
        if row["skip"]:
            continue
        title = row["title"].upper()
        eas = gregorian_easter(row["date"].year)
        offset = (row["date"] - eas).days
        if "RESURRECTION OF OUR LORD" in title:
            named["pascha"].append((row["date"], offset, row["title"]))
        if "PENTECOST SUNDAY" in title or title.startswith("PENTECOST"):
            named["pentecost"].append((row["date"], offset, row["title"]))
        if "THOMAS SUNDAY" in title:
            named["thomas"].append((row["date"], offset, row["title"]))
        if "ZACCHAEUS" in title:
            named["zacchaeus"].append((row["date"], offset, row["title"]))
        if "PALM SUNDAY" in title:
            named["palm"].append((row["date"], offset, row["title"]))
        if "PUBLICAN" in title or "PHARISEE" in title:
            named["publican"].append((row["date"], offset, row["title"]))
        if "PRODIGAL" in title:
            named["prodigal"].append((row["date"], offset, row["title"]))
        if "MEATFARE" in title:
            named["meatfare"].append((row["date"], offset, row["title"]))
        if "CHEESEFARE" in title:
            named["cheesefare"].append((row["date"], offset, row["title"]))
        if "ALL SAINTS" in title:
            named["allsaints"].append((row["date"], offset, row["title"]))
        if "ASCENSION" in title:
            named["ascension"].append((row["date"], offset, row["title"]))
    for key, items in named.items():
        print(f"\n{key}:")
        for d, offset, title in items:
            print(f"  {d} offset={offset:+d} {title[:80]}")

    print("\n=== Tone mismatches (Sundays, non-skip) ===")
    tone_ok = tone_bad = tone_missing = 0
    for row in sundays:
        if row["skip"]:
            continue
        eas = gregorian_easter(row["date"].year)
        pred = predicted_tone(row["date"], eas)
        obs = int(row["tone"]) if row["tone"] and row["tone"].isdigit() else None
        if pred is None:
            if obs is None:
                tone_ok += 1
            else:
                tone_bad += 1
                print(f"  expected untoned {row['date']} got {obs} {row['title'][:70]}")
            continue
        if obs is None:
            tone_missing += 1
            print(f"  missing tone {row['date']} expected {pred} {row['title'][:70]}")
            continue
        if obs != pred:
            tone_bad += 1
            print(f"  tone {row['date']} expected {pred} got {obs} {row['title'][:70]}")
        else:
            tone_ok += 1
    print(f"tone ok={tone_ok} bad={tone_bad} missing={tone_missing}")

    print("\n=== Matins: Thomas-based vs All-Saints-based (Sundays with observed matins) ===")
    t_ok = t_bad = a_ok = a_bad = 0
    for row in sundays:
        if row["skip"] or not row["matins"] or not row["matins"].isdigit():
            continue
        eas = gregorian_easter(row["date"].year)
        obs = int(row["matins"])
        t_pred = predicted_matins_from_thomas(row["date"], eas)
        a_pred = predicted_matins_from_allsaints(row["date"], eas)
        if t_pred == obs:
            t_ok += 1
        else:
            t_bad += 1
        if a_pred is None:
            continue
        if a_pred == obs:
            a_ok += 1
        else:
            a_bad += 1
    print(f"thomas-cycle compared={t_ok + t_bad} ok={t_ok} bad={t_bad}")
    print(f"allsaints-cycle compared={a_ok + a_bad} ok={a_ok} bad={a_bad}")

    print("\n=== Pentecost ordinal mismatches ===")
    n_ok = n_bad = n_unparsed = 0
    for row in sundays:
        if row["skip"]:
            continue
        eas = gregorian_easter(row["date"].year)
        pred = pentecost_ordinal(row["date"], eas)
        match = ORDINAL_RE.search(row["title"])
        if pred is None:
            continue
        if not match:
            n_unparsed += 1
            if "AFTER PENTECOST" in row["title"].upper() or "HOLY CROSS" in row["title"].upper():
                print(f"  no ordinal parse {row['date']} pred={pred} {row['title'][:80]}")
            continue
        obs = int(match.group(1))
        if obs != pred:
            n_bad += 1
            print(f"  ordinal {row['date']} expected {pred} got {obs} {row['title'][:80]}")
        else:
            n_ok += 1
    print(f"ordinal ok={n_ok} bad={n_bad} unparsed_in_window={n_unparsed}")

    print("\n=== Sunday dump (date, offset, tone obs/pred, matins, n, title) ===")
    for row in sundays:
        if row["skip"]:
            print(f"SKIP {row['date']} {row['title'][:90]}")
            continue
        eas = gregorian_easter(row["date"].year)
        offset = (row["date"] - eas).days
        print(
            f"{row['date']} off={offset:+4d} tone={row['tone'] or '-':>2}/{predicted_tone(row['date'], eas) or '-'} "
            f"mat={row['matins'] or '-':>2} n={pentecost_ordinal(row['date'], eas) or '-':>2} "
            f"{row['title'][:90]}"
        )

    print("\n=== Holy days of obligation ===")
    for row in rows:
        if row["holy"] and not row["skip"]:
            print(f"  {row['date']} {row['date'].strftime('%A')} {row['title'][:90]}")

    print("\n=== Fasting values by month (weekdays only sample counts) ===")
    fasting = Counter()
    for row in rows:
        if row["fasting"]:
            fasting[row["fasting"]] += 1
    for name, count in fasting.most_common():
        print(f"  {count:4d} {name}")

    print("\n=== Major fixed feasts on Sundays (readings vs weekday of other years) ===")
    by_md = defaultdict(list)
    for row in rows:
        if row["skip"]:
            continue
        md = row["date"].strftime("%m-%d")
        by_md[md].append(row)
    for md in ("01-01", "01-06", "03-25", "08-06", "08-15", "09-08", "09-14", "12-25"):
        print(f"\n{md}:")
        for row in by_md.get(md, []):
            print(
                f"  {row['date']} {row['date'].strftime('%A')} holy={row['holy']} "
                f"ep={row['epistle'] or '-'} g={row['gospel'] or '-'} {row['title'][:70]}"
            )


if __name__ == "__main__":
    main()
