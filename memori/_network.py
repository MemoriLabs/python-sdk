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
from functools import partial

import aiohttp
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from memori._config import Config


class _ApiRetryRecoverable(Retry):
    def is_retry(self, method, status_code, has_retry_after=False):
        return 500 <= status_code <= 599


class AsyncRequest:
    def __init__(self, config: Config):
        self.config = config

    def configure_session(self, session: requests.Session):
        adapter = HTTPAdapter(
            max_retries=_ApiRetryRecoverable(
                allowed_methods=["GET", "PATCH", "POST", "PUT", "DELETE"],
                backoff_factor=self.config.request_backoff_factor,
                raise_on_status=False,
                status=None,
                total=self.config.request_num_backoff,
            )
        )

        session.mount("https://", adapter)
        session.mount("http://", adapter)

        return session

    def delete(self, url: str, **kwargs):
        return self.send("DELETE", url, **kwargs)

    def get(self, url: str, **kwargs):
        return self.send("GET", url, **kwargs)

    def patch(self, url: str, **kwargs):
        return self.send("PATCH", url, **kwargs)

    def post(self, url: str, **kwargs):
        return self.send("POST", url, **kwargs)

    def put(self, url: str, **kwargs):
        return self.send("PUT", url, **kwargs)

    def send(self, method: str, url: str, **kwargs):
        try:
            loop = asyncio.get_running_loop()

            return self.send_async(method, url, **kwargs)
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            func = partial(self.send_sync, method, url, **kwargs)

            return loop.run_until_complete(
                loop.run_in_executor(self.config.thread_pool_executor, func)
            )

    async def send_async(self, method: str, url: str, **kwargs):
        attempts = 0

        while True:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.request(
                        method.upper(),
                        url,
                        timeout=self.config.request_secs_timeout,
                        **kwargs,
                    ) as r:
                        r.raise_for_status()

                        await r.json()

                        return r
            except Exception as e:
                if isinstance(e, aiohttp.ClientResponseError):
                    if e.status < 500 or e.status > 599:
                        raise

                if attempts >= self.config.request_num_backoff:
                    raise

                sleep = self.config.request_backoff_factor * (2**attempts)
                await asyncio.sleep(sleep)
                attempts += 1

    def send_sync(self, method: str, url: str, **kwargs):
        session = self.configure_session(requests.Session())

        r = session.request(method.upper(), url, **kwargs)

        r.raise_for_status()
        return r
