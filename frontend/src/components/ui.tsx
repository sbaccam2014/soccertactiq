import type { ButtonHTMLAttributes, InputHTMLAttributes, ReactNode } from 'react';

/**
 * Small shared UI primitives. Kept in one file deliberately for this
 * version's scope — a handful of buttons/fields/states, not a design
 * system. All touch targets are at least 44px tall per mobile
 * accessibility guidance.
 *
 * Visual language follows catch.co's pattern (full-pill buttons, soft
 * rounded icon tiles, bold headlines, white cards with soft shadows),
 * kept on SoccerTactiq's existing green palette rather than Catch's
 * purple.
 */

export function PrimaryButton({
  children,
  className = '',
  ...rest
}: ButtonHTMLAttributes<HTMLButtonElement> & { children: ReactNode }) {
  return (
    <button
      className={`min-h-11 w-full rounded-full bg-[var(--soccertactiq-pitch-500)] px-5 py-3 text-base font-semibold text-white transition active:scale-[0.98] disabled:cursor-not-allowed disabled:opacity-50 ${className}`}
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
      className={`min-h-11 w-full rounded-full border-2 border-[var(--soccertactiq-border)] bg-[var(--soccertactiq-surface)] px-5 py-3 text-base font-semibold text-[var(--soccertactiq-text)] transition active:scale-[0.98] disabled:cursor-not-allowed disabled:opacity-50 ${className}`}
      {...rest}
    >
      {children}
    </button>
  );
}

/**
 * Rounded-square icon tile — catch.co's recurring pattern for giving an
 * icon a soft colored background instead of floating bare. `tone`
 * picks the tint; `size` controls the tile (icon scales with it).
 */
export function IconTile({
  children,
  tone = 'pitch',
  size = 'md',
  className = '',
}: {
  children: ReactNode;
  tone?: 'pitch' | 'accent' | 'neutral';
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}) {
  const toneClasses = {
    pitch: 'bg-[var(--soccertactiq-pitch-100)] text-[var(--soccertactiq-pitch-600)]',
    accent: 'bg-[var(--soccertactiq-accent-100)] text-[var(--soccertactiq-accent-600)]',
    neutral: 'bg-[var(--soccertactiq-border)] text-[var(--soccertactiq-text-muted)]',
  }[tone];
  const sizeClasses = {
    sm: 'h-9 w-9 rounded-xl [&>svg]:h-5 [&>svg]:w-5',
    md: 'h-12 w-12 rounded-2xl [&>svg]:h-6 [&>svg]:w-6',
    lg: 'h-16 w-16 rounded-2xl [&>svg]:h-8 [&>svg]:w-8',
  }[size];

  return (
    <span className={`flex shrink-0 items-center justify-center ${sizeClasses} ${toneClasses} ${className}`}>
      {children}
    </span>
  );
}

/** Page title with a leading icon tile, matching catch.co's section headers. */
export function PageHeader({ icon, children }: { icon: ReactNode; children: ReactNode }) {
  return (
    <div className="flex items-center gap-3">
      <IconTile size="md">{icon}</IconTile>
      <h1 className="text-2xl font-bold text-[var(--soccertactiq-pitch-700)]">{children}</h1>
    </div>
  );
}

export function TextField({
  label,
  error,
  id,
  className,
  ...rest
}: InputHTMLAttributes<HTMLInputElement> & { label: string; error?: string; id: string }) {
  return (
    <div className="flex flex-col gap-1.5 text-left">
      <label htmlFor={id} className="text-sm font-medium text-[var(--soccertactiq-text)]">
        {label}
      </label>
      <input
        id={id}
        className={`min-h-11 rounded-xl border-2 border-[var(--soccertactiq-border)] bg-[var(--soccertactiq-surface)] px-3 py-2 text-base text-[var(--soccertactiq-text)] outline-none ${className ?? ''}`}
        aria-invalid={error ? 'true' : undefined}
        aria-describedby={error ? `${id}-error` : undefined}
        {...rest}
      />
      {error && (
        <p id={`${id}-error`} role="alert" className="text-sm text-[var(--soccertactiq-danger)]">
          {error}
        </p>
      )}
    </div>
  );
}

export function LoadingState({ label = 'Loading…' }: { label?: string }) {
  return (
    <div role="status" className="flex flex-1 items-center justify-center py-16 text-[var(--soccertactiq-text-muted)]">
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
      className="flex flex-col items-center gap-3 rounded-xl border-2 border-[var(--soccertactiq-danger)] bg-[var(--soccertactiq-danger-bg)] p-4 text-center text-[var(--soccertactiq-danger)]"
    >
      <p>{message}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="min-h-11 rounded-xl border-2 border-[var(--soccertactiq-danger)] px-4 py-2 font-semibold"
        >
          Try again
        </button>
      )}
    </div>
  );
}

export function EmptyState({ children }: { children: ReactNode }) {
  return (
    <div className="flex flex-1 items-center justify-center py-16 text-center text-[var(--soccertactiq-text-muted)]">
      {children}
    </div>
  );
}

export function Card({ children, className = '' }: { children: ReactNode; className?: string }) {
  return (
    <div
      className={`rounded-2xl border border-[var(--soccertactiq-border)] bg-[var(--soccertactiq-surface)] p-4 shadow-[0_2px_10px_-2px_rgba(15,61,46,0.08)] ${className}`}
    >
      {children}
    </div>
  );
}
