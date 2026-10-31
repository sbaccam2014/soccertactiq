import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { fetchVideos } from '../api/content';
import type { VideoListItem } from '../types';
import { Card, EmptyState, ErrorState, LoadingState } from '../components/ui';

type LoadState = 'loading' | 'error' | 'ready';

export function VideosPage() {
  const [videos, setVideos] = useState<VideoListItem[]>([]);
  const [state, setState] = useState<LoadState>('loading');

  async function load() {
    setState('loading');
    try {
      const page = await fetchVideos();
      setVideos(page.results);
      setState('ready');
    } catch {
      setState('error');
    }
  }

  useEffect(() => {
    load();
  }, []);

  if (state === 'loading') return <LoadingState label="Loading videos…" />;
  if (state === 'error') {
    return <ErrorState message="Couldn't load videos." onRetry={load} />;
  }

  return (
    <div className="flex flex-col gap-4">
      <h1 className="text-2xl font-bold text-[var(--soccertactiq-pitch-700)]">Videos & Questions</h1>

      {videos.length === 0 ? (
        <EmptyState>No videos are published yet. Check back soon.</EmptyState>
      ) : (
        <ul className="flex flex-col gap-3">
          {videos.map((video) => (
            <li key={video.id}>
              <Link to={`/videos-questions/${video.id}`} className="block">
                <Card className="transition active:scale-[0.99]">
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <h2 className="font-semibold text-[var(--soccertactiq-text)]">{video.title}</h2>
                      <p className="mt-1 text-sm text-[var(--soccertactiq-text-muted)]">
                        {video.description}
                      </p>
                    </div>
                    <VideoStatusBadge video={video} />
                  </div>
                </Card>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

function VideoStatusBadge({ video }: { video: VideoListItem }) {
  if (!video.is_completed) {
    return (
      <span className="shrink-0 rounded-full bg-[var(--soccertactiq-pitch-100)] px-2.5 py-1 text-xs font-semibold text-[var(--soccertactiq-pitch-700)]">
        New
      </span>
    );
  }
  return (
    <span className="shrink-0 rounded-full bg-[var(--soccertactiq-success-bg)] px-2.5 py-1 text-xs font-semibold text-[var(--soccertactiq-success)]">
      {Math.round(Number(video.latest_score))}%
    </span>
  );
}
