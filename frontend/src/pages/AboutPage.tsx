import type { ReactNode } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Card, IconTile, PageHeader } from '../components/ui';
import { AddVideoIcon, BallIcon, ChartIcon, InfoIcon, PeopleIcon, VideoIcon } from '../components/icons';

interface FeatureCardProps {
  icon: ReactNode;
  title: string;
  description: string;
  to?: string;
}

function FeatureCard({ icon, title, description, to }: FeatureCardProps) {
  const content = (
    <Card className={`flex items-start gap-3 ${to ? 'transition active:scale-[0.99]' : ''}`}>
      <IconTile>{icon}</IconTile>
      <div>
        <p className="font-semibold text-[var(--soccertactiq-text)]">{title}</p>
        <p className="mt-0.5 text-sm text-[var(--soccertactiq-text-muted)]">{description}</p>
      </div>
    </Card>
  );

  return to ? (
    <Link to={to} className="block">
      {content}
    </Link>
  ) : (
    content
  );
}

export function AboutPage() {
  const { user } = useAuth();

  return (
    <div className="flex flex-col gap-4">
      <PageHeader icon={<InfoIcon />}>About SoccerTactiq</PageHeader>

      <p className="text-[var(--soccertactiq-text)]">
        SoccerTactiq helps you learn to read the game. Watch short tactics
        videos and build a daily training habit — all in one place.
      </p>

      {user?.is_coach ? (
        <>
          <FeatureCard
            icon={<PeopleIcon />}
            title="My Players"
            description="See your assigned players' watched videos and training streaks."
            to="/coach"
          />
          <FeatureCard
            icon={<AddVideoIcon />}
            title="Add Video"
            description="Add your own tactics videos — they publish right away for your players."
            to="/coach/videos/new"
          />
        </>
      ) : user?.is_parent ? (
        <FeatureCard
          icon={<PeopleIcon />}
          title="My Kids"
          description="See your kids' watched videos and training streaks."
          to="/parent"
        />
      ) : (
        <>
          <FeatureCard
            icon={<VideoIcon />}
            title="Videos"
            description="Browse videos by category — Defense, Midfield, Drills, and more — and mark each one watched."
            to="/dashboard"
          />
          <FeatureCard
            icon={<BallIcon />}
            title="Training"
            description="Check in once a day to log at least 10 minutes of ball work. Build a streak, see how many days you've trained this month and year, and use the calendar to add a day you forgot to log."
            to="/training"
          />
          <FeatureCard
            icon={<ChartIcon />}
            title="Progress"
            description="See which videos you've watched and which are still new."
            to="/progress"
          />
          <FeatureCard
            icon={<PeopleIcon />}
            title="Coaches & Parents"
            description="Coaches get their own dashboard to see assigned players' progress and add their own videos. Parents can follow their kids' progress and training too."
          />
        </>
      )}
    </div>
  );
}
