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
