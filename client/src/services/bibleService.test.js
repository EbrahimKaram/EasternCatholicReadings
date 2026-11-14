import { afterEach, describe, it } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { fetchScriptureText } from './bibleService.js';
import { parseReadingDescription } from '../utils/readingParser.js';

const originalFetch = globalThis.fetch;
const originalStorage = globalThis.localStorage;
const originalError = console.error;

function mockApi(responses) {
  const requests = [];
  globalThis.localStorage = {
    getItem: () => null,
    setItem: () => {},
    removeItem: () => {},
  };
  globalThis.fetch = async (url) => {
    const ref = decodeURIComponent(new URL(url).pathname.slice(1));
    requests.push(ref);
    const result = responses[ref];
    return result
      ? { ok: true, json: async () => ({ verses: result }) }
      : { ok: false, status: 404 };
  };
  return requests;
}

function verses(chapter, start, end) {
  return Array.from({ length: end - start + 1 }, (_, index) => ({
    chapter,
    verse: start + index,
    text: `Verse ${start + index}`,
  }));
}

afterEach(() => {
  globalThis.fetch = originalFetch;
  globalThis.localStorage = originalStorage;
  console.error = originalError;
});

describe('Bible API passages', () => {
  it('does not interpret the twelve Gospels as a Gospel reference', () => {
    const parsed = parseReadingDescription('Great and Holy Thursday: Reading of 12 Gospels');
    assert.equal(parsed.gospel, null);
    assert.match(parsed.notes, /12 Gospels/);
    assert.equal(parseReadingDescription('Gospel: Lk. 1:24-38').gospel, 'Lk. 1:24-38');
  });

  it('fetches both parts of the original Malachi reading', async () => {
    const requests = mockApi({
      'Malachi 2:1-1': verses(2, 1, 1),
      'Malachi 2:5-9': verses(2, 5, 9),
    });
    const html = await fetchScriptureText('Ma 2:1-1#Ma 2:5-9');
    assert.deepEqual(requests, ['Malachi 2:1-1', 'Malachi 2:5-9']);
    assert.match(html, /Verse 1/);
    assert.match(html, /Verse 9/);
  });

  it('retains the full book name in continuation ranges', async () => {
    const requests = mockApi({
      'Song of Solomon 5:2-8': verses(5, 2, 8),
      'Song of Solomon 5:10-12': verses(5, 10, 12),
    });
    assert.ok(await fetchScriptureText('Ct 5:2-8; 10-12'));
    assert.deepEqual(requests, ['Song of Solomon 5:2-8', 'Song of Solomon 5:10-12']);
  });

  it('accepts a book abbreviation without a space after the period', async () => {
    const requests = mockApi({ 'Mk 1:1-8': verses(1, 1, 8) });
    assert.ok(await fetchScriptureText('Mk.1:1-8'));
    assert.deepEqual(requests, ['Mk 1:1-8']);
  });

  it('accepts a complete cross-chapter passage', async () => {
    mockApi({ 'Heb 11:33-12:2': [...verses(11, 33, 40), ...verses(12, 1, 2)] });
    assert.ok(await fetchScriptureText('Heb. 11: 33-12: 2'));
  });

  it('maps and labels verified Douay-Rheims verse numbering', async () => {
    const cases = [
      ['1 Th 4:13-18', '1 Thessalonians 4:12-17', 4, 12, 17],
      ['2 Th 2:13-17', '2 Thessalonians 2:12-16', 2, 12, 16],
      ['Mc 4:33-41', 'Mark 4:33-40', 4, 33, 40],
      ['Mt 17:24-27', 'Matthew 17:23-26', 17, 23, 26],
      ['Ac 14:19-28', 'Acts 14:18-27', 14, 18, 27],
      ['3 Jn 1:1-15', '3 John 1:1-14', 1, 1, 14],
      ['Mc 9:38-50', 'Mark 9:37-49', 9, 37, 49],
      ['Ac 7:51-60', 'Acts 7:51-59', 7, 51, 59],
      ['Acts 7:47-60', 'Acts 7:47-59', 7, 47, 59],
    ];
    for (const [reference, apiRef, chapter, start, end] of cases) {
      const requests = mockApi({ [apiRef]: verses(chapter, start, end) });
      const html = await fetchScriptureText(reference);
      assert.deepEqual(requests, [apiRef]);
      assert.match(html, new RegExp(`Douay-Rheims numbering: ${apiRef}`));
    }
  });

  it('maps the combined Isaiah reference without duplicating verse 9:1', async () => {
    const requests = mockApi({ 'Isaiah 9:1-5': verses(9, 1, 5) });
    const html = await fetchScriptureText('Is 8:23-23; Is 9:1-5');
    assert.match(html, /Douay-Rheims numbering: Isaiah 9:1-5/);
    assert.deepEqual(requests, ['Isaiah 9:1-5']);
  });

  it('does not return the first part when a later part fails', async () => {
    mockApi({ 'Malachi 2:1-1': verses(2, 1, 1) });
    console.error = () => {};
    assert.equal(await fetchScriptureText('Ma 2:1-1#Ma 2:5-9'), null);
  });

  it('rejects empty, truncated, and internally incomplete API results', async () => {
    mockApi({
      'John 12:17-6:2': [],
      'Malachi 2:5-9': [...verses(2, 5, 6), ...verses(2, 8, 9)],
      'Matthew 3:1-5': verses(3, 1, 4),
    });
    console.error = () => {};
    assert.equal(await fetchScriptureText('John 12:17-6:2'), null);
    assert.equal(await fetchScriptureText('Malachi 2:5-9'), null);
    assert.equal(await fetchScriptureText('Matthew 3:1-5'), null);
  });

  it('constructs valid requests for both lectionaries', async () => {
    const references = new Set();
    const collect = (value) => {
      if (!value || typeof value !== 'object') return;
      if (typeof value.reference === 'string') references.add(value.reference);
      Object.values(value).forEach(collect);
    };
    for (const name of ['maroniteLectionary', 'byzantineLectionary']) {
      collect(JSON.parse(readFileSync(new URL(`../data/${name}.json`, import.meta.url), 'utf8')));
    }

    globalThis.localStorage = { getItem: () => null, setItem: () => {}, removeItem: () => {} };
    console.error = () => {};
    globalThis.fetch = async (url) => {
      const ref = decodeURIComponent(new URL(url).pathname.slice(1));
      const match = ref.match(/^(?:\d\s+)?[A-Za-z]+(?:\s+[A-Za-z]+)*\s+(\d+):(\d+)(?:-(?:(\d+):)?(\d+))?$/);
      if (!match) return { ok: false, status: 404 };
      const startChapter = Number(match[1]);
      const startVerse = Number(match[2]);
      const endChapter = Number(match[3] || match[1]);
      const endVerse = Number(match[4] || match[2]);
      if (endChapter < startChapter || (endChapter === startChapter && endVerse < startVerse)) {
        return { ok: false, status: 404 };
      }
      const result = endChapter === startChapter
        ? verses(startChapter, startVerse, endVerse)
        : [
            ...verses(startChapter, startVerse, startVerse),
            ...Array.from({ length: endChapter - startChapter - 1 }, (_, index) =>
              verses(startChapter + index + 1, 1, 1)).flat(),
            ...verses(endChapter, 1, endVerse),
          ];
      return { ok: true, json: async () => ({ verses: result }) };
    };
    const failures = [];
    for (const reference of references) {
      if (!await fetchScriptureText(reference)) failures.push(reference);
    }
    assert.deepEqual(failures, []);
  });
});
