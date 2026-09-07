import lectionary from '../data/byzantineLectionary.json';
import { isHolyDayDate, resolveByzantineDay } from './byzantineCalendar.js';

const pad = (n) => String(n).padStart(2, '0');

const toDateString = (date) => {
  const d = new Date(date);
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
};

const readingRef = (readings, type) => readings.find((item) => item.type === type)?.reference;

export const getByzantineReadings = (date) => {
  if (!date) return null;
  const day = resolveByzantineDay(date, lectionary);
  if (!day) return null;
  if (!day.readings?.length && day.season === 'unknown' && !day.title) return null;

  const descriptionParts = [];
  const epistle = readingRef(day.readings, 'epistle');
  const gospel = readingRef(day.readings, 'gospel');
  if (epistle) descriptionParts.push(`Epistle: ${epistle}`);
  if (gospel) descriptionParts.push(`Gospel: ${gospel}`);
  if (day.tone) descriptionParts.push(`Tone ${day.tone}`);
  if (day.matinsGospel) descriptionParts.push(`Matins Gospel: ${day.matinsGospel}`);
  if (day.notes) descriptionParts.push(day.notes);

  const startDateStr = toDateString(date);
  const nextDay = new Date(date);
  nextDay.setDate(nextDay.getDate() + 1);

  return {
    id: `byzantine-${startDateStr}`,
    summary: day.title,
    description: descriptionParts.join('\n'),
    htmlLink: '',
    fasting: day.fasting,
    usaHoliday: null,
    canadaHoliday: null,
    isHolyDayOfObligation: day.isHolyDayOfObligation,
    start: { date: startDateStr },
    end: { date: toDateString(nextDay) },
  };
};

export const isByzantineHolyDay = (date) => isHolyDayDate(date, lectionary);
