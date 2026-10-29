import { buildYoutubeEmbedUrl, buildYoutubeLink } from '../lib/youtube';

interface VideoLike {
  video_url: string;
  video_start_seconds: number | null;
}

/**
 * An inline YouTube embed (via youtube.com/embed/, YouTube's own
 * official embed endpoint — not a scrape, download, or proxy) with a
 * small "Open on YouTube" fallback link underneath for fullscreen,
 * the YouTube app, or when the video can't be identified for
 * embedding (e.g. the seed data's PLACEHOLDER value).
 */
export function VideoPlayer({ video, title }: { video: VideoLike; title: string }) {
  const embedUrl = buildYoutubeEmbedUrl(video);
  const watchUrl = buildYoutubeLink(video);

  return (
    <div className="flex flex-col gap-2">
      {embedUrl ? (
        <div className="aspect-video w-full overflow-hidden rounded-lg bg-black">
          <iframe
            className="h-full w-full"
            src={embedUrl}
            title={title}
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
            allowFullScreen
          />
        </div>
      ) : (
        <p className="text-sm text-[var(--soccertactiq-text-muted)]">
          This video can't be embedded — use the link below to watch it.
        </p>
      )}
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
