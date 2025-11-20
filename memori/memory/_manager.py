r"""
 __  __                           _
|  \/  | ___ _ __ ___   ___  _ __(_)
| |\/| |/ _ \ '_ ` _ \ / _ \| '__| |
| |  | |  __/ | | | | | (_) | |  | |
|_|  |_|\___|_| |_| |_|\___/|_|  |_|
                  perfectam memoriam
                       memorilabs.ai
"""

from memori._config import Config
from memori.memory._collector import Collector
from memori.memory._writer import Writer


class Manager:
    def __init__(self, config: Config):
        self.config = config

    def execute(self, payload):
        if self.config.api_key is not None:
            Collector(self.config).fire_and_forget(payload)
        else:
            Writer(self.config).execute(payload)

        return self
