#!/usr/bin/env python3

import asyncio
import os

from openai import AsyncOpenAI

from memori import Memori
from tests.database.core import TestDBSession

if os.environ.get("OPENAI_API_KEY", None) is None:
    raise RuntimeError("OPENAI_API_KEY is not set")

os.environ["MEMORI_TEST_MODE"] = "1"
os.environ["MEMORI_API_KEY"] = "dev-no-such-key"


async def run():
    session = TestDBSession
    client = AsyncOpenAI()

    mem = Memori(conn=session).openai.register(client, stream=True)

    # Multiple registrations should not cause an issue.
    mem.openai.register(client)

    mem.attribution(parent_id="123", process_id="456")

    print("-" * 25)

    query = "What color is the planet Mars?"
    print(f"me: {query}")

    print("-" * 25)
    print("COLLECTOR PAYLOAD OCCURRED HERE!\n")

    response = ""
    async for chunk in client.chat.completions.create(
        model="gpt-4o-mini", messages=[{"role": "user", "content": query}], stream=True
    ):
        try:
            if chunk.choices[0].delta.content is not None:
                response += chunk.choices[0].delta.content
        except IndexError:
            pass

    print("-" * 25)


if __name__ == "__main__":
    asyncio.run(run())
