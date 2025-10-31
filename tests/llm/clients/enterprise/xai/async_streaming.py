#!/usr/bin/env python3

import asyncio
import os

from xai_sdk import AsyncClient
from xai_sdk.chat import user

from memori import Memori
from tests.database.core import TestDBSession

if os.environ.get("XAI_API_KEY", None) is None:
    raise RuntimeError("XAI_API_KEY is not set")

os.environ["MEMORI_TEST_MODE"] = "1"
os.environ["MEMORI_API_KEY"] = "dev-no-such-key"


async def run():
    session = TestDBSession()
    client = AsyncClient(api_key=os.environ.get("XAI_API_KEY"))

    mem = Memori(conn=session).xai.register(client, stream=True)

    mem.xai.register(client, stream=True)

    mem.attribution(parent_id="123", process_id="456")

    print("-" * 25)

    query = "What color is the planet Mars?"
    print(f"me: {query}")

    print("-" * 25)
    print("COLLECTOR PAYLOAD OCCURRED HERE!\n")

    chat = client.chat.create(
        model="grok-4",
        messages=[user(query)],
    )

    response = ""
    async for item in chat.stream():
        if isinstance(item, tuple) and len(item) == 2:
            _, delta = item
            if hasattr(delta, "content") and delta.content:
                response += delta.content
        elif hasattr(item, "content") and item.content:
            response += item.content

    print("-" * 25)


if __name__ == "__main__":
    asyncio.run(run())
