# Baccam Soccer Academy (BSA)

A mobile-first youth soccer learning web app. Players watch a short
YouTube clip, answer a few questions about reading the game (scanning,
passing angles, movement off the ball, supporting teammates), and get
scored explanations of the soccer reasoning — not just right/wrong.

This README covers local setup, running tests, content authoring, and
deploying to Railway.

## Stack

- **Frontend**: React + TypeScript, Vite, Tailwind CSS (`frontend/`)
- **Backend**: Python + Django + Django REST Framework (`backend/`)
- **Database**: PostgreSQL (dev and prod)
- **Auth**: Django sessions + django-allauth, headless mode (JSON API, no
  server-rendered auth pages), username + password only
- **Content administration**: Django admin
- **Deployment target**: Railway (app + Postgres as separate services)

In production, Django serves both `/api/` and the built React app from
one origin — see "Deploying to Railway" below for why, and
`scripts/build.sh` for how the React build gets into Django's static
files.

## Prerequisites

- Python 3.12 (project was built and tested against 3.12.13; Django 5.2
  also supports 3.10+ if that's what you have)
- Node.js 20+ and npm
- PostgreSQL 16 (or any reasonably recent Postgres)
- `git`

On macOS with Homebrew:

```bash
brew install python@3.12 postgresql@16
brew services start postgresql@16
```

## Local setup

### 1. Clone and create the database

```bash
git clone <your-fork-or-remote-url> baccam-soccer-academy
cd baccam-soccer-academy

# Create a local Postgres role + database for development.
# (Adjust the password; it only needs to match backend/.env below.)
psql postgres -c "CREATE ROLE bsa_dev WITH LOGIN PASSWORD 'bsa_dev_local_pw' CREATEDB;"
psql postgres -c "CREATE DATABASE bsa_dev OWNER bsa_dev;"
```

### 2. Backend

```bash
cd backend
python3.12 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# Edit .env: at minimum set DJANGO_SECRET_KEY to a random string
# (python -c "from django.core.management.utils import get_random_secret_key as g; print(g())")
# and confirm DATABASE_URL matches the role/database you just created.

python manage.py migrate
python manage.py createsuperuser   # for Django admin access
python manage.py seed_demo_lesson  # creates the one seed lesson as a draft
```

Run the backend:

```bash
python manage.py runserver
```

The API is now live at `http://127.0.0.1:8000/`. Django admin is at
`http://127.0.0.1:8000/admin/`.

### 3. Frontend

In a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173/`. The Vite dev server proxies `/api/`,
`/_allauth/`, `/admin/`, and `/static/` to the Django dev server (see
`frontend/vite.config.ts`), so the browser only ever talks to one origin
during development — the same way it will in production — and session
cookies/CSRF behave identically to production from day one.

### 4. Try it out

1. Go to `http://localhost:5173/`, register a player account.
2. In Django admin (`/admin/`), open **Lessons & questions → Lessons**,
   open "Create a Passing Option", and use the **Publish selected
   lessons** admin action (select it in the lessons list, not the detail
   page) to publish it. It will refuse to publish if any question
   doesn't have exactly one correct choice.
3. Back in the app, the lesson now appears on the dashboard. Complete it
   and confirm the result shows on **My Progress**, and still shows
   after logging out and back in.

## Running tests

Backend (Django's test runner, against a disposable test database on
the same Postgres server as `DATABASE_URL`):

```bash
cd backend
source .venv/bin/activate
python manage.py test
```

As of this writing: **42 tests, all passing.** They cover:
registration/login/logout and case-insensitive username uniqueness; one
user being unable to read another user's attempts; server-side scoring
and rejection of invalid/mismatched choice submissions; hidden answer
keys and unpublished/draft/unavailable lessons; duplicate-submission
prevention via idempotency keys; historical attempt accuracy after
lesson/question edits; and Django admin's publish-validation and
staff-only access.

Frontend type-check, lint, and production build:

```bash
cd frontend
npx tsc -b        # type check
npx oxlint src     # lint
npm run build      # production build (also type-checks)
```

All three currently pass cleanly (lint has a few informational-only
`react(set-state-in-effect)`/`react(only-export-components)` warnings
from idiomatic data-fetching-on-mount and provider+hook co-location
patterns — not errors, and not indicative of bugs).

## Content authoring workflow (Django admin)

No separate coach dashboard exists in this version — all lesson
authoring happens in Django admin at `/admin/`, under **Lessons &
questions**.

1. **Create a lesson** (Lessons → Add lesson): title, description,
   learning objective, topic, and a YouTube URL (see "YouTube links"
   below for the allowed formats). Optional start/end timestamps give
   players "watch from X to Y" guidance. New lessons start as **Draft**
   and are invisible to players.
2. **Add questions and choices**: on the lesson's edit page, add
   questions inline (prompt, explanation, display order). Each
   question's answer choices are edited on the *question's own* admin
   page (Django admin doesn't support nesting inlines two levels deep;
   the lesson page links directly to each question's edit page once
   saved). Give each question at least two choices with **exactly one**
   marked "is correct."
3. **Preview**: there's no dedicated preview screen — view the lesson as
   a draft through the player app by logging in as a staff user's own
   player account, or simply read it back in admin. (A true preview mode
   is a reasonable follow-up, not required for this version.)
4. **Publish**: from the **Lessons** list (not the edit page), select
   the lesson's checkbox and choose the **"Publish selected lessons"**
   action. This validates that every question has at least two choices
   and exactly one correct choice, and refuses to publish (with an
   error message naming the problem) otherwise.
5. **Unpublish / mark unavailable**: same list-action pattern —
   "Unpublish selected lessons" returns a lesson to Draft; "Mark
   selected lessons unavailable" is for a lesson whose video has become
   unavailable (see below) — historic attempts against it are preserved
   either way, since results are snapshotted at submission time and
   don't depend on the lesson still being published.
6. **Editing a published lesson**: edits to a question's prompt,
   explanation, or choice text take effect immediately for players who
   haven't yet attempted the lesson, and never change how a *past*
   attempt is displayed (each `AttemptAnswer` snapshots the prompt,
   explanation, selected choice text, and correct choice text as they
   were at submission time).
7. **If a video link breaks or is taken down**: edit the lesson's
   `video_url` to a working replacement and keep the lesson published,
   or use "Mark selected lessons unavailable" if no replacement is
   available yet. Either way, players' existing results for that lesson
   remain intact and accurate.

### YouTube links

- Only plain `youtube.com/watch?v=...`, `youtube.com/embed/...`, and
  `youtu.be/...` URLs are accepted (enforced by
  `content.validators.validate_youtube_url`); anything else is rejected
  at save time in admin.
- The backend **never fetches** the URL — it's stored and handed to the
  player as an ordinary link that opens in a new tab, exactly as
  entered (with a `?t=` timestamp appended if a start time is set). No
  scraping, downloading, rehosting, or playback-restriction bypass of
  any kind.
- The seed lesson ships with a clearly-marked placeholder
  (`https://www.youtube.com/watch?v=PLACEHOLDER`, with
  `is_placeholder_video` checked) rather than a real video ID — replace
  it with a real, authorized video before publishing for actual players.
  Public availability of a video doesn't by itself establish permission
  to use it; prefer official/authorized uploads and verify rights before
  publishing.

### Administrator-assisted password reset

There is no self-serve, email-based password reset in this version
(the brief's account model is username + password only, no email
required). To reset a player's password:

1. In Django admin, confirm the requester's identity through whatever
   out-of-band means your organization uses (e.g. a parent/coach who
   already knows the player in person) — **never reset a password
   solely because someone supplied a username**, since usernames aren't
   secret.
2. Open **Accounts → Users**, find the account, and use the "this form
   doesn't change the password" link / the separate **"Change
   password"** admin link Django provides on the user's edit page to set
   a new temporary password.
3. Tell the player (or their parent/coach) the new password through a
   channel you've already verified belongs to them, and ask them to
   change it after logging in if you want extra hygiene (not enforced
   by the app in this version).

This is intentionally a manual, human-verified process — the brief
explicitly asks for identity verification rather than any automated
"reset by username" flow.

## API reference

Base path for BSA's own endpoints: `/api/`. Registration/login/logout
are handled by django-allauth's **headless** API instead of custom
endpoints, mounted separately at `/_allauth/browser/v1/`.

All endpoints below (except registration/login) require an
authenticated session; anonymous requests get 401/403.

### Auth (django-allauth headless, browser/session-cookie client)

| Action | Method | Path |
| --- | --- | --- |
| Get current session | GET | `/_allauth/browser/v1/auth/session` |
| Register | POST | `/_allauth/browser/v1/auth/signup` — body `{"username", "password"}` |
| Log in | POST | `/_allauth/browser/v1/auth/login` — body `{"username", "password"}` |
| Log out | DELETE | `/_allauth/browser/v1/auth/session` — **returns 401 by design** (the resulting, now-unauthenticated session state); this is the expected successful outcome, not an error |

A GET to the session endpoint also sets the `csrftoken` cookie, which
every subsequent non-GET request must echo back as the `X-CSRFToken`
header (see `frontend/src/api/client.ts`). Registration and login are
rate-limited server-side (`ACCOUNT_RATE_LIMITS` in `bsa/settings.py`).

### BSA API (`/api/`)

| Action | Method | Path | Notes |
| --- | --- | --- | --- |
| Current user | GET | `/api/auth/me/` | id, username, display name, staff flag |
| List published lessons | GET | `/api/lessons/` | paginated; includes each lesson's completion status + latest score for the current player |
| Lesson detail | GET | `/api/lessons/<id>/` | 404 for draft/unavailable lessons; **never includes the answer key** (no `explanation`, no `is_correct`) |
| Submit an attempt | POST | `/api/lessons/<id>/attempts/` | body `{"idempotency_key", "answers": [{"question_id", "choice_id"}, ...]}`; scores server-side, writes atomically, returns the full result (including explanations); a repeated request with the same `idempotency_key` returns the original result instead of creating a duplicate |
| Attempt detail | GET | `/api/attempts/<id>/` | only the owning player can retrieve it (404, not 403, for anyone else) |
| My progress | GET | `/api/progress/` | paginated list of the current player's past attempts, most recent first |

## Data model notes

See `backend/accounts/models.py`, `backend/content/models.py`, and
`backend/progress/models.py` for the authoritative definitions; a few
decisions worth calling out:

- **`accounts.User`** is a custom model (`AbstractUser` subclass) in
  place from the very first migration, with a case-insensitive unique
  constraint on `username` (`Lower("username")`) as the source of truth,
  backed up by a matching check in the Django admin user-creation form
  (allauth's own signup already does this check natively for the
  player-registration path). The user's integer primary key is the only
  thing saved progress ever references — never the username or email.
- **`accounts.PlayerProfile`** is a separate one-to-one model from
  `User`, auto-created via a signal on user creation. It's split out now
  so a later parent/coach-account model can own one or more player
  profiles without a disruptive migration — not built in this version.
- **`progress.Attempt` / `progress.AttemptAnswer`** snapshot everything
  needed to redisplay a past result accurately (question prompt,
  explanation, selected/correct choice text) independent of later edits
  to the live `content` models. Lessons and questions are archived
  (`Lesson.status = unavailable`), never cascade-deleted, so historical
  attempts always have a valid reference.

## Environment variables

See `backend/.env.example` for the full list with inline comments.
Summary:

| Variable | Purpose |
| --- | --- |
| `DJANGO_SECRET_KEY` | Django's cryptographic signing key — generate a real random value for every environment, never reuse the example |
| `DJANGO_DEBUG` | `True` locally, `False` in production |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated hostnames Django will serve |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | Comma-separated origins (with scheme) allowed to pass CSRF checks |
| `DJANGO_SECURE_COOKIES` | `True` once served over HTTPS — makes session/CSRF cookies `Secure` |
| `DATABASE_URL` | Postgres connection string |
| `DJANGO_CORS_ALLOWED_ORIGINS` | Only needed if the frontend is ever served from a different origin than the backend (not the default same-origin setup) |

`frontend/.env.example` exists too but is currently empty of
required values — the frontend talks to whatever origin it's served
from (same-origin in both dev, via the Vite proxy, and production).

## Deploying to Railway

This deploys as **two Railway services in one project**: the Django app,
and a managed PostgreSQL database. Railway builds from this repo using
Nixpacks by default; the steps below assume that.

### 1. Create the project

1. In Railway, create a new project from this GitHub repo (see "GitHub
   deployment instructions" below if it isn't pushed yet).
2. Add a **PostgreSQL** database service to the project (Railway's
   "+ New" → "Database" → "PostgreSQL"). Railway provisions it and
   exposes a `DATABASE_URL`-shaped set of variables automatically.

### 2. Configure the app service

**Build command:**

```bash
bash scripts/build.sh
```

This installs frontend deps, type-checks and builds the React app,
copies the build into `backend/staticfiles_frontend/`, installs backend
deps, and runs `collectstatic`. See `scripts/build.sh`.

**Start command** (also captured in the repo's `Procfile`, which
Railway/Nixpacks will pick up automatically if no explicit start
command is set):

```bash
cd backend && python manage.py migrate --noinput && gunicorn bsa.wsgi:application --bind 0.0.0.0:$PORT
```

Running `migrate` at boot keeps this a one-command deploy for a single
web service; if you ever scale to multiple web replicas, move the
migrate step to a separate one-off Railway run instead of leaving it in
every replica's boot command.

**Environment variables** (Settings → Variables on the app service):

| Variable | Value |
| --- | --- |
| `DJANGO_SECRET_KEY` | A long random string, generated once for this environment and not reused anywhere else |
| `DJANGO_DEBUG` | `False` |
| `DJANGO_ALLOWED_HOSTS` | Your Railway domain, e.g. `bsa-production.up.railway.app` (and any custom domain once attached) |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | `https://bsa-production.up.railway.app` (full origin, with scheme; add your custom domain too once attached) |
| `DJANGO_SECURE_COOKIES` | `True` |
| `DATABASE_URL` | Reference the Postgres service's connection variable (Railway lets you reference another service's variable directly, e.g. `${{Postgres.DATABASE_URL}}`) |

Railway terminates TLS at its edge and forwards plain HTTP with an
`X-Forwarded-Proto` header; `bsa/settings.py` already sets
`SECURE_PROXY_SSL_HEADER` accordingly whenever `DEBUG=False`, so Django
correctly recognizes the original request as HTTPS (needed for secure
cookies and `SECURE_SSL_REDIRECT` to behave correctly, rather than
redirect-looping).

### 3. First deploy

1. Push to the branch Railway is watching; it runs the build command,
   then the start command (which runs migrations automatically).
2. Create an administrator account by opening a one-off shell against
   the running service (Railway's dashboard has a "Shell" / exec
   feature) and running:
   ```bash
   cd backend && python manage.py createsuperuser
   ```
3. Optionally seed the demo lesson the same way:
   ```bash
   cd backend && python manage.py seed_demo_lesson
   ```
4. Log into `/admin/` on your Railway domain, review/replace the seed
   lesson's placeholder video, and publish it.

### 4. Static assets

`collectstatic` (run during the build) plus `whitenoise` (already in
`MIDDLEWARE`, configured with `CompressedManifestStaticFilesStorage`
whenever `DEBUG=False`) serve both the React build's assets and Django
admin/DRF's own static files directly from the Django process — no
separate CDN or static-hosting service is required for this version's
scale.

### 5. Backup / restore

Railway's PostgreSQL service supports on-demand and scheduled backups
through its dashboard (Database service → Backups) — enable scheduled
backups there for anything beyond local development. For a manual
backup/restore from your machine:

```bash
# Backup (run against the DATABASE_URL Railway shows for the Postgres service)
pg_dump "$DATABASE_URL" -Fc -f bsa_backup.dump

# Restore into a (different or recreated) database
pg_restore --clean --if-exists -d "$DATABASE_URL" bsa_backup.dump
```

Treat any downloaded backup as containing real player data once this
app has real users — store and delete it accordingly.

## GitHub deployment instructions

No specific account is assumed — push this repository to any GitHub
account or organization you control, then point Railway at it:

```bash
git remote add origin git@github.com:<your-username>/<your-repo>.git
git push -u origin main
```

In Railway: **New Project → Deploy from GitHub repo**, select the repo,
and follow "Deploying to Railway" above. Railway auto-redeploys on every
push to the watched branch once connected.

## Remaining launch decisions and known limitations

These are explicitly **not resolved** by this version and should be
decided by the product owner before any public launch involving real
children:

- **Age range, parental/guardian consent, and privacy notice**: not yet
  defined. Username-only registration (no email, no real name required)
  minimizes data collection but does **not** by itself make this app
  compliant with children's privacy law (e.g. COPPA in the US) —
  compliance depends on the actual age range served, what if anything is
  collected beyond what exists today, and how data is handled; this
  needs a real legal/policy review before public launch.
- **Account deletion / data retention**: no self-serve "delete my
  account" flow exists yet. An administrator can delete a `User` via
  Django admin today — this **cascades** through `PlayerProfile` to
  that player's entire `Attempt`/`AttemptAnswer` history, deleting it
  permanently (by design, so a real deletion request actually removes
  the data, rather than orphaning it). There is currently no "soft
  delete" or export-before-delete step; if you need to retain
  attempt history for analytics while still honoring a deletion
  request, build that explicitly before relying on it. Define a
  retention policy and a proper deletion procedure before launch.
- **Email / password-recovery transition**: the data model is already
  shaped to add verified email and email-based password recovery later
  without disrupting existing accounts (see `accounts.User.email`,
  currently optional and unverified) — but that flow isn't built yet.
  Current admin-assisted reset (documented above) is the only recovery
  path.
- **Video rights**: the seed lesson uses a placeholder video URL on
  purpose. Before publishing any real lesson, confirm you have the
  right to point players at that specific video for this purpose —
  public availability alone doesn't establish that.
- **Scale assumptions**: this version assumes a single Railway web
  process; the `migrate`-on-boot start command and WhiteNoise-served
  static files are both simplicity choices appropriate at this scale,
  not large-scale-production patterns. Revisit both if usage grows
  significantly.
- **No native app / app store presence** in this version, by design
  (per the brief) — mobile access is via the phone browser only.
- **Preview before publish** in Django admin is informal (there's no
  dedicated "preview as a player" screen) — a real coach-facing preview
  is reasonable future work, not required for this milestone.
