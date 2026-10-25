from pathlib import Path

from django.conf import settings
from django.http import HttpResponse, HttpResponseNotFound

_FRONTEND_INDEX = settings.BASE_DIR / "staticfiles_frontend" / "index.html"


def spa_index(request):
    """
    Serves the built React SPA's index.html for any route that isn't
    /admin/, /_allauth/, /api/, or /static/ — i.e. every client-side
    route (/, /login, /dashboard, /lessons/3, ...). React Router then
    takes over in the browser. See README.md for the build step that
    populates staticfiles_frontend/ before this file exists.
    """
    if not _FRONTEND_INDEX.exists():
        return HttpResponseNotFound(
            "Frontend build not found. Run the frontend build step described "
            "in README.md (npm run build, then copy dist/ into "
            "backend/staticfiles_frontend/) before serving this route."
        )
    return HttpResponse(Path(_FRONTEND_INDEX).read_text(), content_type="text/html")
