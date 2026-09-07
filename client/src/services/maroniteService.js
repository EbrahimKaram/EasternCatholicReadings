import lectionary from '../data/maroniteLectionary.json';
import { resolveMaroniteDay } from './maroniteCalendar.js';

export const getMaroniteReadings = async (date) => {
  if (!date) return null;
  const day = resolveMaroniteDay(date, lectionary);
  if (!day.readings.length && day.season === 'unknown') return null;
  return {
    liturgic_title: day.liturgic_title,
    readings: day.readings,
    slot: day.slot,
    season: day.season,
  };
};
