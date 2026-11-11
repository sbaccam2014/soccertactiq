from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import BsaUserChangeForm, BsaUserCreationForm
from .models import CoachAssignment, ParentLink, PlayerProfile, Team, User


@admin.register(User)
class BsaUserAdmin(UserAdmin):
    """
    Standard Django UserAdmin, pointed at our custom User model. Staff
    manage accounts here (e.g. administrator-assisted password resets —
    see README for the documented process since there is no self-serve
    email-based reset without a verified email on file).
    """

    add_form = BsaUserCreationForm
    form = BsaUserChangeForm
    ordering = ("username",)
    search_fields = ("username", "email")
    list_display = ("username", "email", "is_coach", "is_parent", "is_staff", "is_active")
    list_filter = ("is_coach", "is_parent", "is_staff", "is_superuser", "is_active")
    fieldsets = UserAdmin.fieldsets + (
        ("Coach access", {"fields": ("is_coach",)}),
        ("Parent access", {"fields": ("is_parent",)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Coach access", {"fields": ("is_coach",)}),
        ("Parent access", {"fields": ("is_parent",)}),
    )


class PlayerProfileInline(admin.StackedInline):
    model = PlayerProfile
    extra = 0


class CoachAssignmentInline(admin.TabularInline):
    model = CoachAssignment
    extra = 1
    autocomplete_fields = ("coach",)


class ParentLinkInline(admin.TabularInline):
    model = ParentLink
    extra = 1
    autocomplete_fields = ("parent",)


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at")
    search_fields = ("name",)


@admin.register(PlayerProfile)
class PlayerProfileAdmin(admin.ModelAdmin):
    list_display = ("display_name", "user", "team", "created_at")
    list_filter = ("team",)
    search_fields = ("display_name", "user__username")
    autocomplete_fields = ("user", "team")
    inlines = (CoachAssignmentInline, ParentLinkInline)


@admin.register(CoachAssignment)
class CoachAssignmentAdmin(admin.ModelAdmin):
    list_display = ("coach", "player_profile", "created_at")
    search_fields = ("coach__username", "player_profile__display_name", "player_profile__user__username")
    autocomplete_fields = ("coach", "player_profile")


@admin.register(ParentLink)
class ParentLinkAdmin(admin.ModelAdmin):
    list_display = ("parent", "player_profile", "created_at")
    search_fields = ("parent__username", "player_profile__display_name", "player_profile__user__username")
    autocomplete_fields = ("parent", "player_profile")
