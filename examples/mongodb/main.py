"""
Minimal Memori + OpenAI + MongoDB example using PyMongo.

Demonstrates:
- Memori integration with NoSQL document database
- MongoDB Atlas cloud connection
- Document-based message storage
- Schema-less persistence for flexible data models

Requirements:
- Environment variables:
  - OPENAI_API_KEY
  - MONGODB_CONNECTION_STRING (e.g., mongodb+srv://user:pass@cluster/dbname?retryWrites=true&w=majority)
  - Optional: MONGODB_DATABASE (used if URL has no default database)

Behavior:
- Verifies MongoDB connection with ping command
- Initializes Memori collections (messages, conversations, etc.)
- Interactive chat with document-based persistence
- Messages stored as flexible JSON documents
"""

import os

import certifi
from dotenv import load_dotenv
from openai import OpenAI
from pymongo import MongoClient
from pymongo.server_api import ServerApi

from memori import Memori

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise RuntimeError("OPENAI_API_KEY is not set")

mongo_url = os.getenv("MONGODB_CONNECTION_STRING")
if not mongo_url:
    raise RuntimeError("MONGODB_CONNECTION_STRING is not set")

client = OpenAI(api_key=api_key)
mongo_client = MongoClient(
    mongo_url, server_api=ServerApi("1"), tlsCAFile=certifi.where()
)
db_name = os.getenv("MONGODB_DATABASE", "memori")
db = mongo_client[db_name]

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# FIX FOR PYMONGO + MEMORI ADAPTER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PyMongo Database objects treat any attribute access as a Collection.
# Memori's adapter checks hasattr(conn, "get_default_database") which returns
# a Collection object (interpreting it as True), then tries to call it.
# This monkeypatch ensures get_default_database returns the database itself.
db.get_default_database = lambda: db

mongo_client.admin.command("ping")
print("Database connection OK: ping=1")

if __name__ == "__main__":
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # MEMORI SETUP
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    # Register OpenAI client with Memori for automatic persistence
    # Pass the database object - Memori will wrap it in a factory internally
    mem = Memori(conn=db).openai.register(client)

    try:
        # Track conversations by user (entity_id) and session (process_id)
        mem.attribution(entity_id="12345", process_id="my-ai-bot")

        # Build database schema (creates MongoDB collections)
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
    except Exception as e:
        print(f"Error: {e}")
    finally:
        mongo_client.close()
