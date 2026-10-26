import { useEffect, useState } from 'react';
import { fetchPositionVideos } from '../api/content';
import { buildYoutubeLink, formatTimestampGuidance } from '../lib/youtube';
import type { Position, PositionVideo } from '../types';
import { Card, EmptyState, ErrorState, LoadingState } from '../components/ui';

type LoadState = 'loading' | 'error' | 'ready';

const POSITIONS: { value: Position; label: string }[] = [
  { value: 'fullback', label: 'Fullback' },
  { value: 'midfielder', label: 'Midfielder' },
  { value: 'forward', label: 'Forward' },
];

export function PositionsPage() {
  const [selected, setSelected] = useState<Position>('fullback');
  const [videos, setVideos] = useState<PositionVideo[]>([]);
  const [state, setState] = useState<LoadState>('loading');

  async function load(position: Position) {
    setState('loading');
    try {
      const page = await fetchPositionVideos(position);
      setVideos(page.results);
      setState('ready');
    } catch {
      setState('error');
    }
  }

  useEffect(() => {
    load(selected);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selected]);

  return (
    <div className="flex flex-col gap-4">
      <h1 className="text-2xl font-bold text-[var(--soccertactiq-pitch-700)]">By Position</h1>

      <div
        role="tablist"
        aria-label="Playing position"
        className="flex gap-2 rounded-lg bg-[var(--soccertactiq-pitch-100)] p-1"
      >
        {POSITIONS.map((position) => (
          <button
            key={position.value}
            role="tab"
            aria-selected={selected === position.value}
            onClick={() => setSelected(position.value)}
            className={`min-h-11 flex-1 rounded-md text-sm font-semibold transition ${
              selected === position.value
                ? 'bg-[var(--soccertactiq-surface)] text-[var(--soccertactiq-pitch-700)] shadow-sm'
                : 'text-[var(--soccertactiq-text-muted)]'
            }`}
          >
            {position.label}
          </button>
        ))}
      </div>

      {state === 'loading' && <LoadingState label="Loading videos…" />}
      {state === 'error' && (
        <ErrorState message="Couldn't load videos." onRetry={() => load(selected)} />
      )}
      {state === 'ready' && videos.length === 0 && (
        <EmptyState>No videos yet for this position. Check back soon.</EmptyState>
      )}
      {state === 'ready' && videos.length > 0 && (
        <ul className="flex flex-col gap-3">
          {videos.map((video) => {
            const timestampGuidance = formatTimestampGuidance(video);
            return (
              <li key={video.id}>
                <Card>
                  <h2 className="font-semibold text-[var(--soccertactiq-text)]">{video.title}</h2>
                  {video.description && (
                    <p className="mt-1 text-sm text-[var(--soccertactiq-text-muted)]">
                      {video.description}
                    </p>
                  )}
                  <a
                    href={buildYoutubeLink(video)}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="mt-3 flex min-h-11 items-center justify-center rounded-lg border-2 border-[var(--soccertactiq-pitch-500)] px-4 text-center text-sm font-semibold text-[var(--soccertactiq-pitch-600)]"
                  >
                    Watch on YouTube ↗
                  </a>
                  {timestampGuidance && (
                    <p className="mt-2 text-center text-xs text-[var(--soccertactiq-text-muted)]">
                      {timestampGuidance}
                    </p>
                  )}
                </Card>
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}
