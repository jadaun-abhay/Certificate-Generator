from jadaun.initializer.apps import AppConfig


class CoreConfig(AppConfig):
    name = 'modules.core'

    def ready(self) -> None:
        from modules.core import openapi  # noqa: F401 - registers the drf-spectacular auth scheme
