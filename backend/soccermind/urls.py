"""
URL configuration for the SoccerMind project.

API namespace: everything under /api/ is documented in README.md. Auth
registration/login/logout is handled by django-allauth's headless API,
mounted at /_allauth/browser/v1/auth/ (not under /api/, since it's a
separably-versioned third-party surface) — see README.md "API reference"
for the exact endpoints the frontend calls.

Everything else falls through to the React SPA's index.html (see
soccermind.views.spa_index), so client-side routes like /dashboard or
/lessons/3 resolve correctly on a hard refresh. This view only exists
once the frontend has been built (see README.md's build step) — in
local dev the Vite dev server serves the SPA directly and this
fallback is simply unused.
"""
from django.contrib import admin
from django.urls import include, path, re_path

from . import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("_allauth/", include("allauth.headless.urls")),
    path("api/", include("api.urls")),
    re_path(r"^(?!static/).*$", views.spa_index, name="spa-index"),
]
