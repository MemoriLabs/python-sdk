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
    lambda conn: hasattr(conn, 'database') and hasattr(conn, 'list_collection_names')
)
class Adapter(BaseStorageAdapter):
    """MongoDB storage adapter for MongoDB database connections."""
    
    def execute(self, collection_name, operation, *args, **kwargs):
        """Execute MongoDB operations on a collection.
        
        Args:
            collection_name: Name of the MongoDB collection
            operation: MongoDB operation (find_one, insert_one, find, etc.)
            *args: Positional arguments for the operation
            **kwargs: Keyword arguments for the operation
        """
        collection = self.conn[collection_name]
        return getattr(collection, operation)(*args, **kwargs)

    def get_dialect(self):
        return "mongodb"
