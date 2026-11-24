from typing import ClassVar

from ._core import Settings


class DevSettings(Settings):
    # `my_app` is our reference implementation - a hand-written app we're
    # rebuilding as a proper class-based, folder-routed jadaun app. It stays
    # dev-only (not a real third-party dependency, not shipped to prod).
    DEV_APPS: ClassVar[list[str]] = ["my_app"]
