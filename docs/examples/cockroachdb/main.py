"""
Minimal Memori + OpenAI + CockroachDB example using psycopg2.

Demonstrates:
- Memori integration with distributed SQL (CockroachDB)
- Raw psycopg2 driver usage (non-ORM)
- SSL-enabled connection for production security
- Message persistence across distributed database nodes

Requirements:
- Environment variables:
  - OPENAI_API_KEY
  - COCKROACH_CONNECTION_STRING (e.g., postgresql://user:pass@host:port/db?sslmode=require)

Behavior:
- Verifies CockroachDB connection with test query
- Builds Memori schema (distributed across cluster)
- Interactive chat with automatic persistence
- Transactions committed after each LLM interaction
"""

import os

import psycopg2
from dotenv import load_dotenv
from openai import OpenAI

from memori import Memori

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise RuntimeError("OPENAI_API_KEY is not set")

database_url = os.getenv("COCKROACH_CONNECTION_STRING")
if not database_url:
    raise RuntimeError("COCKROACH_CONNECTION_STRING is not set")

client = OpenAI(api_key=api_key)
conn = psycopg2.connect(database_url)


def get_connection():
    """Return the CockroachDB connection."""
    return conn


if __name__ == "__main__":
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT now()")
            res = cur.fetchall()
            conn.commit()
            print(f"Database connection OK: {res}")

        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # MEMORI SETUP
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

        # Register OpenAI client with Memori for automatic persistence
        # Pass a function that returns the connection when needed
        mem = Memori(conn=get_connection).openai.register(client)

        # Track conversations by user (parent_id) and session (process_id)
        mem.attribution(parent_id="12345", process_id="my-ai-bot")

        # Build database schema (distributed across CockroachDB cluster)
        mem.storage.build()

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

            # Commit distributed transaction
            conn.commit()
    finally:
        conn.close()
