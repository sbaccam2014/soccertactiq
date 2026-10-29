import { useState } from 'react';
import {
  buildYoutubeEmbedUrl,
  buildYoutubeLink,
  buildYoutubeThumbnailUrl,
  isYoutubeShorts,
} from '../lib/youtube';

interface VideoLike {
  video_url: string;
  video_start_seconds: number | null;
}

/**
 * A compact YouTube preview: a thumbnail (from YouTube's own public
 * thumbnail CDN) with a play button overlay, sized appropriately for
 * Shorts (vertical, 9:16, capped narrow so it doesn't dominate the
 * screen) vs. ordinary videos (horizontal, 16:9, full card width).
 * Tapping it swaps in the actual youtube.com/embed/ player — loading
 * the iframe only on demand keeps a list of many videos light, and
 * means a video whose embedding is restricted still shows a usable
 * preview with a working "Open on YouTube" link, rather than an
 * always-loaded iframe showing an embed error.
 *
 * Some videos have embedding disabled by their uploader (YouTube's
 * own "Error 153 / Video player configuration error"), and that error
 * renders entirely inside YouTube's cross-origin iframe — there's no
 * JS event this page can catch to detect it automatically. Rather
 * than leave a dead-end error screen, the "Open on YouTube" link and
 * a "Back to preview" control stay visible right under the player at
 * all times once it's playing, so there's always a visible way out.
 */
export function VideoPlayer({ video, title }: { video: VideoLike; title: string }) {
  const [isPlaying, setIsPlaying] = useState(false);

  const embedUrl = buildYoutubeEmbedUrl(video);
  const thumbnailUrl = buildYoutubeThumbnailUrl(video.video_url);
  const watchUrl = buildYoutubeLink(video);
  const isShorts = isYoutubeShorts(video.video_url);

  // Shorts are vertical (9:16) and read better capped at a modest
  // width than stretched to the full card; ordinary videos use the
  // full card width at their native 16:9.
  const frameClassName = isShorts
    ? 'relative mx-auto aspect-[9/16] w-full max-w-[220px] overflow-hidden rounded-lg bg-black'
    : 'relative aspect-video w-full overflow-hidden rounded-lg bg-black';

  if (!embedUrl || !thumbnailUrl) {
    return (
      <div className="flex flex-col gap-2">
        <p className="text-sm text-[var(--soccertactiq-text-muted)]">
          This video can't be previewed — use the link below to watch it.
        </p>
        <a
          href={watchUrl}
          target="_blank"
          rel="noopener noreferrer"
          className="self-start text-sm font-semibold text-[var(--soccertactiq-pitch-600)]"
        >
          Open on YouTube ↗
        </a>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-2">
      <div className={frameClassName}>
        {isPlaying ? (
          <iframe
            className="h-full w-full"
            src={embedUrl}
            title={title}
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
            allowFullScreen
          />
        ) : (
          <button
            type="button"
            onClick={() => setIsPlaying(true)}
            className="group h-full w-full"
            aria-label={`Play ${title}`}
          >
            <img
              src={thumbnailUrl}
              alt=""
              className="h-full w-full object-cover"
              loading="lazy"
            />
            <span className="absolute inset-0 flex items-center justify-center bg-black/20 transition group-hover:bg-black/30">
              <span className="flex h-12 w-12 items-center justify-center rounded-full bg-white/90 shadow-md">
                <svg viewBox="0 0 24 24" className="ml-0.5 h-6 w-6 fill-[var(--soccertactiq-pitch-700)]">
                  <path d="M8 5v14l11-7z" />
                </svg>
              </span>
            </span>
          </button>
        )}
      </div>
      <div className="flex items-center gap-3">
        <a
          href={watchUrl}
          target="_blank"
          rel="noopener noreferrer"
          className="text-sm font-semibold text-[var(--soccertactiq-pitch-600)]"
        >
          Open on YouTube ↗
        </a>
        {isPlaying && (
          <button
            type="button"
            onClick={() => setIsPlaying(false)}
            className="text-sm text-[var(--soccertactiq-text-muted)] underline"
          >
            Back to preview
          </button>
        )}
      </div>
      {isPlaying && (
        <p className="text-xs text-[var(--soccertactiq-text-muted)]">
          Video not playing? Some videos can only be watched on YouTube directly — use the
          link above.
        </p>
      )}
    </div>
  );
}
