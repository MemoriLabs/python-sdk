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

import copy
import json
import pprint

from google.protobuf import json_format

from memori._config import Config
from memori._utils import merge_chunk
from memori.llm._utils import (
    llm_is_anthropic,
    llm_is_bedrock,
    llm_is_google,
    llm_is_openai,
    provider_is_langchain,
)


class BaseClient:
    def __init__(self, config: Config):
        self.config = config
        self.stream = False


class BaseInvoke:
    def __init__(self, config: Config, method):
        self.config = config
        self._method = method
        self._client_provider = None
        self._client_title = None
        self._client_version = None
        self._uses_protobuf = False

    def configure_for_streaming_usage(self, kwargs):
        if llm_is_openai(self._client_provider, self._client_title):
            if kwargs.get("stream", None):
                stream_options = kwargs.get("stream_options", None)
                if stream_options is None or not isinstance(
                    kwargs["stream_options"], dict
                ):
                    kwargs["stream_options"] = {}

                kwargs["stream_options"]["include_usage"] = True

        return kwargs

    def dict_to_json(self, dict_):
        result = {}
        for key, value in dict_.items():
            if isinstance(value, list):
                result[key] = self.list_to_json(value)
            elif isinstance(value, dict):
                result[key] = self.dict_to_json(value)
            else:
                if hasattr(value, "__dict__"):
                    result[key] = self.dict_to_json(value.__dict__)
                else:
                    result[key] = value

        return result

    def _format_kwargs(self, kwargs):
        if self._uses_protobuf:
            formatted_kwargs = json.loads(
                json_format.MessageToJson(kwargs["request"].__dict__["_pb"])
            )
        else:
            formatted_kwargs = copy.deepcopy(kwargs)
            if provider_is_langchain(self._client_provider):
                if "response_format" in formatted_kwargs and isinstance(
                    formatted_kwargs["response_format"], object
                ):
                    """
                    We are likely processing the result of LangChain's structured
                    output runnable. The object defined in "response_format" is
                    recursive (it refers to itself) so formatting it into a dictionary
                    will result in an RecursionError. We also do not need the data in
                    this object so we are going to discard it here.
                    """

                    del formatted_kwargs["response_format"]

            formatted_kwargs = self.dict_to_json(formatted_kwargs)

        return formatted_kwargs

    def _format_payload(
        self,
        client_provider,
        client_title,
        client_version,
        start_time,
        end_time,
        query,
        response,
    ):
        response_json = self.response_to_json(response)

        payload = {
            "attribution": {
                "parent": {"id": self.config.parent_id},
                "process": {"id": self.config.process_id},
            },
            "conversation": {
                "client": {
                    "provider": client_provider,
                    "title": client_title,
                    "version": client_version,
                },
                "query": query,
                "response": response_json,
            },
            "meta": {
                "api": {"key": self.config.api_key},
                "fnfg": {
                    "exc": None,
                    "status": "succeeded",
                },
                "sdk": {"client": "python", "version": self.config.version},
            },
            "session": {"uuid": str(self.config.session_id)},
            "time": {"end": end_time, "start": start_time},
        }

        return payload

    def _format_response(self, raw_response):
        formatted_response = copy.deepcopy(raw_response)
        if self._uses_protobuf:
            if not isinstance(formatted_response, list):
                formatted_response = json.loads(
                    json_format.MessageToJson(formatted_response.__dict__["_pb"])
                )

        return formatted_response

    def get_response_content(self, raw_response):
        if (
            raw_response.__class__.__name__ == "LegacyAPIResponse"
            and raw_response.__class__.__module__ == "openai._legacy_response"
        ):
            """
            Library: langchain-openai
            Version: > 0.3.31

            Calling the chat / invoke method of the client no longer returns the JSON
            response but instead an object that looks like an API response. This
            object does not inherit from a base class we can reliably identify and
            we do not want to force the OpenAI library as a dependency.
            """

            return json.loads(raw_response.text)

        return raw_response

    def inject_conversation_messages(self, kwargs):
        if self.config.cache.conversation_id is None:
            return kwargs

        messages = self.config.driver.conversation.messages.read(
            self.config.cache.conversation_id
        )
        if len(messages) == 0:
            return kwargs

        if (
            llm_is_openai(self._client_provider, self._client_title)
            or llm_is_anthropic(self._client_provider, self._client_title)
            or llm_is_bedrock(self._client_provider, self._client_title)
        ):
            kwargs["messages"] = messages + kwargs["messages"]
        elif llm_is_google(self._client_provider, self._client_title):
            contents = []
            for message in messages:
                contents.append(
                    {"parts": [{"text": message["content"]}], "role": message["role"]}
                )

            formatted_kwargs = json.loads(
                json_format.MessageToJson(kwargs["request"].__dict__["_pb"])
            )
            formatted_kwargs["contents"] = contents + formatted_kwargs["contents"]

            json_format.ParseDict(formatted_kwargs, kwargs["request"].__dict__["_pb"])
        else:
            raise NotImplementedError

        if self.config.is_test_mode():
            pprint.pprint(kwargs)

        return kwargs

    def list_to_json(self, list_):
        result = []
        for entry in list_:
            if isinstance(entry, list):
                result.append(self.list_to_json(entry))
            elif isinstance(entry, dict):
                result.append(self.dict_to_json(entry))
            else:
                if hasattr(entry, "__dict__"):
                    result.append(self.dict_to_json(entry.__dict__))
                else:
                    result.append(entry)

        return result

    def response_to_json(self, response):
        data = response
        if isinstance(data, list):
            result = self.list_to_json(data)
        else:
            if not isinstance(data, dict):
                data = response.__dict__

            result = {}

            for key, value in data.items():
                if isinstance(value, list):
                    result[key] = self.list_to_json(value)
                elif isinstance(value, dict):
                    result[key] = self.dict_to_json(value)
                else:
                    if hasattr(value, "__dict__"):
                        result[key] = self.dict_to_json(value.__dict__)
                    else:
                        result[key] = value

        return result

    def set_client(self, provider, title, version):
        self._client_provider = provider
        self._client_title = title
        self._client_version = version
        return self

    def uses_protobuf(self):
        self._uses_protobuf = True
        return self


class BaseIterator:
    def __init__(self, config: Config, source_iterator):
        self.config = config
        self.source_iterator = source_iterator
        self.iterator = None
        self.raw_response: dict | list | None = None

    def configure_invoke(self, invoke: BaseInvoke):
        self.invoke = invoke
        return self

    def configure_request(self, kwargs, time_start):
        self._kwargs = kwargs
        self._time_start = time_start
        return self

    def process_chunk(self, chunk):
        if self.invoke._uses_protobuf is True:
            formatted_chunk = copy.deepcopy(chunk)
            if isinstance(self.raw_response, list):
                self.raw_response.append(
                    json.loads(
                        json_format.MessageToJson(formatted_chunk.__dict__["_pb"])
                    )
                )
        else:
            if isinstance(self.raw_response, dict):
                self.raw_response = merge_chunk(self.raw_response, chunk.__dict__)

        return self

    def set_raw_response(self):
        if self.raw_response is not None:
            return self

        self.raw_response = {}
        if self.invoke._uses_protobuf:
            self.raw_response = []

        return self


class BaseLlmAdaptor:
    def get_formatted_query(self, payload):
        raise NotImplementedError

    def get_formatted_response(self, payload):
        raise NotImplementedError


class BaseProvider:
    def __init__(self, parent):
        self.client = None
        self.parent = parent
        self.config = parent.config
