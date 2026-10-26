/**
 * Builds the ordinary YouTube link we send the player to, adding a
 * start-time query param when specified. We only ever open the
 * official youtube.com/youtu.be link in a new tab — never embed,
 * fetch, or proxy the video ourselves. Works for both full Lessons and
 * the simpler CategoryVideo library, which share this video_url +
 * video_start_seconds shape.
 */
export function buildYoutubeLink(video: {
  video_url: string;
  video_start_seconds: number | null;
}): string {
  if (video.video_start_seconds == null) {
    return video.video_url;
  }
  const url = new URL(video.video_url);
  url.searchParams.set('t', `${video.video_start_seconds}s`);
  return url.toString();
}

export function formatTimestampGuidance(video: {
  video_start_seconds: number | null;
  video_end_seconds?: number | null;
}): string | null {
  const video_start_seconds = video.video_start_seconds;
  const video_end_seconds = video.video_end_seconds ?? null;
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
