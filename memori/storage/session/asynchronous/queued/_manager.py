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
import atexit
import inspect
import threading
import weakref
from typing import Any

from memori._config import Config
from memori.storage.session.asynchronous.queued._transaction import Task, Transaction


class Manager:
    def __init__(self, config: Config, caller: Any) -> None:
        self.config = config
        self.queue = Queue(self.config, caller)

    def run(self, transaction: Transaction) -> Any:
        return self.queue.enqueue(transaction)

    def start(self) -> Transaction:
        return Transaction(self.config)


class Queue:
    def __init__(self, config: Config, caller: Any) -> None:
        self.config = config
        self._loop: asyncio.AbstractEventLoop | None = None
        self._running: bool = False
        self._thread: threading.Thread | None = None
        self._ready: threading.Event = threading.Event()
        self.transactions: asyncio.Queue | None = None
        self.worker: asyncio.Task | None = None

        weakref.finalize(caller, self._on_caller_finalize)
        atexit.register(self._on_exit)

    def enqueue(self, transaction: Transaction) -> Any:
        if not self._ready.wait(timeout=10):
            raise RuntimeError("Queue failed to start within timeout")

        if self._loop is None:
            raise RuntimeError("Event loop not initialized")

        coroutine = self._enqueue_coroutine(transaction)

        return asyncio.run_coroutine_threadsafe(coroutine, self._loop).result()

    async def _enqueue_coroutine(self, transaction):
        if self.transactions is None:
            raise RuntimeError("Transactions queue not initialized")

        future = asyncio.get_running_loop().create_future()

        await self.transactions.put((future, transaction))

        return await future

    def _on_caller_finalize(self):
        try:
            self.stop()
        except Exception:
            pass

    def _on_exit(self):
        try:
            self.stop()
        except Exception:
            pass

    def _run_loop(self):
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)

        self.transactions = asyncio.Queue()

        self.worker = self._loop.create_task(self._worker())
        self._ready.set()
        self._loop.run_forever()

    def start(self):
        if self._running is True:
            return

        self._running = True
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

    def stop(self):
        if not self._running or self._loop is None:
            return

        if self.transactions is None:
            return

        future = asyncio.run_coroutine_threadsafe(
            self.transactions.put(None), self._loop
        )
        future.result()

        if self.worker is not None:
            self.worker.cancel()
        self._loop.call_soon_threadsafe(self._loop.stop)
        if self._thread is not None:
            self._thread.join()

        self._running = False

    async def _worker(self):
        if self.transactions is None:
            raise RuntimeError("Transactions queue not initialized")

        while True:
            entry = await self.transactions.get()
            if entry is None:
                break

            future, transaction = entry

            try:
                if self.config.storage is None or self.config.storage.adapter is None:
                    if not future.done():
                        future.set_result(None)
                else:
                    adapter = self.config.storage.adapter
                    result = None

                    for task in transaction.tasks:
                        if task.type_id == Task.TASK_TYPE_COMMIT:
                            adapter.commit()
                        elif task.type_id == Task.TASK_TYPE_EXECUTE:
                            args = task.args or ()
                            kwargs = task.kwargs or {}
                            result = adapter.execute(*args, **kwargs)
                            if inspect.iscoroutine(result):
                                result = await result
                        elif task.type_id == Task.TASK_TYPE_FLUSH:
                            adapter.flush()

                    if not future.done():
                        future.set_result(result)
            except Exception as e:
                if not future.done():
                    future.set_exception(e)
            finally:
                if self.transactions is not None:
                    self.transactions.task_done()
