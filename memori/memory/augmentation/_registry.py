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

import os

from memori._config import Config


class Registry:
    def adapter(self, config: Config):
        if config.is_test_mode():
            return None

        if os.environ.get("MEMORI_API_KEY", None) is not None:
            return MemoriAugmentation(config)

        return None
