#!/usr/bin/env python3

import asyncio
import os

from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

from memori import Memori
from tests.database.core import TestDBSession

if os.environ.get("OPENAI_API_KEY", None) is None:
    raise RuntimeError("OPENAI_API_KEY is not set")

os.environ["MEMORI_TEST_MODE"] = "1"
os.environ["MEMORI_API_KEY"] = "dev-no-such-key"


async def main():
    session = TestDBSession
    client = ChatOpenAI(model="gpt-4.1", streaming=True)

    mem = Memori(conn=session).langchain.register(chatopenai=client)

    # Multiple registrations should not cause an issue.
    mem.langchain.register(chatopenai=client)

    mem.attribution(entity_id="123", process_id="456")

    print("-" * 25)

    query = "What color is the planet Mars?"
    print(f"me: {query}")

    print("-" * 25)
    print("COLLECTOR PAYLOAD OCCURRED HERE!\n")

    async for _ in client.astream([HumanMessage(content=query)]):
        pass

    print("-" * 25)


if __name__ == "__main__":
    asyncio.run(main())
