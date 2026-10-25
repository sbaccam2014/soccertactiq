import type { ButtonHTMLAttributes, InputHTMLAttributes, ReactNode } from 'react';

/**
 * Small shared UI primitives. Kept in one file deliberately for this
 * version's scope — a handful of buttons/fields/states, not a design
 * system. All touch targets are at least 44px tall per mobile
 * accessibility guidance.
 */

export function PrimaryButton({
  children,
  className = '',
  ...rest
}: ButtonHTMLAttributes<HTMLButtonElement> & { children: ReactNode }) {
  return (
    <button
      className={`min-h-11 w-full rounded-lg bg-[var(--bsa-pitch-500)] px-4 py-3 text-base font-semibold text-white transition active:scale-[0.98] disabled:cursor-not-allowed disabled:opacity-50 ${className}`}
      {...rest}
    >
      {children}
    </button>
  );
}

export function SecondaryButton({
  children,
  className = '',
  ...rest
}: ButtonHTMLAttributes<HTMLButtonElement> & { children: ReactNode }) {
  return (
    <button
      className={`min-h-11 w-full rounded-lg border-2 border-[var(--bsa-border)] bg-[var(--bsa-surface)] px-4 py-3 text-base font-semibold text-[var(--bsa-text)] transition active:scale-[0.98] disabled:cursor-not-allowed disabled:opacity-50 ${className}`}
      {...rest}
    >
      {children}
    </button>
  );
}

export function TextField({
  label,
  error,
  id,
  ...rest
}: InputHTMLAttributes<HTMLInputElement> & { label: string; error?: string; id: string }) {
  return (
    <div className="flex flex-col gap-1.5 text-left">
      <label htmlFor={id} className="text-sm font-medium text-[var(--bsa-text)]">
        {label}
      </label>
      <input
        id={id}
        className="min-h-11 rounded-lg border-2 border-[var(--bsa-border)] bg-[var(--bsa-surface)] px-3 py-2 text-base text-[var(--bsa-text)] outline-none"
        aria-invalid={error ? 'true' : undefined}
        aria-describedby={error ? `${id}-error` : undefined}
        {...rest}
      />
      {error && (
        <p id={`${id}-error`} role="alert" className="text-sm text-[var(--bsa-danger)]">
          {error}
        </p>
      )}
    </div>
  );
}

export function LoadingState({ label = 'Loading…' }: { label?: string }) {
  return (
    <div role="status" className="flex flex-1 items-center justify-center py-16 text-[var(--bsa-text-muted)]">
      <span>{label}</span>
    </div>
  );
}

export function ErrorState({
  message,
  onRetry,
}: {
  message: string;
  onRetry?: () => void;
}) {
  return (
    <div
      role="alert"
      className="flex flex-col items-center gap-3 rounded-lg border-2 border-[var(--bsa-danger)] bg-[var(--bsa-danger-bg)] p-4 text-center text-[var(--bsa-danger)]"
    >
      <p>{message}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="min-h-11 rounded-lg border-2 border-[var(--bsa-danger)] px-4 py-2 font-semibold"
        >
          Try again
        </button>
      )}
    </div>
  );
}

export function EmptyState({ children }: { children: ReactNode }) {
  return (
    <div className="flex flex-1 items-center justify-center py-16 text-center text-[var(--bsa-text-muted)]">
      {children}
    </div>
  );
}

export function Card({ children, className = '' }: { children: ReactNode; className?: string }) {
  return (
    <div
      className={`rounded-xl border border-[var(--bsa-border)] bg-[var(--bsa-surface)] p-4 shadow-sm ${className}`}
    >
      {children}
    </div>
  );
}
