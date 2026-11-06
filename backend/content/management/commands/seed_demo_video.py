from django.core.management.base import BaseCommand
from django.db import transaction

from content.models import Video

SEED_TITLE = "Create a Passing Option"


class Command(BaseCommand):
    help = (
        "Create (or update) the one seed video described in the SoccerTactiq "
        "build brief: 'Create a Passing Option', as a DRAFT with a "
        "clearly-marked placeholder video. Safe to run more than once — "
        "it updates the existing seed video in place rather than "
        "duplicating it."
    )

    def handle(self, *args, **options):
        with transaction.atomic():
            video, created = Video.objects.update_or_create(
                title=SEED_TITLE,
                defaults=dict(
                    category="Midfield",
                    description=(
                        "Illustrative video on creating a clear passing "
                        "option: moving to open an angle, checking toward "
                        "the ball, and receiving with good body position."
                    ),
                    video_url="https://www.youtube.com/watch?v=PLACEHOLDER",
                    is_placeholder_video=True,
                    status=Video.Status.DRAFT,
                ),
            )

        verb = "Created" if created else "Updated"
        self.stdout.write(
            self.style.SUCCESS(
                f'{verb} seed video "{SEED_TITLE}" (id={video.id}) as DRAFT '
                "with a placeholder video. Publish it from Django admin "
                "once reviewed (and replace the placeholder video_url "
                "with a real, authorized video before publishing for real "
                "players)."
            )
        )
