import { useEffect, useState } from 'react';
import { fetchCategoryVideos, fetchVideoCategories } from '../api/content';
import { formatTimestampGuidance } from '../lib/youtube';
import type { CategoryVideo } from '../types';
import { Card, EmptyState, ErrorState, LoadingState } from '../components/ui';
import { VideoPlayer } from '../components/VideoPlayer';

type LoadState = 'loading' | 'error' | 'ready';

export function VideoLibraryPage() {
  const [categories, setCategories] = useState<string[]>([]);
  const [categoriesState, setCategoriesState] = useState<LoadState>('loading');
  const [selected, setSelected] = useState<string | null>(null);

  const [videos, setVideos] = useState<CategoryVideo[]>([]);
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
      const page = await fetchCategoryVideos(category);
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

  if (categoriesState === 'loading') return <LoadingState label="Loading categories…" />;
  if (categoriesState === 'error') {
    return <ErrorState message="Couldn't load video categories." onRetry={loadCategories} />;
  }

  return (
    <div className="flex flex-col gap-4">
      <h1 className="text-2xl font-bold text-[var(--soccertactiq-pitch-700)]">Video Library</h1>

      {categories.length === 0 ? (
        <EmptyState>No videos are published yet. Check back soon.</EmptyState>
      ) : (
        <>
          <div
            role="tablist"
            aria-label="Video category"
            className="flex flex-wrap gap-2 rounded-lg bg-[var(--soccertactiq-pitch-100)] p-1"
          >
            {categories.map((category) => (
              <button
                key={category}
                role="tab"
                aria-selected={selected === category}
                onClick={() => setSelected(category)}
                className={`min-h-11 flex-1 rounded-md px-3 text-sm font-semibold transition ${
                  selected === category
                    ? 'bg-[var(--soccertactiq-surface)] text-[var(--soccertactiq-pitch-700)] shadow-sm'
                    : 'text-[var(--soccertactiq-text-muted)]'
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
              {videos.map((video) => {
                const timestampGuidance = formatTimestampGuidance(video);
                return (
                  <li key={video.id}>
                    <Card>
                      <h2 className="font-semibold text-[var(--soccertactiq-text)]">
                        {video.title}
                      </h2>
                      {video.description && (
                        <p className="mt-1 mb-3 text-sm text-[var(--soccertactiq-text-muted)]">
                          {video.description}
                        </p>
                      )}
                      <div className="mt-3">
                        <VideoPlayer video={video} title={video.title} />
                      </div>
                      {timestampGuidance && (
                        <p className="mt-2 text-xs text-[var(--soccertactiq-text-muted)]">
                          {timestampGuidance}
                        </p>
                      )}
                    </Card>
                  </li>
                );
              })}
            </ul>
          )}
        </>
      )}
    </div>
  );
}
