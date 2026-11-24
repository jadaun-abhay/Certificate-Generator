from typing import ClassVar

from ._core import Settings


class DevSettings(Settings):
    DEV_APPS: ClassVar[list[str]] = []
