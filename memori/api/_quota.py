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
from memori._network import Api


class Manager:
    def __init__(self, config: Config):
        self.config = config

    def execute(self):
        response = Api(self.config).get("sdk/quota")
        print("Maximum # of Memories: " + f'{response["memories"]["max"]:,}')
        print("Current # of Memories: " + f'{response["memories"]["num"]:,}')

        print("")
        print(response["message"])
        print("")
