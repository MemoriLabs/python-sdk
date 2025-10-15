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

from uuid import uuid4 as uuid4

from memori._config import Config


class Writer:
    def __init__(self, config: Config):
        self.config = config

    def execute(self, payload):
        if self.config.cache.session_id is None:
            self.config.conn.execute(
                """
                insert ignore into memori_session(
                    uuid
                ) values (
                    %s
                )
                """,
                (self.config.session_id,)
            )
            self.config.conn.flush()

            self.config.cache.session_id = (
                self.config.conn.execute(
                    """
                    select id
                      from memori_session
                     where uuid = %s
                    """,
                    (self.config.session_id,)
                )
                .mappings()
                .fetchone()
                .get("id", None)
            )

            if self.config.cache.session_id is None:
                raise RuntimeError("session ID is unexpectedly None")

        if self.config.cache.conversation_id is None:
            uuid = uuid4()

            self.config.conn.execute(
                """
                insert ignore into memori_conversation(
                    uuid,
                    session_id
                ) values (
                    %s,
                    %s
                )
                """,
                (uuid, self.config.cache.session_id,)
            )
            self.config.conn.flush()

            self.config.cache.conversation_id = (
                self.config.conn.execute(
                    """
                    select id
                      from memori_conversation
                     where session_id = %s
                    """,
                    (self.config.cache.session_id,)
                )
                .mappings()
                .fetchone()
                .get("id", None)
            )

            if self.config.cache.conversation_id is None:
                raise RuntimeError("conversation ID is unexpectedly None")

        messages = self.parse_query(payload)
        if len(messages) > 0:
            for message in messages:
                self.config.conn.execute(
                    """
                    insert into memori_conversation_message(
                        uuid,
                        conversation_id,
                        role,
                        content
                    ) values (
                        %s,
                        %s,
                        %s,
                        %s
                    )
                    """,
                    (
                        uuid4(),
                        self.config.cache.conversation_id,
                        message["role"],
                        message["content"],
                    ),
                )

            self.config.conn.flush()

        self.config.conn.commit()

        return self

    def parse_query(self, payload):
        messages = payload["query"].get("messages", None)
        if messages is not None:
            # Anthropic / OpenAI
            # [
            #   {
            #       "content": "...",
            #       "role": "..."
            #   }
            # ]
            return messages

        contents = payload["query"].get("contents", None)
        if contents is not None:
            if contents[0].get("parts", None) is not None:
                # Google
                # [
                #   {
                #       "parts": [
                #           {
                #               "text": "..."
                #           }
                #       ],
                #       "role": "..."
                #   }
                # ]

                messages = []
                for entry in contents:
                    parts = entry.get("parts", None)
                    content = []
                    if parts is not None:
                        for part in parts:
                            text = part.get("text", None)
                            if text is not None and len(text) > 0:
                                content.append(text)

                    if len(content) > 0:
                        messages.append(
                            {"content": " ".join(content), "role": entry["role"]}
                        )

                return messages

        body = payload["query"].get("body", None)
        if body is not None:
            messages = body.get("messages", None)
            if messages is not None:
                # Bedrock
                # [
                #   {
                #       "content": "...",
                #       "role": "..."
                #   }
                # ]
                return messages

        raise NotImplementedError
