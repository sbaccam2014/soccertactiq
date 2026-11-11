import { api } from './client';
import type { Paginated, VideoDetail, VideoListItem, VideoWatch } from '../types';

export async function fetchVideos(category?: string): Promise<Paginated<VideoListItem>> {
  const query = category ? `?category=${encodeURIComponent(category)}` : '';
  return api.get<Paginated<VideoListItem>>(`/api/videos/${query}`);
}

export async function fetchVideo(id: number): Promise<VideoDetail> {
  return api.get<VideoDetail>(`/api/videos/${id}/`);
}

export async function fetchAssignedVideos(): Promise<Paginated<VideoListItem>> {
  return api.get<Paginated<VideoListItem>>('/api/videos/assigned/');
}

export async function markVideoWatched(videoId: number): Promise<VideoWatch> {
  return api.post<VideoWatch>(`/api/videos/${videoId}/watch/`);
}

export async function fetchProgress(): Promise<Paginated<VideoWatch>> {
  return api.get<Paginated<VideoWatch>>('/api/progress/');
}

export async function fetchVideoCategories(): Promise<string[]> {
  return api.get<string[]>('/api/video-categories/');
}
