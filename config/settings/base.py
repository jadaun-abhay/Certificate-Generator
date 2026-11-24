import os
from pathlib import Path
from typing import Any, ClassVar

from dotenv import load_dotenv

from ._core import Settings

_BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(_BASE_DIR / ".env")


class BaseSettings(Settings):
    BASE_DIR: Path = _BASE_DIR
    SECRET_KEY: str = os.getenv(
        "SECRET_KEY", "5q+)1-4#7=(*k@z-kwb1-y!1dyvo6&du79!=ye!+)_uho3(we6"
    )
    DEBUG: bool = os.getenv("DEBUG", "False").strip().lower() == "true"
    AUTH_USER_MODEL: str = "core.User"

    # Frontend runs on a different origin/port than this API (e.g. the Vite
    # dev server on :5173) - session-cookie auth across origins needs all
    # of these together, not just CORS:
    #  - CORS_ALLOWED_ORIGINS/CORS_ALLOW_CREDENTIALS so the browser's
    #    preflight and the actual response both carry the right
    #    Access-Control-Allow-* headers. Scoped to known frontend origins,
    #    not CORS_ALLOW_ALL_ORIGINS - this API sits behind session-cookie
    #    auth, so allowing every origin would let any website make
    #    authenticated requests on a logged-in user's behalf.
    #  - SESSION_COOKIE_SAMESITE="None" so the browser sends the session
    #    cookie on a cross-origin request at all.
    #  - SESSION_COOKIE_SECURE=True because modern browsers refuse to set
    #    or send a SameSite=None cookie over plain HTTP - this is why the
    #    backend needs `runsslserver`, not `runserver`, for the frontend's
    #    login to actually stick.
    CORS_ALLOWED_ORIGINS: ClassVar[list[str]] = os.getenv(
        "CORS_ALLOWED_ORIGINS",
        "http://localhost:5173,https://localhost:5173",
    ).split(",")
    CORS_ALLOW_CREDENTIALS: bool = True
    SESSION_COOKIE_SECURE: bool = True
    SESSION_COOKIE_HTTPONLY: bool = False
    SESSION_COOKIE_SAMESITE: str = "None"
    DEFAULT_APPS_DIR: str = "modules"
    DEFAULT_DJANGO_APPS: ClassVar[list[str]] = [
        "django.contrib.admin",
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django.contrib.sessions",
        "django.contrib.messages",
        "django.contrib.staticfiles",
    ]
    THIRD_PARTY_APPS: ClassVar[list[str]] = [
        "corsheaders",
        "rest_framework",
        "drf_spectacular",
        "django_celery_results",
        "sslserver",
        "jadaun",
    ]
    # CsrfViewMiddleware is deliberately disabled below, so session auth's
    # default CSRF enforcement (which runs independently of that middleware)
    # is swapped out too - see modules/core/authentication.py for why.
    REST_FRAMEWORK: ClassVar[dict[str, Any]] = {
        "DEFAULT_AUTHENTICATION_CLASSES": [
            "modules.core.authentication.CsrfExemptSessionAuthentication",
        ],
        "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    }
    SPECTACULAR_SETTINGS: ClassVar[dict[str, Any]] = {
        "TITLE": "Certificate Generator API",
        "DESCRIPTION": (
            "Auth, a Google-Drive-style file/folder store, and batch "
            "certificate generation."
        ),
        "VERSION": "1.0.0",
        "SERVE_INCLUDE_SCHEMA": False,
        # Every endpoint is namespaced /api/<app>/v1/... already - group the
        # docs by that app name instead of drf-spectacular's path-guessed
        # default, which would otherwise read the version segment as the tag.
        "TAGS": [
            {"name": "core", "description": "Auth and shared primitives."},
            {"name": "drive", "description": "Folders, files, and trash."},
            {
                "name": "handler",
                "description": "Certificate templates and generation jobs.",
            },
        ],
        # `Dropdown.status` and `GenerationJob.status` are both named
        # "status" but have different choice sets - name them explicitly
        # instead of letting drf-spectacular auto-suffix a collision name.
        "ENUM_NAME_OVERRIDES": {
            "DropdownStatusEnum": "modules.core.choices.StatusChoices.choices",
            "JobStatusEnum": "modules.handler.choices.JobStatus.choices",
        },
    }
    DATABASES: ClassVar = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.getenv("DB_NAME", "certifier_db"),
            "USER": os.getenv("DB_USER", "root"),
            "PASSWORD": os.getenv("DB_PASSWORD", ""),
            "HOST": os.getenv("DB_HOST", "localhost"),
            "PORT": os.getenv("DB_PORT", "5432"),
        }
    }
    MIDDLEWARE: ClassVar[list[str]] = [
        "django.middleware.security.SecurityMiddleware",
        "corsheaders.middleware.CorsMiddleware",
        "django.contrib.sessions.middleware.SessionMiddleware",
        "django.middleware.common.CommonMiddleware",
        # 'django.middleware.csrf.CsrfViewMiddleware',
        "django.contrib.auth.middleware.AuthenticationMiddleware",
        "django.contrib.messages.middleware.MessageMiddleware",
        "django.middleware.clickjacking.XFrameOptionsMiddleware",
    ]

    ROOT_URLCONF: str = "config.urls"
    TEMPLATES: ClassVar[list[dict[str, Any]]] = [
        {
            "BACKEND": "django.template.backends.django.DjangoTemplates",
            "DIRS": [],
            "APP_DIRS": True,
            "OPTIONS": {
                "context_processors": [
                    "django.template.context_processors.debug",
                    "django.template.context_processors.request",
                    "django.contrib.auth.context_processors.auth",
                    "django.contrib.messages.context_processors.messages",
                ],
            },
        },
    ]

    WSGI_APPLICATION: str = "config.wsgi.application"

    AUTH_PASSWORD_VALIDATORS: ClassVar = [
        {
            "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
        },
        {
            "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        },
        {
            "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
        },
        {
            "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
        },
    ]

    LANGUAGE_CODE = "en-us"

    TIME_ZONE = "Asia/Kolkata"

    USE_I18N = True

    USE_TZ = False

    DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

    STATIC_URL = "static/"

    MEDIA_ROOT = _BASE_DIR / "media"
    MEDIA_URL = "/media/"

    # Used by `handler` when a `TemplateField` has no font of its own.
    HANDLER_DEFAULT_FONT_PATH: str = str(
        _BASE_DIR / "fonts" / "CaskaydiaCoveNerdFontMono-Regular.ttf"
    )

    # The redis container already running locally (see `docker ps`) doubles
    # as both the Celery broker and, via django-celery-results, task results
    # are stored in Postgres instead (simpler to inspect than Redis).
    # DB index 1, not 0 - this machine's redis container is shared with
    # other local projects already queuing unrelated tasks on DB 0.
    CELERY_BROKER_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/1")
    CELERY_RESULT_BACKEND: str = "django-db"
    CELERY_ACCEPT_CONTENT: ClassVar[list[str]] = ["json"]
    CELERY_TASK_SERIALIZER: str = "json"
    CELERY_RESULT_SERIALIZER: str = "json"
    CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP: bool = True
