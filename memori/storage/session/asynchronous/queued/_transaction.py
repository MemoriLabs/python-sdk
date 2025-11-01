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

from typing import Any

from memori._config import Config


class Task:
    TASK_TYPE_COMMIT = 1
    TASK_TYPE_EXECUTE = 2
    TASK_TYPE_FLUSH = 3

    def __init__(self) -> None:
        self.args: tuple | None = None
        self.kwargs: dict | None = None
        self.type_id: int | None = None

    def commit(self) -> "Task":
        self.type_id = self.TASK_TYPE_COMMIT
        return self

    def execute(self, *args: Any, **kwargs: Any) -> "Task":
        self.args = args
        self.kwargs = kwargs
        self.type_id = self.TASK_TYPE_EXECUTE
        return self

    def flush(self) -> "Task":
        self.type_id = self.TASK_TYPE_FLUSH
        return self


class Transaction:
    def __init__(self, config: Config) -> None:
        self.config = config
        self.tasks: list[Task] = []

    def commit(self) -> "Transaction":
        self.tasks.append(Task().commit())
        return self

    def execute(self, *args: Any, **kwargs: Any) -> "Transaction":
        self.tasks.append(Task().execute(*args, **kwargs))
        return self

    def flush(self) -> "Transaction":
        self.tasks.append(Task().flush())
        return self
