from django.contrib import admin

from .models import Attempt, AttemptAnswer


class AttemptAnswerInline(admin.TabularInline):
    model = AttemptAnswer
    extra = 0
    can_delete = False
    fields = (
        "question_prompt_snapshot",
        "selected_choice_text_snapshot",
        "correct_choice_text_snapshot",
        "is_correct",
    )
    readonly_fields = fields


@admin.register(Attempt)
class AttemptAdmin(admin.ModelAdmin):
    """
    Read-only in admin: attempts are historical records written by the
    scoring API, not something staff should hand-edit. Useful for support
    (e.g. confirming what a player saw and answered).
    """

    list_display = (
        "player_profile",
        "lesson_title_snapshot",
        "score",
        "correct_count",
        "question_count",
        "submitted_at",
    )
    list_filter = ("lesson",)
    search_fields = ("player_profile__display_name", "player_profile__user__username")
    inlines = [AttemptAnswerInline]
    readonly_fields = (
        "player_profile",
        "lesson",
        "lesson_title_snapshot",
        "submitted_at",
        "correct_count",
        "question_count",
        "score",
        "idempotency_key",
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        # Historic results should be preserved; staff can still delete via
        # the database directly if ever truly needed (e.g. data deletion
        # request), but not casually through this list view.
        return request.user.is_superuser
