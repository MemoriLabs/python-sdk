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
from uuid import uuid4

from memori._config import Config
from memori.llm._providers import Anthropic as LlmProviderAnthropic
from memori.llm._providers import Google as LlmProviderGoogle
from memori.llm._providers import LangChain as LlmProviderLangChain
from memori.llm._providers import OpenAi as LlmProviderOpenAi
from memori.llm._providers import PydanticAi as LlmProviderPydanticAi
from memori.storage._manager import Manager as StorageManager
from memori.storage._registry import Registry as StorageRegistry

__all__ = ["Memori"]


class Memori:
    def __init__(self, conn=None):
        self.config = Config()
        self.config.api_key = os.environ.get("MEMORI_API_KEY", None)
        self.config.conn = self.storage_adaptor(conn)
        self.config.driver = self.storage_driver()
        self.config.session_id = uuid4()

        self.anthropic = LlmProviderAnthropic(self)
        self.google = LlmProviderGoogle(self)
        self.langchain = LlmProviderLangChain(self)
        self.openai = LlmProviderOpenAi(self)
        self.pydantic_ai = LlmProviderPydanticAi(self)

        self.storage = StorageManager(self.config)

    def attribution(self, parent_id=None, process_id=None):
        if parent_id is not None:
            parent_id = str(parent_id)

            if len(parent_id) > 100:
                raise RuntimeError("parent_id cannot be greater than 100 characters")

        if process_id is not None:
            process_id = str(process_id)

            if len(process_id) > 100:
                raise RuntimeError("process_id cannot be greater than 100 characters")

        self.config.parent_id = parent_id
        self.config.process_id = process_id

        return self

    def metadata(self, data):
        self.config.metadata = data
        return self

    def new_session(self):
        self.config.session_id = uuid4()
        self.config.reset_cache()
        return self

    def set_session(self, id):
        self.config.session_id = id
        return self

    def storage_adaptor(self, conn):
        if conn is None:
            return None

        return StorageRegistry().adaptor(conn)

    def storage_driver(self):
        if self.config.conn is None:
            return None

        return StorageRegistry().driver(self.config.conn)
