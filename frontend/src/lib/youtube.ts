/**
 * Builds the ordinary YouTube link we send the player to, adding a
 * start-time query param when specified. This is the only way the app
 * links to a video's actual playback — never embedded, fetched, or
 * proxied (an inline youtube.com/embed/ player was tried and dropped:
 * a meaningful share of these Shorts have embedding disabled by their
 * uploader, confirmed directly against YouTube independent of this
 * app, so it failed unpredictably). Works for both full Lessons and
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
 * Builds a youtube.com/shorts/ URL for an extracted video ID — used to
 * tell Shorts (vertical, 9:16) apart from ordinary (horizontal, 16:9)
 * videos so the player can size itself appropriately instead of
 * stretching a vertical clip into a mostly-empty landscape box.
 */
export function isYoutubeShorts(videoUrl: string): boolean {
  try {
    return new URL(videoUrl).pathname.startsWith('/shorts/');
  } catch {
    return false;
  }
}

/**
 * Builds a YouTube thumbnail image URL from i.ytimg.com — YouTube's
 * own public thumbnail CDN (the same images youtube.com itself serves
 * for video previews), not a scrape or a locally-cached copy. Used so
 * the Video Library and Lesson screens can show a lightweight preview
 * image instead of loading 30+ iframes at once; the actual player only
 * loads once a viewer taps to play (see VideoPlayer).
 */
export function buildYoutubeThumbnailUrl(videoUrl: string): string | null {
  const videoId = extractYoutubeVideoId(videoUrl);
  if (!videoId) return null;
  return `https://i.ytimg.com/vi/${videoId}/hqdefault.jpg`;
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
