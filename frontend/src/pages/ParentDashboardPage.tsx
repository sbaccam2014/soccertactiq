import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { fetchLinkedChildren } from '../api/parent';
import type { AssignedPlayer } from '../types';
import { Card, EmptyState, ErrorState, IconTile, LoadingState, PageHeader } from '../components/ui';
import { FlameIcon, PeopleIcon, PersonIcon } from '../components/icons';

type LoadState = 'loading' | 'error' | 'ready';

export function ParentDashboardPage() {
  const [children, setChildren] = useState<AssignedPlayer[]>([]);
  const [state, setState] = useState<LoadState>('loading');

  async function load() {
    setState('loading');
    try {
      setChildren(await fetchLinkedChildren());
      setState('ready');
    } catch {
      setState('error');
    }
  }

  useEffect(() => {
    load();
  }, []);

  if (state === 'loading') return <LoadingState label="Loading your kids…" />;
  if (state === 'error') {
    return <ErrorState message="Couldn't load your kids." onRetry={load} />;
  }

  return (
    <div className="flex flex-col gap-4">
      <PageHeader icon={<PeopleIcon />}>My Kids</PageHeader>

      {children.length === 0 ? (
        <EmptyState>No kids linked to your account yet. Ask an admin to link them.</EmptyState>
      ) : (
        <ul className="flex flex-col gap-3">
          {children.map((child) => (
            <li key={child.id}>
              <Link to={`/parent/children/${child.id}`} className="block">
                <Card className="transition active:scale-[0.99]">
                  <div className="flex items-center gap-3">
                    <IconTile size="sm">
                      <PersonIcon />
                    </IconTile>
                    <div className="flex flex-1 items-center justify-between gap-3">
                      <div>
                        <h2 className="font-semibold text-[var(--soccertactiq-text)]">
                          {child.display_name}
                        </h2>
                        <p className="mt-1 text-sm text-[var(--soccertactiq-text-muted)]">
                          {child.watched_count} video{child.watched_count === 1 ? '' : 's'} watched
                        </p>
                      </div>
                      {child.current_streak > 0 && (
                        <span className="flex shrink-0 items-center gap-1 rounded-full bg-[var(--soccertactiq-pitch-100)] px-2.5 py-1 text-xs font-semibold text-[var(--soccertactiq-pitch-700)]">
                          <FlameIcon className="h-3.5 w-3.5 text-[var(--soccertactiq-accent-500)]" />
                          {child.current_streak}
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
