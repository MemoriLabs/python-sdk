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

from typing import Any, Callable, Dict, Type

from memori.storage._base import BaseStorageAdapter


class Registry:
    _adapters: Dict[Callable[[Any], bool], Type[BaseStorageAdapter]] = {}
    _drivers: Dict[str, Type] = {}

    @classmethod
    def register_adapter(cls, matcher: Callable[[Any], bool]):
        def decorator(adapter_class: Type[BaseStorageAdapter]):
            cls._adapters[matcher] = adapter_class
            return adapter_class

        return decorator

    @classmethod
    def register_driver(cls, dialect: str):
        def decorator(driver_class: Type):
            cls._drivers[dialect] = driver_class
            return driver_class

        return decorator

    def adapter(self, conn: Any) -> BaseStorageAdapter:
        for matcher, adapter_class in self._adapters.items():
            if matcher(conn):
                return adapter_class(conn)

        raise ValueError(
            f"No adapter registered for connection type: {type(conn).__module__}"
        )

    def driver(self, conn: BaseStorageAdapter):
        dialect = conn.get_dialect()
        if dialect not in self._drivers:
            raise ValueError(
                f"No driver registered for dialect: {dialect}. "
                f"Available dialects: {list(self._drivers.keys())}"
            )
        return self._drivers[dialect](conn)
