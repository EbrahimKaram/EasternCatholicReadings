export const pad = (n) => String(n).padStart(2, '0');

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

export const civilDate = (year, month, day) => new Date(year, month - 1, day);

export const addDays = (d, days) => new Date(d.getFullYear(), d.getMonth(), d.getDate() + days);

export const diffDays = (a, b) => Math.round((a - b) / 86400000);

export const weekdayIndex = (d) => (d.getDay() + 6) % 7; // Mon=0 ... Sun=6

export const isSunday = (d) => d.getDay() === 0;

export const monthDayKey = (d) => `${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;

export const isoDate = (d) => `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;

export const sundayOnOrAfter = (d) => addDays(d, (7 - d.getDay()) % 7);

export const sundayBefore = (d) => addDays(d, d.getDay() === 0 ? -7 : -d.getDay());

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
