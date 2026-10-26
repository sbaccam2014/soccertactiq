import { api } from './client';
import type {
  AnswerSubmission,
  AttemptResult,
  AttemptSummary,
  CategoryVideo,
  LessonDetail,
  LessonListItem,
  Paginated,
} from '../types';

export async function fetchLessons(): Promise<Paginated<LessonListItem>> {
  return api.get<Paginated<LessonListItem>>('/api/lessons/');
}

export async function fetchLesson(id: number): Promise<LessonDetail> {
  return api.get<LessonDetail>(`/api/lessons/${id}/`);
}

export async function submitAttempt(
  lessonId: number,
  idempotencyKey: string,
  answers: AnswerSubmission[],
): Promise<AttemptResult> {
  return api.post<AttemptResult>(`/api/lessons/${lessonId}/attempts/`, {
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
