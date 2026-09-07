import { describe, it } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import {
  firstCrossSunday,
  genealogySunday,
  gregorianEaster,
  resolveMaroniteDay,
  temporalSlot,
} from './maroniteCalendar.js';

const root = dirname(fileURLToPath(import.meta.url));
const lectionary = JSON.parse(
  readFileSync(join(root, '../data/maroniteLectionary.json'), 'utf8'),
);

describe('gregorian Easter', () => {
  it('matches Western dates used by the Maronite JSON', () => {
    assert.equal(gregorianEaster(2024).toDateString(), new Date(2024, 2, 31).toDateString());
    assert.equal(gregorianEaster(2025).toDateString(), new Date(2025, 3, 20).toDateString());
    assert.equal(gregorianEaster(2026).toDateString(), new Date(2026, 3, 5).toDateString());
  });
});

describe('season anchors', () => {
  it('places Cana Sunday 49 days before Easter', () => {
    assert.equal(temporalSlot('2024-02-11').key, 'lent:sunday:1');
    assert.equal(temporalSlot('2025-03-02').title, 'First Sunday of Great Lent: Cana Sunday');
    assert.equal(temporalSlot('2026-02-15').key, 'lent:sunday:1');
  });

  it('starts counted Cross Sundays after Sept 14, shifting a week when Sept 14 is Sunday', () => {
    assert.equal(firstCrossSunday(2024).toDateString(), new Date(2024, 8, 15).toDateString());
    assert.equal(temporalSlot('2024-09-15').key, 'cross:sunday:1');
    assert.equal(temporalSlot('2024-09-15').title, 'First Sunday of the Cross');
    assert.equal(firstCrossSunday(2025).toDateString(), new Date(2025, 8, 21).toDateString());
    assert.equal(temporalSlot('2025-09-21').title, 'First Sunday after Holy Cross');
    assert.equal(temporalSlot('2025-09-14').season, 'pentecost');
  });

  it('counts eight Sundays back from Christmas', () => {
    assert.equal(genealogySunday(2024).toDateString(), new Date(2024, 11, 22).toDateString());
    assert.equal(temporalSlot('2024-11-03').key, 'announcement:sunday:consecration');
    assert.equal(temporalSlot('2024-12-22').key, 'announcement:sunday:genealogy');
    assert.equal(temporalSlot('2025-12-21').title, 'Genealogy Sunday');
  });
});

describe('resolveMaroniteDay overlays', () => {
  it('keeps Circumcision on weekdays and Finding on Sunday 1 January 2023', () => {
    const weekday = resolveMaroniteDay('2024-01-01', lectionary);
    assert.equal(weekday.cards.some((card) => /Circumcision/.test(card.liturgic_title)), true);
    const sunday = resolveMaroniteDay('2023-01-01', lectionary);
    assert.match(sunday.liturgic_title, /Finding of the Lord/);
  });

  it('shows Exaltation together with the temporal Sunday when Sept 14 is Sunday', () => {
    const day = resolveMaroniteDay('2025-09-14', lectionary);
    assert.equal(day.cards.length, 2);
    assert.equal(day.cards[0].source, 'temporal');
    assert.match(day.cards[1].liturgic_title, /Exaltation of the Glorious Cross/);
  });

  it('returns gospel and epistle references for Cana Sunday', () => {
    const day = resolveMaroniteDay('2026-02-15', lectionary);
    const types = day.readings.map((r) => r.type);
    assert.ok(types.includes('gospel'));
    assert.ok(day.readings.some((r) => /Jn 2:1-11/.test(r.reference)));
  });

  it('shows Ascension and the coinciding saint as two cards', () => {
    const day = resolveMaroniteDay('2024-05-09', lectionary);
    assert.equal(day.cards[0].liturgic_title, 'The Ascension of Our Lord');
    assert.equal(day.cards[0].source, 'temporal');
    assert.equal(day.cards.length, 2);
    assert.equal(day.cards[1].source, 'sanctoral');
    assert.match(day.cards[1].liturgic_title, /Isaiah/);
  });
});
