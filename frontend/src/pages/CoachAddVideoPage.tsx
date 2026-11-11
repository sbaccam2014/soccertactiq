import { useEffect, useState } from 'react';
import type { FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import { createCoachVideo, fetchAssignedPlayers, fetchCoachTeams } from '../api/coach';
import { fetchVideoCategories } from '../api/content';
import { ApiError } from '../api/client';
import type { AssignedPlayer, CoachTeam } from '../types';
import { PageHeader, PrimaryButton, TextField } from '../components/ui';
import { AddVideoIcon, CheckIcon } from '../components/icons';

export function CoachAddVideoPage() {
  const navigate = useNavigate();

  const [title, setTitle] = useState('');
  const [category, setCategory] = useState('');
  const [videoUrl, setVideoUrl] = useState('');
  const [existingCategories, setExistingCategories] = useState<string[]>([]);
  const [players, setPlayers] = useState<AssignedPlayer[]>([]);
  const [teams, setTeams] = useState<CoachTeam[]>([]);
  const [selectedPlayerIds, setSelectedPlayerIds] = useState<number[]>([]);
  const [selectedTeamIds, setSelectedTeamIds] = useState<number[]>([]);
  const [formError, setFormError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    fetchVideoCategories()
      .then(setExistingCategories)
      .catch(() => {
        // Suggestions are a convenience, not required to submit the form.
      });
    fetchAssignedPlayers()
      .then(setPlayers)
      .catch(() => {
        // Assignment is optional; an empty list just hides those controls.
      });
    fetchCoachTeams()
      .then(setTeams)
      .catch(() => {});
  }, []);

  function toggleId(ids: number[], id: number): number[] {
    return ids.includes(id) ? ids.filter((existing) => existing !== id) : [...ids, id];
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setFormError('');
    setIsSubmitting(true);
    try {
      await createCoachVideo({
        title: title.trim(),
        category: category.trim(),
        video_url: videoUrl.trim(),
        assigned_players: selectedPlayerIds,
        assigned_teams: selectedTeamIds,
      });
      navigate('/coach', { replace: true });
    } catch (err) {
      if (err instanceof ApiError) {
        setFormError(err.message);
      } else {
        setFormError('Something went wrong. Please try again.');
      }
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div className="flex flex-col gap-4">
      <PageHeader icon={<AddVideoIcon />}>Add Video</PageHeader>

      <form onSubmit={handleSubmit} className="flex flex-col gap-4" noValidate>
        <TextField id="title" label="Title" value={title} onChange={(e) => setTitle(e.target.value)} required />
        <div>
          <TextField
            id="category"
            label="Category"
            value={category}
            onChange={(e) => setCategory(e.target.value)}
            placeholder="e.g. Defense, Midfield, Drills"
            list="existing-categories"
            required
          />
          <datalist id="existing-categories">
            {existingCategories.map((c) => (
              <option key={c} value={c} />
            ))}
          </datalist>
          {existingCategories.length > 0 && (
            <p className="mt-1 text-xs text-[var(--soccertactiq-text-muted)]">
              Existing categories: {existingCategories.join(', ')}
            </p>
          )}
        </div>
        <TextField
          id="video_url"
          label="YouTube URL"
          value={videoUrl}
          onChange={(e) => setVideoUrl(e.target.value)}
          required
        />
        <p className="text-xs text-[var(--soccertactiq-text-muted)]">
          The description is pulled from YouTube automatically.
        </p>

        {(teams.length > 0 || players.length > 0) && (
          <div className="flex flex-col gap-3 rounded-lg border border-[var(--soccertactiq-border)] p-3">
            <p className="text-sm font-semibold text-[var(--soccertactiq-text)]">
              Assign (optional)
            </p>
            <p className="text-xs text-[var(--soccertactiq-text-muted)]">
              Every player still sees this video in the global library. Assigning it here
              additionally surfaces it in the "Assigned" tab for the team/players you pick.
            </p>

            {teams.length > 0 && (
              <div>
                <p className="mb-1 text-xs font-semibold text-[var(--soccertactiq-text-muted)]">
                  Teams
                </p>
                <div className="flex flex-wrap gap-2">
                  {teams.map((team) => (
                    <label
                      key={team.id}
                      className={`flex min-h-9 cursor-pointer items-center gap-1.5 rounded-full px-3 text-sm font-medium transition ${
                        selectedTeamIds.includes(team.id)
                          ? 'bg-[var(--soccertactiq-pitch-500)] text-white'
                          : 'bg-[var(--soccertactiq-pitch-100)] text-[var(--soccertactiq-text-muted)]'
                      }`}
                    >
                      <input
                        type="checkbox"
                        className="sr-only"
                        checked={selectedTeamIds.includes(team.id)}
                        onChange={() => setSelectedTeamIds((ids) => toggleId(ids, team.id))}
                      />
                      {team.name}
                    </label>
                  ))}
                </div>
              </div>
            )}

            {players.length > 0 && (
              <div>
                <p className="mb-1 text-xs font-semibold text-[var(--soccertactiq-text-muted)]">
                  Players
                </p>
                <div className="flex flex-wrap gap-2">
                  {players.map((player) => (
                    <label
                      key={player.id}
                      className={`flex min-h-9 cursor-pointer items-center gap-1.5 rounded-full px-3 text-sm font-medium transition ${
                        selectedPlayerIds.includes(player.id)
                          ? 'bg-[var(--soccertactiq-pitch-500)] text-white'
                          : 'bg-[var(--soccertactiq-pitch-100)] text-[var(--soccertactiq-text-muted)]'
                      }`}
                    >
                      <input
                        type="checkbox"
                        className="sr-only"
                        checked={selectedPlayerIds.includes(player.id)}
                        onChange={() => setSelectedPlayerIds((ids) => toggleId(ids, player.id))}
                      />
                      {player.display_name}
                    </label>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {formError && (
          <p role="alert" className="text-sm text-[var(--soccertactiq-danger)]">
            {formError}
          </p>
        )}

        <PrimaryButton type="submit" disabled={isSubmitting} className="flex items-center justify-center gap-2">
          <CheckIcon className="h-5 w-5" />
          {isSubmitting ? 'Publishing…' : 'Publish Video'}
        </PrimaryButton>
      </form>
    </div>
  );
}
