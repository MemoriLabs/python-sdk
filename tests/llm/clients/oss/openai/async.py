#!/usr/bin/env python3

import argparse
import asyncio
import os

from openai import AsyncOpenAI

from memori import Memori
from tests.database.core import (
    TestDBSession,
    PostgresTestDBSession,
    MySQLTestDBSession,
    MongoTestDBSession,
)

if os.environ.get("OPENAI_API_KEY", None) is None:
    raise RuntimeError("OPENAI_API_KEY is not set")

os.environ["MEMORI_TEST_MODE"] = "1"


async def run(db_backend: str = "default"):
    # Select database session based on backend
    if db_backend == "mongodb":
        session = MongoTestDBSession
    elif db_backend == "mysql":
        session = MySQLTestDBSession()
    elif db_backend == "postgres":
        session = PostgresTestDBSession()
    else:
        session = TestDBSession()
    
    client = AsyncOpenAI()

    mem = Memori(conn=session).openai.register(client)

    # Multiple registrations should not cause an issue.
    mem.openai.register(client)

    mem.attribution(parent_id="123", process_id="456")

    print("-" * 25)

    query = "What color is the planet Mars?"
    print(f"me: {query}")
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": query}],
    )

    print("-" * 25)

    print(f"llm: {response.choices[0].message.content}")

    print("-" * 25)

    query = "That planet we're talking about, in order from the sun which one is it?"
    print(f"me: {query}")

    print("-" * 25)
    print("CONVERSATION INJECTION OCCURRED HERE!\n")

    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": query}],
    )

    print("-" * 25)

    print(f"llm: {response.choices[0].message.content}")

    print("-" * 25)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test OpenAI async client with various database backends")
    parser.add_argument(
        "--db",
        choices=["default", "postgres", "mysql", "mongodb"],
        default="default",
        help="Database backend to use (default: uses DATABASE_URL env var)"
    )
    args = parser.parse_args()
    
    asyncio.run(run(args.db))
