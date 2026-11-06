from django.contrib import admin, messages

from .models import Video


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    """
    The category list filter (sidebar on the list view) doubles as a
    quick way to see every category name already in use, so an admin
    typing a new video's category can check there for existing
    spelling/casing before introducing a near-duplicate like "defense"
    vs "Defense".
    """

    list_display = (
        "title",
        "category",
        "status",
        "is_placeholder_video",
        "display_order",
        "created_by",
        "updated_at",
    )
    list_filter = ("category", "status", "is_placeholder_video", "created_by")
    search_fields = ("title", "description", "category")
    actions = ["publish_videos", "unpublish_videos", "mark_unavailable"]
    readonly_fields = ("created_by", "description")
    fieldsets = (
        (None, {"fields": ("title", "category", "description", "display_order")}),
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
        ("Authorship", {"fields": ("created_by",)}),
    )

    @admin.action(description="Publish selected videos")
    def publish_videos(self, request, queryset):
        count = queryset.update(status=Video.Status.PUBLISHED)
        self.message_user(request, f"Published {count} video(s).", level=messages.SUCCESS)

    @admin.action(description="Unpublish selected videos (back to draft)")
    def unpublish_videos(self, request, queryset):
        count = queryset.update(status=Video.Status.DRAFT)
        self.message_user(request, f"Unpublished {count} video(s).")

    @admin.action(description="Mark selected videos unavailable")
    def mark_unavailable(self, request, queryset):
        count = queryset.update(status=Video.Status.UNAVAILABLE)
        self.message_user(
            request,
            f"Marked {count} video(s) unavailable. Historic watch records are "
            "preserved.",
        )
