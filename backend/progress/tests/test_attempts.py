from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from content.models import AnswerChoice, Lesson, Question
from progress.models import Attempt

User = get_user_model()


def make_lesson():
    lesson = Lesson.objects.create(
        title="Scoring Lesson",
        description="desc",
        learning_objective="objective",
        video_url="https://www.youtube.com/watch?v=PLACEHOLDER",
        is_placeholder_video=True,
        status=Lesson.Status.PUBLISHED,
    )
    q1 = Question.objects.create(lesson=lesson, prompt="Q1?", explanation="E1", display_order=1)
    q1_right = AnswerChoice.objects.create(question=q1, text="Right1", is_correct=True, display_order=1)
    AnswerChoice.objects.create(question=q1, text="Wrong1", is_correct=False, display_order=2)

    q2 = Question.objects.create(lesson=lesson, prompt="Q2?", explanation="E2", display_order=2)
    q2_right = AnswerChoice.objects.create(question=q2, text="Right2", is_correct=True, display_order=1)
    q2_wrong = AnswerChoice.objects.create(question=q2, text="Wrong2", is_correct=False, display_order=2)

    return lesson, q1, q1_right, q2, q2_right, q2_wrong


class AttemptSubmissionTests(APITestCase):
    """
    Covers: server-side scoring, invalid/mismatched choice rejection,
    repeated submissions not creating duplicates, and ownership checks.
    """

    def setUp(self):
        self.lesson, self.q1, self.q1_right, self.q2, self.q2_right, self.q2_wrong = make_lesson()
        self.user = User.objects.create_user(username="scorer", password="x")
        self.client.force_authenticate(user=self.user)

    def submit(self, idempotency_key="key-1", answers=None):
        if answers is None:
            answers = [
                {"question_id": self.q1.id, "choice_id": self.q1_right.id},
                {"question_id": self.q2.id, "choice_id": self.q2_wrong.id},
            ]
        return self.client.post(
            f"/api/lessons/{self.lesson.id}/attempts/",
            {"idempotency_key": idempotency_key, "answers": answers},
            format="json",
        )

    def test_scores_correctly_on_server(self):
        response = self.submit()
        self.assertEqual(response.status_code, 201)
        body = response.json()
        self.assertEqual(body["correct_count"], 1)
        self.assertEqual(body["question_count"], 2)
        self.assertEqual(float(body["score"]), 50.0)

    def test_response_includes_explanations_and_correct_answers(self):
        response = self.submit()
        body = response.json()
        for answer in body["answers"]:
            self.assertTrue(answer["question_explanation_snapshot"])
            self.assertTrue(answer["correct_choice_text_snapshot"])

    def test_missing_answer_for_a_question_rejected(self):
        response = self.submit(
            answers=[{"question_id": self.q1.id, "choice_id": self.q1_right.id}]
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Attempt.objects.count(), 0)

    def test_choice_from_wrong_question_rejected(self):
        response = self.submit(
            answers=[
                {"question_id": self.q1.id, "choice_id": self.q2_right.id},
                {"question_id": self.q2.id, "choice_id": self.q2_wrong.id},
            ]
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Attempt.objects.count(), 0)

    def test_nonexistent_choice_id_rejected(self):
        response = self.submit(
            answers=[
                {"question_id": self.q1.id, "choice_id": 999999},
                {"question_id": self.q2.id, "choice_id": self.q2_wrong.id},
            ]
        )
        self.assertEqual(response.status_code, 400)

    def test_extra_question_not_in_lesson_rejected(self):
        other_lesson, other_q, other_right, *_ = make_lesson()
        response = self.submit(
            answers=[
                {"question_id": self.q1.id, "choice_id": self.q1_right.id},
                {"question_id": self.q2.id, "choice_id": self.q2_wrong.id},
                {"question_id": other_q.id, "choice_id": other_right.id},
            ]
        )
        self.assertEqual(response.status_code, 400)

    def test_repeated_submission_same_key_does_not_duplicate(self):
        first = self.submit(idempotency_key="same-key")
        second = self.submit(idempotency_key="same-key")
        self.assertEqual(first.status_code, 201)
        self.assertEqual(second.status_code, 200)
        self.assertEqual(Attempt.objects.count(), 1)
        self.assertEqual(first.json()["id"], second.json()["id"])

    def test_retry_with_new_key_creates_new_attempt(self):
        self.submit(idempotency_key="key-a")
        self.submit(idempotency_key="key-b")
        self.assertEqual(Attempt.objects.count(), 2)

    def test_draft_lesson_rejects_submission(self):
        self.lesson.status = Lesson.Status.DRAFT
        self.lesson.save()
        response = self.submit()
        self.assertEqual(response.status_code, 404)

    def test_anonymous_cannot_submit(self):
        self.client.force_authenticate(user=None)
        response = self.submit()
        self.assertIn(response.status_code, (401, 403))


class AttemptOwnershipTests(APITestCase):
    """Covers: "One user being unable to read another user's attempts.\""""

    def setUp(self):
        self.lesson, self.q1, self.q1_right, self.q2, self.q2_right, self.q2_wrong = make_lesson()
        self.owner = User.objects.create_user(username="owner", password="x")
        self.intruder = User.objects.create_user(username="intruder", password="x")

        self.client.force_authenticate(user=self.owner)
        response = self.client.post(
            f"/api/lessons/{self.lesson.id}/attempts/",
            {
                "idempotency_key": "owner-key",
                "answers": [
                    {"question_id": self.q1.id, "choice_id": self.q1_right.id},
                    {"question_id": self.q2.id, "choice_id": self.q2_right.id},
                ],
            },
            format="json",
        )
        self.attempt_id = response.json()["id"]

    def test_owner_can_read_own_attempt(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.get(f"/api/attempts/{self.attempt_id}/")
        self.assertEqual(response.status_code, 200)

    def test_other_user_cannot_read_attempt(self):
        self.client.force_authenticate(user=self.intruder)
        response = self.client.get(f"/api/attempts/{self.attempt_id}/")
        self.assertEqual(response.status_code, 404)

    def test_other_user_progress_list_is_empty(self):
        self.client.force_authenticate(user=self.intruder)
        response = self.client.get("/api/progress/")
        self.assertEqual(response.json()["count"], 0)

    def test_owner_progress_list_includes_attempt(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.get("/api/progress/")
        self.assertEqual(response.json()["count"], 1)


class HistoricalAccuracyTests(APITestCase):
    """Covers: "Historical results staying accurate after lesson edits.\""""

    def setUp(self):
        self.lesson, self.q1, self.q1_right, self.q2, self.q2_right, self.q2_wrong = make_lesson()
        self.user = User.objects.create_user(username="historian", password="x")
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            f"/api/lessons/{self.lesson.id}/attempts/",
            {
                "idempotency_key": "hist-key",
                "answers": [
                    {"question_id": self.q1.id, "choice_id": self.q1_right.id},
                    {"question_id": self.q2.id, "choice_id": self.q2_wrong.id},
                ],
            },
            format="json",
        )
        self.attempt_id = response.json()["id"]
        self.original_explanation = self.q1.explanation
        self.original_choice_text = self.q1_right.text

    def test_editing_question_does_not_change_past_attempt(self):
        self.q1.explanation = "A totally different explanation now."
        self.q1.prompt = "A totally different prompt now."
        self.q1.save()
        self.q1_right.text = "A totally different choice text now."
        self.q1_right.save()

        response = self.client.get(f"/api/attempts/{self.attempt_id}/")
        body = response.json()
        q1_answer = next(a for a in body["answers"] if a["question"] == self.q1.id)

        self.assertEqual(q1_answer["question_explanation_snapshot"], self.original_explanation)
        self.assertEqual(q1_answer["selected_choice_text_snapshot"], self.original_choice_text)

    def test_archiving_lesson_preserves_attempt(self):
        self.lesson.status = Lesson.Status.UNAVAILABLE
        self.lesson.save()

        response = self.client.get(f"/api/attempts/{self.attempt_id}/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["lesson_title_snapshot"], self.lesson.title)
