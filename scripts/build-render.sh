#!/usr/bin/env bash
# Render-specific production build: same as scripts/build.sh (frontend
# build -> copy into backend/staticfiles_frontend -> collectstatic),
# plus running migrations here rather than in the start command.
#
# This differs from Railway's build/start split (see scripts/build.sh
# and the Procfile) because Render's web service start command is
# expected to be a single long-running process — gunicorn itself, not
# a "migrate && gunicorn" chain — so migrations run once per deploy, in
# the build step, instead of on every process (re)start.
#
# Use this as Render's Build Command. See README.md "Deploying to
# Render (free tier)".
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

bash "$REPO_ROOT/scripts/build.sh"

echo "==> Running migrations"
cd "$REPO_ROOT/backend"
python manage.py migrate --noinput

echo "==> Render build complete"
