import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { fetchVideoCategories, fetchVideos, markVideoWatched } from '../api/content';
import type { VideoListItem } from '../types';
import { Card, EmptyState, ErrorState, IconTile, LoadingState, PageHeader } from '../components/ui';
import { VideoIcon } from '../components/icons';

type LoadState = 'loading' | 'error' | 'ready';

export function VideosPage() {
  const [categories, setCategories] = useState<string[]>([]);
  const [categoriesState, setCategoriesState] = useState<LoadState>('loading');
  const [selected, setSelected] = useState<string | null>(null);

  const [videos, setVideos] = useState<VideoListItem[]>([]);
  const [videosState, setVideosState] = useState<LoadState>('loading');

  async function loadCategories() {
    setCategoriesState('loading');
    try {
      const result = await fetchVideoCategories();
      setCategories(result);
      setSelected((current) => current ?? result[0] ?? null);
      setCategoriesState('ready');
    } catch {
      setCategoriesState('error');
    }
  }

  async function loadVideos(category: string) {
    setVideosState('loading');
    try {
      const page = await fetchVideos(category);
      setVideos(page.results);
      setVideosState('ready');
    } catch {
      setVideosState('error');
    }
  }

  useEffect(() => {
    loadCategories();
  }, []);

  useEffect(() => {
    if (selected) loadVideos(selected);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selected]);

  if (categoriesState === 'loading') return <LoadingState label="Loading videos…" />;
  if (categoriesState === 'error') {
    return <ErrorState message="Couldn't load videos." onRetry={loadCategories} />;
  }

  return (
    <div className="flex flex-col gap-4">
      <PageHeader icon={<VideoIcon />}>Videos</PageHeader>

      {categories.length === 0 ? (
        <EmptyState>No videos are published yet. Check back soon.</EmptyState>
      ) : (
        <>
          <div
            role="tablist"
            aria-label="Video category"
            className="-mx-4 flex gap-2 overflow-x-auto px-4 pb-1"
          >
            {categories.map((category) => (
              <button
                key={category}
                role="tab"
                aria-selected={selected === category}
                onClick={() => setSelected(category)}
                className={`min-h-11 shrink-0 whitespace-nowrap rounded-full px-4 text-sm font-semibold transition ${
                  selected === category
                    ? 'bg-[var(--soccertactiq-pitch-500)] text-white'
                    : 'bg-[var(--soccertactiq-pitch-100)] text-[var(--soccertactiq-text-muted)]'
                }`}
              >
                {category}
              </button>
            ))}
          </div>

          {videosState === 'loading' && <LoadingState label="Loading videos…" />}
          {videosState === 'error' && selected && (
            <ErrorState message="Couldn't load videos." onRetry={() => loadVideos(selected)} />
          )}
          {videosState === 'ready' && videos.length === 0 && (
            <EmptyState>No videos yet in this category. Check back soon.</EmptyState>
          )}
          {videosState === 'ready' && videos.length > 0 && (
            <ul className="flex flex-col gap-3">
              {videos.map((video) => (
                <li key={video.id}>
                  <Link
                    to={`/videos/${video.id}`}
                    className="block"
                    onClick={() => {
                      // Opening a video from this list is itself "watching"
                      // it. Fire-and-forget: navigation isn't blocked on
                      // this, and VideosPage/ProgressPage re-fetch fresh
                      // watched state on their own next load.
                      markVideoWatched(video.id).catch(() => {});
                    }}
                  >
                    <Card className="transition active:scale-[0.99]">
                      <div className="flex items-start gap-3">
                        <IconTile size="sm">
                          <VideoIcon />
                        </IconTile>
                        <div className="flex flex-1 items-start justify-between gap-3">
                          <div>
                            <h2 className="font-semibold text-[var(--soccertactiq-text)]">{video.title}</h2>
                            <p
                              className={`mt-1 text-sm text-[var(--soccertactiq-text-muted)] ${
                                video.description ? '' : 'italic'
                              }`}
                            >
                              {video.description || 'No description available.'}
                            </p>
                          </div>
                          <VideoStatusBadge video={video} />
                        </div>
                      </div>
                    </Card>
                  </Link>
                </li>
              ))}
            </ul>
          )}
        </>
      )}
    </div>
  );
}

function VideoStatusBadge({ video }: { video: VideoListItem }) {
  if (!video.is_watched) {
    return (
      <span className="shrink-0 rounded-full bg-[var(--soccertactiq-pitch-100)] px-2.5 py-1 text-xs font-semibold text-[var(--soccertactiq-pitch-700)]">
        New
      </span>
    );
  }
  return (
    <span className="shrink-0 rounded-full bg-[var(--soccertactiq-success-bg)] px-2.5 py-1 text-xs font-semibold text-[var(--soccertactiq-success)]">
      Watched
    </span>
  );
}
