from tests.database.core import TestDBSession
from memori import Memori


def init_db():
    try:
        session = TestDBSession()
        mem = Memori(conn=session)
        mem.storage.build()
        print("Database schema initialized successfully")
        return True
    except Exception as e:
        print(f"Failed to initialize database: {e}")
        return False


if __name__ == "__main__":
    init_db()
