from memori.storage.adapters.sqlalchemy._adapter import Adapter


def test_commit(session):
    adapter = Adapter(session)
    adapter.commit()


def test_execute(session):
    adapter = Adapter(session)

    assert adapter.execute("select 1 from dual").mappings().fetchone() == {"1": 1}


def test_flush(session):
    adapter = Adapter(session)
    adapter.flush()


def test_get_dialect(session):
    adapter = Adapter(session)
    assert adapter.get_dialect() == "mysql"


def test_rollback(session):
    adapter = Adapter(session)
    adapter.rollback()


# PostgreSQL tests
def test_commit_postgres(postgres_session):
    adapter = Adapter(postgres_session)
    adapter.commit()


def test_execute_postgres(postgres_session):
    adapter = Adapter(postgres_session)

    assert adapter.execute("select 1 as one").mappings().fetchone() == {"one": 1}


def test_flush_postgres(postgres_session):
    adapter = Adapter(postgres_session)
    adapter.flush()


def test_get_dialect_postgres(postgres_session):
    adapter = Adapter(postgres_session)
    assert adapter.get_dialect() == "postgresql"


def test_rollback_postgres(postgres_session):
    adapter = Adapter(postgres_session)
    adapter.rollback()
