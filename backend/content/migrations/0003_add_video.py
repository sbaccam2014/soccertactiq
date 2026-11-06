import content.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("content", "0002_categoryvideo"),
    ]

    operations = [
        migrations.CreateModel(
            name="Video",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=200)),
                ("description", models.TextField(blank=True, help_text="Shown on the dashboard and video screen.")),
                ("video_url", models.URLField(help_text="An ordinary youtube.com/watch, youtube.com/embed, youtube.com/shorts, or youtu.be link. Use the clearly-marked placeholder for unreviewed seed content.", max_length=500, validators=[content.validators.validate_youtube_url], verbose_name="YouTube URL")),
                ("video_start_seconds", models.PositiveIntegerField(blank=True, help_text="Optional: where players should start watching.", null=True)),
                ("status", models.CharField(choices=[("draft", "Draft"), ("published", "Published"), ("unavailable", "Unavailable")], default="draft", max_length=20)),
                ("is_placeholder_video", models.BooleanField(default=False, help_text="Mark on if video_url is a placeholder rather than a reviewed, real video. Shown to admins; not asserted to players as fact about an unwatched video.")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
    ]
