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
        "django_celery_results",
        "jadaun",
    ]
    # CsrfViewMiddleware is deliberately disabled below, so session auth's
    # default CSRF enforcement (which runs independently of that middleware)
    # is swapped out too - see modules/core/authentication.py for why.
    REST_FRAMEWORK: ClassVar[dict[str, list[str]]] = {
        "DEFAULT_AUTHENTICATION_CLASSES": [
            "modules.core.authentication.CsrfExemptSessionAuthentication",
        ],
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

    # Used by the legacy `my_app` reference views (zipify/drive_structure).
    WHITELISTED_IMAGE_TYPES: ClassVar[dict[str, str]] = {
        "jpeg": "image/jpeg",
        "jpg": "image/jpeg",
        "png": "image/png",
    }
    WHITELISTED_FILE_TYPES: ClassVar[dict[str, str]] = {
        "json": "application/json",
        "csv": "text/csv",
        "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "txt": "text/plain",
    }

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
