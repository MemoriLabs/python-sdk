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
mongo_client = MongoClient(mongo_url, server_api=ServerApi("1"))
db_name = os.getenv("MONGODB_DATABASE", "memori")


def get_db():
    """Return the MongoDB database connection."""
    return mongo_client[db_name]


if __name__ == "__main__":
    try:
        mongo_client.admin.command("ping")
        print("Database connection OK: ping=1")

        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # MEMORI SETUP
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

        # Register OpenAI client with Memori for automatic persistence
        # Pass a function that returns the database when needed
        mem = Memori(conn=get_db).openai.register(client)

        # Track conversations by user (parent_id) and session (process_id)
        mem.attribution(parent_id="12345", process_id="my-ai-bot")

        # Build database schema (creates MongoDB collections)
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
            # MongoDB writes are immediate - no commit needed
    finally:
        mongo_client.close()
