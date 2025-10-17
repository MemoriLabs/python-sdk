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

from memori._config import Config
from memori.llm._registry import Registry as LlmRegistry


class Writer:
    def __init__(self, config: Config):
        self.config = config

    def execute(self, payload):
        if self.config.parent_id is not None:
            if self.config.cache.parent_id is None:
                self.config.cache.parent_id = self.config.driver.parent.create(
                    self.config.parent_id
                )
                if self.config.cache.parent_id is None:
                    raise RuntimeError("parent ID is unexpectedly None")

        if self.config.process_id is not None:
            if self.config.cache.process_id is None:
                self.config.cache.process_id = self.config.driver.process.create(
                    self.config.process_id
                )
                if self.config.cache.process_id is None:
                    raise RuntimeError("process ID is unexpectedly None")

        if self.config.cache.session_id is None:
            self.config.cache.session_id = self.config.driver.session.create(
                self.config.session_id,
                self.config.cache.parent_id,
                self.config.cache.process_id,
            )
            if self.config.cache.session_id is None:
                raise RuntimeError("session ID is unexpectedly None")

        if self.config.cache.conversation_id is None:
            self.config.cache.conversation_id = self.config.driver.conversation.create(
                self.config.cache.session_id
            )
            if self.config.cache.conversation_id is None:
                raise RuntimeError("conversation ID is unexpectedly None")

        llm = LlmRegistry().llm(
            payload["conversation"]["client"]["provider"],
            payload["conversation"]["client"]["title"],
        )

        messages = llm.get_formatted_query(payload)
        if len(messages) > 0:
            for message in messages:
                self.config.driver.conversation.message.create(
                    self.config.cache.conversation_id,
                    message["role"],
                    None,
                    message["content"],
                )

        responses = llm.get_formatted_response(payload)
        if len(responses) > 0:
            for response in responses:
                self.config.driver.conversation.message.create(
                    self.config.cache.conversation_id,
                    response["role"],
                    response["type"],
                    response["text"],
                )

        self.config.conn.flush()

        return self
