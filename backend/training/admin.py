from django.contrib import admin

from .models import TrainingLog


@admin.register(TrainingLog)
class TrainingLogAdmin(admin.ModelAdmin):
    """
    Read-only in admin: training logs are written by players through
    the app, not something staff should hand-edit. Useful for a coach
    to spot-check whether a player is logging consistently.
    """

    list_display = ("player_profile", "date", "trained", "updated_at")
    list_filter = ("trained", "date")
    search_fields = ("player_profile__display_name", "player_profile__user__username")
    readonly_fields = ("player_profile", "date", "trained", "created_at", "updated_at")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser
