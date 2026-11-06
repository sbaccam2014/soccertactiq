import { Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { roleHome } from '../lib/roleHome';
import { LoadingState } from './ui';

export function CoachProtectedRoute({ children }: { children: React.ReactNode }) {
  const { user, isLoading } = useAuth();

  if (isLoading) return <LoadingState label="Checking your session…" />;
  if (!user) return <Navigate to="/login" replace />;
  if (!user.is_coach) return <Navigate to={roleHome(user)} replace />;
  return <>{children}</>;
}
