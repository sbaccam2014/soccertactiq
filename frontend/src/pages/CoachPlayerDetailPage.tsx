import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { fetchPlayerDetail } from '../api/coach';
import type { PlayerDetail } from '../types';
import { Card, EmptyState, ErrorState, IconTile, LoadingState, PageHeader } from '../components/ui';
import { CheckIcon, PersonIcon, VideoIcon, XIcon } from '../components/icons';

type LoadState = 'loading' | 'error' | 'ready';

export function CoachPlayerDetailPage() {
  const { playerId } = useParams<{ playerId: string }>();
  const [player, setPlayer] = useState<PlayerDetail | null>(null);
  const [state, setState] = useState<LoadState>('loading');

  async function load() {
    setState('loading');
    try {
      setPlayer(await fetchPlayerDetail(Number(playerId)));
      setState('ready');
    } catch {
      setState('error');
    }
  }

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [playerId]);

  if (state === 'loading') return <LoadingState label="Loading player…" />;
  if (state === 'error' || !player) {
    return <ErrorState message="Couldn't load this player." onRetry={load} />;
  }

  return (
    <div className="flex flex-col gap-4">
      <PageHeader icon={<PersonIcon />}>{player.display_name}</PageHeader>

      <h2 className="text-lg font-semibold text-[var(--soccertactiq-text)]">Videos Watched</h2>
      {player.watches.length === 0 ? (
        <EmptyState>No videos watched yet.</EmptyState>
      ) : (
        <ul className="flex flex-col gap-2">
          {player.watches.map((watch) => (
            <li key={watch.id}>
              <Card className="flex items-center gap-3 py-2.5">
                <IconTile size="sm">
                  <VideoIcon />
                </IconTile>
                <div>
                  <p className="text-sm font-semibold text-[var(--soccertactiq-text)]">
                    {watch.video_title_snapshot}
                  </p>
                  <p className="text-xs text-[var(--soccertactiq-text-muted)]">
                    {new Date(watch.watched_at).toLocaleDateString(undefined, {
                      weekday: 'short',
                      month: 'short',
                      day: 'numeric',
                    })}
                  </p>
                </div>
              </Card>
            </li>
          ))}
        </ul>
      )}

      <h2 className="text-lg font-semibold text-[var(--soccertactiq-text)]">Training Log</h2>
      {player.training_logs.length === 0 ? (
        <EmptyState>No training logged yet.</EmptyState>
      ) : (
        <ul className="flex flex-col gap-2">
          {player.training_logs.map((log) => (
            <li key={log.id}>
              <Card className="flex items-center justify-between py-2.5">
                <div className="flex items-center gap-3">
                  <IconTile size="sm" tone={log.trained ? 'pitch' : 'neutral'}>
                    {log.trained ? <CheckIcon /> : <XIcon />}
                  </IconTile>
                  <span className="text-sm text-[var(--soccertactiq-text)]">
                    {new Date(log.date + 'T00:00:00').toLocaleDateString(undefined, {
                      weekday: 'short',
                      month: 'short',
                      day: 'numeric',
                    })}
                  </span>
                </div>
                <span
                  className={`text-sm font-semibold ${
                    log.trained
                      ? 'text-[var(--soccertactiq-success)]'
                      : 'text-[var(--soccertactiq-text-muted)]'
                  }`}
                >
                  {log.trained ? 'Trained' : 'Not logged'}
                </span>
              </Card>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
