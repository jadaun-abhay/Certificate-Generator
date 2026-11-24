import inspect
from typing import Any, ClassVar


class Settings:
    _env_registry: ClassVar[dict[str, dict[str, Any]]] = {}
    settings: ClassVar[dict[str, Any]] = {}

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        extracted = {
            k: v
            for k, v in cls.__dict__.items()
            if not k.startswith("_")
            and not inspect.isroutine(v)
            and not isinstance(v, (classmethod, staticmethod, property))
        }

        name = cls.__name__.lower()

        if "base" in name:
            Settings._env_registry["base"] = extracted
        elif "dev" in name:
            Settings._env_registry["dev"] = extracted
        elif "prod" in name:
            Settings._env_registry["prod"] = extracted

        # Rebuild active settings whenever any subclass is registered
        Settings._resolve()

    @classmethod
    def _resolve(cls):
        base = Settings._env_registry.get("base", {})
        is_debug = base.get("DEBUG", False)
        active_env = "dev" if is_debug else "prod"

        # Merge base settings with the active environment's overrides. Always
        # written onto `Settings` itself (not `cls`) - `__init_subclass__`
        # calls this once per subclass (Base/Dev/Prod), and each of those is
        # a *different* `cls`, so writing to `cls.settings` would scatter the
        # result across whichever subclass happened to register last instead
        # of landing on `Settings`, which is what `Settings()` instances read.
        Settings.settings = {
            **base,
            **Settings._env_registry.get(active_env, {}),
        }
