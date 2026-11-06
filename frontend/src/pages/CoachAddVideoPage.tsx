import { useEffect, useState } from 'react';
import type { FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import { createCoachVideo } from '../api/coach';
import { fetchVideoCategories } from '../api/content';
import { ApiError } from '../api/client';
import { PageHeader, PrimaryButton, TextField } from '../components/ui';
import { AddVideoIcon, CheckIcon } from '../components/icons';

export function CoachAddVideoPage() {
  const navigate = useNavigate();

  const [title, setTitle] = useState('');
  const [category, setCategory] = useState('');
  const [videoUrl, setVideoUrl] = useState('');
  const [existingCategories, setExistingCategories] = useState<string[]>([]);
  const [formError, setFormError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    fetchVideoCategories()
      .then(setExistingCategories)
      .catch(() => {
        // Suggestions are a convenience, not required to submit the form.
      });
  }, []);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setFormError('');
    setIsSubmitting(true);
    try {
      await createCoachVideo({
        title: title.trim(),
        category: category.trim(),
        video_url: videoUrl.trim(),
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
