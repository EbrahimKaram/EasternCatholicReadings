const WEEKDAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
const ORDINALS = [
  '',
  'First',
  'Second',
  'Third',
  'Fourth',
  'Fifth',
  'Sixth',
  'Seventh',
  'Eighth',
  'Ninth',
  'Tenth',
  'Eleventh',
  'Twelfth',
  'Thirteenth',
  'Fourteenth',
  'Fifteenth',
  'Sixteenth',
  'Seventeenth',
  'Eighteenth',
  'Nineteenth',
  'Twentieth',
];

const LENT_SUNDAYS = {
  1: 'First Sunday of Great Lent: Cana Sunday',
  2: 'Second Sunday of Great Lent: Healing of the Leper',
  3: 'Third Sunday of Great Lent: Healing of the Hemorrhaging Woman',
  4: 'Fourth Sunday of Great Lent: Parable of the Prodigal Son',
  5: 'Fifth Sunday of Great Lent: Sunday of the Paralytic',
  6: 'Sixth Sunday of Great Lent: Healing of the Blind Man',
};

const RESURRECTION_SUNDAYS = {
  1: 'Great Sunday of the Resurrection',
  2: 'Second Sunday of the Resurrection: New Sunday',
  3: 'Third Sunday of the Resurrection: Appearance to the Disciples of Emmaus',
  4: 'Fourth Sunday of the Resurrection: Appearance to the Disciples by the Sea of Tiberias',
  5: 'Fifth Sunday of the Resurrection: Peter Receives his Ministry',
  6: 'Sixth Sunday of the Resurrection: Appearance to the 12',
  7: 'Seventh Sunday of the Resurrection: New Commandment',
};

const PENTECOST_SUNDAYS = {
  1: 'Pentecost',
  2: 'Second Sunday of Pentecost: Most Holy Trinity',
  3: 'Third Sunday of Pentecost: Holy Spirit Teaches',
  4: 'Fourth Sunday of Pentecost: Jesus Rejoice in the Holy Spirit',
  5: 'Fifth Sunday of Pentecost: Call of the Apostles',
  6: 'Sixth Sunday of Pentecost: Sending of the Apostles',
  7: 'Seventh Sunday of Pentecost: Sending of the Seventy-two',
  8: 'Eighth Sunday of Pentecost: Jesus the Servant Beloved',
  9: 'Ninth Sunday of Pentecost: Jesus in the Synagogue of Nazareth',
  10: 'Tenth Sunday of Pentecost: Jesus and Beelzebul',
  11: 'Eleventh Sunday of Pentecost: Zacchaeus the Chief Tax Collector',
  12: 'Twelfth Sunday of Pentecost: The Canaanite Women',
  13: 'Thirteenth Sunday of Pentecost: Parable of the Sower',
  14: 'Fourteenth Sunday of Pentecost: Martha and Mary',
  15: 'Fifteenth Sunday of Pentecost: Repentance of a Sinful Woman',
  16: 'Sixteenth Sunday of Pentecost: Parable of the Pharisee and the Tax Collector',
  17: 'Seventeenth Sunday of Pentecost: Parable of the Good Samaritan',
};

const CROSS_SUNDAYS = {
  1: 'First Sunday of the Cross',
  2: 'Second Sunday of the Cross',
  3: 'Third Sunday of the Cross: False Messiahs and Coming of the Son of Man',
  4: 'Fourth Sunday of the Cross: Faithful and Wise Slave',
  5: 'Fifth Sunday of the Cross: Parable of the Ten Bridesmaids',
  6: 'Sixth Sunday of the Cross: Parable of the Talents',
  7: 'Seventh Sunday of the Cross: Judgment of the Nations',
};

const ANNOUNCEMENT_SUNDAYS = [
  'Sunday of the Consecration of the Church',
  'Sunday of the Renewal of the Church',
  'Sunday of the Announcement to Zechariah',
  'Sunday of the Announcement to the Virgin Mary',
  'Sunday of the Visitation to Elizabeth',
  'Sunday of the Birth of St John the Baptizer',
  'Sunday of the Revelation to St Joseph',
  'Genealogy Sunday',
];

const ANNOUNCEMENT_KEYS = [
  'consecration',
  'renewal',
  'zechariah',
  'virgin',
  'visitation',
  'john',
  'joseph',
  'genealogy',
];

const PRELENT = {
  priests: 'Sunday of the Priests',
  righteous: 'Sunday of the Righteous and the Just',
  departed: 'Sunday of the Faithful Departed',
};

const pad = (n) => String(n).padStart(2, '0');

export const toDateParts = (input) => {
  if (input instanceof Date) {
    return {
      year: input.getFullYear(),
      month: input.getMonth() + 1,
      day: input.getDate(),
    };
  }
  const [year, month, day] = String(input).split('-').map(Number);
  return { year, month, day };
};

const civilDate = (year, month, day) => new Date(year, month - 1, day);

const addDays = (d, days) => {
  const next = new Date(d.getFullYear(), d.getMonth(), d.getDate() + days);
  return next;
};

const diffDays = (a, b) => Math.round((a - b) / 86400000);

const weekdayIndex = (d) => (d.getDay() + 6) % 7; // Mon=0 ... Sun=6
const isSunday = (d) => d.getDay() === 0;
const weekdayName = (d) => WEEKDAYS[weekdayIndex(d)];
const ordinal = (n) => ORDINALS[n] ?? String(n);
const monthDayKey = (d) => `${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;

export const gregorianEaster = (year) => {
  const a = year % 19;
  const b = Math.floor(year / 100);
  const c = year % 100;
  const d = Math.floor(b / 4);
  const e = b % 4;
  const f = Math.floor((b + 8) / 25);
  const g = Math.floor((b - f + 1) / 3);
  const h = (19 * a + b - d - g + 15) % 30;
  const i = Math.floor(c / 4);
  const k = c % 4;
  const l = (32 + 2 * e + 2 * i - h - k) % 7;
  const m = Math.floor((a + 11 * h + 22 * l) / 451);
  const month = Math.floor((h + l - 7 * m + 114) / 31);
  const day = ((h + l - 7 * m + 114) % 31) + 1;
  return civilDate(year, month, day);
};

const sundayOnOrAfter = (d) => addDays(d, (7 - d.getDay()) % 7);

const sundayBefore = (d) => addDays(d, d.getDay() === 0 ? -7 : -d.getDay());

export const firstCrossSunday = (year) => {
  const exaltation = civilDate(year, 9, 14);
  if (exaltation.getDay() === 0) return addDays(exaltation, 7);
  return sundayOnOrAfter(exaltation);
};

export const genealogySunday = (year) => sundayBefore(civilDate(year, 12, 25));
export const consecrationSunday = (year) => addDays(genealogySunday(year), -49);

const announcementIndex = (d) => {
  const year = d.getMonth() + 1 >= 10 ? d.getFullYear() : d.getFullYear() - 1;
  if (year < 1) return null;
  const start = consecrationSunday(year);
  const end = civilDate(year, 12, 24);
  if (d < start || d > end) return null;
  const sunday = isSunday(d) ? d : addDays(d, -d.getDay());
  const weeks = Math.floor(diffDays(sunday, start) / 7);
  if (weeks >= 0 && weeks <= 7) return weeks;
  return null;
};

const slot = (key, title, season, week = null) => ({ key, title, season, week });

export const temporalSlot = (input) => {
  const { year, month, day } = toDateParts(input);
  const d = civilDate(year, month, day);
  const eas = gregorianEaster(year);
  const cana = addDays(eas, -49);
  const pentecost = addDays(eas, 49);
  const offset = diffDays(d, eas);
  const dow = weekdayIndex(d);
  const sunday = isSunday(d);

  const epiphany = civilDate(year, 1, 6);
  const firstEpiphanySunday = sundayOnOrAfter(addDays(epiphany, 1));
  let christmas = null;
  if (d >= civilDate(year, 12, 25)) christmas = civilDate(year, 12, 25);
  else if (d < firstEpiphanySunday) christmas = civilDate(year - 1, 12, 25);

  if (offset === 0) return slot('pascha:sunday', RESURRECTION_SUNDAYS[1], 'pascha');
  if (offset === 39) return slot('pascha:ascension', 'The Ascension of Our Lord', 'pascha');
  if (offset === 49) return slot('pentecost:sunday:1', PENTECOST_SUNDAYS[1], 'pentecost', 1);
  if (offset === -1) return slot('holyweek:saturday', 'Great Saturday of the Light', 'holyweek');
  if (offset === -2) return slot('holyweek:friday', 'Great Friday of the Crucifixion', 'holyweek');
  if (offset === -3) return slot('holyweek:mysteries', 'Thursday of the Mysteries', 'holyweek');
  if (offset >= -6 && offset <= -4) {
    return slot(`holyweek:passion:${dow}`, `${weekdayName(d)} of Passion week`, 'holyweek');
  }
  if (offset === -7) return slot('holyweek:hosanna', 'Hosanna Sunday', 'holyweek');
  if (offset === -8) return slot('lent:lazarus', 'Lazarus Saturday', 'lent');
  if (offset === -9) {
    return slot('lent:friday40', 'Friday the 40th day of Great Lent: Temptation of Jesus', 'lent');
  }
  if (offset >= 1 && offset <= 6) {
    return slot(`pascha:hawarayeen:${dow}`, `${weekdayName(d)} of the Week of Hawarayeen`, 'pascha');
  }
  if (offset >= 7 && offset <= 48) {
    const week = Math.floor(offset / 7) + 1;
    if (sunday) {
      return slot(
        `resurrection:sunday:${week}`,
        RESURRECTION_SUNDAYS[week] ?? `${ordinal(week)} Sunday of the Resurrection`,
        'resurrection',
        week,
      );
    }
    return slot(
      `resurrection:weekday:${week}:${dow}`,
      `${weekdayName(d)} of the ${ordinal(week)} Week of the Resurrection`,
      'resurrection',
      week,
    );
  }
  if (offset >= -48 && offset <= -10) {
    const week = Math.floor(diffDays(d, cana) / 7) + 1;
    if (sunday) {
      return slot(
        `lent:sunday:${week}`,
        LENT_SUNDAYS[week] ?? `${ordinal(week)} Sunday of Great Lent`,
        'lent',
        week,
      );
    }
    return slot(
      `lent:weekday:${week}:${dow}`,
      `${weekdayName(d)} of the ${ordinal(week)} Week of Great Lent`,
      'lent',
      week,
    );
  }
  if (sunday && offset === -49) return slot('lent:sunday:1', LENT_SUNDAYS[1], 'lent', 1);

  const ann = announcementIndex(d);
  if (ann !== null) {
    const key = ANNOUNCEMENT_KEYS[ann];
    const sundayTitle = ANNOUNCEMENT_SUNDAYS[ann];
    if (sunday) return slot(`announcement:sunday:${key}`, sundayTitle, 'announcement', ann + 1);
    return slot(
      `announcement:weekday:${key}:${dow}`,
      `${weekdayName(d)} after the ${sundayTitle}`,
      'announcement',
      ann + 1,
    );
  }

  const cross0 = firstCrossSunday(year);
  const cons = consecrationSunday(year);
  if (d >= cross0 && d < cons) {
    const week = Math.floor(diffDays(d, cross0) / 7) + 1;
    if (sunday) {
      let title = CROSS_SUNDAYS[week] ?? `${ordinal(week)} Sunday of the Cross`;
      if (civilDate(year, 9, 14).getDay() === 0 && week === 1) {
        title = 'First Sunday after Holy Cross';
      }
      return slot(`cross:sunday:${week}`, title, 'cross', week);
    }
    return slot(
      `cross:weekday:${week}:${dow}`,
      `${weekdayName(d)} of the ${ordinal(week)} Week of the Cross`,
      'cross',
      week,
    );
  }

  if (d > pentecost && d < cross0) {
    const week = Math.floor(diffDays(d, pentecost) / 7) + 1;
    if (sunday) {
      return slot(
        `pentecost:sunday:${week}`,
        PENTECOST_SUNDAYS[week] ?? `${ordinal(week)} Sunday of Pentecost`,
        'pentecost',
        week,
      );
    }
    return slot(
      `pentecost:weekday:${week}:${dow}`,
      `${weekdayName(d)} of the ${ordinal(week)} Week of Pentecost`,
      'pentecost',
      week,
    );
  }

  if (christmas) {
    const epiphanyOfSeason = civilDate(christmas.getFullYear() + 1, 1, 6);
    const firstAfterEpiphany = sundayOnOrAfter(addDays(epiphanyOfSeason, 1));
    const firstAfterChristmas = sundayOnOrAfter(addDays(christmas, 1));
    const incarnated = christmas.getDay() === 0 ? null : firstAfterChristmas;
    const finding = christmas.getDay() === 0
      ? firstAfterChristmas
      : addDays(firstAfterChristmas, 7);
    if (d.getTime() === christmas.getTime()) {
      return slot('christmas:nativity', 'Feast of the Glorious Birth of Our Lord', 'christmas');
    }
    if (sunday && incarnated && d.getTime() === incarnated.getTime() && d < epiphanyOfSeason) {
      return slot('christmas:incarnated_logos', 'Incarnated Logos', 'christmas');
    }
    if (sunday && finding && d.getTime() === finding.getTime() && d <= epiphanyOfSeason) {
      return slot('christmas:finding', 'Sunday of the Finding of the Lord in the Temple', 'christmas');
    }
    if (d.getTime() === epiphanyOfSeason.getTime()) {
      return slot('christmas:epiphany', 'Feast of the Glorious Epiphany', 'christmas');
    }
    if (d.getTime() === addDays(epiphanyOfSeason, -1).getTime() && !sunday) {
      return slot('christmas:epiphany_vigil', 'Vigil of the Glorious Epiphany', 'christmas');
    }
    if (d.getTime() === civilDate(christmas.getFullYear() + 1, 1, 1).getTime() && !sunday) {
      return slot('christmas:circumcision', 'Feast of the Circumcision of the Lord Jesus', 'christmas');
    }
    if (d.getTime() === addDays(epiphanyOfSeason, 1).getTime() && !sunday) {
      return slot('christmas:john_baptist', 'Praises to John the Baptist', 'christmas');
    }
    if (d > epiphanyOfSeason && d < firstAfterEpiphany && !sunday) {
      const n = diffDays(d, epiphanyOfSeason);
      return slot(`christmas:epiphany_day:${n}`, `${ordinal(n)} day after the Epiphany`, 'christmas');
    }
    if (d > christmas && d < firstAfterEpiphany && !sunday) {
      return slot(
        `christmas:weekday:${monthDayKey(d)}`,
        `${weekdayName(d)} of the Christmas Season`,
        'christmas',
      );
    }
  }

  const priests = addDays(cana, -21);
  const righteous = addDays(cana, -14);
  const departed = addDays(cana, -7);
  if (d >= firstEpiphanySunday && d < cana) {
    if (sunday) {
      if (d.getTime() === priests.getTime()) return slot('prelent:sunday:priests', PRELENT.priests, 'prelent');
      if (d.getTime() === righteous.getTime()) return slot('prelent:sunday:righteous', PRELENT.righteous, 'prelent');
      if (d.getTime() === departed.getTime()) return slot('prelent:sunday:departed', PRELENT.departed, 'prelent');
      const week = Math.floor(diffDays(d, firstEpiphanySunday) / 7) + 1;
      return slot(`epiphany:sunday:${week}`, `${ordinal(week)} Sunday after Epiphany`, 'epiphany', week);
    }
    const weekSunday = addDays(d, -d.getDay());
    if (weekSunday.getTime() === priests.getTime()) {
      return slot(`prelent:weekday:priests:${dow}`, `${weekdayName(d)} after the Sunday of the Priests`, 'prelent');
    }
    if (weekSunday.getTime() === righteous.getTime()) {
      return slot(
        `prelent:weekday:righteous:${dow}`,
        `${weekdayName(d)} after the Sunday of the Righteous and the Just`,
        'prelent',
      );
    }
    if (weekSunday.getTime() === departed.getTime()) {
      return slot(
        `prelent:weekday:departed:${dow}`,
        `${weekdayName(d)} after the Sunday of the Faithful Departed`,
        'prelent',
      );
    }
    const week = Math.floor(diffDays(weekSunday, firstEpiphanySunday) / 7) + 1;
    if (week >= 1) {
      return slot(
        `epiphany:weekday:${week}:${dow}`,
        `${weekdayName(d)} of the ${ordinal(week)} Week of Epiphany`,
        'epiphany',
        week,
      );
    }
  }

  return slot(`unknown:${year}-${pad(month)}-${pad(day)}`, weekdayName(d), 'unknown');
};

const toReadings = (table) => (table?.readings ?? []).map((reading) => ({
  type: reading.type,
  reference: reading.reference,
  book: reading.book || '',
  text: '',
}));

const normalizeTitle = (title) => String(title || '')
  .toLowerCase()
  .replace(/[^a-z0-9]+/g, ' ')
  .trim();

const gospelKey = (readings) => readings
  .filter((reading) => reading.type === 'gospel')
  .map((reading) => reading.reference)
  .join('|');

const isDuplicateCard = (a, b) => {
  if (!a || !b) return false;
  if (normalizeTitle(a.liturgic_title) === normalizeTitle(b.liturgic_title)) return true;
  const aGospel = gospelKey(a.readings);
  const bGospel = gospelKey(b.readings);
  return Boolean(aGospel) && aGospel === bGospel;
};

export const resolveMaroniteDay = (input, lectionary) => {
  const { year, month, day } = toDateParts(input);
  const d = civilDate(year, month, day);
  const temporal = temporalSlot(d);
  const feast = lectionary?.sanctoral?.[monthDayKey(d)];
  const temporalTable = lectionary?.temporal?.[temporal.key];

  const temporalCard = {
    liturgic_title: temporal.title,
    readings: toReadings(temporalTable),
    slot: temporal.key,
    season: temporal.season,
    source: 'temporal',
  };

  const feastCard = feast
    ? {
      liturgic_title: feast.title,
      readings: toReadings(feast),
      slot: `sanctoral:${monthDayKey(d)}`,
      season: 'sanctoral',
      source: 'sanctoral',
    }
    : null;

  const cards = [];
  const temporalHasReadings = temporalCard.readings.length > 0 && temporal.season !== 'unknown';
  if (temporalHasReadings) cards.push(temporalCard);
  if (feastCard && !cards.some((card) => isDuplicateCard(card, feastCard))) {
    cards.push(feastCard);
  }
  if (!cards.length && feastCard) cards.push(feastCard);

  const primary = cards[0] ?? {
    liturgic_title: temporal.title,
    readings: [],
    slot: temporal.key,
    season: temporal.season,
    source: 'temporal',
  };

  return {
    liturgic_title: primary.liturgic_title,
    readings: primary.readings,
    slot: primary.slot,
    season: primary.season,
    source: primary.source,
    cards,
  };
};
