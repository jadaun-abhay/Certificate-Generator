# Certificate Generator

A Django backend for generating batches of certificates (course completions,
event attendance, etc.) from a template image + a data file, plus a
general-purpose "drive" (folders/files, Google-Drive-style) that the
generated output lands in.

Routing, app discovery and project settings are built on **jadaun**
(`../jadaun`, a local editable package) rather than Django's usual manual
`urls.py`/`INSTALLED_APPS` wiring - see the "jadaun conventions" section
before adding anything new.

## Stack

- Django 6.1, Django REST Framework
- Postgres (shared by dev and prod - see `config/settings/`)
- Celery + Redis for background jobs (certificate generation)
- jadaun for dynamic app discovery, folder-based URL routing, and `startapp`
  scaffolding

## Apps (`modules/`)

### `core`
Auth and shared primitives.
- `User` - custom user model (`AUTH_USER_MODEL = "core.User"`), email as the
  username, no `username` field.
- `Dropdown` - generic self-referential label tree (for arbitrary
  category/subcategory dropdowns in the frontend).
- `BaseModel` (abstract) - `created_at`/`updated_at`/`status`
  (`StatusChoices`), inherited by nearly every model in the project.
- Routes: `POST/GET api/core/v1/auth/` (login + "am I logged in" status),
  `POST api/core/v1/auth/register/`, `GET/POST api/core/v1/dropdown/`,
  `GET/PATCH api/core/v1/dropdown/<pk>/`.

### `drive`
Generic file/folder storage - the Google-Drive-like feature. `Folder` is
self-referential (`parent=None` = root); `File` optionally belongs to a
`Folder`. Both soft-delete via `is_deleted`/`deleted_at` (no separate
`Trash` table - trash is just a filter on the same tables) and support
starring.
- Routes: `GET/POST api/drive/v1/folder/` (`?parent=`), `GET/PATCH/DELETE
  api/drive/v1/folder/<pk>/`, `GET/POST api/drive/v1/file/` (`?folder=`),
  `GET/PATCH/DELETE api/drive/v1/file/<pk>/`, `GET api/drive/v1/trash/`,
  `PATCH/DELETE api/drive/v1/trash/<folder|file>/<pk>/` (restore / permanent
  delete).

### `handler`
Certificate generation. A `CertificateTemplate` (image, pulled from an
existing `drive.File`) has `TemplateField` rectangles (where each data
column gets drawn, with alignment/color/optional custom `Font`). A
`GenerationJob` ties a template + a data file (csv/json/xlsx, also a
`drive.File`) + a `purpose` name together; running it creates/reuses
`Certificates/<purpose>/` in the user's drive and drops the output zip
there.
- `POST api/handler/v1/font/`, `GET api/handler/v1/font/`
- `POST api/handler/v1/template/` (template + field rectangles in one call)
- `GET api/handler/v1/template/<pk>/`
- `POST api/handler/v1/template/<pk>/preview/` - renders **one** sample row
  synchronously, returns a PNG, nothing persisted. For eyeballing a template
  before committing to a full run.
- `POST api/handler/v1/job/` - creates the job and dispatches it to Celery
  (`modules/handler/tasks.py:generate_certificates_task`).
- `GET api/handler/v1/job/<pk>/` - poll status (`pending` → `processing` →
  `completed`/`failed`) and the resulting `output_zip`.

The actual rendering (`modules/handler/api/v1/services/rendering.py`) is a
rewrite, not a port, of the old `my_app/functions.py` logic - that code had
a real crash bug (`draw.text(start_co_ordinate, w, ...)`, `w` undefined)
and a half-finished multi-field branch.

### `my_app`
The original, pre-jadaun implementation of (roughly) `core` + `drive` +
`handler` combined into one app, kept around purely as a **reference** for
porting logic - not meant to gain new features. Still wired into
`config/urls.py` under `/my_app/`, and still in
`DEV_APPS` (dev-only, not in `PROD_APPS`). Safe to delete once nothing in it
is still being referenced for porting.

## jadaun conventions

- `DEFAULT_APPS_DIR = "modules"` - every first-party app lives under
  `modules/`, declared in `jadaun.config.yaml` (`modules: <app>: {allowed,
  default}`), and scaffolded with `uv run manage.py startapp <name>`
  (interactive wizard if run with no args).
- Each app is split `api/v1/{selectors,services,serializers,views}/` -
  selectors read, services write, serializers shape, views are thin
  (`jadaun.views.BaseAPIView` subclasses). Selectors/services are
  class-based with `@staticmethod`s (e.g. `UserSelector.get_by_email(...)`),
  not bare module functions.
- Views use **folder-based routing**: the `views/` package's directory
  structure *is* the URL structure. A folder needs an `__init__.py` to be
  walked at all; that `__init__.py` can itself be a real view (binds to the
  folder's own path) or just a namespace. A literal Django path converter
  can be a folder name, e.g. `views/folder/<int:pk>/`. See any existing
  app's `views/` tree for the pattern before adding a new route.
- `INSTALLED_APPS` is computed by `autowire(globals())` at the bottom of
  `config/settings/base.py` - never add an app directly to
  `INSTALLED_APPS`; add it to `THIRD_PARTY_APPS`/`DEV_APPS`/`PROD_APPS` (for
  real third-party/pip apps) or to `jadaun.config.yaml` (for first-party
  `modules/` apps).

## Settings (`config/settings/`)

Not a single `settings.py` - a small package with its own base/dev/prod
class-registry (`_core.py`'s `Settings`, `__init_subclass__`-based). `base.py`
holds everything shared + reads `.env` via `python-dotenv`; `dev.py`/`prod.py`
currently only differ on `DEV_APPS`/`PROD_APPS` (both share one Postgres DB
right now, by choice).

Known deliberate (non-default) choices, each with a reason in a comment at
its definition in `base.py`:
- `CsrfViewMiddleware` is commented out of `MIDDLEWARE`, and DRF's
  `SessionAuthentication` is swapped for `modules.core.authentication.
  CsrfExemptSessionAuthentication` to match - CSRF protection is **off**
  for this API, on purpose, for now.
- `CELERY_BROKER_URL` points at Redis **DB 1**, not 0 - DB 0 on this
  machine's shared `redis` container is already used by an unrelated local
  project.
- `django-stubs` is a dev dependency for IDE/pyright typing; without its
  mypy plugin (which pyright/basedpyright can't run) it still leaves some
  false positives on Django's dynamic attributes (`<fk>_id`,
  `request.user.id`, DRF's `validated_data`) - known, not a bug.

## Running it

```bash
uv run manage.py createdb     # creates the Postgres DB if it doesn't exist
uv run manage.py migrate
uv run manage.py runserver
uv run celery -A config worker --loglevel=info   # for handler jobs
```

## Known gaps / not yet built

- `handler`'s preview only takes a manually-typed sample row, not "preview
  row N from the uploaded data file."
- No push notification when a `GenerationJob` finishes - clients have to
  poll `GET job/<pk>/`.
- No tests yet in any app (`tests/` directories are the stock Django
  stubs).
- `my_app` is still routed and still has real tables (fonts, zips,
  templates, folder structure) that haven't been ported/retired yet.
