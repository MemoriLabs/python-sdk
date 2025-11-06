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

import asyncio
import threading
from dataclasses import dataclass, field
from typing import Any

from memori._config import Config
from memori.memory.augmentation._registry import Registry as AugmentationRegistry
from memori.storage._connection import connection_context


@dataclass
class _AugmentationRuntime:
    loop: asyncio.AbstractEventLoop | None = None
    thread: threading.Thread | None = None
    ready: threading.Event = field(default_factory=threading.Event)
    semaphore: asyncio.Semaphore | None = None
    lock: threading.Lock = field(default_factory=threading.Lock)
    max_workers: int = Config.augmentation_max_workers

    def ensure_started(self, max_workers: int) -> None:
        with self.lock:
            if self.loop is not None:
                return

            self.max_workers = max_workers
            self.thread = threading.Thread(
                target=self._run_loop, daemon=True, name="memori-augmentation"
            )
            self.thread.start()

    def _run_loop(self) -> None:
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.semaphore = asyncio.Semaphore(self.max_workers)
        self.ready.set()
        self.loop.run_forever()


_runtime = _AugmentationRuntime()


class Manager:
    def __init__(self, config: Config) -> None:
        self.config = config
        self.augmentations = AugmentationRegistry().augmentations()
        self.conn_factory = None
        self._active: bool = False

    def start(self, conn) -> "Manager":
        if conn is None:
            return self

        self.conn_factory = conn
        self._active = True
        _runtime.ensure_started(self.config.augmentation_max_workers)
        return self

    def enqueue(self, payload: dict[str, Any]) -> "Manager":
        if not self._active or not self.conn_factory:
            return self

        if not _runtime.ready.wait(timeout=1.0):
            raise RuntimeError("Augmentation runtime is not available")

        if _runtime.loop is None:
            raise RuntimeError("Event loop is not available")

        asyncio.run_coroutine_threadsafe(
            self._process_augmentations(payload), _runtime.loop
        )
        return self

    async def _process_augmentations(self, payload: dict[str, Any]) -> None:
        if not self.augmentations:
            return

        if _runtime.semaphore is None:
            return

        async with _runtime.semaphore:
            with connection_context(self.conn_factory) as (conn, adapter, driver):
                for aug in self.augmentations:
                    if aug.enabled:
                        await aug.process(payload, driver)
