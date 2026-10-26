import { Link, Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { PrimaryButton, SecondaryButton } from '../components/ui';

export function LandingPage() {
  const { user, isLoading } = useAuth();

  if (!isLoading && user) {
    return <Navigate to="/dashboard" replace />;
  }

  return (
    <div className="flex flex-1 flex-col items-center justify-center gap-6 text-center">
      <div>
        <h1 className="text-3xl font-bold text-[var(--soccermind-pitch-700)]">
          SoccerMind
        </h1>
        <p className="mt-3 max-w-sm text-[var(--soccermind-text-muted)]">
          Learn to read the game. Watch short video lessons, then answer
          questions about scanning, passing angles, movement off the
          ball, and supporting your teammates — with explanations that
          teach the "why," not just whether you got it right.
        </p>
      </div>

      <div className="flex w-full max-w-xs flex-col gap-3">
        <Link to="/register">
          <PrimaryButton>Create an account</PrimaryButton>
        </Link>
        <Link to="/login">
          <SecondaryButton>Log in</SecondaryButton>
        </Link>
      </div>
    </div>
  );
}
