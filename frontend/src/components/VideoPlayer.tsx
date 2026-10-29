import { buildYoutubeLink, buildYoutubeThumbnailUrl, isYoutubeShorts } from '../lib/youtube';

interface VideoLike {
  video_url: string;
  video_start_seconds: number | null;
}

/**
 * A compact YouTube preview: a thumbnail (from YouTube's own public
 * thumbnail CDN) with a play button overlay, sized appropriately for
 * Shorts (vertical, 9:16, capped narrow so it doesn't dominate the
 * screen) vs. ordinary videos (horizontal, 16:9, full card width).
 * Tapping it opens the video on YouTube in a new tab rather than
 * attempting an inline embed — many of the Shorts in this library
 * have embedding disabled by their uploader (YouTube's own "Error
 * 153 / Video player configuration error"), confirmed directly
 * against youtube.com/embed/ independent of this app, so an inline
 * player would fail unpredictably for a meaningful share of videos.
 * Opening on YouTube directly is reliable for all of them.
 */
export function VideoPlayer({ video, title }: { video: VideoLike; title: string }) {
  const thumbnailUrl = buildYoutubeThumbnailUrl(video.video_url);
  const watchUrl = buildYoutubeLink(video);
  const isShorts = isYoutubeShorts(video.video_url);

  // Shorts are vertical (9:16) and read better capped at a modest
  // width than stretched to the full card; ordinary videos use the
  // full card width at their native 16:9.
  const frameClassName = isShorts
    ? 'relative mx-auto aspect-[9/16] w-full max-w-[220px] overflow-hidden rounded-lg bg-black'
    : 'relative aspect-video w-full overflow-hidden rounded-lg bg-black';

  if (!thumbnailUrl) {
    return (
      <a
        href={watchUrl}
        target="_blank"
        rel="noopener noreferrer"
        className="self-start text-sm font-semibold text-[var(--soccertactiq-pitch-600)]"
      >
        Watch on YouTube ↗
      </a>
    );
  }

  return (
    <a
      href={watchUrl}
      target="_blank"
      rel="noopener noreferrer"
      className={`${frameClassName} block`}
      aria-label={`Watch ${title} on YouTube`}
    >
      <img src={thumbnailUrl} alt="" className="h-full w-full object-cover" loading="lazy" />
      <span className="absolute inset-0 flex items-center justify-center bg-black/20 transition hover:bg-black/30">
        <span className="flex h-12 w-12 items-center justify-center rounded-full bg-white/90 shadow-md">
          <svg viewBox="0 0 24 24" className="ml-0.5 h-6 w-6 fill-[var(--soccertactiq-pitch-700)]">
            <path d="M8 5v14l11-7z" />
          </svg>
        </span>
      </span>
    </a>
  );
}
