from django.db import migrations, models


def copy_category_videos_into_video(apps, schema_editor):
    CategoryVideo = apps.get_model("content", "CategoryVideo")
    Video = apps.get_model("content", "Video")
    for cv in CategoryVideo.objects.all():
        Video.objects.create(
            title=cv.title,
            category=cv.category,
            description=cv.description,
            video_url=cv.video_url,
            video_start_seconds=cv.video_start_seconds,
            status=cv.status,
            is_placeholder_video=cv.is_placeholder_video,
            display_order=cv.display_order,
            created_at=cv.created_at,
            updated_at=cv.updated_at,
        )


def noop_reverse(apps, schema_editor):
    # Not reversible: once CategoryVideo rows are copied into Video and
    # CategoryVideo is dropped, there's no way to tell which Video rows
    # originated from CategoryVideo vs. were authored directly as Video.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("content", "0003_add_video"),
        # AttemptAnswer (progress) FKs into content.question and
        # content.answerchoice, dropped below — must be gone first.
        ("progress", "0002_drop_attempt"),
    ]

    operations = [
        migrations.RemoveField(model_name="answerchoice", name="question"),
        migrations.RemoveField(model_name="question", name="lesson"),
        migrations.DeleteModel(name="AnswerChoice"),
        migrations.DeleteModel(name="Question"),
        migrations.DeleteModel(name="Lesson"),
        migrations.AddField(
            model_name="video",
            name="category",
            field=models.CharField(
                default="",
                max_length=50,
                help_text='Free-text category, e.g. "Defense", "Midfield", '
                '"Work Ethics", "Drills". Matched exactly (case-sensitive) when '
                "players filter by category, so reuse existing spelling/casing "
                "for a category rather than creating near-duplicates.",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="video",
            name="display_order",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterModelOptions(
            name="video",
            options={"ordering": ["category", "display_order", "-created_at"]},
        ),
        migrations.RunPython(copy_category_videos_into_video, noop_reverse),
        migrations.DeleteModel(name="CategoryVideo"),
    ]
