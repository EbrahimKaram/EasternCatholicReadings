"""Byzantine two-anchor temporal cycle (Pascha + Pentecost).

Python mirror of client/src/services/byzantineCalendar.js.
Zacchaeus is the Sunday before Publican Sunday (Pascha - 77), not -76.
Tone restarts at 1 on Thomas Sunday and skips Pascha and Pentecost.
Matins gospel uses a Paschal-season map, then an 11-week loop from All Saints.
"""
from __future__ import annotations

from datetime import date, timedelta

TONE_CYCLE = 8
MATINS_CYCLE = 11

PASCHAL_MATINS = {
    7: 1,   # Thomas
    14: 4,  # Myrrhbearers
    21: 5,  # Paralytic
    28: 7,  # Samaritan
    35: 8,  # Blind
    42: 10, # Fathers of Nicaea
}

LENT_SUNDAYS = {
    1: "1st Sunday of Lent: Sunday of Orthodoxy",
    2: "2nd Sunday of Lent: Gregory Palamas",
    3: "3rd Sunday of Lent: Veneration of the Holy Cross",
    4: "4th Sunday of Lent: Ven. Father John of the Ladder",
    5: "5th Sunday of Lent: Ven. Mother Mary of Egypt",
}

HOLY_WEEK = {
    -7: ("holyweek:palm", "Palm Sunday"),
    -6: ("holyweek:monday", "Great and Holy Monday"),
    -5: ("holyweek:tuesday", "Great and Holy Tuesday"),
    -4: ("holyweek:wednesday", "Great and Holy Wednesday"),
    -3: ("holyweek:thursday", "Great and Holy Thursday"),
    -2: ("holyweek:friday", "Great and Holy Friday"),
    -1: ("holyweek:saturday", "Great and Holy Saturday"),
}

BRIGHT_WEEK = {
    1: "Bright Monday",
    2: "Bright Tuesday",
    3: "Bright Wednesday",
    4: "Bright Thursday",
    5: "Bright Friday",
    6: "Bright Saturday",
}

WEEKDAYS = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")

BEATS_SUNDAY_DATES = {
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


def nth(n: int) -> str:
    if 10 <= n % 100 <= 20:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"


def sunday_before(d: date) -> date:
    return d - timedelta(days=(d.weekday() + 1 if d.weekday() != 6 else 7))


def sunday_on_or_after(d: date) -> date:
    return d + timedelta(days=(6 - d.weekday()) % 7)


def sunday_after(d: date) -> date:
    if d.weekday() == 6:
        return d + timedelta(days=7)
    return sunday_on_or_after(d)


def zacchaeus_sunday(year: int) -> date:
    d = gregorian_easter(year) - timedelta(days=77)
    if d.strftime("%m-%d") in BEATS_SUNDAY_DATES:
        return d - timedelta(days=7)
    return d


def anchors(year: int) -> dict:
    pascha = gregorian_easter(year)
    return {
        "pascha": pascha,
        "publican": pascha - timedelta(days=70),
        "zacchaeus": zacchaeus_sunday(year),
        "pentecost": pascha + timedelta(days=49),
        "thomas": pascha + timedelta(days=7),
        "allsaints": pascha + timedelta(days=56),
    }


def pentecost_for(d: date, year: int, pascha: date) -> date:
    publican = pascha - timedelta(days=70)
    if d < publican:
        return gregorian_easter(year - 1) + timedelta(days=49)
    return pascha + timedelta(days=49)


def allsaints_for_matins(d: date, year: int, pascha: date) -> date:
    allsaints = pascha + timedelta(days=56)
    if d >= allsaints:
        return allsaints
    return gregorian_easter(year - 1) + timedelta(days=56)


def predicted_tone(d: date, year: int, pascha: date) -> int | None:
    if d.weekday() != 6:
        return None
    if d == pascha or d == pascha + timedelta(days=49):
        return None
    thomas = pascha + timedelta(days=7)
    if d >= thomas:
        weeks = (d - thomas).days // 7
        return (weeks % TONE_CYCLE) + 1
    prev_thomas = gregorian_easter(year - 1) + timedelta(days=7)
    weeks = (d - prev_thomas).days // 7
    return (weeks % TONE_CYCLE) + 1


def predicted_matins(d: date, year: int, pascha: date) -> int | None:
    if d.weekday() != 6:
        return None
    offset = (d - pascha).days
    if offset in (0, 49):
        return None
    if offset in PASCHAL_MATINS:
        return PASCHAL_MATINS[offset]
    allsaints = allsaints_for_matins(d, year, pascha)
    weeks = (d - allsaints).days // 7
    return (weeks % MATINS_CYCLE) + 1


def cosmetic_sunday(d: date) -> str | None:
    before_exaltation = sunday_before(date(d.year, 9, 14))
    after_exaltation = sunday_after(date(d.year, 9, 14))
    before_nativity = sunday_before(date(d.year, 12, 25))
    after_nativity = sunday_after(date(d.year, 12, 25))
    before_theophany = sunday_before(date(d.year, 1, 6))
    after_theophany = sunday_after(date(d.year, 1, 6))
    ancestors = before_nativity - timedelta(days=7)
    fathers_six_start = date(d.year, 7, 13)
    fathers_six_end = date(d.year, 7, 19)
    fathers_seven_start = date(d.year, 10, 11)
    fathers_seven_end = date(d.year, 10, 17)

    if d == before_theophany:
        return "Sunday before the Theophany"
    if d == after_theophany:
        return "Sunday after the Theophany"
    if d == before_exaltation:
        return "Sunday before the Exaltation of the Cross"
    if d == after_exaltation:
        return "Sunday after the Exaltation of the Cross"
    if d == before_nativity:
        return "Sunday before Nativity of Our Lord Jesus Christ"
    if d == after_nativity:
        return "Sunday after Nativity of Our Lord Jesus Christ"
    if d == ancestors:
        return "Sunday of the Holy Ancestors"
    if fathers_six_start <= d <= fathers_six_end:
        return "Sunday of the Holy Fathers of the First Six Ecumenical Councils"
    if fathers_seven_start <= d <= fathers_seven_end:
        return "Sunday of the Holy Fathers of the Seventh Ecumenical Council"
    return None


def after_pentecost_title(d: date, n: int, zacchaeus: date) -> str:
    label = cosmetic_sunday(d)
    after_exaltation = sunday_after(date(d.year, 9, 14))
    if d == zacchaeus:
        return f"Zacchaeus Sunday ({nth(n)} Sunday after Pentecost)"
    if n == 1:
        return "1st Sunday after Pentecost: Sunday of All Saints"
    if label:
        if d >= after_exaltation and "Exaltation" not in label and "Theophany" not in label:
            return f"{label} ({nth(n)} Sunday after Pentecost)"
        return label
    if d == date(d.year, 9, 1):
        return f"Indiction; beginning of the Church year {nth(n)} Sunday after Pentecost"
    if d > after_exaltation:
        cross_n = (d - after_exaltation).days // 7
        return f"{nth(cross_n)} Sunday after Holy Cross ({nth(n)} Sunday after Pentecost)"
    return f"{nth(n)} Sunday after Pentecost"


def temporal_slot(d: date) -> dict:
    year = d.year
    pascha = gregorian_easter(year)
    offset = (d - pascha).days
    is_sun = d.weekday() == 6
    tone = predicted_tone(d, year, pascha)
    matins = predicted_matins(d, year, pascha)
    publican = pascha - timedelta(days=70)
    zacchaeus = zacchaeus_sunday(year)
    pentecost = pascha + timedelta(days=49)

    def result(key, title, season, week=None):
        return {
            "key": key,
            "title": title,
            "season": season,
            "week": week,
            "tone": tone,
            "matinsGospel": matins,
            "offset": offset,
        }

    named_sundays = {
        -70: ("triodion:publican", "Sunday of the Publican and the Pharisee", "triodion"),
        -63: ("triodion:prodigal", "Sunday of the Prodigal Son", "triodion"),
        -56: ("triodion:meatfare", "Meatfare Sunday: Sunday of the Last Judgement", "triodion"),
        -49: ("triodion:cheesefare", "Cheesefare Sunday: Forgiveness Sunday", "triodion"),
        0: ("pascha:sunday", "Resurrection of Our Lord", "pascha"),
        7: ("pascha:thomas", "Thomas Sunday", "pascha"),
        14: ("pascha:myrrhbearers", "Sunday of the Myrrh-Bearing Women", "pascha"),
        21: ("pascha:paralytic", "Sunday of the Paralytic", "pascha"),
        28: ("pascha:samaritan", "Sunday of the Samaritan Woman", "pascha"),
        35: ("pascha:blind", "Sunday of the Man Born Blind", "pascha"),
        42: ("pascha:fathers", "Sunday of the Fathers of the First Ecumenical Council", "pascha"),
        49: ("pentecost:sunday", "Pentecost Sunday", "pentecost"),
    }

    if offset == 39:
        return result("pascha:ascension", "Ascension of the Lord", "pascha")

    if is_sun and offset in named_sundays:
        key, title, season = named_sundays[offset]
        week = { -70: 1, -63: 2, -56: 3, -49: 4, 7: 2, 14: 3, 21: 4, 28: 5, 35: 6, 42: 7 }.get(offset)
        return result(key, title, season, week)

    if is_sun and offset in (-42, -35, -28, -21, -14):
        week = { -42: 1, -35: 2, -28: 3, -21: 4, -14: 5 }[offset]
        return result(f"lent:sunday:{week}", LENT_SUNDAYS[week], "lent", week)

    if offset in HOLY_WEEK:
        key, title = HOLY_WEEK[offset]
        return result(key, title, "holyweek")

    if 1 <= offset <= 6:
        return result(f"pascha:bright:{offset}", BRIGHT_WEEK[offset], "pascha")

    if is_sun and d == zacchaeus:
        n = (d - pentecost_for(d, year, pascha)).days // 7
        return result("triodion:zacchaeus", after_pentecost_title(d, n, zacchaeus), "triodion", n)

    if d < publican or d > pentecost:
        if is_sun:
            pent = pentecost_for(d, year, pascha)
            n = (d - pent).days // 7
            z = zacchaeus if d < publican else zacchaeus_sunday(year + 1)
            title = after_pentecost_title(d, n, z)
            return result(f"afterPentecost:sunday:{n}", title, "afterPentecost", n)
        week_sunday = d if d.weekday() == 6 else d - timedelta(days=d.weekday() + 1)
        pent = pentecost_for(week_sunday, year, pascha)
        n = max(1, (week_sunday - pent).days // 7)
        return result(
            f"afterPentecost:weekday:{n}:{d.weekday()}",
            f"{WEEKDAYS[d.weekday()]} of the {nth(n)} week after Pentecost",
            "afterPentecost",
            n,
        )

    if -48 <= offset <= -8:
        week = ((d - (pascha - timedelta(days=49))).days // 7) + 1
        return result(
            f"lent:weekday:{week}:{d.weekday()}",
            f"{WEEKDAYS[d.weekday()]} of the {nth(week)} week of Great Lent",
            "lent",
            week,
        )

    if 8 <= offset <= 48:
        week = (offset // 7) + 1
        return result(
            f"pascha:weekday:{week}:{d.weekday()}",
            f"{WEEKDAYS[d.weekday()]} of the {nth(week)} week of Easter",
            "pascha",
            week,
        )

    return result(f"unknown:{d.isoformat()}", WEEKDAYS[d.weekday()], "unknown")
