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
