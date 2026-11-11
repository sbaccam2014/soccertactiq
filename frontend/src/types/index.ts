export interface CurrentUser {
  id: number;
  username: string;
  display_name: string;
  is_staff: boolean;
  is_coach: boolean;
  is_parent: boolean;
}

export interface VideoListItem {
  id: number;
  title: string;
  category: string;
  description: string;
  status: 'draft' | 'published' | 'unavailable';
  is_watched: boolean;
}

export interface VideoDetail {
  id: number;
  title: string;
  category: string;
  description: string;
  video_url: string;
  video_start_seconds: number | null;
  status: 'draft' | 'published' | 'unavailable';
}

export interface VideoWatch {
  id: number;
  video: number;
  video_title_snapshot: string;
  watched_at: string;
}

export interface Paginated<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface TrainingLog {
  id: number;
  date: string;
  trained: boolean;
}

export interface TrainingStatus {
  today: TrainingLog | null;
  current_streak: number;
  month_trained_days: number;
  year_trained_days: number;
}

export interface AssignedPlayer {
  id: number;
  display_name: string;
  username: string;
  watched_count: number;
  current_streak: number;
}

export interface PlayerDetail {
  id: number;
  display_name: string;
  username: string;
  watches: VideoWatch[];
  training_logs: TrainingLog[];
}

export interface CoachVideoInput {
  title: string;
  category: string;
  video_url: string;
  video_start_seconds?: number | null;
  assigned_teams?: number[];
  assigned_players?: number[];
}

export interface CoachVideo {
  id: number;
  title: string;
  category: string;
  description: string;
  video_url: string;
  video_start_seconds: number | null;
  status: 'draft' | 'published' | 'unavailable';
  created_by: number | null;
  created_at: string;
  assigned_teams: number[];
  assigned_players: number[];
}

export interface CoachTeam {
  id: number;
  name: string;
}
