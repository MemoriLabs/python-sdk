r"""
 __  __                           _
|  \/  | ___ _ __ ___   ___  _ __(_)
| |\/| |/ _ \ '_ ` _ \ / _ \| '__| |
| |  | |  __/ | | | | | (_) | |  | |
|_|  |_|\___|_| |_| |_|\___/|_|  |_|
                  perfectam memoriam
                         by GibsonAI
                       memorilabs.ai
"""

import pyfiglet

from memori._config import Config


class Cli:
    def __init__(self, config: Config):
        self.config = config

    def banner(self):
        print(pyfiglet.figlet_format("Memori", font="standard").rstrip())
        print(" " * 18 + "perfectam memoriam")
        print(" " * 25 + "by GibsonAI")
        print(" " * 23 + "memorilabs.ai")
        print(" " * 30 + "v" + str(self.config.version) + "\n")

    def newline(self):
        print("")

    def notice(self, message, ident=0):
        prefix = "+ "
        if ident > 0:
            prefix = ""

        print(prefix + " " * (ident * 4) + message)
