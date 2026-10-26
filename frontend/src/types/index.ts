export interface CurrentUser {
  id: number;
  username: string;
  display_name: string;
  is_staff: boolean;
}

export interface LessonListItem {
  id: number;
  title: string;
  description: string;
  topic: string;
  status: 'draft' | 'published' | 'unavailable';
  is_completed: boolean;
  latest_score: string | null;
  latest_attempt_id: number | null;
}

export interface AnswerChoicePublic {
  id: number;
  text: string;
  display_order: number;
}

export interface QuestionPublic {
  id: number;
  prompt: string;
  display_order: number;
  choices: AnswerChoicePublic[];
}

export interface LessonDetail {
  id: number;
  title: string;
  description: string;
  learning_objective: string;
  topic: string;
  video_url: string;
  video_start_seconds: number | null;
  video_end_seconds: number | null;
  status: 'draft' | 'published' | 'unavailable';
  questions: QuestionPublic[];
}

export interface AttemptAnswerResult {
  question: number;
  question_prompt_snapshot: string;
  question_explanation_snapshot: string;
  selected_choice_text_snapshot: string;
  correct_choice_text_snapshot: string;
  is_correct: boolean;
}

export interface AttemptResult {
  id: number;
  lesson: number;
  lesson_title_snapshot: string;
  submitted_at: string;
  correct_count: number;
  question_count: number;
  score: string;
  answers: AttemptAnswerResult[];
}

export interface AttemptSummary {
  id: number;
  lesson: number;
  lesson_title_snapshot: string;
  submitted_at: string;
  correct_count: number;
  question_count: number;
  score: string;
}

export interface Paginated<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface AnswerSubmission {
  question_id: number;
  choice_id: number;
}


export type Position = 'fullback' | 'midfielder' | 'forward';

export interface PositionVideo {
  id: number;
  title: string;
  position: Position;
  description: string;
  video_url: string;
  video_start_seconds: number | null;
  display_order: number;
}
