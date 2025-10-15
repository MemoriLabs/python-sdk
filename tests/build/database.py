from core.settings import settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

test_db_core = create_engine(
    settings.SQLALCHEMY_TEST_DATABASE_URI, pool_pre_ping=True, pool_recycle=300
)
TestDBSession = sessionmaker(autocommit=False, autoflush=False, bind=test_db_core)
