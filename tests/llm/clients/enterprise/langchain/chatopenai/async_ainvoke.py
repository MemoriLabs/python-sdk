#!/usr/bin/env python3

import asyncio
import os

from database.core import TestDBSession
from langchain_community.chat_models import ChatOpenAI
from langchain_core.messages import HumanMessage

from memori import Memori

if os.environ.get("OPENAI_API_KEY", None) is None:
    raise RuntimeError("OPENAI_API_KEY is not set")

os.environ["MEMORI_TEST_MODE"] = "1"
os.environ["MEMORI_API_KEY"] = "dev-no-such-key"


async def run():
    session = TestDBSession()
    client = ChatOpenAI(model="gpt-4.1", streaming=True)
    message = HumanMessage(content="What color is the planet Mars?")

    mem = Memori(conn=session).langchain.register(chatopenai=client)

    # Multiple registrations should not cause an issue.
    mem.langchain.register(chatopenai=client)

    mem.attribution(parent_id="123", process_id="456")

    print("-" * 25)
    print("me: What color is the planet Mars?")

    print("-" * 25)
    print("COLLECTOR PAYLOAD OCCURRED HERE!\n")

    await client.ainvoke([message])

    print("-" * 25)


if __name__ == "__main__":
    asyncio.run(run())
