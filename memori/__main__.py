r"""
 __  __                           _
|  \/  | ___ _ __ ___   ___  _ __(_)
| |\/| |/ _ \ '_ ` _ \ / _ \| '__| |
| |  | |  __/ | | | | | (_) | |  | |
|_|  |_|\___|_| |_| |_|\___/|_|  |_|
                  perfectam memoriam
                       memorilabs.ai
"""

import sys

from memori._cli import Cli
from memori._config import Config
from memori.api._quota import Manager as ApiQuotaManager
from memori.api._sign_up import Manager as ApiSignUpManager


def main():
    cli = Cli(Config())
    cli.banner()

    if len(sys.argv) > 1:
        if sys.argv[1] == "quota":
            ApiQuotaManager(Config()).execute()
        elif sys.argv[1] == "sign-up":
            if len(sys.argv) != 3:
                print("usage: python -m memori sign-up <email_address>\n")
                sys.exit(1)

            ApiSignUpManager(Config()).execute(sys.argv[2])

    sys.exit(0)


if __name__ == "__main__":
    main()
