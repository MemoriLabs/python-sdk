r"""
 __  __                           _
|  \/  | ___ _ __ ___   ___  _ __(_)
| |\/| |/ _ \ '_ ` _ \ / _ \| '__| |
| |  | |  __/ | | | | | (_) | |  | |
|_|  |_|\___|_| |_| |_|\___/|_|  |_|
                  perfectam memoriam
                         by GibsonAI
                       trymemori.com
"""

from memori.storage._registry import Registry

# Import adapters and drivers to trigger their self-registration decorators
from memori.storage.adapters.sqlalchemy import _adapter  # noqa: F401
from memori.storage.drivers.mysql import _driver  # noqa: F401
from memori.storage.drivers.postgresql import _driver  # noqa: F401

__all__ = ["Registry"]

