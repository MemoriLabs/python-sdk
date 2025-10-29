#!/usr/bin/env python3

import asyncio
import os

from google import genai

from memori import Memori
from tests.database.core import TestDBSession

if os.environ.get("GEMINI_API_KEY", None) is None:
    raise RuntimeError("GEMINI_API_KEY is not set")

os.environ["MEMORI_TEST_MODE"] = "1"
os.environ["MEMORI_API_KEY"] = "dev-no-such-key"


async def main():
    session = TestDBSession()
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

    mem = Memori(conn=session).google.register(client)

    # Multiple registrations should not cause an issue.
    mem.google.register(client)

    mem.attribution(parent_id="123", process_id="456")

    print("-" * 25)

    query = "What color is the planet Mars?"
    print(f"me: {query}")

    print("-" * 25)
    print("COLLECTOR PAYLOAD OCCURRED HERE!\n")

    async for _chunk in await client.aio.models.generate_content_stream(
        model="gemini-2.0-flash",
        contents=[{"role": "user", "parts": [{"text": query}]}],
    ):
        pass

    print("-" * 25)


if __name__ == "__main__":
    asyncio.run(main())
