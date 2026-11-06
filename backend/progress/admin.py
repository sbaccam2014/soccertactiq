from django.contrib import admin

from .models import VideoWatch


@admin.register(VideoWatch)
class VideoWatchAdmin(admin.ModelAdmin):
    """
    Read-only in admin: watch records are historical facts written by
    the API, not something staff should hand-edit. Useful for support
    (e.g. confirming whether a player actually watched a video).
    """

    list_display = ("player_profile", "video_title_snapshot", "watched_at")
    list_filter = ("video",)
    search_fields = ("player_profile__display_name", "player_profile__user__username")
    readonly_fields = ("player_profile", "video", "video_title_snapshot", "watched_at")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser
