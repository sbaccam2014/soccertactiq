import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { fetchProgress } from '../api/content';
import type { AttemptSummary } from '../types';
import { Card, EmptyState, ErrorState, LoadingState } from '../components/ui';

export function ProgressPage() {
  const [attempts, setAttempts] = useState<AttemptSummary[]>([]);
  const [state, setState] = useState<'loading' | 'error' | 'ready'>('loading');

  async function load() {
    setState('loading');
    try {
      const page = await fetchProgress();
      setAttempts(page.results);
      setState('ready');
    } catch {
      setState('error');
    }
  }

  useEffect(() => {
    load();
  }, []);

  if (state === 'loading') return <LoadingState label="Loading your progress…" />;
  if (state === 'error') {
    return <ErrorState message="Couldn't load your progress." onRetry={load} />;
  }

  return (
    <div className="flex flex-col gap-4">
      <h1 className="text-2xl font-bold text-[var(--soccermind-pitch-700)]">My Progress</h1>

      {attempts.length === 0 ? (
        <EmptyState>You haven't completed a lesson yet. Pick one from Lessons to start.</EmptyState>
      ) : (
        <ul className="flex flex-col gap-3">
          {attempts.map((attempt) => (
            <li key={attempt.id}>
              <Link to={`/attempts/${attempt.id}`} className="block">
                <Card className="transition active:scale-[0.99]">
                  <div className="flex items-center justify-between gap-3">
                    <div>
                      <h2 className="font-semibold text-[var(--soccermind-text)]">
                        {attempt.lesson_title_snapshot}
                      </h2>
                      <p className="text-sm text-[var(--soccermind-text-muted)]">
                        {new Date(attempt.submitted_at).toLocaleDateString(undefined, {
                          year: 'numeric',
                          month: 'short',
                          day: 'numeric',
                        })}
                      </p>
                    </div>
                    <span className="shrink-0 rounded-full bg-[var(--soccermind-pitch-100)] px-2.5 py-1 text-xs font-semibold text-[var(--soccermind-pitch-700)]">
                      {attempt.correct_count}/{attempt.question_count}
                    </span>
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
