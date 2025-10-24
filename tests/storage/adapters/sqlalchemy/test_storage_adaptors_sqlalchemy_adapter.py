from memori.storage.adapters.sqlalchemy._adapter import Adapter as SqlAlchemyAdapter
from memori.storage.adapters.mongodb._adapter import Adapter as MongoAdapter


def test_commit(session):
    adapter = SqlAlchemyAdapter(session)
    adapter.commit()


def test_execute(session):
    adapter = SqlAlchemyAdapter(session)

    assert adapter.execute("select 1 from dual").mappings().fetchone() == {"1": 1}


def test_flush(session):
    adapter = SqlAlchemyAdapter(session)
    adapter.flush()


def test_get_dialect(session):
    adapter = SqlAlchemyAdapter(session)
    assert adapter.get_dialect() == "mysql"


def test_rollback(session):
    adapter = SqlAlchemyAdapter(session)
    adapter.rollback()


# PostgreSQL tests
def test_commit_postgres(postgres_session):
    adapter = SqlAlchemyAdapter(postgres_session)
    adapter.commit()


def test_execute_postgres(postgres_session):
    adapter = SqlAlchemyAdapter(postgres_session)

    assert adapter.execute("select 1 as one").mappings().fetchone() == {"one": 1}


def test_flush_postgres(postgres_session):
    adapter = SqlAlchemyAdapter(postgres_session)
    adapter.flush()


def test_get_dialect_postgres(postgres_session):
    adapter = SqlAlchemyAdapter(postgres_session)
    assert adapter.get_dialect() == "postgresql"


def test_rollback_postgres(postgres_session):
    adapter = SqlAlchemyAdapter(postgres_session)
    adapter.rollback()


# MongoDB tests
def test_mongodb_adapter_execute(mongodb_conn):
    """Test MongoDB adapter execute method."""
    adapter = MongoAdapter(mongodb_conn)
    
    # Test find_one operation
    result = adapter.execute("test_collection", "find_one", {"test": "value"})
    # The mock should return the mocked result
    
    # Test insert_one operation
    result = adapter.execute("test_collection", "insert_one", {"test": "value"})
    # The mock should return the mocked result


def test_mongodb_adapter_get_dialect(mongodb_conn):
    """Test MongoDB adapter get_dialect method."""
    adapter = MongoAdapter(mongodb_conn)
    assert adapter.get_dialect() == "mongodb"


def test_mongodb_adapter_execute_with_args(mongodb_conn):
    """Test MongoDB adapter execute method with various arguments."""
    adapter = MongoAdapter(mongodb_conn)
    
    # Test find operation with projection
    result = adapter.execute("test_collection", "find", {"test": "value"}, {"field": 1, "_id": 0})
    
    # Test delete_many operation
    result = adapter.execute("test_collection", "delete_many", {"test": "value"})


def test_mongodb_adapter_execute_with_kwargs(mongodb_conn):
    """Test MongoDB adapter execute method with keyword arguments."""
    adapter = MongoAdapter(mongodb_conn)
    
    # Test update_one with upsert
    result = adapter.execute("test_collection", "update_one", 
                           {"test": "value"}, 
                           {"$set": {"updated": True}}, 
                           upsert=True)