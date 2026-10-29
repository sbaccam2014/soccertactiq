/**
 * Builds the ordinary YouTube link we send the player to, adding a
 * start-time query param when specified. Used for the "Open on
 * YouTube" fallback link — never embed, fetch, or proxy the video
 * ourselves beyond YouTube's own official embed player (see
 * buildYoutubeEmbedUrl below). Works for both full Lessons and the
 * simpler CategoryVideo library, which share this video_url +
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

/**
 * Extracts the 11-character YouTube video ID from any of the formats
 * the backend allowlists (youtube.com/watch?v=, youtube.com/embed/,
 * youtube.com/shorts/, youtu.be/). Returns null if the URL doesn't
 * match a recognized format, in which case callers should fall back
 * to the plain link instead of attempting to embed.
 */
export function extractYoutubeVideoId(videoUrl: string): string | null {
  try {
    const url = new URL(videoUrl);
    if (url.hostname === 'youtu.be') {
      return url.pathname.slice(1) || null;
    }
    if (url.hostname === 'www.youtube.com' || url.hostname === 'youtube.com') {
      if (url.pathname === '/watch') {
        return url.searchParams.get('v');
      }
      const embedMatch = url.pathname.match(/^\/embed\/([\w-]+)/);
      if (embedMatch) return embedMatch[1];
      const shortsMatch = url.pathname.match(/^\/shorts\/([\w-]+)/);
      if (shortsMatch) return shortsMatch[1];
    }
    return null;
  } catch {
    return null;
  }
}

/**
 * Builds a youtube.com/embed/ URL — YouTube's own official embed
 * endpoint, the sanctioned way to show a player inline — for use in an
 * <iframe>. Returns null if the video's URL doesn't yield a
 * recognizable video ID (e.g. the seed data's PLACEHOLDER value),
 * in which case callers should show the "Open on YouTube" link only.
 */
export function buildYoutubeEmbedUrl(video: {
  video_url: string;
  video_start_seconds: number | null;
}): string | null {
  const videoId = extractYoutubeVideoId(video.video_url);
  if (!videoId) return null;
  const embedUrl = new URL(`https://www.youtube.com/embed/${videoId}`);
  if (video.video_start_seconds != null) {
    embedUrl.searchParams.set('start', String(video.video_start_seconds));
  }
  return embedUrl.toString();
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
