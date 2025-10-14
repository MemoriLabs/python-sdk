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

import time
from collections.abc import AsyncIterator, Iterator

from botocore.eventstream import EventStream
from grpc.experimental.aio import UnaryStreamCall

from memori._network import Collector
from memori._utils import merge_chunk
from memori.llm._base import BaseInvoke
from memori.llm._iterable import Iterable as MemoriIterable
from memori.llm._iterator import AsyncIterator as MemoriAsyncIterator
from memori.llm._iterator import Iterator as MemoriIterator
from memori.llm._streaming import StreamingBody as MemoriStreamingBody


class Invoke(BaseInvoke):
    def invoke(self, **kwargs):
        start = time.time()

        kwargs = self.configure_for_streaming_usage(kwargs)

        raw_response = self._method(**kwargs)

        if isinstance(raw_response, Iterator):
            return (
                MemoriIterator(self.config, raw_response)
                .configure_invoke(self)
                .configure_request(kwargs, start)
            )
        elif self.client_is_bedrock():
            if isinstance(raw_response["body"], EventStream):
                raw_response["body"] = (
                    MemoriIterable(self.config, raw_response["body"])
                    .configure_invoke(self)
                    .configure_request(kwargs, start)
                )
            else:
                raw_response["body"] = (
                    MemoriStreamingBody(self.config, raw_response["body"])
                    .configure_invoke(self)
                    .configure_request(kwargs, start)
                )

            return raw_response
        else:
            Collector(self.config).fire_and_forget(
                self._format_payload(
                    self._client_provider,
                    self._client_title,
                    self._client_version,
                    start,
                    time.time(),
                    self._format_kwargs(kwargs),
                    self._format_response(self.get_response_content(raw_response)),
                )
            )

            return raw_response


class InvokeAsync(BaseInvoke):
    async def invoke(self, **kwargs):
        start = time.time()

        kwargs = self.configure_for_streaming_usage(kwargs)

        raw_response = await self._method(**kwargs)

        Collector(self.config).fire_and_forget(
            self._format_payload(
                self._client_provider,
                self._client_title,
                self._client_version,
                start,
                time.time(),
                self._format_kwargs(kwargs),
                self._format_response(self.get_response_content(raw_response)),
            )
        )

        return raw_response


class InvokeAsyncIterator(BaseInvoke):
    async def invoke(self, **kwargs):
        start = time.time()

        kwargs = self.configure_for_streaming_usage(kwargs)

        raw_response = await self._method(**kwargs)
        if isinstance(raw_response, AsyncIterator) or isinstance(
            raw_response, UnaryStreamCall
        ):
            return (
                MemoriAsyncIterator(self.config, raw_response)
                .configure_invoke(self)
                .configure_request(kwargs, start)
            )
        else:
            Collector(self.config).fire_and_forget(
                self._format_payload(
                    self._client_provider,
                    self._client_title,
                    self._client_version,
                    start,
                    time.time(),
                    self._format_kwargs(kwargs),
                    self._format_response(self.get_response_content(raw_response)),
                )
            )

            return raw_response


class InvokeAsyncStream(BaseInvoke):
    async def invoke(self, **kwargs):
        start = time.time()

        kwargs = self.configure_for_streaming_usage(kwargs)

        stream = await self._method(**kwargs)

        raw_response = {}
        async for chunk in stream:
            raw_response = merge_chunk(raw_response, chunk.__dict__)
            yield chunk

        Collector(self.config).fire_and_forget(
            self._format_payload(
                self._client_provider,
                self._client_title,
                self._client_version,
                start,
                time.time(),
                self._format_kwargs(kwargs),
                self._format_response(self.get_response_content(raw_response)),
            )
        )


class InvokeStream(BaseInvoke):
    async def invoke(self, **kwargs):
        start = time.time()

        kwargs = self.configure_for_streaming_usage(kwargs)

        raw_response = await self._method(**kwargs)

        Collector(self.config).fire_and_forget(
            self._format_payload(
                self._client_provider,
                self._client_title,
                self._client_version,
                start,
                time.time(),
                self._format_kwargs(kwargs),
                self._format_response(self.get_response_content(raw_response)),
            )
        )

        return raw_response
