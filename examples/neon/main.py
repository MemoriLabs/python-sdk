"""
Minimal Memori + OpenAI + Neon example using SQLAlchemy.

Demonstrates:
- SQLAlchemy ORM session management with Neon serverless Postgres
- Production-ready Neon connection with pooling
- Automatic message persistence via Memori

Requirements:
- Environment variables:
  - OPENAI_API_KEY
  - NEON_CONNECTION_STRING (e.g., postgresql://user:pass@ep-xyz-123.us-east-2.aws.neon.tech/dbname?sslmode=require)

Behavior:
- Builds schema once, commits DDL
- Runs interactive chat loop
- Commits after each LLM call to persist messages

Note: Neon is PostgreSQL-compatible, so this uses the same PostgreSQL driver (psycopg3)
"""

import os

from dotenv import load_dotenv
from openai import OpenAI
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from memori import Memori

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise RuntimeError("OPENAI_API_KEY is not set")

database_url = os.getenv("NEON_CONNECTION_STRING")
if not database_url:
    raise RuntimeError("NEON_CONNECTION_STRING is not set")

client = OpenAI(api_key=api_key)

# Neon works best with connection pooling
engine = create_engine(database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

with engine.connect() as conn:
    result = conn.execute(text("SELECT 1")).scalar_one()
    print(f"Neon database connection OK: {result}")

if __name__ == "__main__":
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # MEMORI SETUP
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    # Register OpenAI client with Memori for automatic persistence
    # Pass a function that creates a new session when needed
    mem = Memori(conn=SessionLocal).openai.register(client)

    try:
        # Track conversations by user (entity_id) and session (process_id)
        mem.attribution(entity_id="12345", process_id="my-ai-bot")

        # Build database schema (creates tables for messages, conversations, etc.)
        mem.config.storage.build()

        print("\nType 'exit' to quit.\n")
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

            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            # Use OpenAI client normally - Memori handles the rest
            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": user_input}],
            )
            assistant_reply = response.choices[0].message.content
            print(f"AI: {assistant_reply}")

            # Persist conversation to database
            mem.config.storage.adapter.commit()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if mem.config.storage.adapter:
            mem.config.storage.adapter.close()
