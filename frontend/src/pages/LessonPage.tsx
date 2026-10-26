import { useEffect, useMemo, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { fetchLesson, submitAttempt } from '../api/content';
import { ApiError } from '../api/client';
import type { LessonDetail } from '../types';
import { buildYoutubeLink, formatTimestampGuidance } from '../lib/youtube';
import { generateIdempotencyKey } from '../lib/idempotency';
import { EmptyState, ErrorState, LoadingState, PrimaryButton, SecondaryButton } from '../components/ui';

type LoadState = 'loading' | 'error' | 'not-found' | 'ready';

export function LessonPage() {
  const { lessonId } = useParams<{ lessonId: string }>();
  const navigate = useNavigate();
  const id = Number(lessonId);

  const [lesson, setLesson] = useState<LessonDetail | null>(null);
  const [state, setState] = useState<LoadState>('loading');

  // questionIndex: -1 = intro screen (title/goal/video), 0..n-1 = questions
  const [questionIndex, setQuestionIndex] = useState(-1);
  // Answers keyed by question id, retained across Back/Next navigation.
  const [answers, setAnswers] = useState<Record<number, number>>({});
  const [hasOpenedVideo, setHasOpenedVideo] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState('');
  // One idempotency key per "attempt in progress," generated once when
  // the player opens this lesson and reused for every submit (including
  // a manual retry after a network error) so a repeated request can
  // never create a duplicate Attempt. Opening the lesson again later
  // (a genuinely new attempt) remounts this component and gets a fresh
  // key via this lazy initializer.
  const [idempotencyKey] = useState(generateIdempotencyKey);

  async function load() {
    setState('loading');
    try {
      const data = await fetchLesson(id);
      setLesson(data);
      setState('ready');
    } catch (err) {
      if (err instanceof ApiError && err.status === 404) {
        setState('not-found');
      } else {
        setState('error');
      }
    }
  }

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id]);

  const timestampGuidance = useMemo(() => (lesson ? formatTimestampGuidance(lesson) : null), [lesson]);

  if (state === 'loading') return <LoadingState label="Loading lesson…" />;
  if (state === 'not-found') {
    return <EmptyState>This lesson isn't available right now.</EmptyState>;
  }
  if (state === 'error' || !lesson) {
    return <ErrorState message="Couldn't load this lesson." onRetry={load} />;
  }

  const currentLessonId = lesson.id;
  const questions = lesson.questions;
  const currentQuestion = questionIndex >= 0 ? questions[questionIndex] : null;
  const allAnswered = questions.every((q) => answers[q.id] != null);

  async function handleConfirmSubmit() {
    setIsSubmitting(true);
    setSubmitError('');
    try {
      const result = await submitAttempt(
        currentLessonId,
        idempotencyKey,
        questions.map((q) => ({ question_id: q.id, choice_id: answers[q.id] })),
      );
      navigate(`/attempts/${result.id}`, { replace: true });
    } catch {
      setSubmitError('Could not submit your answers. Check your connection and try again.');
      setShowConfirm(false);
    } finally {
      setIsSubmitting(false);
    }
  }

  // --- Intro screen: title, learning goal, video link, timestamp guidance ---
  if (questionIndex === -1) {
    return (
      <div className="flex flex-col gap-4">
        <h1 className="text-2xl font-bold text-[var(--soccertactiq-pitch-700)]">{lesson.title}</h1>
        <p className="text-[var(--soccertactiq-text)]">{lesson.description}</p>

        <div className="rounded-lg bg-[var(--soccertactiq-pitch-100)] p-3">
          <h2 className="text-sm font-semibold text-[var(--soccertactiq-pitch-700)]">
            What you're learning
          </h2>
          <p className="mt-1 text-sm text-[var(--soccertactiq-text)]">{lesson.learning_objective}</p>
        </div>

        <a
          href={buildYoutubeLink(lesson)}
          target="_blank"
          rel="noopener noreferrer"
          onClick={() => setHasOpenedVideo(true)}
          className="min-h-11 flex items-center justify-center rounded-lg border-2 border-[var(--soccertactiq-pitch-500)] px-4 py-3 text-center font-semibold text-[var(--soccertactiq-pitch-600)]"
        >
          Watch the video on YouTube ↗
        </a>
        {timestampGuidance && (
          <p className="text-center text-sm text-[var(--soccertactiq-text-muted)]">{timestampGuidance}</p>
        )}
        {!hasOpenedVideo && (
          <p className="text-center text-sm text-[var(--soccertactiq-text-muted)]">
            Watch the video before answering — the questions assume you have.
          </p>
        )}

        <PrimaryButton onClick={() => setQuestionIndex(0)} disabled={questions.length === 0}>
          {questions.length === 0 ? 'No questions yet' : 'Start questions'}
        </PrimaryButton>
      </div>
    );
  }

  // --- Confirmation before final submit ---
  if (showConfirm) {
    return (
      <div className="flex flex-1 flex-col items-center justify-center gap-4 text-center">
        <h1 className="text-xl font-bold text-[var(--soccertactiq-pitch-700)]">Submit your answers?</h1>
        <p className="text-[var(--soccertactiq-text-muted)]">
          You won't be able to change your answers after submitting. You can retry the lesson
          later for a new attempt.
        </p>
        {submitError && (
          <p role="alert" className="text-sm text-[var(--soccertactiq-danger)]">
            {submitError}
          </p>
        )}
        <div className="flex w-full max-w-xs flex-col gap-3">
          <PrimaryButton onClick={handleConfirmSubmit} disabled={isSubmitting}>
            {isSubmitting ? 'Submitting…' : 'Yes, submit'}
          </PrimaryButton>
          <SecondaryButton onClick={() => setShowConfirm(false)} disabled={isSubmitting}>
            Go back and review
          </SecondaryButton>
        </div>
      </div>
    );
  }

  // --- One question at a time ---
  if (!currentQuestion) return null;
  const isLastQuestion = questionIndex === questions.length - 1;

  return (
    <div className="flex flex-1 flex-col gap-4">
      <p className="text-center text-sm font-semibold text-[var(--soccertactiq-text-muted)]">
        Question {questionIndex + 1} of {questions.length}
      </p>

      <fieldset className="flex flex-col gap-3">
        <legend className="text-lg font-semibold text-[var(--soccertactiq-text)]">
          {currentQuestion.prompt}
        </legend>
        {currentQuestion.choices.map((choice) => {
          const inputId = `choice-${choice.id}`;
          const checked = answers[currentQuestion.id] === choice.id;
          return (
            <label
              key={choice.id}
              htmlFor={inputId}
              className={`min-h-11 flex cursor-pointer items-center gap-3 rounded-lg border-2 px-3 py-3 ${
                checked
                  ? 'border-[var(--soccertactiq-pitch-500)] bg-[var(--soccertactiq-pitch-100)]'
                  : 'border-[var(--soccertactiq-border)]'
              }`}
            >
              <input
                id={inputId}
                type="radio"
                name={`question-${currentQuestion.id}`}
                checked={checked}
                onChange={() =>
                  setAnswers((prev) => ({ ...prev, [currentQuestion.id]: choice.id }))
                }
                className="h-5 w-5 shrink-0"
              />
              <span>{choice.text}</span>
            </label>
          );
        })}
      </fieldset>

      <div className="mt-auto flex gap-3 pt-4">
        <SecondaryButton
          onClick={() => setQuestionIndex((i) => (i === 0 ? -1 : i - 1))}
          className="flex-1"
        >
          Back
        </SecondaryButton>
        {isLastQuestion ? (
          <PrimaryButton
            onClick={() => setShowConfirm(true)}
            disabled={!allAnswered}
            className="flex-1"
          >
            Review &amp; submit
          </PrimaryButton>
        ) : (
          <PrimaryButton
            onClick={() => setQuestionIndex((i) => i + 1)}
            disabled={answers[currentQuestion.id] == null}
            className="flex-1"
          >
            Next
          </PrimaryButton>
        )}
      </div>
    </div>
  );
}
