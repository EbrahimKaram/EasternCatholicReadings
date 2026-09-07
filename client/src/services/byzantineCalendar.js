import {
  addDays,
  civilDate,
  diffDays,
  gregorianEaster,
  isoDate,
  isSunday,
  monthDayKey,
  sundayBefore,
  sundayOnOrAfter,
  toDateParts,
  weekdayIndex,
} from './calendarMath.js';

export { gregorianEaster, toDateParts };

const WEEKDAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
const TONE_CYCLE = 8;
const MATINS_CYCLE = 11;

const PASCHAL_MATINS = {
  7: 1,
  14: 4,
  21: 5,
  28: 7,
  35: 8,
  42: 10,
};

const LENT_SUNDAYS = {
  1: '1st Sunday of Lent: Sunday of Orthodoxy',
  2: '2nd Sunday of Lent: Gregory Palamas',
  3: '3rd Sunday of Lent: Veneration of the Holy Cross',
  4: '4th Sunday of Lent: Ven. Father John of the Ladder',
  5: '5th Sunday of Lent: Ven. Mother Mary of Egypt',
};

const HOLY_WEEK = {
  [-7]: ['holyweek:palm', 'Palm Sunday'],
  [-6]: ['holyweek:monday', 'Great and Holy Monday'],
  [-5]: ['holyweek:tuesday', 'Great and Holy Tuesday'],
  [-4]: ['holyweek:wednesday', 'Great and Holy Wednesday'],
  [-3]: ['holyweek:thursday', 'Great and Holy Thursday'],
  [-2]: ['holyweek:friday', 'Great and Holy Friday'],
  [-1]: ['holyweek:saturday', 'Great and Holy Saturday'],
};

const BRIGHT_WEEK = {
  1: 'Bright Monday',
  2: 'Bright Tuesday',
  3: 'Bright Wednesday',
  4: 'Bright Thursday',
  5: 'Bright Friday',
  6: 'Bright Saturday',
};

const NAMED_SUNDAYS = {
  [-70]: ['triodion:publican', 'Sunday of the Publican and the Pharisee', 'triodion', 1],
  [-63]: ['triodion:prodigal', 'Sunday of the Prodigal Son', 'triodion', 2],
  [-56]: ['triodion:meatfare', 'Meatfare Sunday: Sunday of the Last Judgement', 'triodion', 3],
  [-49]: ['triodion:cheesefare', 'Cheesefare Sunday: Forgiveness Sunday', 'triodion', 4],
  0: ['pascha:sunday', 'Resurrection of Our Lord', 'pascha', null],
  7: ['pascha:thomas', 'Thomas Sunday', 'pascha', 2],
  14: ['pascha:myrrhbearers', 'Sunday of the Myrrh-Bearing Women', 'pascha', 3],
  21: ['pascha:paralytic', 'Sunday of the Paralytic', 'pascha', 4],
  28: ['pascha:samaritan', 'Sunday of the Samaritan Woman', 'pascha', 5],
  35: ['pascha:blind', 'Sunday of the Man Born Blind', 'pascha', 6],
  42: ['pascha:fathers', 'Sunday of the Fathers of the First Ecumenical Council', 'pascha', 7],
  49: ['pentecost:sunday', 'Pentecost Sunday', 'pentecost', null],
};

const LENT_SUNDAY_OFFSETS = {
  [-42]: 1,
  [-35]: 2,
  [-28]: 3,
  [-21]: 4,
  [-14]: 5,
};

const MOVABLE_HOLY_KEYS = new Set([
  'pascha:sunday',
  'pentecost:sunday',
  'pascha:ascension',
]);

const BEATS_SUNDAY_DATES = new Set([
  '01-01',
  '01-06',
  '02-02',
  '03-25',
  '06-29',
  '08-06',
  '08-15',
  '09-08',
  '09-14',
  '11-21',
  '12-25',
  '12-26',
]);

const nth = (n) => {
  const mod100 = n % 100;
  const mod10 = n % 10;
  let suffix = 'th';
  if (mod100 < 10 || mod100 > 20) {
    if (mod10 === 1) suffix = 'st';
    else if (mod10 === 2) suffix = 'nd';
    else if (mod10 === 3) suffix = 'rd';
  }
  return `${n}${suffix}`;
};

const sundayAfter = (d) => {
  if (isSunday(d)) return addDays(d, 7);
  return sundayOnOrAfter(d);
};

export const zacchaeusSunday = (year) => {
  let d = addDays(gregorianEaster(year), -77);
  if (BEATS_SUNDAY_DATES.has(monthDayKey(d))) d = addDays(d, -7);
  return d;
};

const weekdayName = (d) => WEEKDAYS[weekdayIndex(d)];

const pentecostFor = (d, year, pascha) => {
  const publican = addDays(pascha, -70);
  if (d < publican) return addDays(gregorianEaster(year - 1), 49);
  return addDays(pascha, 49);
};

const allSaintsForMatins = (d, year, pascha) => {
  const allSaints = addDays(pascha, 56);
  if (d >= allSaints) return allSaints;
  return addDays(gregorianEaster(year - 1), 56);
};

export const predictedTone = (input) => {
  const { year, month, day } = toDateParts(input);
  const d = civilDate(year, month, day);
  const pascha = gregorianEaster(year);
  if (!isSunday(d)) return null;
  if (diffDays(d, pascha) === 0 || diffDays(d, pascha) === 49) return null;
  const thomas = addDays(pascha, 7);
  const origin = d >= thomas ? thomas : addDays(gregorianEaster(year - 1), 7);
  return (Math.floor(diffDays(d, origin) / 7) % TONE_CYCLE) + 1;
};

export const predictedMatins = (input) => {
  const { year, month, day } = toDateParts(input);
  const d = civilDate(year, month, day);
  const pascha = gregorianEaster(year);
  if (!isSunday(d)) return null;
  const offset = diffDays(d, pascha);
  if (offset === 0 || offset === 49) return null;
  if (PASCHAL_MATINS[offset]) return PASCHAL_MATINS[offset];
  const origin = allSaintsForMatins(d, year, pascha);
  return (Math.floor(diffDays(d, origin) / 7) % MATINS_CYCLE) + 1;
};

const cosmeticSunday = (d) => {
  const year = d.getFullYear();
  const beforeExaltation = sundayBefore(civilDate(year, 9, 14));
  const afterExaltation = sundayAfter(civilDate(year, 9, 14));
  const beforeNativity = sundayBefore(civilDate(year, 12, 25));
  const afterNativity = sundayAfter(civilDate(year, 12, 25));
  const beforeTheophany = sundayBefore(civilDate(year, 1, 6));
  const afterTheophany = sundayAfter(civilDate(year, 1, 6));
  const ancestors = addDays(beforeNativity, -7);
  if (diffDays(d, beforeTheophany) === 0) return 'Sunday before the Theophany';
  if (diffDays(d, afterTheophany) === 0) return 'Sunday after the Theophany';
  if (diffDays(d, beforeExaltation) === 0) return 'Sunday before the Exaltation of the Cross';
  if (diffDays(d, afterExaltation) === 0) return 'Sunday after the Exaltation of the Cross';
  if (diffDays(d, beforeNativity) === 0) return 'Sunday before Nativity of Our Lord Jesus Christ';
  if (diffDays(d, afterNativity) === 0) return 'Sunday after Nativity of Our Lord Jesus Christ';
  if (diffDays(d, ancestors) === 0) return 'Sunday of the Holy Ancestors';
  const month = d.getMonth() + 1;
  const day = d.getDate();
  if (month === 7 && day >= 13 && day <= 19) {
    return 'Sunday of the Holy Fathers of the First Six Ecumenical Councils';
  }
  if (month === 10 && day >= 11 && day <= 17) {
    return 'Sunday of the Holy Fathers of the Seventh Ecumenical Council';
  }
  return null;
};

const afterPentecostTitle = (d, n, zacchaeus) => {
  const label = cosmeticSunday(d);
  const afterExaltation = sundayAfter(civilDate(d.getFullYear(), 9, 14));
  if (diffDays(d, zacchaeus) === 0) {
    return `Zacchaeus Sunday (${nth(n)} Sunday after Pentecost)`;
  }
  if (n === 1) return '1st Sunday after Pentecost: Sunday of All Saints';
  if (label) {
    if (d >= afterExaltation && !label.includes('Exaltation') && !label.includes('Theophany')) {
      return `${label} (${nth(n)} Sunday after Pentecost)`;
    }
    return label;
  }
  if (d.getMonth() === 8 && d.getDate() === 1) {
    return `Indiction; beginning of the Church year ${nth(n)} Sunday after Pentecost`;
  }
  if (d > afterExaltation) {
    const crossN = Math.floor(diffDays(d, afterExaltation) / 7);
    return `${nth(crossN)} Sunday after Holy Cross (${nth(n)} Sunday after Pentecost)`;
  }
  return `${nth(n)} Sunday after Pentecost`;
};

const slot = (key, title, season, week, tone, matins, offset) => ({
  key,
  title,
  season,
  week,
  tone,
  matinsGospel: matins,
  offset,
});

export const temporalSlot = (input) => {
  const { year, month, day } = toDateParts(input);
  const d = civilDate(year, month, day);
  const pascha = gregorianEaster(year);
  const offset = diffDays(d, pascha);
  const sunday = isSunday(d);
  const tone = predictedTone(d);
  const matins = predictedMatins(d);
  const publican = addDays(pascha, -70);
  const zacchaeus = zacchaeusSunday(year);
  const pentecost = addDays(pascha, 49);

  if (offset === 39) {
    return slot('pascha:ascension', 'Ascension of the Lord', 'pascha', null, tone, matins, offset);
  }

  if (sunday && NAMED_SUNDAYS[offset]) {
    const [key, title, season, week] = NAMED_SUNDAYS[offset];
    return slot(key, title, season, week, tone, matins, offset);
  }

  if (sunday && LENT_SUNDAY_OFFSETS[offset]) {
    const week = LENT_SUNDAY_OFFSETS[offset];
    return slot(`lent:sunday:${week}`, LENT_SUNDAYS[week], 'lent', week, tone, matins, offset);
  }

  if (HOLY_WEEK[offset]) {
    const [key, title] = HOLY_WEEK[offset];
    return slot(key, title, 'holyweek', null, tone, matins, offset);
  }

  if (offset >= 1 && offset <= 6) {
    return slot(`pascha:bright:${offset}`, BRIGHT_WEEK[offset], 'pascha', null, tone, matins, offset);
  }

  if (sunday && diffDays(d, zacchaeus) === 0) {
    const pent = pentecostFor(d, year, pascha);
    const n = Math.floor(diffDays(d, pent) / 7);
    return slot('triodion:zacchaeus', afterPentecostTitle(d, n, zacchaeus), 'triodion', n, tone, matins, offset);
  }

  if (d < publican || d > pentecost) {
    if (sunday) {
      const pent = pentecostFor(d, year, pascha);
      const n = Math.floor(diffDays(d, pent) / 7);
      const z = d > pentecost ? zacchaeusSunday(year + 1) : zacchaeus;
      return slot(
        `afterPentecost:sunday:${n}`,
        afterPentecostTitle(d, n, z),
        'afterPentecost',
        n,
        tone,
        matins,
        offset,
      );
    }
    const weekSunday = isSunday(d) ? d : addDays(d, -d.getDay());
    const pent = pentecostFor(weekSunday, year, pascha);
    const n = Math.max(1, Math.floor(diffDays(weekSunday, pent) / 7));
    return slot(
      `afterPentecost:weekday:${n}:${weekdayIndex(d)}`,
      `${weekdayName(d)} of the ${nth(n)} week after Pentecost`,
      'afterPentecost',
      n,
      tone,
      matins,
      offset,
    );
  }

  if (offset >= -48 && offset <= -8) {
    const week = Math.floor(diffDays(d, addDays(pascha, -49)) / 7) + 1;
    return slot(
      `lent:weekday:${week}:${weekdayIndex(d)}`,
      `${weekdayName(d)} of the ${nth(week)} week of Great Lent`,
      'lent',
      week,
      tone,
      matins,
      offset,
    );
  }

  if (offset >= 8 && offset <= 48) {
    const week = Math.floor(offset / 7) + 1;
    return slot(
      `pascha:weekday:${week}:${weekdayIndex(d)}`,
      `${weekdayName(d)} of the ${nth(week)} week of Easter`,
      'pascha',
      week,
      tone,
      matins,
      offset,
    );
  }

  return slot(`unknown:${isoDate(d)}`, weekdayName(d), 'unknown', null, tone, matins, offset);
};

const toReadings = (entry) => {
  if (!entry?.readings?.length) return [];
  return entry.readings
    .map((item) => ({
      type: item.type,
      reference: item.reference,
      book: item.book || '',
    }))
    .filter((item) => item.reference);
};

const combineTitle = (temporalTitle, feastTitle) => {
  if (!feastTitle) return temporalTitle;
  if (!temporalTitle) return feastTitle;
  if (temporalTitle.toLowerCase().includes(feastTitle.toLowerCase())) return temporalTitle;
  if (feastTitle.toLowerCase().includes(temporalTitle.toLowerCase())) return feastTitle;
  return `${temporalTitle}. ${feastTitle}`;
};

export const resolveByzantineDay = (input, lectionary) => {
  const { year, month, day } = toDateParts(input);
  const d = civilDate(year, month, day);
  const temporal = temporalSlot(d);
  const md = monthDayKey(d);
  const feast = lectionary?.sanctoral?.[md] ?? null;
  const temporalTable = lectionary?.temporal?.[temporal.key] ?? null;
  const sunday = isSunday(d);
  const feastReadings = toReadings(feast);
  const temporalReadings = toReadings(temporalTable);

  let title = temporal.title;
  let readings = temporalReadings;
  let source = 'temporal';

  if (feast) {
    if (sunday && feast.beatsSunday) {
      title = feast.title;
      readings = feastReadings.length ? feastReadings : temporalReadings;
      source = 'sanctoral';
    } else if (sunday) {
      title = combineTitle(temporal.title, feast.title);
      readings = temporalReadings.length ? temporalReadings : feastReadings;
      source = temporalReadings.length ? 'temporal' : 'sanctoral';
    } else {
      title = combineTitle(temporal.title, feast.title);
      if (temporal.season === 'afterPentecost' || temporal.season === 'unknown') {
        title = feast.title;
      }
      readings = feastReadings.length ? feastReadings : temporalReadings;
      source = feastReadings.length ? 'sanctoral' : 'temporal';
    }
  }

  const isHolyDayOfObligation = Boolean(
    MOVABLE_HOLY_KEYS.has(temporal.key) || feast?.holyDayOfObligation,
  );

  return {
    title,
    liturgic_title: title,
    readings,
    slot: source === 'sanctoral' ? `sanctoral:${md}` : temporal.key,
    season: temporal.season,
    source,
    tone: temporal.tone,
    matinsGospel: temporal.matinsGospel,
    fasting: feast?.fasting || null,
    isHolyDayOfObligation,
    notes: feast?.notes || null,
  };
};

export const isHolyDayDate = (input, lectionary) => {
  const day = resolveByzantineDay(input, lectionary);
  return Boolean(day?.isHolyDayOfObligation);
};
