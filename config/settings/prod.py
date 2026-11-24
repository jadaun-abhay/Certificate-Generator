from typing import ClassVar

from ._core import Settings


class ProdSettings(Settings):
    # Dev and prod share the same Postgres database - see DATABASES in
    # base.py. Nothing to override here yet.
    PROD_APPS: ClassVar[list[str]] = []
