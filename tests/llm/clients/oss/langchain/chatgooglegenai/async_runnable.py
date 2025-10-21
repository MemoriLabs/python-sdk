#!/usr/bin/env python3

import asyncio
import os

from database.core import TestDBSession
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

from memori import Memori

if os.environ.get("GOOGLE_API_KEY", None) is None:
    raise RuntimeError("GOOGLE_API_KEY is not set")

os.environ["MEMORI_TEST_MODE"] = "1"


async def main():
    session = TestDBSession()
    client = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
    prompt = ChatPromptTemplate.from_messages(
        [
            ("human", "{question}"),
        ]
    )
    chain = prompt | client | StrOutputParser()

    mem = Memori(conn=session).langchain.register(chatgooglegenai=client)

    # Multiple registrations should not cause an issue.
    mem.langchain.register(chatgooglegenai=client)

    mem.attribution(parent_id="123", process_id="456")

    print("-" * 25)

    query = "What color is the planet Mars?"
    print(f"me: {query}")

    print("-" * 25)

    async for chunk in chain.astream({"question": query}):
        print(chunk, end="", flush=True)

    print("-" * 25)

    query = "That planet we're talking about, in order from the sun which one is it?"
    print(f"me: {query}")

    print("-" * 25)
    print("CONVERSATION INJECTION OCCURRED HERE!\n")

    async for chunk in chain.astream({"question": query}):
        print(chunk, end="", flush=True)

    print("-" * 25)


if __name__ == "__main__":
    asyncio.run(main())
