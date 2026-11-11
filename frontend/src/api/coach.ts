import { api } from './client';
import type {
  AssignedPlayer,
  CoachTeam,
  CoachVideo,
  CoachVideoInput,
  Paginated,
  PlayerDetail,
} from '../types';

export async function fetchAssignedPlayers(): Promise<AssignedPlayer[]> {
  return api.get<AssignedPlayer[]>('/api/coach/players/');
}

export async function fetchPlayerDetail(playerProfileId: number): Promise<PlayerDetail> {
  return api.get<PlayerDetail>(`/api/coach/players/${playerProfileId}/`);
}

export async function fetchCoachVideos(): Promise<Paginated<CoachVideo>> {
  return api.get<Paginated<CoachVideo>>('/api/coach/videos/');
}

export async function createCoachVideo(input: CoachVideoInput): Promise<CoachVideo> {
  return api.post<CoachVideo>('/api/coach/videos/', input);
}

export async function updateCoachVideoAssignment(
  videoId: number,
  input: Pick<CoachVideoInput, 'assigned_teams' | 'assigned_players'>,
): Promise<CoachVideo> {
  return api.patch<CoachVideo>(`/api/coach/videos/${videoId}/`, input);
}

export async function fetchCoachTeams(): Promise<CoachTeam[]> {
  return api.get<CoachTeam[]>('/api/coach/teams/');
}
