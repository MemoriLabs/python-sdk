from memori.storage.adaptors.sqlalchemy._adaptor import Adaptor


def test_commit(session):
    adaptor = Adaptor(session)
    adaptor.commit()


def test_execute(session):
    adaptor = Adaptor(session)

    assert adaptor.execute("select 1 from dual").mappings().fetchone() == {"1": 1}


def test_flush(session):
    adaptor = Adaptor(session)
    adaptor.flush()


def test_get_dialect(session):
    adaptor = Adaptor(session)
    assert adaptor.get_dialect() == "mysql"


def test_rollback(session):
    adaptor = Adaptor(session)
    adaptor.rollback()
