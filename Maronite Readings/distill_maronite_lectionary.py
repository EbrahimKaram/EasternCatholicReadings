"""Distill a compact Maronite lectionary from scraped yearly JSON.

Reads maronite_calendar.json, assigns each day a temporal slot via the
three-anchor calendar, and writes client/src/data/maroniteLectionary.json
with reference-only temporal + sanctoral tables.

Usage:
    python distill_maronite_lectionary.py
    python distill_maronite_lectionary.py --input maronite_calendar.json --output ../client/src/data/maroniteLectionary.json
"""
from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from datetime import date, timedelta
from pathlib import Path

WEEKDAYS = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")
ORDINALS = (
    "",
    "First",
    "Second",
    "Third",
    "Fourth",
    "Fifth",
    "Sixth",
    "Seventh",
    "Eighth",
    "Ninth",
    "Tenth",
    "Eleventh",
    "Twelfth",
    "Thirteenth",
    "Fourteenth",
    "Fifteenth",
    "Sixteenth",
    "Seventeenth",
    "Eighteenth",
    "Nineteenth",
    "Twentieth",
)

LENT_SUNDAYS = {
    1: "First Sunday of Great Lent: Cana Sunday",
    2: "Second Sunday of Great Lent: Healing of the Leper",
    3: "Third Sunday of Great Lent: Healing of the Hemorrhaging Woman",
    4: "Fourth Sunday of Great Lent: Parable of the Prodigal Son",
    5: "Fifth Sunday of Great Lent: Sunday of the Paralytic",
    6: "Sixth Sunday of Great Lent: Healing of the Blind Man",
}

RESURRECTION_SUNDAYS = {
    1: "Great Sunday of the Resurrection",
    2: "Second Sunday of the Resurrection: New Sunday",
    3: "Third Sunday of the Resurrection: Appearance to the Disciples of Emmaus",
    4: "Fourth Sunday of the Resurrection: Appearance to the Disciples by the Sea of Tiberias",
    5: "Fifth Sunday of the Resurrection: Peter Receives his Ministry",
    6: "Sixth Sunday of the Resurrection: Appearance to the 12",
    7: "Seventh Sunday of the Resurrection: New Commandment",
}

PENTECOST_SUNDAYS = {
    1: "Pentecost",
    2: "Second Sunday of Pentecost: Most Holy Trinity",
    3: "Third Sunday of Pentecost: Holy Spirit Teaches",
    4: "Fourth Sunday of Pentecost: Jesus Rejoice in the Holy Spirit",
    5: "Fifth Sunday of Pentecost: Call of the Apostles",
    6: "Sixth Sunday of Pentecost: Sending of the Apostles",
    7: "Seventh Sunday of Pentecost: Sending of the Seventy-two",
    8: "Eighth Sunday of Pentecost: Jesus the Servant Beloved",
    9: "Ninth Sunday of Pentecost: Jesus in the Synagogue of Nazareth",
    10: "Tenth Sunday of Pentecost: Jesus and Beelzebul",
    11: "Eleventh Sunday of Pentecost: Zacchaeus the Chief Tax Collector",
    12: "Twelfth Sunday of Pentecost: The Canaanite Women",
    13: "Thirteenth Sunday of Pentecost: Parable of the Sower",
    14: "Fourteenth Sunday of Pentecost: Martha and Mary",
    15: "Fifteenth Sunday of Pentecost: Repentance of a Sinful Woman",
    16: "Sixteenth Sunday of Pentecost: Parable of the Pharisee and the Tax Collector",
    17: "Seventeenth Sunday of Pentecost: Parable of the Good Samaritan",
}

CROSS_SUNDAYS = {
    1: "First Sunday of the Cross",
    2: "Second Sunday of the Cross",
    3: "Third Sunday of the Cross: False Messiahs and Coming of the Son of Man",
    4: "Fourth Sunday of the Cross: Faithful and Wise Slave",
    5: "Fifth Sunday of the Cross: Parable of the Ten Bridesmaids",
    6: "Sixth Sunday of the Cross: Parable of the Talents",
    7: "Seventh Sunday of the Cross: Judgment of the Nations",
}

ANNOUNCEMENT_SUNDAYS = (
    "Sunday of the Consecration of the Church",
    "Sunday of the Renewal of the Church",
    "Sunday of the Announcement to Zechariah",
    "Sunday of the Announcement to the Virgin Mary",
    "Sunday of the Visitation to Elizabeth",
    "Sunday of the Birth of St John the Baptizer",
    "Sunday of the Revelation to St Joseph",
    "Genealogy Sunday",
)

ANNOUNCEMENT_KEYS = (
    "consecration",
    "renewal",
    "zechariah",
    "virgin",
    "visitation",
    "john",
    "joseph",
    "genealogy",
)

PRELENT = (
    ("priests", "Sunday of the Priests"),
    ("righteous", "Sunday of the Righteous and the Just"),
    ("departed", "Sunday of the Faithful Departed"),
)

FEAST_TITLE_RE = re.compile(
    r"^(Feast|The Exaltation|Nativity of the Blessed|Assumption|"
    r"Martyrdom of|Praises to the Virgin|The Adoration of the Magi|"
    r"The Flight into Egypt|The Word Became Flesh|"
    r"Praises of John|Praises to John|"
    r"Vigil of the Glorious Epiphany)",
    re.I,
)

GOSPEL_REF_RE = re.compile(r"^(Mt|Mc|Lc|Jn|Mk|Lk|Matt)\b", re.I)
OT_REF_RE = re.compile(
    r"^(Gn|Ex|Lv|Nb|Dt|Jos|Jg|Rt|1 S|2 S|1 R|2 R|1 Ch|2 Ch|Esd|Ne|"
    r"Tb|Jdt|Est|1 M|2 M|Jb|Ps|Pr|Qo|Ct|Sg|Ws|Si|"
    r"Is|Jr|Lm|Ba|Ez|Dn|Ho|Jl|Am|Ob|Jon|Mi|Na|Ha|So|Hg|Za|Ml|"
    r"Gen|Exod|Lev|Num|Deut|Josh|Judg|Ruth|Sam|Kgs|Chr|Ezra|"
    r"Neh|Job|Prov|Eccl|Song|Wis|Sir|Isa|Jer|Lam|Bar|Ezek|"
    r"Dan|Hos|Joel|Amos|Obad|Mic|Nah|Hab|Zeph|Hag|Zech|Mal)\b",
    re.I,
)

SEASONAL_HINT_RE = re.compile(
    r"Sunday of|Week of|after Epiphany|after Holy Cross|after the Holy Cross|"
    r"Great Lent|Hosanna|Lazarus|Passion week|Mysteries|"
    r"Great Friday|Great Saturday|Great Sunday|"
    r"Hawarayeen|Resurrection|Pentecost|of the Cross|"
    r"Consecration of the Church|Renewal of the Church|"
    r"Announcement to|Visitation to|Revelation to|"
    r"Genealogy Sunday|Incarnated Logos|"
    r"Finding of the Lord|Cana Sunday|"
    r"Monday after|Tuesday after|Wednesday after|"
    r"Thursday after|Friday after|Saturday after",
    re.I,
)


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


def sunday_on_or_after(d: date) -> date:
    return d + timedelta(days=(6 - d.weekday()) % 7)


def sunday_before(d: date) -> date:
    return d - timedelta(days=(d.weekday() + 1 if d.weekday() != 6 else 7))


def first_cross_sunday(year: int) -> date:
    exaltation = date(year, 9, 14)
    if exaltation.weekday() == 6:
        return exaltation + timedelta(days=7)
    return sunday_on_or_after(exaltation)


def genealogy_sunday(year: int) -> date:
    return sunday_before(date(year, 12, 25))


def consecration_sunday(year: int) -> date:
    return genealogy_sunday(year) - timedelta(weeks=7)


def weekday_name(d: date) -> str:
    return WEEKDAYS[d.weekday()]


def ordinal(n: int) -> str:
    if 1 <= n < len(ORDINALS):
        return ORDINALS[n]
    return str(n)


def normalize_reference(ref: str) -> str:
    text = (ref or "").replace("#", "; ")
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"(\d)[ab]\b", r"\1", text)
    return text


def canonical_type(item: dict) -> str:
    book = item.get("book") or ""
    ref = item.get("reference") or ""
    raw_type = (item.get("type") or "").lower()
    if raw_type == "gospel" or "Gospel" in book or GOSPEL_REF_RE.match(ref):
        return "gospel"
    if "Gospel" not in book and (OT_REF_RE.match(ref) or any(
        token in book
        for token in (
            "Genesis", "Exodus", "Leviticus", "Numbers", "Deuteronomy",
            "Joshua", "Judges", "Ruth", "Samuel", "Kings", "Chronicles",
            "Ezra", "Nehemiah", "Tobit", "Judith", "Esther", "Maccab",
            "Job", "Psalm", "Proverb", "Ecclesiastes", "Song", "Wisdom",
            "Sirach", "Isaiah", "Jeremiah", "Lamentation", "Baruch",
            "Ezekiel", "Daniel", "Hosea", "Joel", "Amos", "Obadiah",
            "Jonah", "Micah", "Nahum", "Habakkuk", "Zephaniah", "Haggai",
            "Zechariah", "Malachi",
        )
    )):
        return "reading"
    return "psalm"


def strip_readings(readings: list[dict]) -> list[dict]:
    out = []
    for item in readings or []:
        ref = normalize_reference(item.get("reference") or "")
        out.append(
            {
                "type": canonical_type({**item, "reference": ref}),
                "reference": ref,
                "book": item.get("book") or "",
            }
        )
    return out


def readings_key(readings: list[dict]) -> tuple:
    return tuple((r.get("type"), r.get("reference")) for r in readings)


def is_feast_title(title: str) -> bool:
    if not title:
        return False
    if SEASONAL_HINT_RE.search(title) and not FEAST_TITLE_RE.search(title):
        return False
    if FEAST_TITLE_RE.search(title):
        return True
    if title.startswith("Feast"):
        return True
    return False


def announcement_index(d: date) -> int | None:
    year = d.year if d.month >= 10 else d.year - 1
    if year < 1:
        return None
    start = consecration_sunday(year)
    end = genealogy_sunday(year)
    if not (start <= d <= date(year, 12, 24)):
        return None
    if d.weekday() == 6:
        weeks = (d - start).days // 7
        if 0 <= weeks <= 7:
            return weeks
        return None
    sunday = d - timedelta(days=d.weekday() + 1)
    weeks = (sunday - start).days // 7
    if 0 <= weeks <= 7:
        return weeks
    return None


def temporal_slot(d: date) -> dict:
    """Return slot metadata for the temporal cycle, ignoring sanctoral overlays."""
    year = d.year
    eas = gregorian_easter(year)
    cana = eas - timedelta(days=49)
    pentecost = eas + timedelta(days=49)
    offset = (d - eas).days
    dow = d.weekday()  # Mon=0 ... Sun=6
    is_sunday = dow == 6

    epiphany = date(year, 1, 6)
    first_epiphany_sunday = sunday_on_or_after(epiphany + timedelta(days=1))
    if d >= date(year, 12, 25):
        christmas = date(year, 12, 25)
    elif d < first_epiphany_sunday:
        christmas = date(year - 1, 12, 25)
    else:
        christmas = None

    if offset == 0:
        return slot("pascha:sunday", RESURRECTION_SUNDAYS[1], "pascha")
    if offset == 39:
        return slot("pascha:ascension", "The Ascension of Our Lord", "pascha")
    if offset == 49:
        return slot("pentecost:sunday:1", PENTECOST_SUNDAYS[1], "pentecost", week=1)
    if offset == -1:
        return slot("holyweek:saturday", "Great Saturday of the Light", "holyweek")
    if offset == -2:
        return slot("holyweek:friday", "Great Friday of the Crucifixion", "holyweek")
    if offset == -3:
        return slot("holyweek:mysteries", "Thursday of the Mysteries", "holyweek")
    if -6 <= offset <= -4:
        return slot(
            f"holyweek:passion:{dow}",
            f"{weekday_name(d)} of Passion week",
            "holyweek",
        )
    if offset == -7:
        return slot("holyweek:hosanna", "Hosanna Sunday", "holyweek")
    if offset == -8:
        return slot("lent:lazarus", "Lazarus Saturday", "lent")
    if offset == -9:
        return slot(
            "lent:friday40",
            "Friday the 40th day of Great Lent: Temptation of Jesus",
            "lent",
        )
    if 1 <= offset <= 6:
        return slot(
            f"pascha:hawarayeen:{dow}",
            f"{weekday_name(d)} of the Week of Hawarayeen",
            "pascha",
        )
    if 7 <= offset <= 48:
        week = (offset // 7) + 1
        if is_sunday:
            title = RESURRECTION_SUNDAYS.get(week, f"{ordinal(week)} Sunday of the Resurrection")
            return slot(f"resurrection:sunday:{week}", title, "resurrection", week=week)
        title = f"{weekday_name(d)} of the {ordinal(week)} Week of the Resurrection"
        return slot(f"resurrection:weekday:{week}:{dow}", title, "resurrection", week=week)
    if -48 <= offset <= -10:
        week = ((d - cana).days // 7) + 1
        if is_sunday:
            title = LENT_SUNDAYS.get(week, f"{ordinal(week)} Sunday of Great Lent")
            return slot(f"lent:sunday:{week}", title, "lent", week=week)
        title = f"{weekday_name(d)} of the {ordinal(week)} Week of Great Lent"
        return slot(f"lent:weekday:{week}:{dow}", title, "lent", week=week)
    if is_sunday and offset == -49:
        return slot("lent:sunday:1", LENT_SUNDAYS[1], "lent", week=1)

    ann = announcement_index(d)
    if ann is not None:
        key = ANNOUNCEMENT_KEYS[ann]
        sunday_title = ANNOUNCEMENT_SUNDAYS[ann]
        if is_sunday:
            return slot(f"announcement:sunday:{key}", sunday_title, "announcement", week=ann + 1)
        return slot(
            f"announcement:weekday:{key}:{dow}",
            f"{weekday_name(d)} after the {sunday_title}",
            "announcement",
            week=ann + 1,
        )

    cross0 = first_cross_sunday(year)
    cons = consecration_sunday(year)
    if cross0 <= d < cons:
        week = ((d - cross0).days // 7) + 1
        if is_sunday:
            title = CROSS_SUNDAYS.get(week, f"{ordinal(week)} Sunday of the Cross")
            if date(year, 9, 14).weekday() == 6 and week == 1:
                title = "First Sunday after Holy Cross"
            return slot(f"cross:sunday:{week}", title, "cross", week=week)
        title = f"{weekday_name(d)} of the {ordinal(week)} Week of the Cross"
        return slot(f"cross:weekday:{week}:{dow}", title, "cross", week=week)

    if pentecost < d < cross0:
        week = ((d - pentecost).days // 7) + 1
        if is_sunday:
            title = PENTECOST_SUNDAYS.get(week, f"{ordinal(week)} Sunday of Pentecost")
            return slot(f"pentecost:sunday:{week}", title, "pentecost", week=week)
        title = f"{weekday_name(d)} of the {ordinal(week)} Week of Pentecost"
        return slot(f"pentecost:weekday:{week}:{dow}", title, "pentecost", week=week)

    if christmas:
        epiphany_of_season = date(christmas.year + 1, 1, 6)
        first_after_epiphany = sunday_on_or_after(epiphany_of_season + timedelta(days=1))
        first_after_christmas = sunday_on_or_after(christmas + timedelta(days=1))
        if christmas.weekday() == 6:
            incarnated = None
            finding = first_after_christmas
        else:
            incarnated = first_after_christmas
            finding = first_after_christmas + timedelta(days=7)
        if d == christmas:
            return slot("christmas:nativity", "Feast of the Glorious Birth of Our Lord", "christmas")
        if is_sunday and incarnated and d == incarnated and d < epiphany_of_season:
            return slot("christmas:incarnated_logos", "Incarnated Logos", "christmas")
        if is_sunday and finding and d == finding and d <= epiphany_of_season:
            return slot("christmas:finding", "Sunday of the Finding of the Lord in the Temple", "christmas")
        if d == epiphany_of_season:
            return slot("christmas:epiphany", "Feast of the Glorious Epiphany", "christmas")
        if d == epiphany_of_season - timedelta(days=1) and not is_sunday:
            return slot("christmas:epiphany_vigil", "Vigil of the Glorious Epiphany", "christmas")
        if d == date(christmas.year + 1, 1, 1) and not is_sunday:
            return slot("christmas:circumcision", "Feast of the Circumcision of the Lord Jesus", "christmas")
        if d == epiphany_of_season + timedelta(days=1) and not is_sunday:
            return slot("christmas:john_baptist", "Praises to John the Baptist", "christmas")
        if epiphany_of_season < d < first_after_epiphany and not is_sunday:
            n = (d - epiphany_of_season).days
            return slot(
                f"christmas:epiphany_day:{n}",
                f"{ordinal(n)} day after the Epiphany",
                "christmas",
            )
        if christmas < d < first_after_epiphany and not is_sunday:
            return slot(
                f"christmas:weekday:{d.month:02d}-{d.day:02d}",
                f"{weekday_name(d)} of the Christmas Season",
                "christmas",
            )

    priests = cana - timedelta(weeks=3)
    righteous = cana - timedelta(weeks=2)
    departed = cana - timedelta(weeks=1)
    if first_epiphany_sunday <= d < cana:
        if is_sunday:
            if d == priests:
                return slot("prelent:sunday:priests", PRELENT[0][1], "prelent")
            if d == righteous:
                return slot("prelent:sunday:righteous", PRELENT[1][1], "prelent")
            if d == departed:
                return slot("prelent:sunday:departed", PRELENT[2][1], "prelent")
            week = ((d - first_epiphany_sunday).days // 7) + 1
            title = f"{ordinal(week)} Sunday after Epiphany"
            return slot(f"epiphany:sunday:{week}", title, "epiphany", week=week)
        sunday = d - timedelta(days=dow + 1)
        if sunday == priests:
            return slot(
                f"prelent:weekday:priests:{dow}",
                f"{weekday_name(d)} after the Sunday of the Priests",
                "prelent",
            )
        if sunday == righteous:
            return slot(
                f"prelent:weekday:righteous:{dow}",
                f"{weekday_name(d)} after the Sunday of the Righteous and the Just",
                "prelent",
            )
        if sunday == departed:
            return slot(
                f"prelent:weekday:departed:{dow}",
                f"{weekday_name(d)} after the Sunday of the Faithful Departed",
                "prelent",
            )
        week = ((sunday - first_epiphany_sunday).days // 7) + 1
        if week >= 1:
            title = f"{weekday_name(d)} of the {ordinal(week)} Week of Epiphany"
            return slot(f"epiphany:weekday:{week}:{dow}", title, "epiphany", week=week)

    return slot(f"unknown:{d.isoformat()}", d.strftime("%A"), "unknown")


def slot(key: str, title: str, season: str, week: int | None = None) -> dict:
    return {"key": key, "title": title, "season": season, "week": week}


def pick_majority(counter: Counter):
    if not counter:
        return None
    return counter.most_common(1)[0][0]


def distill(calendar: dict) -> tuple[dict, dict]:
    temporal_titles: dict[str, Counter] = defaultdict(Counter)
    temporal_readings: dict[str, Counter] = defaultdict(Counter)
    temporal_reading_map: dict[str, dict[tuple, list]] = defaultdict(dict)
    sanctoral_titles: dict[str, Counter] = defaultdict(Counter)
    sanctoral_readings: dict[str, Counter] = defaultdict(Counter)
    sanctoral_reading_map: dict[str, dict[tuple, list]] = defaultdict(dict)
    sanctoral_sunday: dict[str, bool] = defaultdict(bool)
    mismatches = []
    unassigned = []

    for key in sorted(calendar):
        d = date.fromisoformat(key)
        entry = calendar[key]
        observed = (entry.get("liturgic_title") or "").strip()
        readings = strip_readings(entry.get("readings") or [])
        rkey = readings_key(readings)
        meta = temporal_slot(d)
        slot_key = meta["key"]

        feast = is_feast_title(observed)
        if feast:
            md = f"{d.month:02d}-{d.day:02d}"
            sanctoral_titles[md][observed] += 1
            sanctoral_readings[md][rkey] += 1
            sanctoral_reading_map[md][rkey] = readings
            if d.weekday() == 6:
                sanctoral_sunday[md] = True
            continue

        if slot_key.startswith("unknown:"):
            unassigned.append((key, observed, slot_key))
            continue

        temporal_titles[slot_key][observed or meta["title"]] += 1
        temporal_readings[slot_key][rkey] += 1
        temporal_reading_map[slot_key][rkey] = readings

        # Title-family mismatch for report (not fatal)
        expected = meta["title"].lower()
        obs = observed.lower()
        if expected.split(":")[0][:18] not in obs and obs[:18] not in expected:
            if not any(token in obs for token in expected.lower().split()[:3]):
                mismatches.append((key, observed, meta["title"], slot_key))

    temporal = {}
    conflicts = []
    for slot_key, title_counts in temporal_titles.items():
        title = pick_majority(title_counts)
        rcounts = temporal_readings[slot_key]
        if len(rcounts) > 1:
            conflicts.append(
                {
                    "slot": slot_key,
                    "variants": {str(k): v for k, v in rcounts.items()},
                }
            )
        best = pick_majority(rcounts)
        temporal[slot_key] = {
            "title": title,
            "readings": temporal_reading_map[slot_key].get(best, []),
        }

    sanctoral = {}
    for md, title_counts in sanctoral_titles.items():
        title = pick_majority(title_counts)
        rcounts = sanctoral_readings[md]
        best = pick_majority(rcounts)
        sanctoral[md] = {
            "title": title,
            "readings": sanctoral_reading_map[md].get(best, []),
            "beatsSunday": bool(sanctoral_sunday[md]),
        }

    report = {
        "days": len(calendar),
        "temporalSlots": len(temporal),
        "sanctoralDates": len(sanctoral),
        "unassigned": unassigned[:80],
        "unassignedCount": len(unassigned),
        "titleMismatches": mismatches[:80],
        "titleMismatchCount": len(mismatches),
        "readingConflicts": conflicts,
    }
    return {"temporal": temporal, "sanctoral": sanctoral}, report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    root = Path(__file__).resolve().parent
    parser.add_argument("--input", default=str(root / "maronite_calendar.json"))
    parser.add_argument(
        "--output",
        default=str(root.parent / "client" / "src" / "data" / "maroniteLectionary.json"),
    )
    args = parser.parse_args()

    calendar = json.loads(Path(args.input).read_text(encoding="utf-8"))
    lectionary, report = distill(calendar)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(lectionary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print(f"Wrote {output_path}")
    print(f"  temporal slots: {report['temporalSlots']}")
    print(f"  sanctoral dates: {report['sanctoralDates']}")
    print(f"  unassigned: {report['unassignedCount']}")
    print(f"  title mismatches: {report['titleMismatchCount']}")
    print(f"  reading conflicts: {len(report['readingConflicts'])}")
    if report["unassigned"]:
        print("  sample unassigned:")
        for row in report["unassigned"][:20]:
            print("   ", row)
    if report["readingConflicts"]:
        print("  conflicts:")
        for row in report["readingConflicts"][:20]:
            print("   ", row["slot"], row["variants"])


if __name__ == "__main__":
    main()
