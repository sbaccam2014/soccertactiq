"""
URL configuration for the BSA project.

API namespace: everything under /api/ is documented in README.md. Auth
registration/login/logout is handled by django-allauth's headless API,
mounted at /_allauth/browser/v1/auth/ (not under /api/, since it's a
separably-versioned third-party surface) — see README.md "API reference"
for the exact endpoints the frontend calls.
"""
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("_allauth/", include("allauth.headless.urls")),
    path("api/", include("api.urls")),
]
