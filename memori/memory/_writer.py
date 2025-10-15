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
                (self.config.session_id,),
            )
            self.config.conn.flush()

            self.config.cache.session_id = (
                self.config.conn.execute(
                    """
                    select id
                      from memori_session
                     where uuid = %s
                    """,
                    (self.config.session_id,),
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
                (
                    uuid,
                    self.config.cache.session_id,
                ),
            )
            self.config.conn.flush()

            self.config.cache.conversation_id = (
                self.config.conn.execute(
                    """
                    select id
                      from memori_conversation
                     where session_id = %s
                    """,
                    (self.config.cache.session_id,),
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
        messages = payload["conversation"]["query"].get("messages", None)
        if messages is not None:
            # Anthropic / OpenAI
            # [
            #   {
            #       "content": "...",
            #       "role": "..."
            #   }
            # ]
            return messages

        contents = payload["conversation"]["query"].get("contents", None)
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

        body = payload["conversation"]["query"].get("body", None)
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

    def parse_response(self, payload):
        if isinstance(payload["conversation"]["response"], list):
            if "chunk" in payload["conversation"]["response"][0]:
                # Bedrock (streaming)
                # [
                #   {
                #       "chunk": {
                #           "bytes": {
                #               "delta": {
                #                   "text": "...",
                #                   "type": "..."
                #               }
                #           }
                #       }
                #   }
                # ]
                response = []
                text = []
                role = None
                for entry in payload["conversation"]["response"]:
                    chunk = entry.get("chunk", None)
                    if chunk is not None:
                        bytes_ = chunk.get("bytes", None)
                        if bytes_ is not None:
                            message = bytes_.get("message", None)
                            if message is not None:
                                role = message["role"]
                            else:
                                delta = bytes_.get("delta", None)
                                if delta is not None:
                                    text_content = delta.get("text", None)
                                    if (
                                        text_content is not None
                                        and len(text_content) > 0
                                    ):
                                        text.append(text_content)

                if len(text) > 0:
                    response.append(
                        {"role": role, "text": "".join(text), "type": "text"}
                    )

                return response
            elif "candidates" in payload["conversation"]["response"][0]:
                # Google (streamed)
                #   [
                #       {
                #           "candidates": [
                #               {
                #                   "content": {
                #                       "parts": [
                #                           {
                #                               "text": "..."
                #                           }
                #                       ],
                #                       "role": "model"
                #                   }
                #               }
                #           ]
                #       }
                #   ]
                response = []
                text = []
                role = None
                for entry in payload["conversation"]["response"]:
                    candidates = entry.get("candidates", None)
                    if candidates is not None:
                        for candidate in candidates:
                            content = candidate.get("content", None)
                            if content is not None:
                                parts = content.get("parts", None)
                                if parts is not None:
                                    for part in parts:
                                        text_content = part.get("text", None)
                                        if (
                                            text_content is not None
                                            and len(text_content) > 0
                                        ):
                                            text.append(text_content)

                                if role is None:
                                    role = content.get("role", None)

                if len(text) > 0:
                    response.append(
                        {"role": role, "text": "".join(text), "type": "text"}
                    )

                return response
        else:
            content = payload["conversation"]["response"].get("content", None)
            if content is not None:
                # Anthropic (unstreamed)
                # [
                #   {
                #       "citations": None,
                #       "text": "...",
                #       "type": "..."
                #   }
                # ]
                response = []
                for entry in content:
                    response.append(
                        {"role": "model", "text": entry["text"], "type": entry["type"]}
                    )

                return response

            candidates = payload["conversation"]["response"].get("candidates", None)
            if candidates is not None:
                # Google (unstreamed)
                # [
                #   {
                #       "avgLogprobs": ...,
                #       "content": {
                #           "parts": [
                #               {
                #                   "text": "..."
                #               }
                #           ],
                #           "role": "model"
                #       },
                #       "finishReason": "..."
                #   }
                # ]
                response = []
                for candidate in candidates:
                    content = candidate.get("content", None)
                    if content is not None:
                        parts = content.get("parts", None)
                        if parts is not None:
                            text = []
                            for part in parts:
                                text_content = part.get("text", None)
                                if text_content is not None:
                                    text.append(text_content)

                            if len(text) > 0:
                                response.append(
                                    {
                                        "role": content["role"],
                                        "text": "".join(text),
                                        "type": "text",
                                    }
                                )

                return response

            choices = payload["conversation"]["response"].get("choices", None)
            if choices is not None:
                response = []
                if payload["conversation"]["query"].get("stream", None) is True:
                    # OpenAI (streamed)
                    # [
                    #   {
                    #       "delta": {
                    #           "content": "...",
                    #           "function_call": ...,
                    #           "refusal": ...,
                    #           "role": "...",
                    #           "tool_calls": ...
                    #       }
                    #   }
                    # ]
                    content = []
                    role = None
                    for choice in choices:
                        delta = choice.get("delta", None)
                        if delta is not None:
                            text_content = delta.get("content", None)
                            if text_content is not None and len(text_content) > 0:
                                content.append(text_content)

                                if role is None:
                                    role = delta["role"]

                    if len(content) > 0:
                        response.append(
                            {"role": role, "text": "".join(content), "type": "text"}
                        )
                else:
                    # OpenAI (unstreamed)
                    # [
                    #   {
                    #       "finish_reason": "...",
                    #       "index": ...,
                    #       "logprobs": ...,
                    #       "message": {
                    #           "annotations": ...,
                    #           "audio": ...,
                    #           "content": "...",
                    #           "functional_calls": ...,
                    #           "parsed": ...,
                    #           "refusal": ...,
                    #           "role": "...",
                    #           "tool_calls": ...
                    #       }
                    #   }
                    # ]
                    for choice in choices:
                        message = choice.get("message", None)
                        if message is not None:
                            content = message.get("content", None)
                            if content is not None:
                                response.append(
                                    {
                                        "role": message["role"],
                                        "text": content,
                                        "type": "text",
                                    }
                                )

                return response

        raise NotImplementedError
