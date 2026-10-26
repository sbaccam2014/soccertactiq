import { NavLink, Outlet } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export function AppLayout() {
  const { user, logout } = useAuth();

  return (
    <div className="flex min-h-svh flex-col">
      <header className="sticky top-0 z-10 flex items-center justify-between border-b border-[var(--soccermind-border)] bg-[var(--soccermind-surface)] px-4 py-3">
        <span className="text-lg font-bold text-[var(--soccermind-pitch-700)]">SoccerMind</span>
        {user && (
          <button
            onClick={() => logout()}
            className="min-h-11 rounded-lg px-3 text-sm font-semibold text-[var(--soccermind-text-muted)]"
          >
            Log out
          </button>
        )}
      </header>

      <main className="flex flex-1 flex-col px-4 py-4">
        <Outlet />
      </main>

      {user && (
        <nav
          aria-label="Primary"
          className="sticky bottom-0 z-10 flex border-t border-[var(--soccermind-border)] bg-[var(--soccermind-surface)]"
        >
          <NavTab to="/dashboard" label="Lessons" />
          <NavTab to="/progress" label="My Progress" />
        </nav>
      )}
    </div>
  );
}

function NavTab({ to, label }: { to: string; label: string }) {
  return (
    <NavLink
      to={to}
      className={({ isActive }) =>
        `flex min-h-14 flex-1 items-center justify-center text-sm font-semibold ${
          isActive ? 'text-[var(--soccermind-pitch-500)]' : 'text-[var(--soccermind-text-muted)]'
        }`
      }
    >
      {label}
    </NavLink>
  );
}
