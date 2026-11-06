import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { fetchVideoCategories, fetchVideos } from '../api/content';
import type { VideoListItem } from '../types';
import { Card, EmptyState, ErrorState, IconTile, LoadingState, PageHeader } from '../components/ui';
import { CheckIcon, ChartIcon } from '../components/icons';

const ALL_TAB = 'All';

type LoadState = 'loading' | 'error' | 'ready';

export function ProgressPage() {
  const [categories, setCategories] = useState<string[]>([]);
  const [categoriesState, setCategoriesState] = useState<LoadState>('loading');
  const [selected, setSelected] = useState<string>(ALL_TAB);

  const [videos, setVideos] = useState<VideoListItem[]>([]);
  const [videosState, setVideosState] = useState<LoadState>('loading');

  async function loadCategories() {
    setCategoriesState('loading');
    try {
      setCategories(await fetchVideoCategories());
      setCategoriesState('ready');
    } catch {
      setCategoriesState('error');
    }
  }

  async function loadVideos(category: string) {
    setVideosState('loading');
    try {
      const page = await fetchVideos(category === ALL_TAB ? undefined : category);
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
    loadVideos(selected);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selected]);

  if (categoriesState === 'loading') return <LoadingState label="Loading your progress…" />;
  if (categoriesState === 'error') {
    return <ErrorState message="Couldn't load your progress." onRetry={loadCategories} />;
  }

  const watched = videos.filter((v) => v.is_watched);
  const tabs = [ALL_TAB, ...categories];

  return (
    <div className="flex flex-col gap-4">
      <PageHeader icon={<ChartIcon />}>My Progress</PageHeader>

      {categories.length === 0 ? (
        <EmptyState>No videos are published yet. Check back soon.</EmptyState>
      ) : (
        <>
          <div
            role="tablist"
            aria-label="Video category"
            className="-mx-4 flex gap-2 overflow-x-auto px-4 pb-1"
          >
            {tabs.map((tab) => (
              <button
                key={tab}
                role="tab"
                aria-selected={selected === tab}
                onClick={() => setSelected(tab)}
                className={`min-h-11 shrink-0 whitespace-nowrap rounded-full px-4 text-sm font-semibold transition ${
                  selected === tab
                    ? 'bg-[var(--soccertactiq-pitch-500)] text-white'
                    : 'bg-[var(--soccertactiq-pitch-100)] text-[var(--soccertactiq-text-muted)]'
                }`}
              >
                {tab}
              </button>
            ))}
          </div>

          {videosState === 'loading' && <LoadingState label="Loading…" />}
          {videosState === 'error' && (
            <ErrorState message="Couldn't load your progress." onRetry={() => loadVideos(selected)} />
          )}
          {videosState === 'ready' && watched.length === 0 && (
            <EmptyState>
              No videos watched yet{selected !== ALL_TAB ? ` in ${selected}` : ''}.
            </EmptyState>
          )}
          {videosState === 'ready' && watched.length > 0 && (
            <>
              <p className="text-sm font-semibold text-[var(--soccertactiq-text-muted)]">
                {watched.length} video{watched.length === 1 ? '' : 's'} watched
              </p>
              <ul className="flex flex-col gap-3">
                {watched.map((video) => (
                  <li key={video.id}>
                    <Link to={`/videos/${video.id}`} className="block">
                      <Card className="transition active:scale-[0.99]">
                        <div className="flex items-center gap-3">
                          <IconTile size="sm">
                            <CheckIcon />
                          </IconTile>
                          <div className="flex flex-1 items-center justify-between gap-3">
                            <h2 className="font-semibold text-[var(--soccertactiq-text)]">
                              {video.title}
                            </h2>
                            <span className="shrink-0 rounded-full bg-[var(--soccertactiq-pitch-100)] px-2.5 py-1 text-xs font-semibold text-[var(--soccertactiq-pitch-700)]">
                              {video.category}
                            </span>
                          </div>
                        </div>
                      </Card>
                    </Link>
                  </li>
                ))}
              </ul>
            </>
          )}
        </>
      )}
    </div>
  );
}
