# Certificate Generator

A Django + DRF backend for two things that work together:

1. **A general-purpose drive** - folders and files, Google-Drive-style
   (create, list, rename, move, star, trash/restore, permanently delete).
2. **Batch certificate generation** - upload a template image, mark where
   each piece of data goes on it (name, course, date, ...), preview one
   before committing, then generate the whole batch from a CSV/JSON/XLSX
   file in the background. The output lands directly in the user's drive,
   under `Certificates/<purpose>/`.

Routing and app discovery are built on [jadaun](../jadaun) rather than
Django's usual manual `urls.py`/`INSTALLED_APPS` wiring. See
[`AGENTS.md`](./AGENTS.md) for the architecture, conventions, and every
deliberate non-default setting if you're going to work on this codebase.

## Stack

- **Django 6.1** + **Django REST Framework**
- **PostgreSQL** (one database, shared by dev and prod right now, by choice)
- **Celery** + **Redis** for background certificate-generation jobs
- **jadaun** for dynamic app discovery, folder-based URL routing, and
  `startapp` scaffolding
- **Pillow** for image compositing, **openpyxl** for `.xlsx` parsing

## Getting started

```bash
# 1. Install dependencies (uv manages the venv for you)
uv sync

# 2. Configure the database + secret key
cp .env.example .env   # then fill in DB_USER / DB_PASSWORD / SECRET_KEY
```

`.env` needs:

| Variable       | Purpose                                              | Default (if unset)      |
| -------------- | ----------------------------------------------------- | ------------------------ |
| `SECRET_KEY`   | Django's secret key                                  | an insecure dev fallback |
| `DEBUG`        | `True`/`False` - selects dev vs. prod settings       | `False`                  |
| `DB_NAME`      | Postgres database name                               | `certifier_db`           |
| `DB_USER`      | Postgres user                                        | `root`                   |
| `DB_PASSWORD`  | Postgres password                                    | `""`                     |
| `DB_HOST`      | Postgres host                                        | `localhost`              |
| `DB_PORT`      | Postgres port                                        | `5432`                   |
| `REDIS_URL`    | Celery broker (results go to Postgres, not Redis)    | `redis://localhost:6379/1` |

```bash
# 3. Create the database (migrate can't create it for you) and migrate
uv run manage.py createdb
uv run manage.py migrate

# 4. Run it
uv run manage.py runserver
uv run celery -A config worker --loglevel=info   # separate terminal, needed for certificate jobs
```

Everything lives under `api/<app>/<version>/...`, e.g.
`api/drive/v1/folder/`, `api/handler/v1/job/`.

## What's where

| App       | Responsibility                                                        |
| --------- | ----------------------------------------------------------------------- |
| `core`    | Custom email-based user auth (login/register/status), a generic self-referential `Dropdown` for arbitrary category trees |
| `drive`   | Folders and files - the storage layer everything else builds on       |
| `handler` | Certificate templates, field placement, preview rendering, and the Celery-backed batch generation job |

### Auth (`core`)

```
POST /api/core/v1/auth/register/   {"email", "password", "first_name", "last_name"}
POST /api/core/v1/auth/            {"email", "password"}              -> login
GET  /api/core/v1/auth/                                               -> am I logged in?
```

Session-cookie auth (no CSRF token required right now - see `AGENTS.md`
for why that's a deliberate, not default, choice).

### Drive

```
GET/POST   /api/drive/v1/folder/            ?parent=<id>
GET/PATCH/DELETE /api/drive/v1/folder/<id>/
GET/POST   /api/drive/v1/file/              ?folder=<id>
GET/PATCH/DELETE /api/drive/v1/file/<id>/
GET        /api/drive/v1/trash/
PATCH/DELETE /api/drive/v1/trash/<folder|file>/<id>/   -> restore / permanently delete
```

`DELETE` on a folder/file moves it to trash (`is_deleted=True`); the
`trash/` endpoints restore it or delete it for real.

### Certificate generation (`handler`)

The flow a frontend would drive:

1. Upload a template image and a data file through `drive`'s `file/`
   endpoint - everything `handler` touches is a `drive.File`, so it shows
   up in the user's drive too.
2. `POST /api/handler/v1/template/` - register the template plus the
   rectangles where each field gets drawn (`field_name`, box corners,
   alignment, color, optional custom font).
3. `POST /api/handler/v1/template/<id>/preview/` with one sample row of
   data - get back a PNG, synchronously, nothing saved. For the user to
   eyeball before committing to a full run.
4. Happy with it? `POST /api/handler/v1/job/` with the template, the real
   data file, and a `purpose` name. This creates/reuses a
   `Certificates/<purpose>/` folder in the user's drive and dispatches the
   actual rendering to a Celery worker.
5. `GET /api/handler/v1/job/<id>/` to poll status
   (`pending` → `processing` → `completed`/`failed`) and grab the
   resulting zip once it's done.

## Project layout

```
config/            # Django project package (settings, urls, wsgi/asgi, celery app)
modules/
  core/            # auth, Dropdown
  drive/           # folders, files, trash
  handler/         # templates, fields, generation jobs
fonts/             # bundled .ttf/.otf files (default rendering font)
```

See [`AGENTS.md`](./AGENTS.md) for the jadaun conventions (folder-based
routing, the selector/service/serializer split) to follow when adding
anything new.
