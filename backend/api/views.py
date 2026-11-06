from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView


class CurrentUserView(APIView):
    """
    GET /api/auth/me/ — the authenticated player's own identity. A thin
    SoccerTactiq-shaped convenience endpoint; registration/login/logout themselves
    are handled by django-allauth's headless API (see README.md "API
    reference"), not duplicated here.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        profile = getattr(user, "player_profile", None)
        return Response(
            {
                "id": user.id,
                "username": user.username,
                "display_name": (profile.display_name if profile else "") or user.username,
                "is_staff": user.is_staff,
                "is_coach": user.is_coach,
                "is_parent": user.is_parent,
            }
        )
