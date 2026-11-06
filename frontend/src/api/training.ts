import { api } from './client';
import type { Paginated, TrainingLog, TrainingStatus } from '../types';

export async function fetchTrainingStatus(): Promise<TrainingStatus> {
  return api.get<TrainingStatus>('/api/training/today/');
}

export async function setTodayTraining(trained: boolean): Promise<TrainingStatus> {
  return api.post<TrainingStatus>('/api/training/today/', { trained });
}

export async function fetchTrainingHistory(): Promise<Paginated<TrainingLog>> {
  return api.get<Paginated<TrainingLog>>('/api/training/');
}

export async function fetchTrainingCalendar(year: number, month: number): Promise<TrainingLog[]> {
  return api.get<TrainingLog[]>(`/api/training/calendar/?year=${year}&month=${month}`);
}

/** date is 'YYYY-MM-DD'. Sets/corrects any date up to and including today — for backfilling a day the player forgot to log. */
export async function setDayTraining(date: string, trained: boolean): Promise<TrainingStatus> {
  return api.post<TrainingStatus>(`/api/training/${date}/`, { trained });
}
