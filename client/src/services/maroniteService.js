import lectionary from '../data/maroniteLectionary.json';
import { resolveMaroniteDay } from './maroniteCalendar.js';

export const getMaroniteReadings = async (date) => {
  if (!date) return null;
  const day = resolveMaroniteDay(date, lectionary);
  const cards = (day.cards?.length ? day.cards : [{
    liturgic_title: day.liturgic_title,
    readings: day.readings,
    slot: day.slot,
    season: day.season,
    source: day.source,
  }]).filter((card) => card.readings?.length || card.season !== 'unknown');
  if (!cards.length) return null;
  return cards;
};
