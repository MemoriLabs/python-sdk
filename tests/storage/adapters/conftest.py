from unittest.mock import MagicMock, Mock

import pytest


@pytest.fixture
def mongodb_conn():
    """Create a mock MongoDB database connection."""
    # Mock MongoDB database connection
    mock_db = MagicMock()
    mock_db.database = MagicMock()
    mock_db.list_collection_names = MagicMock(return_value=["test_collection"])
    
    # Mock collection
    mock_collection = MagicMock()
    mock_collection.find_one = MagicMock(return_value={"test": "value"})
    mock_collection.insert_one = MagicMock(return_value=MagicMock(inserted_id="507f1f77bcf86cd799439011"))
    mock_collection.find = MagicMock(return_value=[{"test": "value"}])
    mock_collection.delete_many = MagicMock(return_value=MagicMock(deleted_count=1))
    mock_collection.update_one = MagicMock(return_value=MagicMock(modified_count=1))
    
    # Mock database to return collection when accessed with []
    mock_db.__getitem__ = MagicMock(return_value=mock_collection)
    
    return mock_db
