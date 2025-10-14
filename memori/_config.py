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


class Config:
    def __init__(self):
        self.api_key = None
        self.metadata = None
        self.parent_id = None
        self.process_id = None
        self.raise_final_request_attempt = True
        self.secs_post_timeout = 5
        self.session_id = None
        self.version = "3.0.0"
