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

import os
from concurrent.futures import ThreadPoolExecutor


class Cache:
    def __init__(self):
        self.conversation_id = None
        self.parent_id = None
        self.process_id = None
        self.session_id = None


class Config:
    def __init__(self):
        self.api_key = None
        self.augmentation = None
        self.cache = Cache()
        self.llm = Llm()
        self.framework = Framework()
        self.parent_id = None
        self.process_id = None
        self.raise_final_request_attempt = True
        self.request_backoff_factor = 1
        self.request_num_backoff = 5
        self.request_secs_timeout = 5
        self.session_id = None
        self.storage = None
        self.thread_pool_executor = ThreadPoolExecutor(max_workers=15)
        self.version = "3.0.0"

    def is_test_mode(self):
        return os.environ.get("MEMORI_TEST_MODE", None) is not None

    def reset_cache(self):
        self.cache = Cache()
        return self


class Framework:
    def __init__(self):
        self.provider = None


class Llm:
    def __init__(self):
        self.provider = None
        self.version = None
