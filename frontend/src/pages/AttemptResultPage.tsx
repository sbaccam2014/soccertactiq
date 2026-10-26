import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { fetchAttempt } from '../api/content';
import type { AttemptResult } from '../types';
import { Card, ErrorState, LoadingState, PrimaryButton } from '../components/ui';

export function AttemptResultPage() {
  const { attemptId } = useParams<{ attemptId: string }>();
  const id = Number(attemptId);

  const [attempt, setAttempt] = useState<AttemptResult | null>(null);
  const [state, setState] = useState<'loading' | 'error' | 'ready'>('loading');

  async function load() {
    setState('loading');
    try {
      setAttempt(await fetchAttempt(id));
      setState('ready');
    } catch {
      setState('error');
    }
  }

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id]);

  if (state === 'loading') return <LoadingState label="Loading your result…" />;
  if (state === 'error' || !attempt) {
    return <ErrorState message="Couldn't load this result." onRetry={load} />;
  }

  return (
    <div className="flex flex-col gap-4">
      <div className="text-center">
        <h1 className="text-2xl font-bold text-[var(--soccertactiq-pitch-700)]">
          {attempt.lesson_title_snapshot}
        </h1>
        <p className="mt-2 text-3xl font-bold text-[var(--soccertactiq-pitch-500)]">
          {attempt.correct_count}/{attempt.question_count} correct
        </p>
        <p className="text-sm text-[var(--soccertactiq-text-muted)]">
          Submitted {new Date(attempt.submitted_at).toLocaleString()}
        </p>
      </div>

      <ul className="flex flex-col gap-3">
        {attempt.answers.map((answer, index) => (
          <li key={answer.question}>
            <Card className={answer.is_correct ? '' : 'border-[var(--soccertactiq-danger)]'}>
              <p className="text-xs font-semibold text-[var(--soccertactiq-text-muted)]">
                Question {index + 1}
              </p>
              <p className="mt-1 font-medium text-[var(--soccertactiq-text)]">
                {answer.question_prompt_snapshot}
              </p>
              <p
                className={`mt-2 text-sm font-semibold ${
                  answer.is_correct ? 'text-[var(--soccertactiq-success)]' : 'text-[var(--soccertactiq-danger)]'
                }`}
              >
                Your answer: {answer.selected_choice_text_snapshot}
                {answer.is_correct ? ' — correct' : ' — not quite'}
              </p>
              {!answer.is_correct && (
                <p className="mt-1 text-sm text-[var(--soccertactiq-text)]">
                  Correct answer: {answer.correct_choice_text_snapshot}
                </p>
              )}
              <p className="mt-2 text-sm text-[var(--soccertactiq-text-muted)]">
                {answer.question_explanation_snapshot}
              </p>
            </Card>
          </li>
        ))}
      </ul>

      <Link to="/dashboard">
        <PrimaryButton>Back to lessons</PrimaryButton>
      </Link>
    </div>
  );
}
