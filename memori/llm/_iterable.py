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

import copy
import json
import time

from memori._config import Config
from memori._utils import bytes_to_json
from memori.llm._base import BaseInvoke
from memori.memory._manager import Manager as MemoryManager


class Iterable:
    def __init__(self, config: Config, source_iterable):
        self.config = config
        self.source_iterable = source_iterable
        self.raw_response = []

    def __getattr__(self, name):
        return getattr(self.source_iterable, name)

    def configure_invoke(self, invoke: BaseInvoke):
        self.invoke = invoke
        return self

    def configure_request(self, kwargs, time_start):
        self._kwargs = kwargs
        self._time_start = time_start

        if self.invoke.client_is_bedrock():
            self._kwargs = bytes_to_json(self._kwargs)

        return self

    def __iter__(self):
        try:
            for raw_event in self.source_iterable:
                if self.invoke.client_is_bedrock():
                    self.raw_response.append(bytes_to_json(copy.deepcopy(raw_event)))

                yield raw_event
        finally:
            MemoryManager(self.config).fire_and_forget(
                self.invoke._format_payload(
                    self.invoke._client_provider,
                    self.invoke._client_title,
                    self.invoke._client_version,
                    self._time_start,
                    time.time(),
                    self.invoke._format_kwargs(self._kwargs),
                    self.invoke._format_response(self.raw_response),
                )
            )
