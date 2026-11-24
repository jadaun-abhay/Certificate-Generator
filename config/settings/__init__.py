from jadaun.autowire import autowire

from . import base, dev, prod  # noqa: F401 - imported for __init_subclass__ registration
from ._core import Settings

setting_instance = Settings()

globals().update({k: v for k, v in setting_instance.settings.items()})

autowire(globals())
