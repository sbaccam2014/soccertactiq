from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0004_drop_quiz_and_merge_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='video',
            name='description',
            field=models.TextField(blank=True, editable=False, help_text='Shown on the dashboard and video screen. Fetched automatically from YouTube when video_url is set — not hand-edited.'),
        ),
    ]
