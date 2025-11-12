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


def db_conn_factory():
    """Create a new CockroachDB connection."""
    return psycopg2.connect(database_url)


if __name__ == "__main__":
    conn = db_conn_factory()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT now()")
            res = cur.fetchall()
            conn.commit()
            print(f"Database connection OK: {res}")
    finally:
        conn.close()

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # MEMORI SETUP
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    # Register OpenAI client with Memori for automatic persistence
    # Pass a function that creates a new connection when needed
    mem = Memori().openai.register(client)

    mem.attribution(parent_id="user_123", process_id="astronomer_agent")

    print()

    user_msg_1 = "What color is Mars?"
    print(f"User: {user_msg_1}")
    response = client.chat.completions.create(
        model="gpt-4o-mini", messages=[{"role": "user", "content": user_msg_1}]
    )
    print(f"AI: {response.choices[0].message.content}\n")

    user_msg_2 = (
        "That planet we are talking about, in order from the sun, which one is it?"
    )
    print(f"User: {user_msg_2}")
    response = client.chat.completions.create(
        model="gpt-4o-mini", messages=[{"role": "user", "content": user_msg_2}]
    )
    print(f"AI: {response.choices[0].message.content}")
