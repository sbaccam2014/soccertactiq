import { api } from './client';
import type {
  AnswerSubmission,
  AttemptResult,
  AttemptSummary,
  CategoryVideo,
  Paginated,
  VideoDetail,
  VideoListItem,
} from '../types';

export async function fetchVideos(): Promise<Paginated<VideoListItem>> {
  return api.get<Paginated<VideoListItem>>('/api/videos/');
}

export async function fetchVideo(id: number): Promise<VideoDetail> {
  return api.get<VideoDetail>(`/api/videos/${id}/`);
}

export async function submitAttempt(
  videoId: number,
  idempotencyKey: string,
  answers: AnswerSubmission[],
): Promise<AttemptResult> {
  return api.post<AttemptResult>(`/api/videos/${videoId}/attempts/`, {
    idempotency_key: idempotencyKey,
    answers,
  });
}

export async function fetchAttempt(id: number): Promise<AttemptResult> {
  return api.get<AttemptResult>(`/api/attempts/${id}/`);
}

export async function fetchProgress(): Promise<Paginated<AttemptSummary>> {
  return api.get<Paginated<AttemptSummary>>('/api/progress/');
}

export async function fetchVideoCategories(): Promise<string[]> {
  return api.get<string[]>('/api/video-categories/');
}

export async function fetchCategoryVideos(
  category?: string,
): Promise<Paginated<CategoryVideo>> {
  const query = category ? `?category=${encodeURIComponent(category)}` : '';
  return api.get<Paginated<CategoryVideo>>(`/api/category-videos/${query}`);
}
