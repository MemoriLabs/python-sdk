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

from memori.llm._registry import Registry

from memori.llm import _clients  # noqa: F401
from memori.llm.adapters.anthropic import _adapter  # noqa: F401
from memori.llm.adapters.bedrock import _adapter  # noqa: F401
from memori.llm.adapters.google import _adapter  # noqa: F401
from memori.llm.adapters.openai import _adapter  # noqa: F401

__all__ = ["Registry"]
