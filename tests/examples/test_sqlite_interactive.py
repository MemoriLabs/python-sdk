"""
Interactive SQLite example for testing local memori package.

Demonstrates:
- Basic Memori integration with local SQLite database
- Automatic schema creation via mem.config.storage.build()
- Message persistence with attribution tracking
- SQLAlchemy session management
- Interactive chat loop

Requirements:
- Environment variables:
  - OPENAI_API_KEY

Behavior:
- Creates SQLite database file if it doesn't exist
- Builds Memori schema (tables for messages, conversations, etc.)
- Interactive chat loop where all messages are automatically persisted
- Each conversation tracked by parent_id and process_id
"""

import os
import sys
import tempfile

from openai import OpenAI
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from memori import Memori


def main():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set")

    os.environ["MEMORI_TEST_MODE"] = "1"

    tmp = tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False)
    db_path = tmp.name
    tmp.close()

    print(f"Using database: {db_path}")
    database_url = f"sqlite:///{db_path}"

    client = OpenAI(api_key=api_key)

    engine = create_engine(
        database_url,
        pool_pre_ping=True,
        connect_args={"check_same_thread": False, "timeout": 30},
    )

    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.close()

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    mem = Memori(conn=SessionLocal).openai.register(client)
    mem.attribution(parent_id="test_user", process_id="test_bot")

    session = mem.config.storage.conn

    print("✅ TemplateAugmentation enabled (runs in background after each response)\n")

    mem.config.storage.build()

    print("Type 'exit' or 'quit' to end the conversation.\n")
    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break

        if user_input.lower() in {"exit", "quit", ":q"}:
            print("Goodbye!")
            break
        if not user_input:
            continue

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": user_input}],
        )
        assistant_reply = response.choices[0].message.content
        print(f"\nAI: {assistant_reply}")

        session.commit()

    session.close()
    print(f"\nDatabase preserved at: {db_path}")


if __name__ == "__main__":
    main()
