from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView


class CurrentUserView(APIView):
    """
    GET /api/auth/me/ — the authenticated player's own identity. A thin
    SoccerMind-shaped convenience endpoint; registration/login/logout themselves
    are handled by django-allauth's headless API (see README.md "API
    reference"), not duplicated here.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        profile = user.player_profile
        return Response(
            {
                "id": user.id,
                "username": user.username,
                "display_name": profile.display_name or user.username,
                "is_staff": user.is_staff,
            }
        )
