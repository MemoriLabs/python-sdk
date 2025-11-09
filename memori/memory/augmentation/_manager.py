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
from typing import Any

from memori._config import Config
from memori.memory.augmentation._base import AugmentationContext
from memori.memory.augmentation._db_writer import WriteTask, get_db_writer
from memori.memory.augmentation._registry import Registry as AugmentationRegistry
from memori.memory.augmentation._runtime import get_runtime
from memori.storage._connection import connection_context


class Manager:
    def __init__(self, config: Config) -> None:
        self.config = config
        self.augmentations = AugmentationRegistry().augmentations()
        self.conn_factory = None
        self._active = False
        self.max_workers = 50
        self.db_writer_batch_size = 100
        self.db_writer_batch_timeout = 0.1
        self.db_writer_queue_size = 1000

    def start(self, conn) -> "Manager":
        if conn is None:
            return self

        self.conn_factory = conn
        self._active = True

        runtime = get_runtime()
        runtime.ensure_started(self.max_workers)

        db_writer = get_db_writer()
        db_writer.configure(self)
        db_writer.ensure_started(conn)

        return self

    def enqueue(self, payload: dict[str, Any]) -> "Manager":
        if not self._active or not self.conn_factory:
            return self

        runtime = get_runtime()

        if not runtime.ready.wait(timeout=1.0):
            raise RuntimeError("Augmentation runtime is not available")

        if runtime.loop is None:
            raise RuntimeError("Event loop is not available")

        asyncio.run_coroutine_threadsafe(
            self._process_augmentations(payload), runtime.loop
        )
        return self

    async def _process_augmentations(self, payload: dict[str, Any]) -> None:
        if not self.augmentations:
            return

        runtime = get_runtime()
        if runtime.semaphore is None:
            return

        async with runtime.semaphore:
            ctx = AugmentationContext(payload=payload)

            with connection_context(self.conn_factory) as (conn, adapter, driver):
                for aug in self.augmentations:
                    if aug.enabled:
                        ctx = await aug.process(ctx, driver)

                if ctx.writes:
                    self._enqueue_writes(ctx.writes)

    def _enqueue_writes(self, writes: list[dict[str, Any]]) -> None:
        db_writer = get_db_writer()

        for write_op in writes:
            task = WriteTask(
                method_path=write_op["method_path"],
                args=write_op["args"],
                kwargs=write_op["kwargs"],
            )
            db_writer.enqueue_write(task)
