"""Distill a compact Byzantine lectionary from readings.csv.

Assigns each day a temporal slot via the two-anchor calendar and writes
client/src/data/byzantineLectionary.json with reference-only temporal +
sanctoral tables.

Usage:
    python distill_byzantine_lectionary.py
"""
from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

from byzantine_calendar import temporal_slot

ROOT = Path(__file__).resolve().parent
DEFAULT_INPUT = ROOT / "readings.csv"
DEFAULT_OUTPUT = ROOT.parent / "client" / "src" / "data" / "byzantineLectionary.json"

SKIP_TITLE_RE = re.compile(
    r"^(?:/|\d{1,2}/\d{1,2}\b)|23/30|13th SUNDAY AFTER HOLY CROSS",
    re.I,
)
TEMPORAL_TITLE_RE = re.compile(
    r"SUNDAY|PENTECOST|PASCHA|RESURRECTION|THOMAS|TRIOdION|PUBLICAN|PRODIGAL|"
    r"MEAT-?FARE|CHEESE-?FARE|PALM SUNDAY|BRIGHT |GREAT AND HOLY|"
    r"MYRRH-BEARING|PARALYTIC|SAMARITAN|BORN BLIND|ASCENSION|"
    r"ZACCHAEUS|ORTHODOXY|GREGORY PALAMAS|VENERATION OF THE HOLY CROSS|"
    r"JOHN OF THE LADDER|MARY OF EGYPT|ALL SAINTS|HOLY CROSS|"
    r"EXALTATION|NATIVITY OF OUR LORD|THEOPHANY|INDICTION|"
    r"HOLY ANCESTORS|HOLY FATHERS|ECUMENICAL",
    re.I,
)
GREAT_FEASTS = {
    "01-01",
    "01-06",
    "02-02",
    "03-25",
    "06-29",
    "08-06",
    "08-15",
    "09-08",
    "09-14",
    "11-21",
    "12-25",
    "12-26",
}


def parse_mmddyy(value: str) -> date | None:
    key = (value or "").strip()
    if len(key) != 6 or not key.isdigit():
        return None
    try:
        return date(2000 + int(key[4:6]), int(key[:2]), int(key[2:4]))
    except ValueError:
        return None


def is_skip_row(title: str) -> bool:
    text = (title or "").strip()
    if not text:
        return True
    return bool(SKIP_TITLE_RE.search(text))


def normalize_ref(value: str | None) -> str | None:
    if not value:
        return None
    text = re.sub(r"\s+", " ", value).strip(" .;")
    return text or None


def readings_from_row(row: dict) -> list[dict]:
    out = []
    epistle = normalize_ref(row.get("epistle"))
    gospel = normalize_ref(row.get("gospel"))
    if epistle:
        out.append({"type": "epistle", "reference": epistle, "book": ""})
    if gospel:
        out.append({"type": "gospel", "reference": gospel, "book": ""})
    return out


def readings_key(readings: list[dict]) -> tuple:
    return tuple((item["type"], item["reference"]) for item in readings)


def clean_title(title: str) -> str:
    text = re.sub(r"\s+", " ", title or "").strip(" .;")
    text = re.sub(r"^Common Abst\.?\s*", "", text, flags=re.I)
    text = re.sub(r"\s*\(Rusalii\).*$", "", text, flags=re.I)
    text = re.sub(r"\s*Liturgy of St\.?\s*(John|Basil).*$", "", text, flags=re.I)
    text = re.sub(r"\s*Blessing of.*$", "", text, flags=re.I)
    text = re.sub(r"\s*Kneeling prayers.*$", "", text, flags=re.I)
    text = re.sub(r"\s*Procession with.*$", "", text, flags=re.I)
    text = re.sub(r"\s*Great Lent begins.*$", "", text, flags=re.I)
    text = re.sub(r"\s*Beginning of Great Lent.*$", "", text, flags=re.I)
    text = re.sub(r"\s*from meat and dairy.*$", "", text, flags=re.I)
    text = re.sub(r"\s*Strict abstinence.*$", "", text, flags=re.I)
    text = re.sub(r", Of the Sunday$", "", text, flags=re.I)
    text = re.sub(r"\s*, Res$", "", text, flags=re.I)
    return text.strip(" .;-")


def load_rows(path: Path) -> list[dict]:
    rows = []
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for raw in reader:
            d = parse_mmddyy(raw.get("Date") or "")
            if not d:
                continue
            title = (raw.get("Title") or "").strip()
            rows.append(
                {
                    "date": d,
                    "title": title,
                    "clean": clean_title(title),
                    "epistle": (raw.get("Epistle") or "").strip() or None,
                    "gospel": (raw.get("Gospel") or "").strip() or None,
                    "fasting": (raw.get("Fasting") or "").strip() or None,
                    "holy": (raw.get("Holy Day of Obligation") or "").strip().lower() == "true",
                    "notes": (raw.get("Notes") or "").strip() or None,
                    "skip": is_skip_row(title),
                }
            )
    return rows


def pick_majority(counter: Counter, default=None):
    if not counter:
        return default
    return counter.most_common(1)[0][0]


def distill(rows: list[dict]) -> tuple[dict, list[str]]:
    temporal_titles = defaultdict(Counter)
    temporal_readings = defaultdict(Counter)
    sanctoral_titles = defaultdict(Counter)
    sanctoral_readings = defaultdict(Counter)
    sanctoral_fasting = defaultdict(Counter)
    sanctoral_holy = defaultdict(int)
    mismatches: list[str] = []

    for row in rows:
        if row["skip"]:
            continue
        d = row["date"]
        meta = temporal_slot(d)
        slot_key = meta["key"]
        readings = readings_from_row(row)
        sunday = d.weekday() == 6
        md = d.strftime("%m-%d")
        title = row["clean"]

        keep_temporal = sunday or meta["season"] in {
            "pascha",
            "holyweek",
            "lent",
            "triodion",
            "pentecost",
        }
        if keep_temporal and readings:
            temporal_titles[slot_key][title or meta["title"]] += 1
            temporal_readings[slot_key][readings_key(readings)] += 1
        elif sunday:
            temporal_titles[slot_key][title or meta["title"]] += 1

        saint_title = title
        if sunday and TEMPORAL_TITLE_RE.search(title) and md not in GREAT_FEASTS:
            continue
        if not sunday:
            if meta["season"] in {"holyweek", "pascha", "lent"} and TEMPORAL_TITLE_RE.search(title):
                saint_title = re.sub(
                    r"^(Bright (Monday|Tuesday|Wednesday|Thursday|Friday|Saturday)|"
                    r"Great and Holy (Monday|Tuesday|Wednesday|Thursday|Friday|Saturday)|"
                    r"Palm Sunday)[:.\s-]*",
                    "",
                    title,
                    flags=re.I,
                ).strip(" .;")
            if not saint_title:
                continue
            sanctoral_titles[md][saint_title] += 1
            if readings and meta["season"] in {"afterPentecost", "unknown", "triodion"}:
                sanctoral_readings[md][readings_key(readings)] += 1
            elif readings and md in GREAT_FEASTS:
                sanctoral_readings[md][readings_key(readings)] += 1
            if row["fasting"]:
                sanctoral_fasting[md][row["fasting"]] += 1
            if row["holy"] and (md in GREAT_FEASTS or not sunday):
                sanctoral_holy[md] += 1
        elif md in GREAT_FEASTS:
            sanctoral_titles[md][title] += 1
            if readings:
                sanctoral_readings[md][readings_key(readings)] += 1
            if row["holy"]:
                sanctoral_holy[md] += 1

        predicted = (meta["title"] or "").lower()
        observed = (title or "").lower()
        if sunday and predicted and observed:
            predicted_tokens = set(re.findall(r"[a-z0-9]+", predicted))
            observed_tokens = set(re.findall(r"[a-z0-9]+", observed))
            if predicted_tokens and observed_tokens and predicted_tokens.isdisjoint(observed_tokens):
                if md not in GREAT_FEASTS:
                    mismatches.append(f"{d.isoformat()} slot={slot_key} pred={meta['title']!r} obs={title!r}")

    temporal = {}
    for key, titles in temporal_titles.items():
        title = pick_majority(titles, key)
        refs = pick_majority(temporal_readings.get(key, Counter()), ())
        readings = [{"type": t, "reference": r, "book": ""} for t, r in refs]
        temporal[key] = {"title": title, "readings": readings}

    sanctoral = {}
    for md, titles in sanctoral_titles.items():
        title = pick_majority(titles, md)
        refs = pick_majority(sanctoral_readings.get(md, Counter()), ())
        readings = [{"type": t, "reference": r, "book": ""} for t, r in refs]
        fasting = pick_majority(sanctoral_fasting.get(md, Counter()))
        holy = sanctoral_holy.get(md, 0) > 0 and md in GREAT_FEASTS
        entry = {
            "title": title,
            "readings": readings,
            "beatsSunday": md in GREAT_FEASTS,
            "holyDayOfObligation": holy,
        }
        if fasting:
            entry["fasting"] = fasting
        sanctoral[md] = entry

    return {
        "meta": {
            "source": "byzantine-calendars/readings.csv",
            "model": "pascha-pentecost-two-anchor",
            "years": [2024, 2025, 2026],
        },
        "temporal": dict(sorted(temporal.items())),
        "sanctoral": dict(sorted(sanctoral.items())),
    }, mismatches


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    rows = load_rows(args.input)
    lectionary, mismatches = distill(rows)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(lectionary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {args.output}")
    print(f"temporal slots={len(lectionary['temporal'])} sanctoral={len(lectionary['sanctoral'])}")
    print(f"title mismatches={len(mismatches)}")
    for line in mismatches[:40]:
        print(f"  {line}")
    if len(mismatches) > 40:
        print(f"  ... {len(mismatches) - 40} more")


if __name__ == "__main__":
    main()
