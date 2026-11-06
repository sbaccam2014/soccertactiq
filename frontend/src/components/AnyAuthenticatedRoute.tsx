import { Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { LoadingState } from './ui';

/** Unlike ProtectedRoute/CoachProtectedRoute/ParentProtectedRoute, this
 * allows any logged-in user regardless of role — for pages (like About)
 * that aren't specific to one role. */
export function AnyAuthenticatedRoute({ children }: { children: React.ReactNode }) {
  const { user, isLoading } = useAuth();

  if (isLoading) return <LoadingState label="Checking your session…" />;
  if (!user) return <Navigate to="/login" replace />;
  return <>{children}</>;
}
