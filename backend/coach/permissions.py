from rest_framework import permissions


class IsCoach(permissions.BasePermission):
    """Grants access only to authenticated users with is_coach=True."""

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.is_coach
        )
