import { api } from './client';
import type { AssignedPlayer, PlayerDetail } from '../types';

export async function fetchLinkedChildren(): Promise<AssignedPlayer[]> {
  return api.get<AssignedPlayer[]>('/api/parent/children/');
}

export async function fetchChildDetail(playerProfileId: number): Promise<PlayerDetail> {
  return api.get<PlayerDetail>(`/api/parent/children/${playerProfileId}/`);
}
