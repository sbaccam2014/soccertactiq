from django import forms
from django.contrib import admin, messages
from django.utils.html import format_html

from .models import AnswerChoice, Lesson, PositionVideo, Question


class AnswerChoiceInline(admin.TabularInline):
    model = AnswerChoice
    extra = 4
    min_num = 2
    fields = ("text", "is_correct", "display_order")


class QuestionAdminForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = "__all__"


class QuestionInline(admin.StackedInline):
    """
    Lets an admin create/edit/order a lesson's questions directly on the
    Lesson page. Choices are edited on the Question's own admin page
    (Django admin doesn't support nested inlines), linked here for
    convenience.
    """

    model = Question
    form = QuestionAdminForm
    extra = 0
    fields = ("prompt", "explanation", "display_order", "edit_choices_link")
    readonly_fields = ("edit_choices_link",)

    def edit_choices_link(self, obj):
        if not obj or not obj.pk:
            return "Save the lesson first, then edit this question to add choices."
        return format_html(
            '<a href="/admin/content/question/{}/change/">Edit choices for this question &rarr;</a>',
            obj.pk,
        )

    edit_choices_link.short_description = "Choices"


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("prompt_preview", "lesson", "display_order", "choice_count")
    list_filter = ("lesson",)
    inlines = [AnswerChoiceInline]
    fields = ("lesson", "prompt", "explanation", "display_order")

    def prompt_preview(self, obj):
        return obj.prompt[:70]

    prompt_preview.short_description = "Prompt"

    def choice_count(self, obj):
        return obj.choices.count()

    choice_count.short_description = "Choices"

    def save_formset(self, request, form, formset, change):
        super().save_formset(request, form, formset, change)
        if formset.model is AnswerChoice:
            question = form.instance
            correct_count = question.choices.filter(is_correct=True).count()
            if correct_count != 1:
                self.message_user(
                    request,
                    f'"{question.prompt[:50]}" has {correct_count} correct '
                    "choices marked — it must have exactly one. Fix it "
                    "before publishing the lesson.",
                    level=messages.WARNING,
                )


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "status",
        "topic",
        "question_count",
        "is_placeholder_video",
        "updated_at",
    )
    list_filter = ("status", "is_placeholder_video")
    search_fields = ("title", "description", "topic")
    inlines = [QuestionInline]
    actions = ["publish_lessons", "unpublish_lessons", "mark_unavailable"]
    fieldsets = (
        (None, {"fields": ("title", "description", "learning_objective", "topic")}),
        (
            "Video",
            {
                "fields": (
                    "video_url",
                    "video_start_seconds",
                    "video_end_seconds",
                    "is_placeholder_video",
                )
            },
        ),
        ("Publishing", {"fields": ("status",)}),
    )

    def question_count(self, obj):
        return obj.questions.count()

    question_count.short_description = "Questions"

    def _validate_publishable(self, lesson) -> list[str]:
        problems = []
        questions = list(lesson.questions.all())
        if not questions:
            problems.append(f'"{lesson.title}" has no questions.')
        for question in questions:
            correct_count = question.choices.filter(is_correct=True).count()
            total = question.choices.count()
            if total < 2:
                problems.append(
                    f'"{lesson.title}": question "{question.prompt[:40]}" '
                    "needs at least two choices."
                )
            if correct_count != 1:
                problems.append(
                    f'"{lesson.title}": question "{question.prompt[:40]}" '
                    f"has {correct_count} correct choices marked (needs exactly 1)."
                )
        return problems

    @admin.action(description="Publish selected lessons")
    def publish_lessons(self, request, queryset):
        published = 0
        for lesson in queryset:
            problems = self._validate_publishable(lesson)
            if problems:
                for problem in problems:
                    self.message_user(request, problem, level=messages.ERROR)
                continue
            lesson.status = Lesson.Status.PUBLISHED
            lesson.save(update_fields=["status"])
            published += 1
        if published:
            self.message_user(
                request, f"Published {published} lesson(s).", level=messages.SUCCESS
            )

    @admin.action(description="Unpublish selected lessons (back to draft)")
    def unpublish_lessons(self, request, queryset):
        count = queryset.update(status=Lesson.Status.DRAFT)
        self.message_user(request, f"Unpublished {count} lesson(s).")

    @admin.action(description="Mark selected lessons unavailable")
    def mark_unavailable(self, request, queryset):
        count = queryset.update(status=Lesson.Status.UNAVAILABLE)
        self.message_user(
            request,
            f"Marked {count} lesson(s) unavailable. Historic attempts are "
            "preserved.",
        )


@admin.register(PositionVideo)
class PositionVideoAdmin(admin.ModelAdmin):
    """
    A lightweight library of reference videos organized by playing
    position (fullback / midfielder / forward) — separate from the
    quiz-based Lessons above. No questions, no scoring; just a curated
    set of links players can browse by their position.
    """

    list_display = (
        "title",
        "position",
        "status",
        "is_placeholder_video",
        "display_order",
        "updated_at",
    )
    list_filter = ("position", "status", "is_placeholder_video")
    search_fields = ("title", "description")
    actions = ["publish_videos", "unpublish_videos", "mark_unavailable"]
    fieldsets = (
        (None, {"fields": ("title", "position", "description", "display_order")}),
        (
            "Video",
            {
                "fields": (
                    "video_url",
                    "video_start_seconds",
                    "is_placeholder_video",
                )
            },
        ),
        ("Publishing", {"fields": ("status",)}),
    )

    @admin.action(description="Publish selected videos")
    def publish_videos(self, request, queryset):
        count = queryset.update(status=PositionVideo.Status.PUBLISHED)
        self.message_user(request, f"Published {count} video(s).", level=messages.SUCCESS)

    @admin.action(description="Unpublish selected videos (back to draft)")
    def unpublish_videos(self, request, queryset):
        count = queryset.update(status=PositionVideo.Status.DRAFT)
        self.message_user(request, f"Unpublished {count} video(s).")

    @admin.action(description="Mark selected videos unavailable")
    def mark_unavailable(self, request, queryset):
        count = queryset.update(status=PositionVideo.Status.UNAVAILABLE)
        self.message_user(request, f"Marked {count} video(s) unavailable.")
