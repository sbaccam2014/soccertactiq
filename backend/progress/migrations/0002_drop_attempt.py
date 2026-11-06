from django.db import migrations


class Migration(migrations.Migration):
    """
    Drops the quiz-attempt tables. Must apply before content's migration
    that drops Lesson/Question/AnswerChoice, since AttemptAnswer holds FKs
    into content.question and content.answerchoice.
    """

    dependencies = [
        ("progress", "0001_initial"),
    ]

    run_before = [
        ("content", "0004_drop_quiz_and_merge_category"),
    ]

    operations = [
        migrations.RemoveField(model_name="attemptanswer", name="attempt"),
        migrations.RemoveField(model_name="attemptanswer", name="question"),
        migrations.RemoveField(model_name="attemptanswer", name="selected_choice"),
        migrations.RemoveField(model_name="attempt", name="lesson"),
        migrations.RemoveField(model_name="attempt", name="player_profile"),
        migrations.DeleteModel(name="AttemptAnswer"),
        migrations.DeleteModel(name="Attempt"),
    ]
