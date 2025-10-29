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

import sys

from memori._cli import Cli
from memori._config import Config
from memori.api._sign_up import Manager as ApiSignUpManager


def main():
    if len(sys.argv) == 1:
        cli = Cli(Config())
        cli.banner()
        sys.exit(0)

    if sys.argv[1] == "sign-up":
        if len(sys.argv) != 3:
            print("usage: python -m memori sign-up <email_address>")
            sys.exit(1)

        ApiSignUpManager(Config()).execute(sys.argv[2])


if __name__ == "__main__":
    main()
