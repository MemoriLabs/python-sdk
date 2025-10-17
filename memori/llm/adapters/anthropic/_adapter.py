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

from memori.llm._base import BaseLlmAdaptor


class Adapter(BaseLlmAdaptor):
    def get_formatted_query(self, payload):
        """
        [
            {
                "content": "...",
                "role": "..."
            }
        ]
        """

        try:
            return payload["conversation"]["query"].get("messages", [])
        except KeyError:
            return []

    def get_formatted_response(self, payload):
        try:
            content = payload["conversation"]["response"].get("content", None)
        except KeyError:
            return []

        response = []
        if content is not None:
            # Unstreamed
            # [
            #   {
            #       "text": "...",
            #       "type": "..."
            #   }
            # ]
            for entry in content:
                response.append(
                    {
                        "role": payload["conversation"]["response"].get("role", None),
                        "text": entry["text"],
                        "type": entry["type"],
                    }
                )
        else:
            # Streamed
            """
            REQUEST FOR CONTRIBUTION

            How do we parse the messages when Anthropic streams the response?
            """
            raise RuntimeError("REQUEST FOR CONTRIBUTION")

        return response
