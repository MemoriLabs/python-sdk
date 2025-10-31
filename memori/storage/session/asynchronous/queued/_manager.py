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
import time
import weakref

from memori._config import Config
from memori.storage.session.asynchronous.queued._transaction import Task, Transaction


class Manager:
    def __init__(self, config: Config, caller):
        self.config = config
        self.queue = Queue(self.config, caller)

    def run(self, transaction: Transaction):
        return self.queue.enqueue(transaction)

    def start(self):
        return Transaction(self.config)


class Queue:
    def __init__(self, config: Config, caller):
        self.config = config
        self._loop = None
        self._running = False
        self._thread = None
        self.transactions = None
        self.worker = None

        weakref.finalize(caller, self._on_caller_finalize)

    def enqueue(self, transaction: Transaction):
        while not self._running or self._loop is None:
            time.sleep(0.001)

        coroutine = self._enqueue_coroutine(transaction)

        return asyncio.run_coroutine_threadsafe(coroutine, self._loop).result()

    async def _enqueue_coroutine(self, transaction):
        future = asyncio.get_running_loop().create_future()

        await self.transactions.put((future, transaction))

        return await future

    def _on_caller_finalize(self):
        try:
            self.stop()
        except Exception:
            pass

    def _run_loop(self):
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)

        self.transactions = asyncio.Queue()

        self.worker = self._loop.create_task(self._worker())
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

        future = asyncio.run_coroutine_threadsafe(
            self.transactions.put(None), self._loop
        )
        future.result()

        self.worker.cancel()
        self._loop.call_soon_threadsafe(self._loop.stop)
        self._thread.join()

        self._running = False

    async def _worker(self):
        while True:
            entry = await self.transactions.get()
            if entry is None:
                break

            future, transaction = entry

            try:
                if len(transaction.tasks) > 0:
                    result = None

                    for task in transaction.tasks:
                        if task.type_id == Task.TASK_TYPE_COMMIT:
                            self.config.storage.adapter.commit()
                        elif task.type_id == Task.TASK_TYPE_EXECUTE:
                            result = self.config.storage.adapter.execute(
                                *task.args, **task.kwargs
                            )
                            future.set_result(result)
                        elif task.type_id == Task.TASK_TYPE_FLUSH:
                            self.config.storage.adapter.flush()

                    await result
            except Exception as e:
                if not future.done():
                    future.set_exception(e)
            finally:
                self.transactions.task_done()
