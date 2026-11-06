import { Link, Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { roleHome } from '../lib/roleHome';
import { Card, IconTile, PrimaryButton } from '../components/ui';
import { BallIcon, ChartIcon, PeopleIcon, VideoIcon } from '../components/icons';

export function LandingPage() {
  const { user, isLoading } = useAuth();

  if (!isLoading && user) {
    return <Navigate to={roleHome(user)} replace />;
  }

  return (
    <div className="flex flex-1 flex-col items-center gap-8 pb-8 text-center">
      <div className="flex flex-col items-center pt-4">
        <img
          src={`${import.meta.env.BASE_URL}logo.png`}
          alt=""
          className="mx-auto h-48 w-48 rounded-2xl shadow-sm"
        />
        <h1 className="mt-4 text-3xl font-bold text-[var(--soccertactiq-pitch-700)]">
          SoccerTactiq
        </h1>
        <p className="mt-3 max-w-sm text-[var(--soccertactiq-text-muted)]">
          Learn to read the game. Watch short video lessons on scanning,
          passing angles, movement off the ball, and supporting your
          teammates, and build a daily training habit.
        </p>

        <div className="mt-6 flex w-full max-w-xs flex-col gap-3">
          <Link to="/login">
            <PrimaryButton>Log in</PrimaryButton>
          </Link>
        </div>
      </div>

      <div className="flex w-full max-w-md flex-col gap-3 text-left">
        <h2 className="text-center text-lg font-bold text-[var(--soccertactiq-text)]">
          What's inside
        </h2>

        <Link to="/login" className="block">
          <Card className="flex items-start gap-3 transition active:scale-[0.99]">
            <IconTile>
              <VideoIcon />
            </IconTile>
            <div>
              <p className="font-semibold text-[var(--soccertactiq-text)]">Videos</p>
              <p className="mt-0.5 text-sm text-[var(--soccertactiq-text-muted)]">
                Short tactics videos on scanning, passing angles, movement off the
                ball, and supporting your teammates.
              </p>
            </div>
          </Card>
        </Link>

        <Link to="/login" className="block">
          <Card className="flex items-start gap-3 transition active:scale-[0.99]">
            <IconTile>
              <BallIcon />
            </IconTile>
            <div>
              <p className="font-semibold text-[var(--soccertactiq-text)]">Daily Training</p>
              <p className="mt-0.5 text-sm text-[var(--soccertactiq-text-muted)]">
                A quick daily check-in for at-home ball work, with a streak and a
                calendar to track every day trained.
              </p>
            </div>
          </Card>
        </Link>

        <Link to="/login" className="block">
          <Card className="flex items-start gap-3 transition active:scale-[0.99]">
            <IconTile>
              <ChartIcon />
            </IconTile>
            <div>
              <p className="font-semibold text-[var(--soccertactiq-text)]">Progress</p>
              <p className="mt-0.5 text-sm text-[var(--soccertactiq-text-muted)]">
                See which videos you've watched and which are still new.
              </p>
            </div>
          </Card>
        </Link>

        <Link to="/login" className="block">
          <Card className="flex items-start gap-3 transition active:scale-[0.99]">
            <IconTile>
              <PeopleIcon />
            </IconTile>
            <div>
              <p className="font-semibold text-[var(--soccertactiq-text)]">Coaches &amp; Parents</p>
              <p className="mt-0.5 text-sm text-[var(--soccertactiq-text-muted)]">
                Coaches can add their own videos and see their assigned players'
                progress; parents can follow along with their kids too.
              </p>
            </div>
          </Card>
        </Link>
      </div>
    </div>
  );
}
