from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import BsaUserChangeForm, BsaUserCreationForm
from .models import PlayerProfile, User


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


class PlayerProfileInline(admin.StackedInline):
    model = PlayerProfile
    extra = 0


@admin.register(PlayerProfile)
class PlayerProfileAdmin(admin.ModelAdmin):
    list_display = ("display_name", "user", "created_at")
    search_fields = ("display_name", "user__username")
    autocomplete_fields = ("user",)
