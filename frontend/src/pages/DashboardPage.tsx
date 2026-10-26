import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { fetchLessons } from '../api/content';
import type { LessonListItem } from '../types';
import { Card, EmptyState, ErrorState, LoadingState } from '../components/ui';

type LoadState = 'loading' | 'error' | 'ready';

export function DashboardPage() {
  const [lessons, setLessons] = useState<LessonListItem[]>([]);
  const [state, setState] = useState<LoadState>('loading');

  async function load() {
    setState('loading');
    try {
      const page = await fetchLessons();
      setLessons(page.results);
      setState('ready');
    } catch {
      setState('error');
    }
  }

  useEffect(() => {
    load();
  }, []);

  if (state === 'loading') return <LoadingState label="Loading lessons…" />;
  if (state === 'error') {
    return <ErrorState message="Couldn't load lessons." onRetry={load} />;
  }

  return (
    <div className="flex flex-col gap-4">
      <h1 className="text-2xl font-bold text-[var(--soccertactiq-pitch-700)]">Lessons</h1>

      {lessons.length === 0 ? (
        <EmptyState>No lessons are published yet. Check back soon.</EmptyState>
      ) : (
        <ul className="flex flex-col gap-3">
          {lessons.map((lesson) => (
            <li key={lesson.id}>
              <Link to={`/lessons/${lesson.id}`} className="block">
                <Card className="transition active:scale-[0.99]">
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <h2 className="font-semibold text-[var(--soccertactiq-text)]">{lesson.title}</h2>
                      <p className="mt-1 text-sm text-[var(--soccertactiq-text-muted)]">
                        {lesson.description}
                      </p>
                    </div>
                    <LessonStatusBadge lesson={lesson} />
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

function LessonStatusBadge({ lesson }: { lesson: LessonListItem }) {
  if (!lesson.is_completed) {
    return (
      <span className="shrink-0 rounded-full bg-[var(--soccertactiq-pitch-100)] px-2.5 py-1 text-xs font-semibold text-[var(--soccertactiq-pitch-700)]">
        New
      </span>
    );
  }
  return (
    <span className="shrink-0 rounded-full bg-[var(--soccertactiq-success-bg)] px-2.5 py-1 text-xs font-semibold text-[var(--soccertactiq-success)]">
      {Math.round(Number(lesson.latest_score))}%
    </span>
  );
}
