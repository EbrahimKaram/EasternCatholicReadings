import { describe, it } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import {
  gregorianEaster,
  predictedMatins,
  predictedTone,
  resolveByzantineDay,
  temporalSlot,
} from './byzantineCalendar.js';

const root = dirname(fileURLToPath(import.meta.url));
const lectionary = JSON.parse(
  readFileSync(join(root, '../data/byzantineLectionary.json'), 'utf8'),
);

const dateString = (year, month, day) => new Date(year, month - 1, day).toDateString();

describe('gregorian Easter', () => {
  it('matches Romanian Byzantine Pascha dates in the CSV', () => {
    assert.equal(gregorianEaster(2024).toDateString(), dateString(2024, 3, 31));
    assert.equal(gregorianEaster(2025).toDateString(), dateString(2025, 4, 20));
    assert.equal(gregorianEaster(2026).toDateString(), dateString(2026, 4, 5));
  });
});

describe('Pascha-relative Sundays', () => {
  it('places Zacchaeus on the Sunday before Publican, transferring a week for Encounter', () => {
    assert.equal(temporalSlot('2024-01-14').key, 'triodion:zacchaeus');
    assert.match(temporalSlot('2024-01-14').title, /Zacchaeus/i);
    assert.equal(temporalSlot('2025-01-26').key, 'triodion:zacchaeus');
    assert.equal(temporalSlot('2026-01-18').key, 'triodion:zacchaeus');
  });

  it('places Publican, Palm, Thomas, Pentecost, and All Saints at fixed offsets', () => {
    assert.equal(temporalSlot('2024-01-21').key, 'triodion:publican');
    assert.equal(temporalSlot('2024-03-24').key, 'holyweek:palm');
    assert.equal(temporalSlot('2024-03-31').key, 'pascha:sunday');
    assert.equal(temporalSlot('2024-04-07').key, 'pascha:thomas');
    assert.equal(temporalSlot('2024-05-19').key, 'pentecost:sunday');
    assert.equal(temporalSlot('2024-05-26').key, 'afterPentecost:sunday:1');
    assert.match(temporalSlot('2024-05-26').title, /All Saints/i);
  });
});

describe('Octoechos tone', () => {
  it('starts at 1 on Thomas Sunday and is omitted on Pascha and Pentecost', () => {
    assert.equal(predictedTone('2024-04-07'), 1);
    assert.equal(predictedTone('2024-03-31'), null);
    assert.equal(predictedTone('2024-05-19'), null);
    assert.equal(temporalSlot('2024-05-26').tone, 8);
    assert.equal(temporalSlot('2025-02-09').tone, 5);
  });
});

describe('Matins gospel', () => {
  it('uses the Paschal map, then an 11-week loop from All Saints', () => {
    assert.equal(predictedMatins('2024-04-07'), 1);
    assert.equal(predictedMatins('2024-04-14'), 4);
    assert.equal(predictedMatins('2024-05-26'), 1);
    assert.equal(predictedMatins('2024-08-04'), 11);
    assert.equal(predictedMatins('2024-08-11'), 1);
    assert.equal(predictedMatins('2024-03-31'), null);
  });
});

describe('cosmetic Sunday labels', () => {
  it('does not reset the Pentecost count at Sept 14 or Christmas', () => {
    const beforeCross = temporalSlot('2024-09-08');
    assert.equal(beforeCross.key, 'afterPentecost:sunday:16');
    assert.match(beforeCross.title, /before the Exaltation/i);

    const afterCross = temporalSlot('2024-09-15');
    assert.equal(afterCross.key, 'afterPentecost:sunday:17');
    assert.match(afterCross.title, /after the Exaltation/i);

    const beforeNativity = temporalSlot('2024-12-22');
    assert.equal(beforeNativity.key, 'afterPentecost:sunday:31');
    assert.match(beforeNativity.title, /before Nativity/i);
  });
});

describe('resolveByzantineDay', () => {
  it('returns Pascha epistle and gospel from the distilled lectionary', () => {
    const day = resolveByzantineDay('2024-03-31', lectionary);
    const refs = day.readings.map((item) => item.reference).join(' ');
    assert.match(refs, /Acts/i);
    assert.match(refs, /Jn|John/i);
    assert.equal(day.isHolyDayOfObligation, true);
  });

  it('keeps All Saints readings on the first Sunday after Pentecost', () => {
    const day = resolveByzantineDay('2026-05-31', lectionary);
    assert.match(day.title, /All Saints/i);
    assert.equal(day.tone, 8);
    assert.ok(day.readings.some((item) => item.type === 'gospel'));
  });

  it('lets Exaltation beat the temporal Sunday when Sept 14 is Sunday', () => {
    const day = resolveByzantineDay('2025-09-14', lectionary);
    assert.match(day.title, /Exaltation/i);
    assert.equal(day.source, 'sanctoral');
  });
});
