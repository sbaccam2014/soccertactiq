import { useEffect, useState } from 'react';
import { fetchTrainingHistory, fetchTrainingStatus, setTodayTraining } from '../api/training';
import type { TrainingLog, TrainingStatus } from '../types';
import {
  Card,
  EmptyState,
  ErrorState,
  IconTile,
  LoadingState,
  PageHeader,
  PrimaryButton,
  SecondaryButton,
} from '../components/ui';
import { BallIcon, CheckIcon, ChartIcon, FlameIcon, XIcon } from '../components/icons';
import { TrainingCalendar } from '../components/TrainingCalendar';

const DAILY_GOAL_MINUTES = 10;

type LoadState = 'loading' | 'error' | 'ready';

export function TrainingPage() {
  const [status, setStatus] = useState<TrainingStatus | null>(null);
  const [statusState, setStatusState] = useState<LoadState>('loading');
  const [isSaving, setIsSaving] = useState(false);

  const [history, setHistory] = useState<TrainingLog[]>([]);
  const [historyState, setHistoryState] = useState<LoadState>('loading');

  async function loadStatus() {
    setStatusState('loading');
    try {
      setStatus(await fetchTrainingStatus());
      setStatusState('ready');
    } catch {
      setStatusState('error');
    }
  }

  async function loadHistory() {
    setHistoryState('loading');
    try {
      const page = await fetchTrainingHistory();
      setHistory(page.results);
      setHistoryState('ready');
    } catch {
      setHistoryState('error');
    }
  }

  useEffect(() => {
    loadStatus();
    loadHistory();
  }, []);

  async function handleSetToday(trained: boolean) {
    setIsSaving(true);
    try {
      const updated = await setTodayTraining(trained);
      setStatus(updated);
      loadHistory();
    } catch {
      // Leave the current state as-is; the buttons remain available to retry.
    } finally {
      setIsSaving(false);
    }
  }

  if (statusState === 'loading') return <LoadingState label="Loading training status…" />;
  if (statusState === 'error' || !status) {
    return <ErrorState message="Couldn't load your training status." onRetry={loadStatus} />;
  }

  const todayTrained = status.today?.trained ?? null;

  return (
    <div className="flex flex-col gap-4">
      <PageHeader icon={<BallIcon />}>Training</PageHeader>

      <Card className="text-center">
        <p className="text-sm font-semibold text-[var(--soccertactiq-text-muted)]">
          Did you do at least {DAILY_GOAL_MINUTES} minutes of ball work today?
        </p>

        <div className="mt-4 flex gap-3">
          <PrimaryButton
            onClick={() => handleSetToday(true)}
            disabled={isSaving}
            className={`flex items-center justify-center gap-2 ${todayTrained === true ? '' : 'opacity-60'}`}
          >
            <CheckIcon className="h-5 w-5" />
            {todayTrained === true ? 'Yes — logged' : 'Yes'}
          </PrimaryButton>
          <SecondaryButton
            onClick={() => handleSetToday(false)}
            disabled={isSaving}
            className={`flex items-center justify-center gap-2 ${todayTrained === false ? 'border-[var(--soccertactiq-danger)] text-[var(--soccertactiq-danger)]' : ''}`}
          >
            <XIcon className="h-5 w-5" />
            {todayTrained === false ? 'Not yet' : 'No'}
          </SecondaryButton>
        </div>

        {status.current_streak > 0 && (
          <p className="mt-4 flex items-center justify-center gap-1.5 text-sm text-[var(--soccertactiq-text-muted)]">
            <FlameIcon className="h-5 w-5 text-[var(--soccertactiq-accent-500)]" />
            {status.current_streak} day{status.current_streak === 1 ? '' : 's'} in a row
          </p>
        )}
      </Card>

      <div className="grid grid-cols-2 gap-3">
        <Card className="flex flex-col items-center gap-2 text-center">
          <IconTile size="sm">
            <ChartIcon />
          </IconTile>
          <p className="text-2xl font-bold text-[var(--soccertactiq-pitch-700)]">
            {status.month_trained_days}
          </p>
          <p className="text-xs font-semibold text-[var(--soccertactiq-text-muted)]">
            days trained this month
          </p>
        </Card>
        <Card className="flex flex-col items-center gap-2 text-center">
          <IconTile size="sm">
            <ChartIcon />
          </IconTile>
          <p className="text-2xl font-bold text-[var(--soccertactiq-pitch-700)]">
            {status.year_trained_days}
          </p>
          <p className="text-xs font-semibold text-[var(--soccertactiq-text-muted)]">
            days trained this year
          </p>
        </Card>
      </div>

      <TrainingCalendar
        onChanged={(updated) => {
          setStatus(updated);
          loadHistory();
        }}
      />

      <h2 className="text-lg font-semibold text-[var(--soccertactiq-text)]">History</h2>

      {historyState === 'loading' && <LoadingState label="Loading history…" />}
      {historyState === 'error' && (
        <ErrorState message="Couldn't load your training history." onRetry={loadHistory} />
      )}
      {historyState === 'ready' && history.length === 0 && (
        <EmptyState>No training logged yet. Check in above once you've trained today.</EmptyState>
      )}
      {historyState === 'ready' && history.length > 0 && (
        <ul className="flex flex-col gap-2">
          {history.map((log) => (
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
                  {log.trained ? `${DAILY_GOAL_MINUTES}+ min` : 'Not logged'}
                </span>
              </Card>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
