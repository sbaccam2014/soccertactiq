#!/usr/bin/env bash
# Production build: compiles the React frontend and places its output
# where Django expects to find it (see backend/bsa/settings.py
# STATICFILES_DIRS and backend/bsa/views.py spa_index), then runs
# collectstatic. Run this from the repo root before deploying, and as
# part of the Railway build command (see README.md "Deploying to
# Railway").
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FRONTEND_DIR="$REPO_ROOT/frontend"
BACKEND_DIR="$REPO_ROOT/backend"
FRONTEND_STATIC_DIR="$BACKEND_DIR/staticfiles_frontend"

echo "==> Installing frontend dependencies"
cd "$FRONTEND_DIR"
npm ci

echo "==> Type-checking and building frontend"
npm run build

echo "==> Copying frontend build into backend/staticfiles_frontend"
rm -rf "$FRONTEND_STATIC_DIR"
mkdir -p "$FRONTEND_STATIC_DIR"
cp -r "$FRONTEND_DIR"/dist/. "$FRONTEND_STATIC_DIR"/

echo "==> Installing backend dependencies"
cd "$BACKEND_DIR"
pip install -r requirements.txt

echo "==> Running collectstatic"
python manage.py collectstatic --noinput

echo "==> Build complete"
