#!/usr/bin/env python3

import asyncio
import os

import anthropic

from memori import Memori
from tests.database.core import TestDBSession

if os.environ.get("ANTHROPIC_API_KEY", None) is None:
    raise RuntimeError("ANTHROPIC_API_KEY is not set")

os.environ["MEMORI_TEST_MODE"] = "1"
os.environ["MEMORI_API_KEY"] = "dev-no-such-key"


async def run():
    session = TestDBSession
    client = anthropic.AsyncAnthropic()

    mem = Memori(conn=session).anthropic.register(client)

    # Multiple registrations should not cause an issue.
    mem.anthropic.register(client)

    mem.attribution(parent_id="123", process_id="456")

    print("-" * 25)

    query = "What color is the planet Mars?"
    print(f"me: {query}")

    print("-" * 25)
    print("COLLECTOR PAYLOAD OCCURRED HERE!\n")

    await client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        messages=[{"role": "user", "content": query}],
    )

    print("-" * 25)


if __name__ == "__main__":
    asyncio.run(run())
