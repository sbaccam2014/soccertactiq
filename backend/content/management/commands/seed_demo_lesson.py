from django.core.management.base import BaseCommand
from django.db import transaction

from content.models import AnswerChoice, Lesson, Question

SEED_TITLE = "Create a Passing Option"


class Command(BaseCommand):
    help = (
        "Create (or update) the one seed lesson described in the BSA "
        "build brief: 'Create a Passing Option', as a DRAFT with a "
        "clearly-marked placeholder video. Safe to run more than once — "
        "it updates the existing seed lesson in place rather than "
        "duplicating it."
    )

    def handle(self, *args, **options):
        with transaction.atomic():
            lesson, created = Lesson.objects.update_or_create(
                title=SEED_TITLE,
                defaults=dict(
                    description=(
                        "Illustrative lesson on creating a clear passing "
                        "option: moving to open an angle, checking toward "
                        "the ball, and receiving with good body position. "
                        "Questions are illustrative until matched to an "
                        "actual clip."
                    ),
                    learning_objective=(
                        "Recognize how movement off the ball — angle, "
                        "timing, and body position — creates a usable "
                        "passing option for a teammate under pressure."
                    ),
                    topic="Passing angles & movement off the ball",
                    video_url="https://www.youtube.com/watch?v=PLACEHOLDER",
                    is_placeholder_video=True,
                    status=Lesson.Status.DRAFT,
                ),
            )
            lesson.questions.all().delete()  # clean re-seed of questions/choices

            q1 = Question.objects.create(
                lesson=lesson,
                display_order=1,
                prompt=(
                    "Illustrative scenario: a player is standing directly "
                    "behind a defender, blocking any pass from their "
                    "teammate on the ball. What is the best next movement "
                    "to create a passing option?"
                ),
                explanation=(
                    "Standing behind a defender puts the defender's body "
                    "in the passing lane, so no safe pass exists no "
                    "matter how well the ball is struck. Moving to open a "
                    "new angle — stepping to one side so the defender is "
                    "no longer between the ball and the receiver — gives "
                    "the passer a lane that doesn't require going through "
                    "an opponent."
                ),
            )
            AnswerChoice.objects.bulk_create(
                [
                    AnswerChoice(
                        question=q1,
                        display_order=1,
                        text="Stay still and call loudly for the ball",
                        is_correct=False,
                    ),
                    AnswerChoice(
                        question=q1,
                        display_order=2,
                        text="Move sideways to open a clear angle away from the defender's body",
                        is_correct=True,
                    ),
                    AnswerChoice(
                        question=q1,
                        display_order=3,
                        text="Sprint directly toward the goal regardless of the defender's position",
                        is_correct=False,
                    ),
                    AnswerChoice(
                        question=q1,
                        display_order=4,
                        text="Stand even closer behind the defender to shield them from the ball",
                        is_correct=False,
                    ),
                ]
            )

            q2 = Question.objects.create(
                lesson=lesson,
                display_order=2,
                prompt=(
                    "Illustrative scenario: a teammate on the ball has no "
                    "short passing option and is under pressure. What "
                    "should a nearby teammate who wants to help do?"
                ),
                explanation=(
                    "Checking toward the ball — taking a few steps closer "
                    "to the teammate on the ball — shortens the distance "
                    "and the time a pass needs to travel, making it "
                    "harder for a defender to intercept and giving the "
                    "passer a safer, quicker option under pressure."
                ),
            )
            AnswerChoice.objects.bulk_create(
                [
                    AnswerChoice(
                        question=q2,
                        display_order=1,
                        text="Check toward the ball to offer a short, quick option",
                        is_correct=True,
                    ),
                    AnswerChoice(
                        question=q2,
                        display_order=2,
                        text="Move further away to stay spread out from the ball",
                        is_correct=False,
                    ),
                    AnswerChoice(
                        question=q2,
                        display_order=3,
                        text="Stand still and wait to see what happens",
                        is_correct=False,
                    ),
                    AnswerChoice(
                        question=q2,
                        display_order=4,
                        text="Run in behind the defense immediately",
                        is_correct=False,
                    ),
                ]
            )

            q3 = Question.objects.create(
                lesson=lesson,
                display_order=3,
                prompt=(
                    "Illustrative scenario: a player is about to receive a "
                    "pass with a defender close behind them. What body "
                    "position best helps them see and play the next pass?"
                ),
                explanation=(
                    "An open, side-on body position lets a player see "
                    "both the ball and most of the field in front of them "
                    "in the same glance, so they can control the ball and "
                    "immediately spot the next pass. Receiving square "
                    "with their back fully to the field hides the play "
                    "developing behind them and forces a slower turn "
                    "before they can even see their options."
                ),
            )
            AnswerChoice.objects.bulk_create(
                [
                    AnswerChoice(
                        question=q3,
                        display_order=1,
                        text="Face the ball with their back fully to the field",
                        is_correct=False,
                    ),
                    AnswerChoice(
                        question=q3,
                        display_order=2,
                        text="Open their body side-on so they can see the ball and the field at once",
                        is_correct=True,
                    ),
                    AnswerChoice(
                        question=q3,
                        display_order=3,
                        text="Close their eyes and control the ball by feel",
                        is_correct=False,
                    ),
                    AnswerChoice(
                        question=q3,
                        display_order=4,
                        text="Turn away from the ball before it arrives",
                        is_correct=False,
                    ),
                ]
            )

        verb = "Created" if created else "Updated"
        self.stdout.write(
            self.style.SUCCESS(
                f'{verb} seed lesson "{SEED_TITLE}" (id={lesson.id}) as DRAFT '
                "with a placeholder video. Publish it from Django admin "
                "once reviewed (and replace the placeholder video_url "
                "with a real, authorized video before publishing for real "
                "players)."
            )
        )
