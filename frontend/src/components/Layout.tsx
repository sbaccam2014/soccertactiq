import { Link, NavLink, Outlet } from 'react-router-dom';
import type { ReactNode } from 'react';
import { useAuth } from '../context/AuthContext';
import { AddVideoIcon, BallIcon, ChartIcon, PeopleIcon, VideoIcon } from './icons';

export function AppLayout() {
  const { user, logout } = useAuth();

  async function handleLogout() {
    await logout();
    // A full page load (not client-side navigate()) avoids a redirect
    // race with ProtectedRoute/LandingPage's own auth-based redirects,
    // which otherwise can land back on /login instead of "/".
    window.location.assign('/');
  }

  return (
    <div className="flex min-h-svh flex-col">
      <header className="sticky top-0 z-10 flex items-center justify-between border-b border-[var(--soccertactiq-border)] bg-[var(--soccertactiq-surface)] px-4 py-3">
        <Link to={user ? '/about' : '/'} className="flex items-center gap-2">
          <img src={`${import.meta.env.BASE_URL}logo-icon.png`} alt="" className="h-11 w-11 rounded-md" />
          <span className="text-lg font-bold text-[var(--soccertactiq-pitch-700)]">SoccerTactiq</span>
        </Link>
        {user && (
          <button
            onClick={handleLogout}
            className="min-h-11 rounded-full px-3 text-sm font-semibold text-[var(--soccertactiq-text-muted)]"
          >
            Log out
          </button>
        )}
      </header>

      <main className="flex flex-1 flex-col px-4 py-4">
        <Outlet />
      </main>

      {user && !user.is_coach && !user.is_parent && (
        <nav
          aria-label="Primary"
          className="sticky bottom-0 z-10 flex border-t border-[var(--soccertactiq-border)] bg-[var(--soccertactiq-surface)]"
        >
          <NavTab to="/dashboard" label="Videos" icon={<VideoIcon />} />
          <NavTab to="/training" label="Training" icon={<BallIcon />} />
          <NavTab to="/progress" label="Progress" icon={<ChartIcon />} />
        </nav>
      )}
      {user && user.is_coach && (
        <nav
          aria-label="Primary"
          className="sticky bottom-0 z-10 flex border-t border-[var(--soccertactiq-border)] bg-[var(--soccertactiq-surface)]"
        >
          <NavTab to="/coach" label="Players" icon={<PeopleIcon />} />
          <NavTab to="/coach/videos/new" label="Add Video" icon={<AddVideoIcon />} />
        </nav>
      )}
      {user && user.is_parent && (
        <nav
          aria-label="Primary"
          className="sticky bottom-0 z-10 flex border-t border-[var(--soccertactiq-border)] bg-[var(--soccertactiq-surface)]"
        >
          <NavTab to="/parent" label="My Kids" icon={<PeopleIcon />} />
        </nav>
      )}
    </div>
  );
}

function NavTab({ to, label, icon }: { to: string; label: string; icon: ReactNode }) {
  return (
    <NavLink
      to={to}
      className={({ isActive }) =>
        `flex min-h-16 flex-1 flex-col items-center justify-center gap-0.5 text-xs font-semibold ${
          isActive ? 'text-[var(--soccertactiq-pitch-500)]' : 'text-[var(--soccertactiq-text-muted)]'
        }`
      }
    >
      <span className="[&>svg]:h-6 [&>svg]:w-6">{icon}</span>
      {label}
    </NavLink>
  );
}
