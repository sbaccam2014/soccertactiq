import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { fetchAssignedPlayers } from '../api/coach';
import type { AssignedPlayer } from '../types';
import { Card, EmptyState, ErrorState, IconTile, LoadingState, PageHeader } from '../components/ui';
import { AddVideoIcon, FlameIcon, PeopleIcon, PersonIcon } from '../components/icons';

type LoadState = 'loading' | 'error' | 'ready';

export function CoachDashboardPage() {
  const [players, setPlayers] = useState<AssignedPlayer[]>([]);
  const [state, setState] = useState<LoadState>('loading');

  async function load() {
    setState('loading');
    try {
      setPlayers(await fetchAssignedPlayers());
      setState('ready');
    } catch {
      setState('error');
    }
  }

  useEffect(() => {
    load();
  }, []);

  if (state === 'loading') return <LoadingState label="Loading your players…" />;
  if (state === 'error') {
    return <ErrorState message="Couldn't load your players." onRetry={load} />;
  }

  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <PageHeader icon={<PeopleIcon />}>My Players</PageHeader>
        <Link
          to="/coach/videos/new"
          className="flex min-h-11 items-center gap-1.5 rounded-full bg-[var(--soccertactiq-pitch-500)] px-3 py-2 text-sm font-semibold text-white"
        >
          <AddVideoIcon className="h-4 w-4" />
          Add Video
        </Link>
      </div>

      {players.length === 0 ? (
        <EmptyState>No players assigned to you yet. Ask an admin to assign players.</EmptyState>
      ) : (
        <ul className="flex flex-col gap-3">
          {players.map((player) => (
            <li key={player.id}>
              <Link to={`/coach/players/${player.id}`} className="block">
                <Card className="transition active:scale-[0.99]">
                  <div className="flex items-center gap-3">
                    <IconTile size="sm">
                      <PersonIcon />
                    </IconTile>
                    <div className="flex flex-1 items-center justify-between gap-3">
                      <div>
                        <h2 className="font-semibold text-[var(--soccertactiq-text)]">
                          {player.display_name}
                        </h2>
                        <p className="mt-1 text-sm text-[var(--soccertactiq-text-muted)]">
                          {player.watched_count} video{player.watched_count === 1 ? '' : 's'} watched
                        </p>
                      </div>
                      {player.current_streak > 0 && (
                        <span className="flex shrink-0 items-center gap-1 rounded-full bg-[var(--soccertactiq-pitch-100)] px-2.5 py-1 text-xs font-semibold text-[var(--soccertactiq-pitch-700)]">
                          <FlameIcon className="h-3.5 w-3.5 text-[var(--soccertactiq-accent-500)]" />
                          {player.current_streak}
                        </span>
                      )}
                    </div>
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
