import type { LessonDetail } from '../types';

/**
 * Builds the ordinary YouTube link we send the player to, adding a
 * start-time query param when the lesson specifies one. We only ever
 * open the official youtube.com/youtu.be link in a new tab — never
 * embed, fetch, or proxy the video ourselves.
 */
export function buildYoutubeLink(lesson: LessonDetail): string {
  if (lesson.video_start_seconds == null) {
    return lesson.video_url;
  }
  const url = new URL(lesson.video_url);
  url.searchParams.set('t', `${lesson.video_start_seconds}s`);
  return url.toString();
}

export function formatTimestampGuidance(lesson: LessonDetail): string | null {
  const { video_start_seconds, video_end_seconds } = lesson;
  if (video_start_seconds == null && video_end_seconds == null) return null;

  const format = (totalSeconds: number) => {
    const minutes = Math.floor(totalSeconds / 60);
    const seconds = totalSeconds % 60;
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
  };

  if (video_start_seconds != null && video_end_seconds != null) {
    return `Watch from ${format(video_start_seconds)} to ${format(video_end_seconds)}.`;
  }
  if (video_start_seconds != null) {
    return `Watch from ${format(video_start_seconds)}.`;
  }
  return `Watch until ${format(video_end_seconds!)}.`;
}
