r"""
 __  __                           _
|  \/  | ___ _ __ ___   ___  _ __(_)
| |\/| |/ _ \ '_ ` _ \ / _ \| '__| |
| |  | |  __/ | | | | | (_) | |  | |
|_|  |_|\___|_| |_| |_|\___|_|  |_|
                  perfectam memoriam
                         by GibsonAI
                       memorilabs.ai
"""

from memori.storage._base import BaseStorageAdapter
from memori.storage._registry import Registry


@Registry.register_adapter(
    lambda conn: hasattr(conn, "database") and hasattr(conn, "list_collection_names")
)
class Adapter(BaseStorageAdapter):
    """MongoDB storage adapter for MongoDB database connections."""

    def execute(self, collection_name_or_code, operation=None, *args, **kwargs):
        """Execute MongoDB operations.

        Args:
            collection_name_or_code: Collection name or MongoDB shell code string
            operation: MongoDB operation (find_one, insert_one, etc.) - optional
            *args: Positional arguments for the operation
            **kwargs: Keyword arguments for the operation
        """
        db = self.conn

        if operation is None:
            exec(collection_name_or_code.strip(), {"db": db})
            return None

        collection = db[collection_name_or_code]
        return getattr(collection, operation)(*args, **kwargs)

    def commit(self):
        """MongoDB doesn't require explicit commits for single operations."""
        pass

    def flush(self):
        """MongoDB doesn't require explicit flushes for single operations."""
        pass

    def rollback(self):
        """MongoDB doesn't require explicit rollbacks for single operations."""
        pass

    def get_dialect(self):
        return "mongodb"
