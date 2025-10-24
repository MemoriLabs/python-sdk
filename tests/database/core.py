import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pymongo import MongoClient

# Default test session - uses DATABASE_URL environment variable
# Falls back to PostgreSQL for backward compatibility
test_db_uri = os.environ.get(
    "DATABASE_URL",
    "postgresql://memori:memori@postgres:5432/memori_test"
)

test_db_core = create_engine(
    test_db_uri,
    pool_pre_ping=True,
    pool_recycle=300
)

TestDBSession = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_db_core
)

# PostgreSQL-specific session
postgres_test_uri = os.environ.get(
    "POSTGRES_DATABASE_URL",
    "postgresql://memori:memori@postgres:5432/memori_test"
)

postgres_test_db_core = create_engine(
    postgres_test_uri,
    pool_pre_ping=True,
    pool_recycle=300
)

PostgresTestDBSession = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=postgres_test_db_core
)

# MySQL-specific session
mysql_test_uri = os.environ.get(
    "MYSQL_DATABASE_URL",
    "mysql+pymysql://memori:memori@mysql:3306/memori_test"
)

mysql_test_db_core = create_engine(
    mysql_test_uri,
    pool_pre_ping=True,
    pool_recycle=300
)

MySQLTestDBSession = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=mysql_test_db_core
)

# MongoDB-specific session
mongodb_test_uri = os.environ.get(
    "MONGODB_URL",
    "mongodb://memori:memori@mongodb:27017/memori_test?authSource=admin"
)

MongoTestDBSession = MongoClient(mongodb_test_uri)
