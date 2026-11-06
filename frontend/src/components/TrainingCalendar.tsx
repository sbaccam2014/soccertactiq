import { useEffect, useState } from 'react';
import { fetchTrainingCalendar, setDayTraining } from '../api/training';
import type { TrainingLog, TrainingStatus } from '../types';
import { Card, PrimaryButton, SecondaryButton } from './ui';
import { CheckIcon, XIcon } from './icons';

const MONTH_NAMES = [
  'January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December',
];
const WEEKDAY_LABELS = ['S', 'M', 'T', 'W', 'T', 'F', 'S'];

type DayStatus = 'trained' | 'missed' | null;

/**
 * Where a day sits within a run of consecutive same-status days, so a
 * run of trained days renders as one connected capsule (rounded only
 * at its two outer ends) rather than N separate circles — matching the
 * reference calendar's "16 17 18 19" pill pattern.
 */
type RunPosition = 'solo' | 'start' | 'middle' | 'end';

function toIsoDate(year: number, month: number, day: number): string {
  return `${year}-${String(month).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
}

export function TrainingCalendar({ onChanged }: { onChanged?: (status: TrainingStatus) => void }) {
  const today = new Date();
  const [year, setYear] = useState(today.getFullYear());
  const [month, setMonth] = useState(today.getMonth() + 1); // 1-12

  const [logs, setLogs] = useState<TrainingLog[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  const [selectedDay, setSelectedDay] = useState<number | null>(null);
  const [isSaving, setIsSaving] = useState(false);

  function loadMonth() {
    setIsLoading(true);
    return fetchTrainingCalendar(year, month)
      .then((result) => setLogs(result))
      .catch(() => setLogs([]))
      .finally(() => setIsLoading(false));
  }

  useEffect(() => {
    let cancelled = false;
    setIsLoading(true);
    fetchTrainingCalendar(year, month)
      .then((result) => {
        if (!cancelled) setLogs(result);
      })
      .catch(() => {
        if (!cancelled) setLogs([]);
      })
      .finally(() => {
        if (!cancelled) setIsLoading(false);
      });
    setSelectedDay(null);
    return () => {
      cancelled = true;
    };
  }, [year, month]);

  function goToPreviousMonth() {
    if (month === 1) {
      setYear((y) => y - 1);
      setMonth(12);
    } else {
      setMonth((m) => m - 1);
    }
  }

  function goToNextMonth() {
    if (month === 12) {
      setYear((y) => y + 1);
      setMonth(1);
    } else {
      setMonth((m) => m + 1);
    }
  }

  async function handleSetDay(day: number, trained: boolean) {
    setIsSaving(true);
    try {
      const status = await setDayTraining(toIsoDate(year, month, day), trained);
      await loadMonth();
      setSelectedDay(null);
      onChanged?.(status);
    } catch {
      // Leave the editor open so the player can retry.
    } finally {
      setIsSaving(false);
    }
  }

  const statusByDay = new Map<number, DayStatus>();
  for (const log of logs) {
    const day = Number(log.date.slice(8, 10));
    statusByDay.set(day, log.trained ? 'trained' : 'missed');
  }

  const firstOfMonth = new Date(year, month - 1, 1);
  const daysInMonth = new Date(year, month, 0).getDate();
  const leadingBlanks = firstOfMonth.getDay(); // 0 = Sunday

  const isCurrentMonth = year === today.getFullYear() && month === today.getMonth() + 1;
  const todayDate = today.getDate();

  const days = Array.from({ length: daysInMonth }, (_, i) => i + 1);
  const runPositionByDay = new Map<number, RunPosition>();
  days.forEach((day, i) => {
    const status = statusByDay.get(day) ?? null;
    if (!status) return;
    // Only days adjacent in the SAME calendar row connect visually, so
    // a run never wraps across the grid onto the next line.
    const sameRow = (a: number, b: number) =>
      Math.floor((leadingBlanks + a - 1) / 7) === Math.floor((leadingBlanks + b - 1) / 7);
    const prevDay = days[i - 1];
    const nextDay = days[i + 1];
    const connectsLeft = prevDay != null && statusByDay.get(prevDay) === status && sameRow(prevDay, day);
    const connectsRight = nextDay != null && statusByDay.get(nextDay) === status && sameRow(nextDay, day);

    if (connectsLeft && connectsRight) runPositionByDay.set(day, 'middle');
    else if (connectsLeft) runPositionByDay.set(day, 'end');
    else if (connectsRight) runPositionByDay.set(day, 'start');
    else runPositionByDay.set(day, 'solo');
  });

  const cells: (number | null)[] = [
    ...Array.from({ length: leadingBlanks }, () => null),
    ...days,
  ];

  const isNextMonthDisabled =
    year > today.getFullYear() || (year === today.getFullYear() && month >= today.getMonth() + 1);

  const isDayEditable = (day: number) => !isCurrentMonth || day <= todayDate;

  return (
    <Card className={isLoading ? 'opacity-60 transition' : 'transition'}>
      <div className="flex items-center justify-center gap-3">
        <button
          type="button"
          onClick={goToPreviousMonth}
          aria-label="Previous month"
          className="flex h-9 w-9 items-center justify-center rounded-full text-lg text-[var(--soccertactiq-text-muted)] active:bg-[var(--soccertactiq-pitch-100)]"
        >
          ‹
        </button>
        <p className="text-lg font-bold text-[var(--soccertactiq-text)]">
          {MONTH_NAMES[month - 1]} {year}
        </p>
        <button
          type="button"
          onClick={goToNextMonth}
          disabled={isNextMonthDisabled}
          aria-label="Next month"
          className="flex h-9 w-9 items-center justify-center rounded-full text-lg text-[var(--soccertactiq-text-muted)] active:bg-[var(--soccertactiq-pitch-100)] disabled:opacity-30"
        >
          ›
        </button>
      </div>

      <p className="mt-2 text-center text-xs text-[var(--soccertactiq-text-muted)]">
        Forgot a day? Tap it to add or fix it.
      </p>

      <div className="mt-3 grid grid-cols-7">
        {WEEKDAY_LABELS.map((label, i) => (
          <div
            key={i}
            className="flex h-7 items-center justify-center text-xs font-semibold text-[var(--soccertactiq-text-muted)]"
          >
            {label}
          </div>
        ))}

        {cells.map((day, i) => {
          if (day === null) return <div key={`blank-${i}`} className="h-11" />;

          const status = statusByDay.get(day) ?? null;
          const isToday = isCurrentMonth && day === todayDate;
          const runPosition = runPositionByDay.get(day) ?? 'solo';
          const editable = isDayEditable(day);
          const isSelected = selectedDay === day;

          const roundedClasses = {
            solo: 'rounded-full',
            start: 'rounded-l-full',
            middle: '',
            end: 'rounded-r-full',
          }[runPosition];

          let fillClasses = 'text-[var(--soccertactiq-text)]';
          if (status === 'trained') {
            fillClasses = 'bg-[var(--soccertactiq-pitch-500)] text-white';
          } else if (status === 'missed') {
            fillClasses = 'bg-[var(--soccertactiq-border)] text-[var(--soccertactiq-text-muted)]';
          } else if (isToday) {
            fillClasses = 'bg-[var(--soccertactiq-accent-500)] text-white rounded-full';
          }

          return (
            <div key={day} className="flex h-11 items-center justify-center">
              <button
                type="button"
                disabled={!editable}
                onClick={() => setSelectedDay((d) => (d === day ? null : day))}
                aria-label={`${MONTH_NAMES[month - 1]} ${day}, ${year}${editable ? ' — tap to log training' : ''}`}
                className={`flex h-9 w-full items-center justify-center text-sm font-semibold disabled:cursor-default ${
                  status ? roundedClasses : editable ? 'rounded-full' : ''
                } ${fillClasses} ${
                  isSelected ? 'ring-2 ring-[var(--soccertactiq-pitch-500)] ring-offset-1' : ''
                }`}
              >
                {day}
              </button>
            </div>
          );
        })}
      </div>

      {selectedDay !== null && (
        <div className="mt-4 flex flex-col gap-2 rounded-xl bg-[var(--soccertactiq-pitch-100)] p-3">
          <p className="text-center text-sm font-semibold text-[var(--soccertactiq-text)]">
            {MONTH_NAMES[month - 1]} {selectedDay}: did you train that day?
          </p>
          <div className="flex gap-2">
            <PrimaryButton
              onClick={() => handleSetDay(selectedDay, true)}
              disabled={isSaving}
              className="flex items-center justify-center gap-2"
            >
              <CheckIcon className="h-5 w-5" />
              Yes
            </PrimaryButton>
            <SecondaryButton
              onClick={() => handleSetDay(selectedDay, false)}
              disabled={isSaving}
              className="flex items-center justify-center gap-2"
            >
              <XIcon className="h-5 w-5" />
              No
            </SecondaryButton>
          </div>
        </div>
      )}
    </Card>
  );
}
